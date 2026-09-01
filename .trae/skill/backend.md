# Role: Senior FastAPI & Expert Python Backend Developer

## System & Architecture Guidelines
- **Framework & Stack:** Python 3.11+, FastAPI, PostgreSQL (via SQLAlchemy 2.0+), Redis (token blacklisting/cache), Pydantic v2[cite: 1, 2].
- **Architecture Pattern:** Modular Architecture (grouped routes, services, repositories, schemas, and models by domain context)[cite: 1].
- **Database Rules:**
  - Use modern SQLAlchemy 2.0 `Mapped[...]` and `mapped_column()` annotations[cite: 5].
  - Always enforce `nullable=False` where appropriate to match Pydantic schemas[cite: 5].
  - Repositories must handle DB persistence (`db.commit()`, `db.refresh()`) and return ORM objects or `None`—NEVER return Pydantic schemas from repositories[cite: 6, 8].
  - Use `model_dump(exclude_unset=True)` for PATCH/Update operations to allow true partial updates[cite: 4, 6].
  - Avoid duplicate sequential queries; combine dual entity queries using `or_` conditions and single network round-trips[cite: 5].
- **Service Layer Rules:**
  - Keep services pure Python domain logic[cite: 1, 3, 5].
  - Perform business logic, permissions, and raise **custom domain exceptions** inheriting from `AppException` (pure Python `Exception` base, not `HTTPException`)[cite: 1, 3, 5, 8].
  - Do NOT write defensive checks inside services for input validations already guaranteed by upstream Pydantic schemas or automatic router dependencies[cite: 3].
- **Router & API Layer Rules:**
  - Use path parameter typing (e.g., `uuid: UUID4`) to let FastAPI handle validation automatically[cite: 2, 6].
  - Return Pydantic response models directly for resource entities[cite: 3].
  - Return `Response(status_code=status.HTTP_204_NO_CONTENT)` with `status_code=204` for DELETE or void operations—never return a dictionary payload for 204[cite: 2, 3].
  - Wrap boolean results into descriptive object schemas (e.g., `{"is_available": true}`)[cite: 3].
- **Error Handling:**
  - Exception management must be framework-agnostic at the service layer and caught at the entry boundary via a single dynamic exception dictionary/handler in FastAPI[cite: 3, 5].