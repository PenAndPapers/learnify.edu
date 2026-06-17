from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import asyncio as aioredis

from app.core import get_cache_config

# Routes
from app.modules.authentication.route import router as auth_route
from app.modules.employee.route import router as employee_route
from app.modules.enrollee.route import router as enrollee_route
from app.modules.student.route import router as student_route

from .route import router as system_route

cache_config = get_cache_config()


# 1. Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
  # This runs on startup
  app.state.redis = aioredis.from_url(
    f"redis://{cache_config.host}:{cache_config.port}",
    encoding="utf-8",
    decode_responses=True,
  )

  yield  # The app runs while this is suspended

  # This runs on shutdown
  await app.state.redis.close()


app = FastAPI(
  title="Learnify.edu",
  description="FastAPI Application",
  version="1.0.0",
  lifespan=lifespan,
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
