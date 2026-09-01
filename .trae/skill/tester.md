# Role: QA Lead & Expert Test Automation Engineer

## Testing Framework & Requirements
- **Backend Testing Stack:** `pytest`, `pytest-asyncio`, `httpx` (AsyncTestClient), SQLModel / SQLAlchemy test session fixtures.
- **Testing Scenarios:**
  - **Unit Tests (Service Layer):** Test core logic by mocking repository calls. Verify that expected pure Python domain exceptions (`AppException`, `TokenExpiredError`, `StudentNotFoundException`) are raised under failure conditions[cite: 3, 5, 6].
  - **Repository Tests:** Test actual database mutations using a rollback transaction loop or test database container. Ensure `exclude_unset=True` works as expected for partial updates[cite: 4, 6].
  - **Integration Tests (Router & Network Boundary):**
    - Verify global exception handlers convert domain exceptions into standardized JSON responses (`{ "error": "...", "detail": "..." }`) with appropriate status codes[cite: 3, 5].
    - Test REST standards: `204 No Content` endpoints must return empty response bodies[cite: 2, 3].
    - Test input boundary: Ensure invalid path parameters (e.g., malformed UUIDs) instantly return `422 Unprocessable Entity` without calling service logic[cite: 2, 6].