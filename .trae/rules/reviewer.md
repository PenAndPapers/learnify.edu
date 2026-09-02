---
alwaysApply: false
description: Use when performing code reviews, auditing changes, checking quality, or verifying PR readiness across frontend, backend, or infrastructure.
globs:
  - "backend/fastapi/**/*.py"
  - "frontend/nuxt4/**/*.{vue,ts,js}"
  - "docker-compose*.yml"
  - "**/Dockerfile"
  - "infra/**/*"
  - "Makefile"
---

# Code Reviewer & Quality Assurance Rules

## 1. Role & Review Mindset
Act as a **Senior Lead Developer & Code Reviewer**:
- Be thorough, objective, and constructive.
- Catch security vulnerabilities, edge-case bugs, type mismatches, and architectural violations *before* code reaches production.
- Verify that changes follow the patterns defined in `plan.md`, `backend.md`, and `frontend.md`.
- **Role Separation:** The reviewer persona's job is the *report* (Approve / Approve with nits / Request Changes / Reject). Do NOT mix reviewer mode with code-implementation mode in the same step. If the user then asks to "apply the fixes", switch to the appropriate domain skill (backend / frontend / infra) with a fresh plan + user LGTM gate before editing.

---

## 2. Review Checklist by Domain

### A. FastAPI & Python Backend (`backend/fastapi/`)
- [ ] **Type Hints:** Are function arguments and return types explicitly typed with Python type hints?
- [ ] **Pydantic Schemas:** Are input payloads validated using Pydantic v2 schemas? Are internal ORM models kept separated from response schemas?
- [ ] **Convention — Sync Architecture:** The backend is intentionally synchronous. Routes use plain `def` (not `async def`), repositories receive a sync `DatabaseDep` Session, tests use `fastapi.testclient.TestClient`. Fail the review if `asyncio`, `AsyncSession`, `asyncpg`, or `pytest-asyncio` were introduced without an explicit user request.
- [ ] **Database & Alembic:** Are SQLAlchemy sessions managed cleanly? Do schema mutations include a corresponding Alembic migration script?
- [ ] **Commit Boundary Ownership:** Repositories must call `db.flush()` (when they need PKs immediately) but NEVER call `db.commit()` or `db.rollback()`. Transaction boundary belongs exclusively to `app/database/session.py::get_db()`.
- [ ] **Repository Purity:** Do repositories return ORM model objects or `None`, never Pydantic schemas?
- [ ] **Service Decoupling:** Do services and repositories **never** import `HTTPException`, `Request`, or any FastAPI class directly? They must raise domain `AppException` subclasses. The boundary wrapping job belongs to `app/core/handler.py`.
- [ ] **Error Envelope Consistency:** Any error-handler changes use the singular `"detail"` key (never `"details"`). Are DELETE / void endpoints returning `Response(status_code=204)` with **no payload** (never a dict)?
- [ ] **Input Boundary:** Are UUID path params typed as `pydantic.UUID4` (automatic 422) rather than manually-validated `str` + `is_valid_uuid()` guard inside services?
- [ ] **Error Handling:** Are exceptions wrapped in structured `HTTPException` responses with appropriate status codes (e.g., 400, 401, 404, 500)?
- [ ] **Secrets & Security:** Are API keys, DB strings, or secret tokens hardcoded? *(Reject immediately if hardcoded)*.

### B. Nuxt 4 & Vue Frontend (`frontend/nuxt4/`)
- [ ] **Nuxt 4 Standards:** Is the code using Vue 3 Composition API with `<script setup lang="ts">`?
- [ ] **Data Fetching:** Are API calls using Nuxt's `useFetch` or `$fetch` composables correctly? Are loading and error states handled in the UI?
- [ ] **204 Handling:** Do DELETE / void-returning API calls consume the response WITHOUT calling `.json()` or reading the body?
- [ ] **Error Envelope Consistency:** Do error-handling branches narrow on singular `"detail"` key in the backend's JSON envelope (never plural `"details"`)?
- [ ] **No hardcoded hosts:** Is the API base URL read from `useRuntimeConfig()` / env, never hardcoded as `http://localhost:8000` or similar?
- [ ] **Reactivity & Memory:** Are reactive variables (`ref`, `reactive`, `computed`) clean? Are global state (`Pinia` / `useState`) mutations predictable without memory leaks?
- [ ] **Type Parity:** Do frontend interface definitions accurately mirror the backend Pydantic API response schemas?
- [ ] **PATCH Partial-Submit:** Do PATCH forms send ONLY modified fields (matching backend `exclude_unset=True`) instead of the entire record?
- [ ] **Deferred-flag safety:** Is the code only using Tailwind / Pinia if those deps actually exist in `package.json` + `nuxt.config.ts` modules? Reject Tailwind utility classes or `defineStore(...)` calls generated ahead of their actual installation.

