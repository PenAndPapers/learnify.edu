# Learnify.edu

Dockerized full-stack admissions & student-management platform.
**Back-end:** Python 3.12 / FastAPI (sync stack) · SQLAlchemy 2.0 · Alembic · PostgreSQL 15 · Redis 7
**Front-end:** Nuxt 4 · Vue 3 · TypeScript · pnpm · Vitest · ESLint · Prettier
**Infrastructure:** Nginx 1.25-alpine gateway (rate-limited reverse proxy) · Mailpit (dev-SMTP + Web UI)
**Orchestration:** Docker Compose + root-level Makefile wrappers

---

## � First 5 Minutes — From zero-click clone → healthy stack

These steps give you a fully-running platform on a fresh clone. **Do this before you open any code files.**

1. **Seed your environment file** — the API container mounts `.env` from the repo root as read-only, so without this file the stack will not boot correctly:

   ```bash
   cp .env.local .env
   ```

   The `.env.local` seed already contains the correct Docker-internal hostnames (`database`, `cache`, `mailpit`). Update passwords, secrets, and app metadata in the copy to match your local environment, but **leave the `*_HOST` values alone** unless you're running services outside Docker.

2. **(Optional) First-time backend host-side setup** — only needed if you want to run Python tooling (Ruff, pytest, Alembic) directly on your macOS/Linux host via `uv`, instead of via `docker compose exec api …` inside the container. If you only plan to use the containerized dev flow, **SKIP this step** and continue straight to step 3.

   Prerequisite: this path requires [`uv`](https://github.com/astral-sh/uv) to be installed on your host machine. Without it, the commands below will fail with `uv: command not found`.

   ```bash
   # From the repo root — use the root-level wrappers:
   make backend-fastapi-install   # Creates backend/fastapi/.venv, compiles requirements.txt from
                                  # pyproject.toml, installs all packages, bootstraps Alembic env
   make backend-fastapi-update    # Run immediately after install to: re-sync deps, refresh the host venv,
                                  # and rebuild the backend container image baselines (so container matches)
   ```

   > **Why not run `make migrate` here yet?** The backend `migrate` target uses `docker compose exec api alembic upgrade head`, which requires the `api` container to already be running. You will run it explicitly (if you choose) in step 5 *after* the stack is up. For the default containerized flow, migration is automatic on container boot, so you never need to run it manually.

3. **Install frontend dependencies** (the Nuxt dev server runs natively on your host, not in a container — backend stack is containerized):

   ```bash
   make frontend-nuxt-install-deps
   ```

4. **Boot everything together (Fullstack mode):**

   ```bash
   make fullstack-up
   # What this does (in order):
   #   1. `make backend-fastapi-up` → compose boots gateway + api + database + cache + mailpit containers
   #        (API container runs `alembic upgrade head` automatically before starting uvicorn)
   #   2. `make frontend-nuxt-dev` → launches native Nuxt dev server
   ```

   > **Backend-only mode (no frontend):** If you only need the backend + supporting services, run `make backend-fastapi-up` instead. This still starts the Nginx gateway.

5. **(Optional) Explicit backend migration.** Skip this for normal containerized dev (auto-migrate already ran during step 4). Only run it if you have edited Alembic revision files manually or need to forcibly re-apply the head revision:

   ```bash
   # Root wrapper available (preferred when working from the repo root).
   # Alternative backend-scoped form still works when you're already cd'd
   # inside backend/fastapi/: `make -C backend/fastapi migrate`.
   make backend-fastapi-migrate
   ```

   This runs `docker compose exec api alembic upgrade head` against the running stack — it does NOT use the host-side Alembic CLI.

6. **Confirm everything is healthy.** Give it ~30 s on first boot (Postgres init + Alembic migrations + container healthchecks need a moment).

   | Check | URL | What a successful result confirms |
   |---|---|---|
   | API health (via Nginx gateway) | `http://localhost/api/v1/system/check-health` | `{"status":"healthy"}` → **all three** of Nginx · Postgres connection · Redis connection are working. 503 = either Postgres or Redis is down. |
   | Direct database connection | Host port `5432` (user/pass/db from `.env`) | You can `SELECT 1` with any Postgres client → DB container is reachable from the host. |
   | Direct Redis connection | Host port `6379` | `redis-cli ping` returns `PONG` → Redis container is reachable from the host. |
   | Mailpit dev-inbox Web UI | `http://localhost:9080` | The inbox page loads → Mailpit SMTP (container-internal `mailpit:1025`) and Web UI are up. Any email sent by the app (account verification, password reset, etc.) will appear here — **nothing is ever actually delivered externally** in this environment. |
   | Nuxt dev site (default port) | `http://localhost:3000` | The Nuxt welcome page loads → frontend build/dev chain is good. |

7. **Shut down cleanly:**

   ```bash
   make fullstack-down            # stops containers, keeps DB/Redis/Mailpit volumes
   make backend-fastapi-down-v    # STOPS + DELETES ALL PERSISTED VOLUMES (database_data, cache_data, mailpit_data)
                                  # — only use this if you want a completely fresh database next boot.
   ```

---

## 🧭 Repository Map

This is a monorepo with three top-level application domains. **Use this table to decide which directory you need to open first.**

| Path | What lives here | Deep-dive documentation |
|---|---|---|
| **[`backend/fastapi/`](./backend/fastapi/)** | FastAPI application package (`app/`), Python tooling (`pyproject.toml`, `requirements.txt`), Alembic migrations env (`alembic.ini`, `app/migrations/versions/`), backend-scoped Makefile + Dockerfile. This is all server-side code. | [Backend README (FastAPI)](./backend/fastapi/README.md) — explains the package-by-feature vertical-slice module pattern (7 files per domain module: route/exception/service/repository/table/validation/dependency) and the request lifecycle. |
| **[`frontend/nuxt4/`](./frontend/nuxt4/)** | Nuxt 4 app (Vue 3 + TypeScript + pnpm). App source lives in `app/`, with standard `nuxt.config.ts`, `package.json`, pnpm lock, frontend-scoped Makefile + Dockerfile. | [Frontend README (Nuxt 4 / Vue 3)](./frontend/nuxt4/README.md) — setup, native dev server, build, and generate commands. |
| **[`infra/`](./infra/)** | Docker image contexts for all four *supporting* containers: Nginx gateway (`infra/nginx/`), Postgres 15 (`infra/postgres/` + `init.sql` hook), Redis 7 (`infra/redis/`), and Mailpit (`infra/mailpit/`). | [Infrastructure README](./infra/README.md) — services matrix with all images/ports/healthchecks/restart-policies, named volumes table, environment variables, compose-profile gotchas, commands, and troubleshooting. |
| **Root orchestration files** (not a directory) | [`Makefile`](./Makefile) · [`docker-compose.yml`](./docker-compose.yml) · [`.env.local`](./.env.local) | See commands section below, and infra README for compose values. These files are the source of truth for how containers are built, wired, and started. |

---

## 📚 Read this First — Before you write any code

(Intent of the original section, preserved and organized by developer role so you only read what's required for your work.)

- **Everyone, regardless of role:** First run the [First 5 Minutes](#-first-5-minutes--from-zero-click-clone--healthy-stack) boot sequence above. Without a running stack you can't validate your changes against the real dependencies (Postgres, Redis, Mailpit).
- **🧑‍💻 Backend engineers:**
  1. [Backend README (FastAPI)](./backend/fastapi/README.md) — module structure, 7-file-per-domain vertical-slice pattern, request lifecycle diagram. Start here.
  2. [Infrastructure README](./infra/README.md) — read only the "Services matrix" + "Environment variables" sections so you know the correct internal hostnames (`database`, `cache`, `mailpit`), which ports are internal-only vs. published (the API port 8000 is **not** published — you test through the gateway `:80` or with `docker compose exec`).
  3. Then open an existing vertical slice like `backend/fastapi/app/modules/student/` to see the seven files wired end-to-end before you create a new module.
- **🎨 Frontend engineers:**
  1. [Frontend README (Nuxt 4 / Vue 3)](./frontend/nuxt4/README.md) — pnpm install + native dev server commands, build/generate.
  2. [Infrastructure README](./infra/README.md) — read "Services matrix" + "Network & Security Notes" so you know what URLs the API is exposed on and that you can trust Mailpit for local email flows.
- **🛠️ DevOps / Infra / SRE:**
  1. [Infrastructure README](./infra/README.md) — full detail on all five container services (gateway, api, database, cache, mailpit), named volumes, healthchecks, nginx rate limit config, profiles, and commands.
  2. Root [`Makefile`](./Makefile) and [`docker-compose.yml`](./docker-compose.yml) — the real definitions.

Reference quick-links (your original list, with the broken frontend path fixed):
- [Docker / Compose commands (root `Makefile`)](./Makefile)
- [Backend README (FastAPI)](./backend/fastapi/README.md)
- [Frontend README (Nuxt 4 / Vue 3)](./frontend/nuxt4/README.md)
- [Infrastructure README](./infra/README.md)

---

## 🛠️ Useful Makefile Commands (Curated)

All wrappers run from the **repository root**. There is no need to `cd` into subdirectories — the root Makefile delegates correctly with `-C <subdir>`.

### Boot, stop, rebuild

| Command | Scope | What it does |
|---|---|---|
| **First-time host-side backend setup (optional — container-only dev does NOT need these)** | | |
| `make backend-fastapi-install` | Backend only (host) | Host-side one-time bootstrapper: creates `backend/fastapi/app/migrations` dir, compiles locked `requirements.txt` from `pyproject.toml`, installs all packages into a new `backend/fastapi/.venv` via `uv`, bootstraps the Alembic env if empty. Requires `uv` installed on your host. |
| `make backend-fastapi-update` | Backend only (host + containers) | Run **after** editing `backend/fastapi/pyproject.toml` (adding/upgrading Python deps). Re-compiles requirements.txt, re-syncs the host-side `.venv`, and triggers `make docker-build` to rebuild container images so they match the new dependency set. |
| `make backend-fastapi-clean` | Backend only (host) | Destroys host-side backend Python tooling: deletes `backend/fastapi/uv.lock`, `requirements.txt`, and `.venv/`. Useful for a clean dependency re-bootstrap after `backend-fastapi-install` got wedged. Needs re-run of `backend-fastapi-install` + `backend-fastapi-update` afterward. |
| **Container boot / stop / rebuild (default path)** | | |
| `make backend-fastapi-up` | Backend + gateway only | Runs `docker compose --profile backend up -d gateway api database cache mailpit` via backend/Makefile delegation. Gateway always starts (explicit service names bypass its profile restriction). |
| `make backend-fastapi-restart` | Backend only | `docker-down` then `docker-up` on all 5 BACKEND_SERVICES. |
| `make backend-fastapi-build` | Backend only | `docker compose build --no-cache` of all BACKEND_SERVICES images. Use this after changing any Dockerfile, `requirements.txt`, or (alongside `backend-fastapi-update`) `pyproject.toml`. |
| `make backend-fastapi-down` | Backend only | Stop + remove containers (preserves named volumes). |
| `make backend-fastapi-down-v` | Backend only | Stop + remove containers **AND DELETE** `database_data` / `cache_data` / `mailpit_data` named volumes. Fresh DB state next boot. |
| `make fullstack-up` | Both | Boot backend containers *then* launch native Nuxt 4 dev server on host (requires `make frontend-nuxt-install-deps` first). |
| `make fullstack-down` | Backend stop only | Stops containers — the native Nuxt dev process runs in your shell; kill it with Ctrl+C. |
| `make docker-clean-all` | Global cleanup | `compose down -v` + force removes any orphan `learnifyedu` containers, networks, and images. Aggressive. |
| **Fullstack quality & tests** | | |
| `make fullstack-lint` | Both (backend → frontend) | Runs backend Ruff lint/format first, then frontend ESLint + Prettier check via `frontend-nuxt-lint`. Fail-fast: aborts on whichever tier surfaces errors first. |
| `make fullstack-test` | Both (backend → frontend, fail-fast) | Runs **backend first**: full pytest suite (unit + integration + e2e) inside the running `api` container (requires `make backend-fastapi-up` to be up beforehand — the in-terminal banner reminds you if the stack isn't live). If backend passes, then runs **frontend**: the full Vitest suite via `frontend-nuxt-test`. If any backend test fails, the frontend phase is skipped to surface infra-level issues quickly. |

### Backend code quality, tests, migrations

All commands below are available as root-level wrappers (preferred when working from the repo root). The backend-scoped `make -C backend/fastapi <name>` form continues to work identically when you're already cd'd inside `backend/fastapi/`. They all delegate to `backend/fastapi/Makefile` and **require the backend stack to already be running**, because they execute commands *inside* the `api` container via `docker compose exec`.

| Command | What it does |
|---|---|
| `make backend-fastapi-lint` | Runs **both** `ruff check --fix` then `ruff format` inside the api container (backend/Makefile `format` target), then `ruff check` without fixes (the `lint` target). |
| **Tests (pytest buckets)** | |
| `make backend-fastapi-test` | `pytest` full suite (unit + integration + e2e) inside the api container. |
| `make backend-fastapi-test-unit` | `pytest tests/unit` only (fast, mocks-heavy). |
| `make backend-fastapi-test-integration` | `pytest tests/integration` only. |
| `make backend-fastapi-test-e2e` | `pytest tests/e2e` only. |
| **Migrations (Alembic)** | |
| `make backend-fastapi-migrate` | `alembic upgrade head` inside the api container (note: the API container **already runs this on boot** — this target is for re-running after a manual migration edit, or to recover a DB to head). |
| `make backend-fastapi-migration` | Interactively prompts for a migration name, then runs `alembic revision --autogenerate -m "<name>"` inside the api container. Always review the generated file in `backend/fastapi/app/migrations/versions/` before committing — `--autogenerate` doesn't catch every schema change perfectly (e.g., Postgres ENUM alterations often need hand-tuning with idempotent `DO $$` blocks). |
| `make backend-fastapi-migrate-down` | `alembic downgrade -1` (rolls back one migration). |
| `make backend-fastapi-migrate-logs` | `alembic history --verbose` — migration timeline with full revision IDs. |
| `make backend-fastapi-migrate-check` | Prints the currently-applied Alembic revision alongside the revision head, so you can quickly see if there are unmigrated revisions without running `upgrade`. Useful in PRs and CI. |

### Frontend (native on host, no container yet)

| Command | What it does |
|---|---|
| **Install / build / run** | |
| `make frontend-nuxt-install-deps` | `(cd frontend/nuxt4 && pnpm install)` — installs pinned Node dependencies. |
| `make frontend-nuxt-update-deps` | `pnpm update --recursive --latest --interactive` — walks you through dependency updates. |
| `make frontend-nuxt-dev` | `pnpm dev` — starts the native Nuxt 4 dev server (default http://localhost:3000). |
| `make frontend-nuxt-build` | `pnpm build` — production build into `.output/`. |
| `make frontend-nuxt-generate` | `pnpm generate` — static pre-rendered output (if you ever want SSG output). |
| `make frontend-nuxt-preview` | `pnpm preview` — previews a `.output/` build locally. |
| `make frontend-nuxt-postinstall` | `pnpm postinstall` — run after install hooks; typically Nuxt auto-runs this. |
| **Code quality gates** (ESLint 10 flat-config + Prettier 3 + @nuxt/eslint preset) | |
| `make frontend-nuxt-lint` | `pnpm lint` — runs ESLint over `app/` and config files. Error exit on any rule violation. Warnings are emitted for Prettier style differences. |
| `make frontend-nuxt-lint-fix` | `pnpm lint:fix` — auto-applies all ESLint rule fixes and Prettier rewrites. Use this before committing to avoid manual style diffs. |
| `make frontend-nuxt-format` | `pnpm format` — runs Prettier `--write` over all tracked files. Fixes formatting without invoking ESLint rule logic. |
| `make frontend-nuxt-format-check` | `pnpm format:check` — Prettier `--check` CI gate: errors on any unstyled file without writing. Use this in pipelines. |
| `make frontend-nuxt-typecheck` | `pnpm typecheck` — runs `npx nuxi typecheck` to validate all Vue SFC `<script lang="ts">` blocks and TS sources against Nuxt's strict TS baseline. This is the recommended CI gate *in addition to* ESLint (catches type bugs ESLint's no-type-info parser can't). |
| **Tests** (Vitest + @vue/test-utils + happy-dom) | |
| `make frontend-nuxt-test` | `pnpm test` — runs Vitest once (`vitest run`) with all component/spec files. Coverage mode is `pnpm test:coverage` (invoked directly from `frontend/nuxt4/` with `--coverage`) when needed. |

---

## 🧱 Architecture at a Glance (3 bullet summary)

For a detailed treatment, click through to the child READMEs. This section is here only so you can orient yourself without clicking anything.

1. **Backend (`backend/fastapi/app/`) is a modular monolith using Package-by-Feature vertical slices.** Each domain (currently `user`, `authentication`, `employee`, `enrollee`, `student`, `exam`, `interview`) lives in its own self-contained directory containing exactly seven files: `route.py`, `exception.py`, `service.py`, `repository.py`, `table.py`, `validation.py`, `dependency.py`. Dependencies flow strictly in one direction: route → service → repository. Database transactions are scoped at the HTTP request level in `database/session.py::get_db()` — repositories call `db.flush()`, not `db.commit()`.

2. **Frontend (`frontend/nuxt4/`) is a standard Nuxt 4 app.** Source lives in the `app/` directory and the dev server runs natively on your host via `pnpm dev` (not containerized for day-to-day work — Dockerfile + Makefile targets exist but are only used for CI/builds).

3. **Infrastructure is four supporting containers + one API container, orchestrated from the root `docker-compose.yml`.** Nginx gateway (`:80` published) rate-limits traffic at 10 r/s per IP and proxies `/` → the FastAPI `api` container (port `8000` internal-only, never published). `api` talks directly to a Postgres 15 container, a Redis 7 container, and a Mailpit container (SMTP: internal `1025`, Web UI: host `9080`). All three stateful services use Docker named volumes for persistence. Container startup order is guarded by healthcheck dependencies (gateway waits for `api:healthy`; `api` waits for `database:healthy`) so there's no thundering herd on boot.

---

## 🤝 Contributing

Baseline expectations for every pull request or patch:

1. **Docs move with code.**
   - If you change docker-compose values (ports, images, healthchecks, profiles, named volumes): update [`infra/README.md`](./infra/README.md) in the same commit.
   - If you change backend module structure or the 7-file pattern: update [`backend/fastapi/README.md`](./backend/fastapi/README.md) in the same commit.
   - If you change the First-5-Minutes onboarding flow, boot commands, or repo layout (e.g., new top-level directory, split backend into more services, new root Makefile targets): update **this** root README in the same commit.
   - Drift between docs and code is a bug. Keep docs as current as source files.

2. **Run checks before you push.**
   - **Backend code:** Run `make backend-fastapi-lint` (Ruff: both `check --fix` + `format`) and `make backend-fastapi-test` (or at minimum the relevant subset via `make backend-fastapi-test-unit` / `-test-integration` / `-test-e2e`) while the stack is running. Root-level wrappers exist for all test and migration commands; use them when working from the repo root. If you add or alter a DB schema, run through the migration workflow (`make backend-fastapi-migration` → inspect generated revision → `make backend-fastapi-migrate` on a fresh volume) and commit both the model change and the Alembic version file together.
   - **Frontend code:** From the repo root run, in order, `make frontend-nuxt-format-check` (fails on unstyled files), `make frontend-nuxt-lint` (fails on ESLint rule violations), `make frontend-nuxt-typecheck` (strict TS across all Vue SFCs), and `make frontend-nuxt-test` (full Vitest suite). For a single one-shot local fix pass that auto-corrects style before re-running the gates, use `make frontend-nuxt-lint-fix` + `make frontend-nuxt-format` first. Each wrapper delegates to `frontend/nuxt4/Makefile` which in turn invokes the `pnpm` scripts defined in `frontend/nuxt4/package.json`.
   - Always run a smoke check of the "Confirm everything is healthy" URLs from §First 5 Minutes after making changes that touch gateway routing, Docker networking, or dependencies.

3. **Where to put tests, migrations, and new files.**
   - Backend tests live under `backend/fastapi/app/tests/` in three subdirectories:
     - `tests/unit/` — fast, mocks-heavy, no live DB/Redis needed. Use FastAPI `Depends()` overrides to inject fake repositories into services.
     - `tests/integration/` — exercises components together (typically service + real repository, with a test database session that rolls back).
     - `tests/e2e/` — simulates real user journeys against the full running stack (HTTP client against the gateway).
   - Backend migrations (schema changes) live as Alembic revision files in `backend/fastapi/app/migrations/versions/`. Generate with `make backend-fastapi-migration` from the repo root (or `make migration` inside `backend/fastapi/`). Never hand-write revision IDs.
   - Frontend tests/components/composables/pages: follow the conventions already established inside `frontend/nuxt4/app/`.

4. **Pull-request hygiene (kept deliberately lightweight — adapt if your team has a stricter formal policy).**
   - Branch naming: `feature/<ticket-or-slug>` for new work, `fix/<ticket-or-slug>` for bug fixes, `chore/<slug>` for dependency bumps / docs-only / tooling changes.
   - PR description should briefly describe: *what changed*, *why*, and *how you verified it* (paste the output of health URLs, a passing test run, or screenshots of a UI change).
   - If the PR changes user-visible behavior, call out where in the docs you updated the corresponding README.

Feel free to open PRs and issues that suggest improvements to the codebase, developer experience, or onboarding documentation itself — this README is a living document, not set in stone.

---

## ✅ Drift Guard

Single sources of truth:

| Domain | Authoritative files |
|---|---|
| Container wiring, ports, profiles, healthchecks, volumes | [`docker-compose.yml`](./docker-compose.yml) |
| Makefile command implementations (root-level wrappers) | [`Makefile`](./Makefile) |
| Backend module architecture, request lifecycle | [`backend/fastapi/README.md`](./backend/fastapi/README.md) + `backend/fastapi/app/modules/*` |
| Frontend setup / build / dev commands | [`frontend/nuxt4/README.md`](./frontend/nuxt4/README.md) + `frontend/nuxt4/Makefile` |
| Supporting-service image Dockerfiles, Nginx configs, env var contracts | [`infra/README.md`](./infra/README.md) + `infra/*/Dockerfile` |

If you modify any authoritative file, **update the corresponding documentation in the same commit**. When in doubt about which README owns a fact: put boot-onboarding and repo-map facts here (root), architecture-of-one-domain facts in the child README.
