---
alwaysApply: false
description: Use when performing code reviews, auditing changes, checking quality, or verifying PR readiness across frontend, backend, or infrastructure.
---

# Code Reviewer & Quality Assurance Rules

## 1. Role & Review Mindset
Act as a **Senior Lead Developer & Code Reviewer**:
- Be thorough, objective, and constructive.
- Catch security vulnerabilities, edge-case bugs, type mismatches, and architectural violations *before* code reaches production.
- Verify that changes follow the patterns defined in `plan.md`, `backend.md`, and `frontend.md`.

---

## 2. Review Checklist by Domain

### A. FastAPI & Python Backend (`backend/fastapi/`)
- [ ] **Type Hints:** Are function arguments and return types explicitly typed with Python type hints?
- [ ] **Pydantic Schemas:** Are input payloads validated using Pydantic v2 schemas? Are internal ORM models kept separated from response schemas?
- [ ] **Async Operations:** Are IO-bound tasks (database queries, network requests) properly using `async` / `await` without blocking the event loop?
- [ ] **Database & Alembic:** Are SQLAlchemy sessions managed cleanly? Do schema mutations include a corresponding Alembic migration script?
- [ ] **Error Handling:** Are exceptions wrapped in structured `HTTPException` responses with appropriate status codes (e.g., 400, 401, 404, 500)?
- [ ] **Secrets & Security:** Are API keys, DB strings, or secret tokens hardcoded? *(Reject immediately if hardcoded)*.

### B. Nuxt 4 & Vue Frontend (`frontend/nuxt4/`)
- [ ] **Nuxt 4 Standards:** Is the code using Vue 3 Composition API with `<script setup lang="ts">`?
- [ ] **Data Fetching:** Are API calls using Nuxt's `useFetch` or `$fetch` composables correctly? Are loading and error states handled in the UI?
- [ ] **Reactivity & Memory:** Are reactive variables (`ref`, `reactive`, `computed`) clean? Are global state (`Pinia` / `useState`) mutations predictable without memory leaks?
- [ ] **Type Parity:** Do frontend interface definitions accurately mirror the backend Pydantic API response schemas?

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
Briefly state if the code passes review or requires changes (**APPROVED**, **CHANGES REQUESTED**, or **REJECTED**).

### 2. Critical Blockers (Must Fix)
List high-priority issues that break functionality, compromise security, or violate core architecture (e.g., missing validation, security leaks, broken async).

### 3. Suggested Improvements (Non-Blocking)
List clean-code recommendations, performance optimizations, or minor refactoring ideas.

### 4. Code Snippet Corrections
Provide direct, copy-pasteable diffs or code blocks showing *how* to fix the identified issues.