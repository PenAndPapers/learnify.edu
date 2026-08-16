from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import TokenRepository
from .service import AuthService, TokenService


def get_token_repository(db: DatabaseDep) -> TokenRepository:
  return TokenRepository(db)


TokenRepositoryDep = Annotated[TokenRepository, Depends(get_token_repository)]


def get_token_service(repository: TokenRepositoryDep,) -> TokenService:
  return TokenService(repository)

TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def get_auth_service(token_service: TokenServiceDep) -> AuthService:
  return AuthService(token_service = token_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
