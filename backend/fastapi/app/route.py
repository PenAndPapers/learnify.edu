from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

# Utils
from app.utils.email.email import send_welcome_email

router = APIRouter(prefix="/api/v1/system", tags=["System"])


@router.get("/")
async def root():
  return {"message": "Fastapi web application"}


@router.get("/check-health")
async def application_health_check(
  request: Request,
  db: Session = Depends(get_db),
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
async def check_database(db: Session = Depends(get_db)) -> dict[str, str]:
  return {"message": "Database connection successful"}


@router.get("/check-redis")
async def check_redis(request: Request) -> dict[str, str]:
  await request.app.state.redis.incr("hits")
  return {"hits": await request.app.state.redis.get("hits")}


@router.get("/check-send-email")
async def check_send_email() -> None:
  await send_welcome_email("testuser@email.com", "Test email subject")
