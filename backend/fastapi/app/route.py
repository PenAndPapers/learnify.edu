from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import text

from app.database import DatabaseDep

# Utils
from app.utils.email.email import send_welcome_email

router = APIRouter(prefix="/api/v1/system", tags=["System"])


@router.get("/")
def root():
  return {"message": "Fastapi web application"}


@router.get("/check-health")
async def application_health_check(
  request: Request,
  db: DatabaseDep,
) -> dict[str, str]:
  try:
    # Use text() for raw SQL
    db.execute(text("SELECT 1"))
    # Check Redis
    await request.app.state.redis.ping()

    return {"status": "healthy"}
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail={"status": "unhealthy", "error": str(e)},
    ) from None


@router.get("/check-database")
def check_database(db: DatabaseDep) -> dict[str, str]:
  try:
    # Use text() for raw SQL
    db.execute(text("SELECT 1"))

    return {"message": "Database connection successful"}
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail={"status": "unhealthy", "error": str(e)},
    ) from None


@router.get("/check-redis")
async def check_redis(request: Request) -> dict[str, str]:
  await request.app.state.redis.incr("hits")
  return {"hits": await request.app.state.redis.get("hits")}


@router.get("/check-send-email")
async def check_send_email() -> None:
  await send_welcome_email("testuser@email.com", "Test email subject")
