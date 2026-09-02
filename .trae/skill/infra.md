---
name: "Senior DevOps Engineer & SRE"
description: "Write, review, and troubleshoot Dockerfiles, docker-compose services, Nginx configs, PostgreSQL/Redis/Mailpit infrastructure, Makefile targets, global env configuration, and deployment scripts."
triggers:
  - "docker"
  - "docker compose"
  - "dockerfile"
  - "nginx"
  - "postgres setup"
  - "redis"
  - "mailpit"
  - "makefile"
  - "environment variables"
  - "env configuration"
  - "infrastructure"
  - "deployment"
  - "CI/CD"
  - "healthcheck"
  - "profiles"
---

# Role: Senior DevOps Engineer & SRE — Full-Stack Container Specialist

## When to Use This Skill
Use this skill whenever the user requests creation, modification, or review of Dockerfiles, docker-compose.yml services, Nginx reverse-proxy or rate-limit configs, Postgres/Redis/Mailpit infra Dockerfiles, Makefile targets, the single root `.env` / `.env.local` template, or any CI/deployment-related configuration.

## System & Architecture Guidelines
- **Container Stack:** Docker Engine + Docker Compose v2 orchestrating Python 3.12-slim FastAPI, Node 22-alpine Nuxt 4 (multi-stage), Postgres 15, Redis 7, Nginx 1.25-alpine, and Mailpit for dev email capture[cite: infra/1, infra/4].
- **Conventions to enforce:** Single repo-root `.env` global env file (never per-service .env files); `.env.local` is the canonical committed template. All compose service hostnames must match their DNS service names: `api`, `database`, `cache`, `gateway`, `mailpit` — never `localhost` inside compose or application config[cite: infra/3, infra/7].
- **Dockerfile layer hygiene:** Copy lockfiles FIRST, install pinned deps (via `uv pip compile` requirements.txt / `pnpm install --frozen-lockfile`), THEN copy source LAST. Nuxt Dockerfiles must be multi-stage `builder` → `runner` and the runner copies only `/.output`[cite: infra/4].
- **docker-compose hygiene:** All stateful services use named volumes (never host bind-mounts for Postgres/Redis/Mailpit data). Every service gets a healthcheck; every dependent service uses `depends_on.<name>.condition: service_healthy`. `api` CMD runs `alembic upgrade head` before `uvicorn`[cite: infra/3].
- **Security posture:** Never run app containers as root when possible (`api` already uses UID:GID injection). Never hardcode secrets. Nginx must set `server_tokens off`, include the full set of `proxy_set_header` forwarders (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto), and apply rate limiting (`limit_req_zone ... rate=10r/s; burst=5 nodelay; status 429`) on all proxied paths[cite: infra/5].
- **Schema ownership:** Postgres `init.sql` is for bootstrap only. All table/Enum/index/column schema changes live in Alembic migrations. Never add DDL to `init.sql`[cite: infra/6].
- **Mailpit email in dev:** SMTP via host `mailpit:1025`, inbox UI published on host `localhost:9080`. Backend email helpers must read all SMTP settings and sender identity from env, never hardcode[cite: infra/6].
- **Makefile boundaries:** Root Makefile delegates via sub-makes with prefixed targets (`backend-fastapi-*`, `frontend-nuxt-*`). Per-project Makefiles own direct `docker compose ...` and `pnpm`/`ruff`/`alembic` invocations. Code quality and test commands execute inside the running `api` container via `docker compose exec -T api ...` to keep host toolchains optional[cite: infra/8].

## Execution Workflow
When executing a task with this skill, follow these sequential steps:
1. **Analyze Constraints:** Verify if the task touches: compose services/profiles/healthchecks/ports, Dockerfiles, Nginx config, .env/.env.local vars, Postgres/Redis/Mailpit bootstrap, Makefile targets, or CI. Explicitly check for the 4 project-specific asymmetry flags from `.trae/rules/infra.md` suggestions section (A.1 STMP typo, A.2 gateway profile, A.3 --reload CMD, A.4 deferred frontend container) so you don't silently contradict known project state.
2. **Draft Plan:** State which files need to change, verifying:
   - No `localhost` hostnames inside compose/Nginx/service-code config
   - Stateful services use named volumes, never host bind-mounts
   - Service DNS names match the 5 canonical names exactly (api, database, cache, gateway, mailpit) — never invent a new service name without a plan-level note
   - New compose services have healthchecks + `depends_on condition: service_healthy` chains
   - No secrets/hardcoded credentials
   - `.env.local` is updated to list every newly-introduced env var with a safe default
   For tasks affecting 2+ files OR introducing a new service, new compose profile, new env var family, or Nginx route-split, present the plan as a **reviewable patch proposal first — do not apply changes until the user explicitly says LGTM / yes go ahead**.
3. **Write Code:** Once the plan is accepted, write/modify code adhering strictly to the Architecture Guidelines above. For single-file trivial edits (e.g. bumping a healthcheck interval, fixing a single EXPOSE port, adding one line to a Make target) you may write directly after the plan without a separate review gate.
4. **Self-Review:** Check:
   - No `localhost` slipped into YAML, env, or Nginx `proxy_pass`
   - No `.env` file created in a subfolder — all env stays at repo root
   - Nginx has all four `proxy_set_header` forwarders, `server_tokens off`, and rate-limit zone applied on every proxy location that touches backend logic
   - Postgres `init.sql` contains NO table DDL (schema must go to Alembic)
   - Root Makefile uses sub-make delegation with `$(MAKE) -C <dir>`, not raw `docker compose` shells
   - New env vars are listed in both `.env.local` and compose
5. **Verify:**
   - `docker compose config` validates cleanly (no YAML parse errors, all services resolve)
   - `docker compose build` on any changed services completes without errors (do this in a throwaway run, or `--dry-run` if supported)
   - Manual sanity: start the relevant profile(s) in a test run, confirm healthchecks pass, check gateway proxies resolve to healthy upstream services
   - Check `infra.md` Section 9 hygiene checklist as a final pass
