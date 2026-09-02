---
alwaysApply: false
description: Use when building backend logic, FastAPI routers, Pydantic schemas, SQLAlchemy models, database migrations, or server-side services.
globs:
  - "backend/fastapi/**/*.py"
  - "backend/fastapi/**/migrations/versions/*.py"
---

# Backend Development Rules & Standards

## 1. Core Stack Standards
- **Framework:** Python 3.12+ & FastAPI
- **Concurrency Model:** Synchronous (blocking) stack — sync SQLAlchemy 2.0 engine + sync `Session` via `psycopg2-binary`. Routes use plain `def`. FastAPI manages the thread pool automatically. Do not introduce `asyncio`, `AsyncSession`, or `asyncpg` unless explicitly requested.
- **ORM & Database:** SQLAlchemy 2.0 (Sync) & PostgreSQL
- **Validation & Settings:** Pydantic v2 & `pydantic-settings`
- **Tooling & Formatting:** Follow PEP 8 guidelines enforced via `ruff` (configuration already defined in `pyproject.toml`)
- **Code Quality Commands (executed inside the running `api` container):**
  - Format: `make format` → `docker compose exec -T api ruff check --fix ... ; ruff format ...`
  - Lint:  `make lint` → `docker compose exec -T api ruff check ...`
  - Test:  `make test-unit` / `make test-integration` / `make test-e2e` / `make test`
  - Migrations: `make migration NAME=...` / `make migrate` / `make migrate-down` / `make-migrate-reset` (see `backend/fastapi/Makefile`)
- **Error Envelope Consistency:** All error responses (handled by `app/core/handler.py`) use: `{ "error": "ERROR_CODE", "detail": "human readable msg" }`. The key is **singular `detail`**, never plural `details`.

---

## 2. Architecture & File Structure

Keep a clean separation of concerns inside `backend/fastapi/`:

```text
backend/fastapi/
├── app/
│   ├── core/               # Settings (config.py), exception base class, handlers, security helpers
│   ├── database/           # SQLAlchemy Base, engine, Session, get_db() dependency
│   ├── helpers/            # Security, UUID validator, email utilities, sanitization
│   ├── modules/
│   │   └── <domain>/       # auth | student | user | employee | enrollee | ... — one folder per BDD module
│   │       ├── table.py    # SQLAlchemy model (Mapped[...], mapped_column, Base subclass)
│   │       ├── validation.py # Pydantic Create/Update/Response schemas (v2)
│   │       ├── repository.py # CRUD against table; returns ORM objects/None (never Pydantic!)
│   │       ├── exception.py  # Domain AppException subclasses (e.g. StudentNotFoundException)
│   │       ├── service.py    # Pure Python domain logic; raises AppExceptions; NO FastAPI imports
│   │       ├── dependency.py # FastAPI Depends() wrappers (Annotated[...]Dep aliases for repo/service)
│   │       └── route.py      # APIRouter endpoints (uuid: UUID4 path typing, 204 Response on DELETE)
│   ├── migrations/versions/ # Alembic revisions
│   ├── utils/email/         # Jinja2-rendered email templates + aiosmtplib sender
│   └── main.py              # FastAPI() app factory, router includes, exception handlers
├── tests/                   # pytest unit | integration | e2e
├── pyproject.toml           # ruff, pytest, pydantic, Python 3.12+
├── requirements.txt         # Compiled via uv pip compile pyproject.toml
├── Dockerfile
└── Makefile                 # Install / docker-* / test-* / format & lint / migration-* targets
```

### Layer Contract Summary
1. **table.py:** Only ORM definitions. No logic.
2. **validation.py:** Only Pydantic schemas. Use `exclude_unset=True` on `.model_dump()` calls for PATCH.
3. **repository.py:** Accepts `DatabaseDep` Session. Returns ORM entities or `None`. May call `db.flush()` when PKs/auto-generated values must be visible before the request ends. **Must NOT** call `db.commit()` or `db.rollback()` — that is owned exclusively by `database/session.py::get_db()` request boundary.
4. **service.py:** Pure Python. Must **NOT** import FastAPI (`HTTPException`, `Request`, etc.). Instead, raise the module's `AppException` subclasses. May reach into helpers (hash_password, etc.). Do not duplicate validation guarantees already enforced by Pydantic schemas or `UUID4` router path coercion.
5. **dependency.py:** Thin. Glues sessions to repositories. Exposes `Annotated[Cls, Depends(...)]` aliases.
6. **route.py:** Declarative FastAPI endpoints. Prefer `uuid: UUID4` path-parameter typing for automatic 422 rejection of malformed inputs. Return `Response(status_code=204)` for DELETE / void endpoints — never a dict payload on 204. Return response models with both `response_model=` decorator AND explicit `Model.model_validate(orm_obj)` for double validation + OpenAPI docs.