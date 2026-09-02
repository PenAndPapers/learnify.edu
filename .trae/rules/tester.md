---
alwaysApply: false
description: Use when writing unit tests, API integration tests, component specs, mocking external services, or setting up test suites.
globs:
  - "backend/fastapi/tests/**/*.py"
  - "backend/fastapi/pyproject.toml"
  - "frontend/nuxt4/**/*.spec.ts"
  - "frontend/nuxt4/**/*.test.ts"
  - "frontend/nuxt4/vitest.config.*"
---

# Test Engineering & Quality Assurance Rules

## 1. Role & QA Strategy
Act as a **QA Automation & Test Engineer**:
- Write deterministic, repeatable, and isolated tests that catch regressions early.
- **Backend:** Test FastAPI routes, synchronous SQLAlchemy sessions, and Pydantic validation using **Pytest** and **FastAPI `TestClient` (sync, httpx-backed)**. Do NOT use `AsyncClient` / `pytest-asyncio` for core backend tests — the project intentionally uses a synchronous architecture.
- **Frontend:** Test Nuxt 4 components, composables, and Pinia stores (when added) using **Vitest** and `@nuxt/test-utils`.
- **Isolation Principle:** Tests must never depend on execution order or persistent external database state. Always use clean fixtures or BEGIN/ROLLBACK transaction wrapping.

---

## 2. Backend Testing Rules (`backend/fastapi/`)

### A. Environment & Framework
- Use **Pytest** as the primary test runner (already configured in `pyproject.toml` with coverage, markers, and testpaths).
- Use **FastAPI `TestClient` (from `fastapi.testclient`)** for endpoint testing — it is synchronous and matches the sync SQLAlchemy + sync route stack.
- Database operations must run against a **separate test database instance** or a synchronous transaction fixture that wraps each test in `begin_nested()`/`rollback()` so committed data is never visible between tests.

### B. Unit & Integration Requirements
- **Route / Controller Tests:** Verify happy paths, invalid payload errors (`400`), unauthorized access (`401`), missing resources (`404`), and schema/UUID validation (`422`).
- **Service Logic:** Test business rules with mocked external HTTP or third-party dependencies (e.g., mock Redis connections, email delivery, or payment gateways). Verify services raise the correct pure-Python `AppException` subclass on failure.
- **Repository Tests (optional but recommended):** Test actual persistence against the rollback-wrapped DB session, especially for `exclude_unset=True` partial updates and relation cascades.
- **Naming Standard:** Place backend test files in `backend/fastapi/tests/` using the `test_<feature>.py` naming convention. Maintain three sub-folders with aligned pytest markers: `tests/unit/` (fast, no DB/network), `tests/integration/` (DB or multiple services), `tests/e2e/` (full stack via TestClient or a real browser driver).

```python
# Example 1: malformed UUID path param → auto 422 from Pydantic UUID4
from fastapi.testclient import TestClient

def test_get_student_returns_422_when_uuid_malformed(client: TestClient):
    response = client.get("/api/v1/students/not-a-uuid")
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["type"] == "uuid_parsing" for e in errors)
```

```python
# Example 2: DELETE → 204 empty body (no .json()!)
from fastapi.testclient import TestClient

def test_delete_student_success_returns_204_no_body(client: TestClient, auth_headers: dict, seed_student_id: str):
    response = client.delete(f"/api/v1/students/{seed_student_id}", headers=auth_headers)
    assert response.status_code == 204
    assert response.content == b""
```

```python
# Example 3: Error envelope uses SINGULAR "detail" key (never "details")
from fastapi.testclient import TestClient

def test_get_missing_student_returns_envelope(client: TestClient, auth_headers: dict):
    unknown = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/students/{unknown}", headers=auth_headers)
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert "detail" in body and isinstance(body["detail"], str)
    assert "details" not in body
```

```python
# Example 4: Service UNIT test (no DB, no HTTP) — raises domain exception
from app.core.exception import StudentNotFoundException
from app.modules.student.service import StudentService

def test_student_service_get_raises_when_missing(student_repository_stub):
    student_repository_stub.get_by_id.return_value = None
    service = StudentService(repository=student_repository_stub)
    try:
        service.get_student_by_id("00000000-0000-0000-0000-000000000000")
    except StudentNotFoundException as exc:
        assert exc.status_code == 404
        assert exc.error_code == "STUDENT_NOT_FOUND"
```

---

## 3. Frontend Testing Rules (`frontend/nuxt4/`)

- **Test runner:** Vitest (or `@vue/test-utils`) plus `@nuxt/test-utils` for server-/route-level spec coverage. Set up in `frontend/nuxt4/vitest.config.ts`; run via `pnpm test` or the matching package script.
- **Scope:** Unit-test composables, pure utility helpers, and presentational components. Avoid snapshot tests unless the component is stable and fully-owned; prefer behavioral assertions on rendered text and emitted events.
- **Mock boundaries:** Mock network calls at the `$fetch` / `ofetch` layer (never inside a component directly). Use the same error-envelope shape as the real backend (`{ error: "CODE", detail: "msg" }`).
- **Pinia/Tailwind flag-safety:** Do not generate `defineStore()` imports, Tailwind class selectors, or CSS snapshot rules in tests if those dependencies are not yet listed in `frontend/nuxt4/package.json` + enabled in `nuxt.config.ts`. Skip Pinia-related test fixtures in that case.

---

## 4. Project Commands — Run Tests Inside Containers or Host
Always prefer the project-provided Make targets so CI and dev use the same invocation:
```make
# Backend (runs inside the `api` container via `docker compose exec -T api ...`)
$ make test-unit         # pytest -m unit
$ make test-integration  # pytest -m integration
$ make test-e2e          # pytest -m e2e
$ make test              # all three in order

# Frontend (host-native inside frontend/nuxt4; wrapper via root Make or direct pnpm)
$ cd frontend/nuxt4 && pnpm test
$ cd frontend/nuxt4 && pnpm typecheck   # treat strict TS failures as a test gate
```