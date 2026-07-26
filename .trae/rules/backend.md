---
alwaysApply: false
description: Use when building backend logic, FastAPI routers, Pydantic schemas, SQLAlchemy models, database migrations, or server-side services.
---

# Backend Development Rules & Standards

## 1. Core Stack Standards
- **Framework:** Python & FastAPI
- **ORM & Database:** SQLAlchemy 2.0 (Async) & PostgreSQL
- **Validation & Settings:** Pydantic v2 & `pydantic-settings`
- **Tooling & Formatting:** Follow PEP 8 guidelines enforced via `ruff`

---

## 2. Architecture & File Structure

Keep a clean separation of concerns inside `backend/fastapi/`:

See `backend/fastapi/README.md` for a detailed file structure.