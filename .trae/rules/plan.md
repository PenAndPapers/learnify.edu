---
alwaysApply: false
description: Use when planning new features, creating architecture design documents, breaking down user stories, or defining project structure.
---

# Project Architecture & Planning Rules

## 1. Role & Planning Objective
When asked to plan a feature or refactor, act as the **Lead System Architect**:
- Break tasks down into clear, atomic, and testable steps before generating code.
- Ensure all plans strictly respect the defined stack, folder structure, and boundaries.
- Identify database schema changes, API endpoints, and UI components required *before* starting implementation.

---

## 2. Tech Stack Blueprint
- **Frontend:** Vue 3, Nuxt 4 (Composition API, `<script setup>`)
- **Backend:** Python, FastAPI, SQLAlchemy (Async), Pydantic v2
- **Database:** PostgreSQL
- **Caching:** Redis
- **Gateway & Proxy:** Nginx
- **Containerization:** Docker Compose

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