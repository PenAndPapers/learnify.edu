---
alwaysApply: false
description: Use when writing Dockerfiles, docker-compose services, Nginx configs, PostgreSQL/Redis/Mailpit infrastructure, Makefile targets, environment variables, or CI deployment scripts.
globs:
  - "docker-compose*.yml"
  - "docker-compose*.yaml"
  - "**/Dockerfile"
  - "infra/**/*"
  - "Makefile"
  - "**/Makefile"
  - ".env.local"
  - ".github/**/*"
---

# Infrastructure & DevOps Rules & Standards

## 1. Core Stack & Principles
- **Container Runtime:** Docker Engine + Docker Compose v2 (plain `docker compose`, not legacy `docker-compose` binary).
- **Image Policy:** Use minimal, pinned base images. Prefer `python:3.12-slim` for the API, `node:22-alpine` for the frontend builder/runtime and Nginx, `postgres:15`, `redis:7`, `axllent/mailpit:latest`. Images must match the versions already in use across the existing Dockerfiles — do not bump major versions without a tracked migration.
- **Security:** Never run application containers as root when avoidable. The `api` service already uses `user: "${UID:-1000}:${GID:-1000}"` to match host file ownership. Do not hardcode secrets, tokens, or credentials in Dockerfiles, YAML, or committed scripts — use the single shared `.env` file pattern defined below.
- **Non-Repeatability:** Prefer locked dependency manifests (`requirements.txt` compiled via `uv pip compile pyproject.toml --extra dev -o requirements.txt`; `pnpm-lock.yaml` with `pnpm install --frozen-lockfile`) inside Dockerfiles so builds are reproducible.
- **Single Responsibility Principle (SRP) of compose services:** Every container runs exactly one logical service: `gateway`, `api`, `database`, `cache`, `mailpit`.

---

## 2. Directory & File Structure

```text
my-project/
├── backend/fastapi/
│   └── Dockerfile              # Python API (slim, pip install from requirements.txt)
├── frontend/nuxt4/
│   └── Dockerfile              # Multi-stage Nuxt 4 (builder → node runner)
├── infra/
│   ├── postgres/
│   │   ├── Dockerfile          # postgres:15 + COPY init.sql
│   │   └── init.sql            # Startup DDL/bootstrap (rare; schema lives in Alembic!)
│   ├── redis/
│   │   └── Dockerfile          # redis:7 base + optional redis.conf
│   ├── nginx/
│   │   ├── Dockerfile          # nginx:1.25-alpine, delete default.conf, COPY our conf
│   │   └── nginx.conf          # Rate-limiting, proxy_set_header forwarding rules
│   └── mailpit/
│       └── Dockerfile          # axllent/mailpit, EXPOSE 1025 8025
├── Makefile                    # Root-level orchestration (sub-make invocations)
├── docker-compose.yml          # All services, profiles, healthchecks, named volumes
└── .env                        # SINGLE global env file. Never scatter per-service .env files!
```

**Rules for files outside their folders:**
- Do NOT create `docker-compose.override.yml` unless the feature explicitly requires developer-specific overrides that must not ship in the repo.
- Do NOT create an `.env` in `backend/fastapi/`, `frontend/nuxt4/`, or `infra/*/`. All env lives in the single repo-root `.env`.

---

## 3. docker-compose.yml Standards

### A. Service Naming & Hostname Convention
Internal Docker DNS names (the compose service names) MUST match the canonical hostnames already referenced in code and `.env`:
- `api`        — FastAPI app, internal port `8000`
- `database`   — PostgreSQL, internal port `5432`
- `cache`      — Redis, internal port `6379`
- `gateway`    — Nginx, published host port `80:80`
- `mailpit`    — Mailpit UI port `9080:8025`, published SMTP `1025` exposed only to compose network

