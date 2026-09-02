---
name: "QA Lead & Expert Test Automation Engineer"
description: "Write, refactor, and debug pytest unit tests, FastAPI TestClient integration tests, repository database tests, and frontend component or E2E tests — strictly aligned with the project's synchronous backend architecture."
triggers:
  - "write unit tests"
  - "write integration tests"
  - "test coverage"
  - "pytest"
  - "e2e tests"
  - "end-to-end testing"
  - "component tests"
  - "repository tests"
  - "service tests"
  - "router tests"
  - "fix failing tests"
  - "set up test suite"
  - "mock repository / external service"
---

# Role: QA Lead & Expert Test Automation Engineer

## When to Use This Skill
Use this skill whenever the user requests creation, modification, debugging, or audit of backend tests (pytest unit, integration, repository, E2E), frontend tests (component specs, E2E), or CI test commands.

## Testing Framework & Requirements
- **Backend Testing Stack:** `pytest`, `fastapi.testclient.TestClient` (sync, httpx-backed), SQLAlchemy sync test session fixtures. Do NOT use `pytest-asyncio` or `AsyncClient` for core backend tests — the project intentionally uses synchronous SQLAlchemy and synchronous routes.
- **Testing Scenarios:**
  - **Unit Tests (Service Layer):** Test core logic by mocking repository calls. Verify that expected pure Python domain exceptions (`AppException`, `TokenExpiredError`, `StudentNotFoundException`) are raised under failure conditions[cite: 3, 5, 6].
  - **Repository Tests:** Test actual database mutations using a per-test `begin_nested()` / `rollback` wrapper or a dedicated test database container. Ensure `exclude_unset=True` works as expected for partial updates[cite: 4, 6].
  - **Integration Tests (Router & Network Boundary):**
    - Verify global exception handlers convert domain exceptions into standardized JSON responses (`{ "error": "...", "detail": "..." }`) with appropriate status codes (singular `detail` key required) [cite: 3, 5].
    - Test REST standards: `204 No Content` endpoints must return empty response bodies[cite: 2, 3].
    - Test input boundary: Ensure invalid path parameters (e.g., malformed UUIDs when `uuid: UUID4` path typing is used) instantly return `422 Unprocessable Entity` without calling service logic[cite: 2, 6].

## Execution Workflow
When executing a testing task with this skill, follow these sequential steps:
1. **Analyze Constraints:** Identify the test layer under scope: unit (service + mocks), repository (real DB session), integration (router + TestClient), E2E, or frontend. Explicitly verify that sync architecture is respected (no `AsyncClient`, no `pytest-asyncio`, no `async def` tests for backend). Check if the module-under-test already has tests so new tests are placed in the correct folder hierarchy (`backend/fastapi/tests/unit|integration|e2e/`) and use existing fixture patterns (conftest.py) rather than inventing new DB/TestClient plumbing.
2. **Draft Plan:** State which test files need to be created/modified; which conftest fixtures (if any) need to be added or extended; and what explicit assertions must be covered per layer. Examples:
   - Service unit tests → Mock every repository method; assert domain exception raised on failure, correct object shape returned on happy path, password was hashed (assert `!=` original plaintext), etc.
   - Repository tests → Rollback per case; assert DB row actually inserted/updated/deleted; assert `exclude_unset=True` partial updates do NOT overwrite untouched columns with NULL.
   - Integration tests → `TestClient`; assert status codes, OpenAPI `response_model` validation via JSON shape, error envelope uses `"detail"` key, 204 responses produce empty bodies, malformed UUID4 path params give 422 before any service code executes.
   For tasks adding 2+ test files OR introducing a new fixture/shared helper, present the plan as a **reviewable patch proposal first — do not apply changes until the user explicitly says LGTM / yes go ahead**.
3. **Write Code:** Once the plan is accepted, write/modify tests adhering strictly to the Testing Framework guidelines above. For single-file edits (adding a couple of unit tests in an existing file) you may write directly after the plan without a separate review gate.
4. **Self-Review:** Check:
   - No `async def test_` or `AsyncClient` / `pytest-asyncio` imports on backend tests
   - Error-envelope assertions use singular `"detail"`
   - 204 assertions check `response.status_code == 204` AND raw body is empty (never `.json()` on 204s)
   - Repository tests roll back data after each test (cleanup guarantee)
   - Every mock in service unit tests uses the same method signatures as the real repository class — no fantasy interfaces
   - No hardcoded credentials/secrets in test data; use random/fake values
5. **Verify:** Run the tests to ensure they pass cleanly, using the Makefile container-exec convention:
   - `make test` (full) or `make test-unit` / `make test-integration` / `make test-e2e` (scoped) as defined in `backend/fastapi/Makefile` (each execs pytest inside the running `api` container)
   - Confirm 0 failures; if tests were added to an empty suite, explicitly note that "N new tests, all passing"
   - If any test fails, attach the full pytest traceback + the relevant source lines in your report so the user can see *why* it failed before you propose a fix