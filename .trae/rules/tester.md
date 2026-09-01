---
alwaysApply: false
description: Use when writing unit tests, API integration tests, component specs, mocking external services, or setting up test suites.
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
- **Naming Standard:** Place backend test files in `backend/fastapi/tests/` using the `test_<feature>.py` naming convention.

```python
# Example: Sync endpoint test standard
from fastapi.testclient import TestClient

def test_get_user_profile_success(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/profile", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()["data"]
```