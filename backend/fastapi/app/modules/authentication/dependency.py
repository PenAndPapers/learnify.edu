from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import TokenRepository
from .service import TokenService


def get_token_repository(db: DatabaseDep) -> TokenRepository:
  return TokenRepository(db)


TokenRepositoryDep = Annotated[TokenRepository, Depends(get_token_repository)]


def get_token_service(repository: TokenRepositoryDep,) -> TokenService:
  return TokenService(repository)


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
