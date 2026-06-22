from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core import AppException, redis_lifespan

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

@app.exception_handler(AppException)
def global_exception_handler(request: Request, exception: AppException):
  return JSONResponse(
    status_code=exception.status_code,
    content={
      "error": exception.error_code,
      "detail": exception.message
    }
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
