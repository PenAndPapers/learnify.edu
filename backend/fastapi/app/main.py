from fastapi import FastAPI

from app.core import redis_lifespan

# Routes
from app.modules.authentication.route import router as auth_route
from app.modules.employee.route import router as employee_route
from app.modules.enrollee.route import router as enrollee_route
from app.modules.student.route import router as student_route

from .route import router as system_route

app = FastAPI(
  title="Learnify.edu",
  description="FastAPI Application",
  version="1.0.0",
  lifespan=redis_lifespan,
)


"""
Application module routers
"""
app.include_router(auth_route)
app.include_router(enrollee_route)
app.include_router(student_route)
app.include_router(employee_route)

"""
System routers
"""
app.include_router(system_route)
