from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import TokenRepository
from .service import TokenService


def get_token_repository(db: Session = Depends(get_db)) -> TokenRepository:
  return TokenRepository(db)


def get_token_service(
  repository: TokenRepository = Depends(get_token_repository),
) -> TokenService:
  return TokenService(repository)
