from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from redis import asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core import env_config, get_cache_config
from app.database import get_db
from app.modules.authentication.route_employee import router as employee_router

# Routes
from app.modules.authentication.route_enrolle import router as enrolle_router
from app.modules.authentication.route_student import router as student_router
from app.utils.email.email import send_welcome_email

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
app.include_router(enrolle_router)
app.include_router(student_router)
app.include_router(employee_router)

"""
Application default routes
"""


@app.get("/")
async def root():
  return {"message": "Fastapi web application"}


@app.get("/check-health")
async def application_health_check(
  db: Session = Depends(get_db),
) -> dict[str, str]:
  try:
    # Use text() for raw SQL
    db.execute(text("SELECT 1"))
    # Check Redis
    await app.state.redis.ping()

    return {"status": "healthy"}
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail={"status": "unhealthy", "error": str(e)},
    ) from None


@app.get("/check-database")
async def check_database(db: Session = Depends(get_db)) -> dict[str, str]:
  return {"message": "Database connection successful"}


@app.get("/check-redis")
async def check_redis() -> dict[str, str]:
  await app.state.redis.incr("hits")
  return {"hits": await app.state.redis.get("hits")}


@app.get("/check-environment-configs")
def check_environment_configs() -> dict[str, Any]:
  return {
    "name": env_config.app_name,
    "version": env_config.app_version,
    "environment": env_config.environment,
    "secret_key": env_config.secret_key,
    "algorithm": env_config.algorithm,
    "access_token_expire_minutes": env_config.access_token_expire_minutes,
    "refresh_token_expire_days": env_config.refresh_token_expire_days,
    "db_host": env_config.postgres_host,
    "db_port": env_config.postgres_port,
    "db_user": env_config.postgres_user,
    "db_password": env_config.postgres_password,
    "db_name": env_config.postgres_db,
    "cache_host": env_config.redis_host,
    "cache_port": env_config.redis_port,
  }


@app.get("/check-send-email")
async def check_send_email() -> None:
  await send_welcome_email("testuser@email.com", "Test email subject")
