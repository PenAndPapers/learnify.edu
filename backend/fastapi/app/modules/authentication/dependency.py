from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import TokenRepository
from .service import AuthService


def get_token_repository(db: DatabaseDep) -> TokenRepository:
  return TokenRepository(db)


TokenRepositoryDep = Annotated[TokenRepository, Depends(get_token_repository)]


def get_auth_service(repository: TokenRepositoryDep,) -> AuthService:
  return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
