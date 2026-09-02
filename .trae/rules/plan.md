---
alwaysApply: false
description: Use when planning new features, creating architecture design documents, breaking down user stories, or defining project structure.
globs:
  - "*.md"
  - "docs/**/*"
---

# Project Architecture & Planning Rules

## 1. Role & Planning Objective
When asked to plan a feature or refactor, act as the **Lead System Architect**:
- Break tasks down into clear, atomic, and testable steps before generating code.
- Ensure all plans strictly respect the defined stack, folder structure, and boundaries.
- Identify database schema changes, API endpoints, and UI components required *before* starting implementation.
- Plans are **proposed artifacts, not auto-execution tickets**: Present the plan for user review first. Do **not** begin code generation until the user explicitly approves the plan (LGTM / "go ahead").
- Cross-reference: Adopt the matching workflow from `.trae/skill/plan.md` for the 5-step planning process.

---

## 2. Tech Stack Blueprint
- **Frontend:** Vue 3, Nuxt 4 (Composition API, `<script setup>`)
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.0 (Sync), Pydantic v2. The backend is intentionally synchronous — see `.trae/rules/backend.md` §1 Concurrency Model. Do not introduce `asyncio`/`asyncpg`/`AsyncSession`/`async def` routes unless explicitly requested.
- **Database:** PostgreSQL
- **Caching:** Redis
- **Gateway & Proxy:** Nginx
- **Containerization:** Docker Compose
- **Dev Email (local):** Mailpit (web inbox `localhost:9080`, SMTP `mailpit:1025`)

---

## 3. Directory & Service Boundaries

```text
my-project/
├── frontend/
│   └── nuxt4/            # Nuxt 4 app (pages, components, composables, stores)
├── backend/
│   └── fastapi/          # FastAPI app (routers, services, models, schemas)
├── infra/
│   ├── database/         # Init scripts, migration files
│   ├── redis/            # Redis configuration
│   ├── nginx/            # Nginx config & SSL reverse proxy
│   └── mailpit/          # Dev email SMTP capture + inbox UI
│   (see `.trae/rules/infra.md` for full Docker, env, Makefile standards)
└── docker-compose.yml    # Orchestration across all services