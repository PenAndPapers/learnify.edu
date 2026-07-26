---
alwaysApply: false
description: Use when writing unit tests, API integration tests, component specs, mocking external services, or setting up test suites.
---

# Test Engineering & Quality Assurance Rules

## 1. Role & QA Strategy
Act as a **QA Automation & Test Engineer**:
- Write deterministic, repeatable, and isolated tests that catch regressions early.
- **Backend:** Test FastAPI routes, async SQLAlchemy queries, and Pydantic validation using **Pytest** and **HTTPX (`AsyncClient`)**.
- **Frontend:** Test Nuxt 4 components, composables, and Pinia stores using **Vitest** and `@nuxt/test-utils`.
- **Isolation Principle:** Tests must never depend on execution order or persistent external database state. Always use clean fixtures or rollbacks.

---

## 2. Backend Testing Rules (`backend/fastapi/`)

### A. Environment & Framework
- Use **Pytest** as the primary test runner.
- Use **HTTPX (`AsyncClient`)** with FastAPI’s `TestClient` or async test setups for endpoint testing.
- Database operations must run against a **separate test database instance** or an async transaction session that automatically rolls back after each test function.

### B. Unit & Integration Requirements
- **Route / Controller Tests:** Verify happy paths, invalid payload errors (`400`), unauthorized access (`401`), and missing resources (`404`).
- **Service Logic:** Test business rules with mocked external HTTP or third-party dependencies (e.g., mock Redis connections or payment gateways).
- **Naming Standard:** Place backend test files in `backend/fastapi/tests/` using the `test_<feature>.py` naming convention.

```python
# Example: Async endpoint test standard
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_user_profile_success(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.get("/api/v1/profile", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()["data"]