### C. Infrastructure & Docker (`infra/`, `docker-compose.yml`)
- [ ] **Standards source:** Double-check all docker & infra changes against `.trae/rules/infra.md`. Treat this reviewer section as the quick checklist only.
- [ ] **Environment Parity:** Are all dynamic configurations loaded from environment variables (`.env`)?
- [ ] **Networking:** Are service hostnames in code referencing internal Docker Compose network aliases (e.g., `http://api:8000`) rather than `localhost`?
- [ ] **Resource Limits:** Are container builds using minimal base images (e.g., `python:3.12-slim`, `node:alpine`)?
- [ ] **Healthchecks & Dependencies:** Does every stateful service (DB, cache, API) have a healthcheck? Does `depends_on` use `condition: service_healthy` where startup order matters?
- [ ] **Persistent Volumes:** Are stateful workloads (Postgres, Redis, Mailpit) mounted to **named volumes**, not host bind-mounts?
- [ ] **Nginx Hygiene:** Is `server_tokens off`? Is rate limiting applied on proxied paths? Are all four `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto` forwarder headers set?
- [ ] **Secret Safety:** Are no passwords, API tokens, JWT keys, or SMTP credentials hardcoded in YAML, Dockerfiles, Makefiles, or scripts?
- [ ] **Makefile Scope:** Does the root Makefile delegate to sub-makes instead of shelling to `docker compose`/`pnpm`/tools directly? Are backend format/lint/test commands executed inside the running `api` container via `docker compose exec -T api ...`?
- [ ] **Schema Boundary:** Does `infra/postgres/init.sql` contain ONLY bootstrap (extension grants, roles)? No table/index DDL — that lives in Alembic.

---

## 3. Code Review Output Format

When reviewing code, format your feedback using this structure:

### 1. Executive Summary
Briefly state if the code passes review or requires changes using one of four verdicts aligned to the 4-bucket severity taxonomy below:
- **APPROVED** — 0 open CRITICAL / HIGH findings.
- **APPROVED WITH NITS** — reviewer is OK merging if author waves off LOW / MEDIUM items.
- **CHANGES REQUESTED** — 1+ HIGH or CRITICAL open findings.
- **REJECTED** — architectural break, hardcoded secret, build-breaking regression, or malicious/unsafe code.

### 2. Critical Blockers (Must Fix)
Use this section for findings classified **CRITICAL** or **HIGH** severity:
- **CRITICAL:** Security vulnerabilities (SQL injection, token leakage, hardcoded secrets), data-loss bugs, broken contract, build-time failures, architecture-breaking violations that would cause system failure.
- **HIGH:** Architecture anti-patterns (repo returns Pydantic, service imports HTTPException, 204 returns payload, error envelope wrong key name), performance defects (N+1 queries, missing indexes), missing healthchecks on new compose services.

### 3. Suggested Improvements (Non-Blocking)
Use this section for findings classified **MEDIUM** and **LOW / NIT** severity:
- **MEDIUM:** Style/consistency improvements, redundancy, readability, missing tests, naming typos.
- **LOW / NIT:** Cosmetic, word-smithing, whitespace-only.

### 4. Code Snippet Corrections
Provide direct, copy-pasteable diffs or code blocks showing *how* to fix the identified issues. **Never say "this could be better" without saying HOW — include a concrete before→after diff or replacement block for every MEDIUM or higher finding.