**Never use `localhost` inside compose service URLs.** Backend code, compose env vars, and Nginx `proxy_pass` all reference the bare service DNS name above: e.g. `POSTGRES_HOST=database`, `proxy_pass http://api:8000;`.

### B. Profiles
Use compose profiles to gate services so the repo supports 3 launch modes:
- `backend` (gateway + api + database + cache + mailpit) — bootable via `backend/fastapi/Makefile` `docker-up` target
- `frontend` — reserved for the future Nuxt 4 container (or static build served by gateway)
- `fullstack` — union of both

If you add a new service, document which profile(s) include it. Services without a `profiles:` key are always-on (typical for `database`/`cache`).

### C. Build Context & Dockerfile Location
- Narrow `build.context` to the owning folder:
  - `api`: `context: ./backend/fastapi`, `dockerfile: Dockerfile`
  - `gateway`/stateful services in `infra/`: `context: .` (so they can COPY files from `infra/**`)
- The `Dockerfile` path in `build.dockerfile` is **relative** to `build.context`.

### D. Volumes
Two volume patterns are used — DO NOT mix them up:
1. **Named volumes for persistent state:** `database_data`, `cache_data`, `mailpit_data`. Declared at the bottom of compose under the top-level `volumes:` key. Bind these to the DB/Redis/Mailpit data directories.
2. **Bind mounts for hot-reload dev loops:** `./backend/fastapi/app:/app/app` (mounts source into running `api` container). Mount the single global `.env` as read-only: `./.env:/app/.env:ro`. **Never do full-root bind mounts like `./backend/fastapi:/app`** — that shadows the container's installed `site-packages` and breaks the build.

### E. depends_on + Healthchecks
Stateful services and the API must have healthchecks:
- `database`: `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` (interval 5s, `start_period: 5s`)
- `cache`: `redis-cli ping`
- `api`: `curl -f http://localhost:8000/api/v1/system/check-health` (interval 10s, 3 retries)
- `gateway → depends_on.api.condition: service_healthy` so Nginx never starts proxying before routes are live.
- `api → depends_on.database.condition: service_healthy` so alembic never runs before Postgres accepts connections.

### F. Command + Startup Duties
The `api` service command runs migrations before starting the server — **never remove the alembic step** from the command or developers will silently run against stale schemas:

