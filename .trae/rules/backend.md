---
alwaysApply: false
description: Use when building backend logic, FastAPI routers, Pydantic schemas, SQLAlchemy models, database migrations, or server-side services.
---

# Backend Development Rules & Standards

## 1. Core Stack Standards
- **Framework:** Python 3.12+ & FastAPI
- **Concurrency Model:** Synchronous (blocking) stack — sync SQLAlchemy 2.0 engine + sync `Session` via `psycopg2-binary`. Routes use plain `def`. FastAPI manages the thread pool automatically. Do not introduce `asyncio`, `AsyncSession`, or `asyncpg` unless explicitly requested.
- **ORM & Database:** SQLAlchemy 2.0 (Sync) & PostgreSQL
- **Validation & Settings:** Pydantic v2 & `pydantic-settings`
- **Tooling & Formatting:** Follow PEP 8 guidelines enforced via `ruff` (configuration already defined in `pyproject.toml`)

---

## 2. Architecture & File Structure

Keep a clean separation of concerns inside `backend/fastapi/`:

See `backend/fastapi/README.md` for a detailed file structure.