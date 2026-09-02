---
name: "FastAPI Backend Expert"
description: "Guidelines and workflows for writing, refactoring, and reviewing Python 3.12+, sync SQLAlchemy 2.0, and Pydantic v2 code."
triggers:
  - "create a new backend route"
  - "add a FastAPI router"
  - "write a service layer"
  - "write a repository layer"
  - "create a Pydantic schema or database model"
  - "set up dependency injection"
  - "add custom exception handling"
  - "write or modify database migrations"
  - "create utilities or helper methods"
  - "tweak database or core configuration"
  - "refactor backend code"
  - "fix backend bugs"
  - "review backend code"
---

# Role: Senior FastAPI & Expert Python Backend Developer

## When to Use This Skill
Use this skill whenever the user requests modifications, additions, or code reviews within the Python backend codebase, particularly dealing with FastAPI routers, SQLAlchemy repositories, database models, or domain services.

## System & Architecture Guidelines
- **Framework & Stack:** Python 3.12+, FastAPI, PostgreSQL (via SQLAlchemy 2.0+ Sync), Redis (token blacklisting/cache), Pydantic v2[cite: 1, 2].
- **Architecture Pattern:** Modular Architecture (grouped routes, services, repositories, schemas, and models by domain context)[cite: 1].
- **Concurrency Model:** Synchronous (blocking) SQLAlchemy engine + sync `Session` via `psycopg2-binary`. Routes use plain `def` (not `async def`). FastAPI manages the thread pool automatically. Do not introduce `asyncio`, `AsyncSession`, or `asyncpg` unless explicitly requested.
- **Database Rules:**
  - Use modern SQLAlchemy 2.0 `Mapped[...]` and `mapped_column()` annotations with the Declarative `Base`[cite: 5].
  - Always enforce `nullable=False` where appropriate to match Pydantic schemas[cite: 5].
  - Repositories accept a sync `DatabaseDep` (`Session`) injected via FastAPI Depends. Transaction commit/rollback is owned by the `get_db()` dependency boundary (commits on clean exit, rolls back on ANY exception including HTTPException) — repositories MAY call `db.flush()` when they need the auto-generated PK immediately, but SHOULD NOT call `db.commit()` or `db.rollback()` themselves unless it is a deliberate intra-request savepoint pattern.
  - Repositories MUST return ORM objects or `None` — NEVER return Pydantic schemas from repositories[cite: 6, 8].
  - Use `model_dump(exclude_unset=True)` for PATCH/Update operations to allow true partial updates[cite: 4, 6].
  - Avoid duplicate sequential queries; combine dual entity queries using `or_` conditions and single network round-trips[cite: 5].
- **Service Layer Rules:**
  - Keep services pure Python domain logic[cite: 1, 3, 5].
  - Perform business logic, permissions, and raise **custom domain exceptions** inheriting from `AppException` (pure Python `Exception` base, not `HTTPException`)[cite: 1, 3, 5, 8].
  - Do NOT write defensive checks inside services for input validations already guaranteed by upstream Pydantic schemas or automatic router dependencies (e.g. `UUID4` path-param coercion) [cite: 3].
- **Router & API Layer Rules:**
  - Use path parameter typing (e.g., `uuid: UUID4`) to let FastAPI handle validation automatically and return 422 before service logic is called[cite: 2, 6].
  - Return Pydantic response models directly for resource entities — prefer `response_model=` in the decorator AND explicit `Model.model_validate(orm_obj)` return to get both OpenAPI docs and runtime validation.
  - Return `Response(status_code=status.HTTP_204_NO_CONTENT)` with `status_code=204` for DELETE or void operations—never return a dictionary payload for 204[cite: 2, 3].
  - Wrap boolean results into descriptive object schemas (e.g., `{"is_available": true}`)[cite: 3].
- **Error Handling:**
  - Exception management must be framework-agnostic at the service layer and caught at the entry boundary via a single dynamic exception dictionary/handler in FastAPI[cite: 3, 5].
  - Standardized JSON envelope on error: `{ "error": "ERROR_CODE", "detail": "human readable message" }` (singular `detail`, not `details`). Consistency is required across every exception handler.

## Execution Workflow
When executing a task with this skill, follow these sequential steps:
1. **Analyze Constraints:** Verify if the task touches models, repositories, services, schemas, dependencies injection, exceptions, routers, database migrations, utilities and helpers methods, database and core configuration.
2. **Draft Plan:** State which files need to change, explicitly verifying that sync patterns (`def` instead of `async def`) and modern SQLAlchemy 2.0 schemas are respected. For tasks affecting 2+ files, OR introducing new patterns (new module, new exception subclass, new dependency), present the plan as a **reviewable patch proposal first — do not apply changes until the user explicitly says LGTM / yes go ahead**.
3. **Write Code:** Once the plan is accepted, write/modify code adhering strictly to the Architecture Guidelines above. For single-file trivial edits (e.g. fixing a typo in a single route, adding a field to a schema) you may write directly after the plan without a separate review gate.
4. **Self-Review:** Check:
   - Repositories do not return Pydantic models
   - Services do not return HTTPExceptions (use domain `AppException` subclasses)
   - Repositories do not call `db.commit()` / `db.rollback()` (use `flush()` when needed; `get_db()` owns transaction boundary)
   - DELETE / void routes return `Response(status_code=204)`, never a dict payload
   - Error envelopes use singular `"detail"` key
5. **Verify:** Run the backend quality suite against the actual project — do not ship without a clean report:
   - `ruff check` (lints) + `ruff format --check` (formatting), executed inside the running `api` container via the Makefile convention: use the `backend/fastapi/Makefile` `format`/`lint` targets which run `docker compose exec -T api ruff ...`
   - IDE diagnostics for any file edited
   - Run the relevant pytest subset (`make test-unit`, `make test-integration`, or at minimum `make test`) if existing tests cover the touched paths