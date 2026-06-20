# FastAPI Modular Monolith - Architecture & Design Patterns

This repository implements a production-ready, highly scalable architectural pattern tailored for FastAPI. Rather than dividing the application by technical layers (standard horizontal MVC), the codebase leverages a **Package-by-Feature (Vertical Slicing)** approach combined with a strict **Layered Architecture** inside each domain module.

---

## 📁 Repository Directory Structure

```text
📁 app/
│
├── 📁 core/               # System-wide configurations, constants, and initialization
├── 📁 database/           # Engine setup and database session lifecycle management
├── 📁 helpers/            # Shared cross-cutting concerns (e.g., encryption, global security tokens)
├── 📁 migrations/         # Alembic database migration environment and version history
├── 📁 utils/              # Generic utility features (e.g., mail clients, third-party integrations)
│
├── 📁 modules/            # 📦 Package-by-Feature Domain Layer
│   │ 
│   └── 📁 feature/        # Self-contained domain module template
│       │── 📄 route.py       # Controller Layer (HTTP Endpoints & Request Routing)
│       │── 📄 service.py     # Business Logic / Domain Service Layer
│       │── 📄 repository.py  # Data Access Layer (Repository Pattern)
│       │── 📄 table.py       # Database Entity Layer (SQLAlchemy ORM Models)
│       │── 📄 validation.py  # Data Transfer Objects / DTOs (Pydantic Schemas)
│       └── 📄 dependency.py  # Dependency Injection Containers & Wiring
│
├── 📄 main.py                # Application bootstrap & FastAPI engine configuration
└── 📄 route.py               # Global API router coordinating module-level entrypoints
```

---

## 🏛️ Architectural Breakdown

### 1. Package by Feature (Modular Monolith)
The application is partitioned into self-contained vertical slices called modules. Every component required to fulfill a specific business capability resides inside its dedicated feature folder. This minimizes cognitive load, ensures high functional cohesion, and simplifies future migration to independent microservices if necessary.

### 2. Internal Layered Architecture
Each domain module enforces a strict separation of concerns, divided into the following clear operational layers:

* **📄 route.py (Controller Layer):** Responsible strictly for handling incoming HTTP requests and structuring HTTP responses. It defines routing paths, operational tags, HTTP status codes, and payload boundaries. *Rule: Keep this layer lean—no business processing or direct persistence logic belongs here.*
* **📄 service.py (Business Logic / Domain Layer):** The primary orchestration engine of the feature. It evaluates domain rules, manages execution state workflows, handles domain-specific exceptions, and coordinates data transformation. It remains completely agnostic of HTTP routing frameworks.
* **📄 repository.py (Data Access Layer / Repository Pattern):** Mediates between the domain and data mapping layers. It abstracts data persistence mechanics away from the business layer using SQLAlchemy ORM expressions (`select`, `update`). This ensures the data engine can be safely mocked out during testing.
* **📄 table.py (Database Entity Layer):** Maps code entities to relational database structures. It declares SQLAlchemy schemas, primary/foreign key mappings, explicit indexing parameters, and relational cascading behaviors.
* **📄 validation.py (Data Transfer Objects / DTO):** Defines strongly typed input and output validation payloads using Pydantic schemas (`BaseModel`). It governs serialization, automated type coercion, and schema parsing (`from_attributes=True`).
* **📄 dependency.py (Dependency Injection Setup):** Manages component lifecycles and instantiates operational graphs using FastAPI's native `Depends` engine. It handles wiring database sessions into repository layers and injecting those repositories smoothly into the target services.

---

## 🔄 Request Lifecycle & Data Flow

When an HTTP request hits the application, data flows deterministically through your architecture layers:

```text
 Client Request ──> [ validation.py (DTO Input Verification) ]
                            │
                            ▼
                    [ route.py (Controller Entry) ]
                            │
                            ▼
                    [ service.py (Business Domain Rules) ]
                            │
                            ▼
                    [ repository.py (Database Abstraction) ]
                            │
                            ▼
                    [ table.py (SQLAlchemy Entity State) ]
                            │
     Client <── [ validation.py (DTO Output Serialization) ]
```

---

## 🚀 Architectural Benefits

1. **Separation of Concerns (SoC):** Distinct technical behaviors are strictly segregated. API route definitions never mutate database queries directly, and storage mechanisms never parse network authentication signatures.
2. **Loose Coupling:** Every layer interacts via predictable public contracts. Upgrading your relational database configuration or switching a storage backend requires altering only your Repository classes—leaving Business Services and Controllers fully untouched.
3. **Optimized Testability:** Because module dependencies are explicitly resolved and injected via constructors, writing isolated unit tests with mocks is straightforward and fast, eliminating the need to spin up a live SQL database instance.
4. **Maintainability & Scale:** New software features can be written as isolated modules without running the risk of introducing accidental side effects across unrelated business domains.