```yaml
command: >
  sh -c "alembic upgrade head &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

Future `frontend` container: choose one startup mode and stick with it. Dev = `pnpm dev --host 0.0.0.0 --port 3000`. Prod = multi-stage build output (`node .output/server/index.mjs`).

### G. Environment + File Ownership
All compose-injected env vars reference `${VAR_NAME}` from the single root `.env` file. The `api` container injects UID/GID override via `user: "${UID:-1000}:${GID:-1000}"` to prevent host-mounted files from being owned by root. Match this ownership pattern for any new service that writes to a bind mount.

---

## 4. Dockerfile Standards

### A. FastAPI Backend Dockerfile (`backend/fastapi/Dockerfile`)
- **Base:** `FROM python:3.12-slim`. Pin major.minor, never `python:slim` unversioned.
- **Packages:** `apt-get install` → always `--no-install-recommends`, **always** `rm -rf /var/lib/apt/lists/*` in the same RUN to keep image small.
- **Layer order for caching:** Copy lockfiles FIRST → install → copy source LAST. Current order is correct: `COPY requirements.txt .` → `pip install --no-cache-dir` → `COPY . .`. Do NOT flip them.
- **Pathing:** Set `WORKDIR /app` and `ENV PYTHONPATH=/app` so imports match the host layout.
- **No secrets in COPY:** Dockerfiles must NEVER COPY `.env` or key files. Inject secrets via compose env + read-only `.env` bind mount.

### B. Nuxt 4 Frontend Dockerfile (`frontend/nuxt4/Dockerfile`)
- **Pattern:** Multi-stage `builder` + `runner` using `node:22-alpine` for both (consistent Node ABI).
- **Corepack + pnpm:** `corepack enable && corepack prepare pnpm@latest --activate` in the builder stage. Use `pnpm install --frozen-lockfile` so build uses the lockfile.
- **Cache layering:** Copy `pnpm-lock.yaml` + `package.json` before `COPY . .`.
- **Runtime stage:** Copy ONLY `--from=builder /app/.output ./.output`. Never copy source, lockfile, or node_modules into the runner image. `ENV NODE_ENV=production`.
- **Expose:** `EXPOSE 3000`. CMD runs the Nitro standalone entrypoint: `["node", ".output/server/index.mjs"]`.

### C. Stateful Infrastructure Dockerfiles (postgres/redis/nginx/mailpit)
- Keep them thin. Don't apt-get install extra tooling inside a `postgres:15` or `redis:7` image.
- `init.sql` for Postgres only lives in `infra/postgres/docker-entrypoint-initdb.d/` via COPY. Alembic owns migrations — `init.sql` is for one-time DB bootstrap extension installs or grants, never for table DDL.
- Nginx Dockerfile removes the default site with `RUN rm /etc/nginx/conf.d/default.conf` before COPYing our `nginx.conf` over the top. Keep that pattern.
- Mailpit: EXPOSE both `1025` (SMTP) and `8025` (Web UI). Configure Mailpit DB path with an env var (`MP_DATABASE=/data/mailpit.db`) and mount a named volume there for message persistence between restarts.

---

## 5. Nginx / Gateway (`infra/nginx/nginx.conf`)

### A. Reverse Proxy Rules
- **`server_tokens off;`** always — never leak Nginx versions.
- **`proxy_set_header`** full set on every proxied location: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`. Backend application code MUST trust these values (not the raw connect IP).
- **Port exposure strategy:** Only the `gateway` container publishes `80` to the host. Backend API and DB ports are accessible on host ONLY for debugging (compose `ports:` publishes them but their security posture is secondary — main security boundary is Nginx).
- **Rate limiting:** Already present as `limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;`. Apply it with `limit_req zone=api_limit burst=5 nodelay; limit_req_status 429;` on every proxied backend location. Do not remove rate limiting from `/`. If you split `/api` from `/` routing in future, apply the zone to both roots that hit backend logic.

### B. Future Frontend + API Split (Reference)
When the frontend container is added, keep this template in mind:
```
location /api/ {
    # rate-limit + proxy_set_header + proxy_pass http://api:8000;
}
location /_nuxt/ {
    # static long-cache + proxy_pass http://frontend:3000;
}
location / {
    # proxy_pass http://frontend:3000; (SSR/SPA fallback)
}
```

---

## 6. PostgreSQL, Redis, Mailpit Infrastructure Rules

### A. Postgres
- Version: `postgres:15`. User, password, and DB name come from env. Credentials in `.env` only.
- Named volume mount: `database_data:/var/lib/postgresql/data`. Never bind-mount a host folder for Postgres data — cross-platform FS incompatibility corrupts tables.
- `init.sql` exists for one-time bootstrap only. All tables, indexes, enums, and DDL schema changes ship via **Alembic migrations** (`backend/fastapi/app/migrations/versions/`). Do NOT add table DDL to `init.sql`.
- Publish `5432` to host (`"${POSTGRES_PORT}:5432"`) for debugging tools — prod deployments should drop this.

### B. Redis
- Version: `redis:7`. Named volume `cache_data:/data`.
- Default config is acceptable for dev; if you drop in a `redis.conf`, enable it via `CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]` (comments in current Dockerfile mark the spot).
- Hostname env in global `.env`: `REDIS_HOST=cache`. Code must use the service DNS, not localhost.

### C. Mailpit (Dev Email Capture)
- Image: `axllent/mailpit:latest`.
- Ports: Publish `9080:8025` for the browser inbox, expose only `1025` to the compose network for SMTP.
- Environment: Set `MP_MAX_MESSAGES=500` and `MP_DATABASE=/data/mailpit.db`. Mount a `mailpit_data` named volume to `/data`.
- SMTP env in global `.env`: `SMTP_HOST=mailpit`, `SMTP_PORT=1025`.
- In dev, Mailpit accepts any username/password — make it explicit that backend email config MUST read host/port/user/pass from env, never hardcode. Dev `.env.local` intentionally leaves SMTP credentials blank; that's valid for Mailpit.
- Production: Replace this service entirely with a real transactional provider (SES, SendGrid, Postmark, Resend). Do not ship Mailpit to production.

---

## 7. Single Global .env Rules

All environment configuration lives in exactly one file: **`${REPO_ROOT}/.env`**.

### A. Rules
- `.env` is gitignored via the root `.gitignore`. Never commit it. Developers create their own by copying `.env.local` and editing secrets.
- `.env.local` IS committed to the repo and is the canonical list of all env vars the project needs. Every variable used in compose or in code via `pydantic-settings` must appear in `.env.local` with a documented safe default.
- Never add per-service env files (`backend/fastapi/.env`, `frontend/nuxt4/.env`). If a framework demands one, document that the real source of truth is the root `.env` and inject it via compose bind mount or a symlink you delete from git history.
- Naming conventions:
  - Use `SCREAMING_SNAKE_CASE`
  - Prefix cluster variables correctly: `POSTGRES_*`, `REDIS_*`, `SMTP_*`, `EMAILS_*`, `API_*`, `APP_*`, `SECURITY_*`
  - Comments in `.env.local` include the note `# Host must be same as docker service` next to each host var (see your existing `.env.local` lines 17, 25, 30). Keep that habit for every new service.

### B. Env Var Checklist (current state documented as the baseline)
Current env family to preserve:
- App identity: `APP_NAME`, `APP_VERSION`, `ENVIRONMENT`
- API server: `API_PORT`
- JWT security: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`
- Postgres: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Redis: `REDIS_HOST`, `REDIS_PORT`
- SMTP + Email Sender: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `STMP_USE_TLS` (note: typo "STMP" in your current `.env.local` line 34 — see Suggestion A.1 below), `EMAILS_FROM_EMAIL`, `EMAILS_FROM_NAME`

---

## 8. Makefile Target Conventions

Three Makefiles exist with strict scope boundaries. Follow these naming rules when adding new targets:

### A. Root `Makefile` (Orchestrator only — never direct commands)
- Prefix every sub-make call with its domain: `backend-fastapi-*`, `frontend-nuxt-*`, `fullstack-*`, `docker-*`
- Never shell out to `docker compose` directly in root Make. Always delegate to the per-project Makefile via `$(MAKE) -C <dir> <target>`.
- Existing `fullstack-up` boots backend compose and then shells out to `frontend-nuxt-dev` for a **native** (non-container) Nuxt 4 dev server. That is intentional per the current "frontend deferred" setup. In future when the Nuxt container is first-class, a sibling `fullstack-container-up` target (or similar) should be introduced alongside it rather than replacing this, to preserve the host-dev workflow.
- `docker-clean-all` is destructive and documented as such. Any new cleanup helper MUST be `-` prefixed and tolerant of partially-torn-down state.

### B. `backend/fastapi/Makefile` (Service-level targets)
- Target categories mirror sections: install/update-deps/clean → docker-* → test* → format/lint → migration/migrate/migrate-*.
- `docker-up` invokes `docker compose --profile backend up -d $(BACKEND_SERVICES)`. Keep `BACKEND_SERVICES := gateway api database cache mailpit` variable synced with actual compose service set.
- `migration` reads a prompt from stdin for the message name — if you need a non-interactive variant (CI), add a `migration-ci NAME=...` sibling target rather than overwriting the interactive one.
- Code quality commands (`format`, `lint`) run **inside the running `api` container** via `docker compose exec -T api ruff ...` with a mounted `/tmp/.ruff_cache`. If you add a new lint tool, prefer running inside the container too so developers don't need matching toolchain versions on their host.
- `test`, `test-unit`, `test-integration`, `test-e2e` all exec pytest inside `api` container. Preserve the `tests/{unit,integration,e2e}/` folder structure that this naming implies (your current `tests/test_main.py` can be bucketed later).

### C. `frontend/nuxt4/Makefile` (Thin passthrough to pnpm)
- Targets are 1:1 with package.json scripts: `install-deps`, `update-deps`, `build`, `dev`, `generate`, `preview`, `postinstall`.
- Each is `pnpm <cmd>`. If you introduce a containerized `frontend` service, add matching `docker-build`/`docker-up` targets here, mirroring the backend Makefile layout.

---

## 9. Compose & Shell Hygiene Checklist (For Reviewer)

When reviewing ANY change to an infra file, verify:

- [ ] No new `localhost` hostnames crept into `docker-compose.yml`, env vars, or Nginx `proxy_pass`.
- [ ] No secrets, passwords, JWT keys, or SMTP credentials are hardcoded in Dockerfiles or compose YAML.
- [ ] New service has a healthcheck and `depends_on.condition: service_healthy` on its dependencies.
- [ ] Persistent state uses a **named volume**, not a host directory bind mount.
- [ ] `docker compose build` still succeeds end-to-end. New base images haven't broken the `uv pip compile` / `pnpm install --frozen-lockfile` steps.
- [ ] Every new env var used in code or compose YAML is listed in both `.env.local` (safe default) and in the root README setup instructions (future).
- [ ] Nginx still has `server_tokens off`, full `proxy_set_header` set, and rate-limit zone applied on proxy locations.
- [ ] Makefile targets in root Makefile are scoped with prefixes and delegate to sub-makes, not shelling out to tools directly.

---

## Suggestions Specific To *Your* Project (NOT rules — flagged for manual review)

These aren't standards to enforce; they're bugs / cleanup opportunities in the current infra files. If you like a suggestion we can turn it into a separate reviewed patch later.

### A.1 `.env.local` typo: `STMP_USE_TLS` → `SMTP_USE_TLS`
Line 34 of `.env.local` currently says `STMP_USE_TLS=True`. Every other variable uses `SMTP_*`. If any backend code reads `SMTP_USE_TLS` via `pydantic-settings`, this env template silently provides the wrong key name. Fix only after confirming what `app/core/config.py` actually reads.

### A.2 `backend/fastapi/Makefile` `BACKEND_SERVICES` lists `gateway` — but `gateway` uses profiles `["frontend", "fullstack"]`
So `docker compose --profile backend up gateway api database cache mailpit` starts `gateway` but it lives under the *frontend/fullstack* profiles. It probably still works because `--profile backend` still allows you to explicitly list any service name, but the intent is muddy. Options:
- Add `backend` to the gateway service's profile list, OR
- Drop `gateway` from `BACKEND_SERVICES` and document that "Backend profile runs only the 4 backend containers; start gateway separately when needed".

### A.3 Backend Dockerfile CMD is `--reload` in production-flavored build
Default CMD in `backend/fastapi/Dockerfile:30` is `uvicorn ... --reload`. This is correct for dev-loop use, but a future "prod" Dockerfile target or multi-stage variant should drop `--reload` and ideally use a process supervisor. OK to leave as-is for current scope.

### A.4 Frontend Nuxt4 service not yet in docker-compose.yml
You explicitly deferred the frontend container decision earlier. When you come back to it, use the same pattern: add as compose service `frontend` with profiles `frontend,fullstack`, depends on (or at least starts after) `api`, bind-mounts source + node_modules volume trick for dev, multi-stage build in prod, with the future Nginx `/api` vs `/` split in Suggestion 5B of the rules above.
