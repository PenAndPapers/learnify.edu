from typing import Annotated

from fastapi import Depends

from app.core.config import (
  AppConfigDep,
  SecurityConfigDep,
)
from app.database import DatabaseDep

from .repository import TokenRepository
from .service import TokenService


def get_token_repository(db: DatabaseDep) -> TokenRepository:
  return TokenRepository(db)


TokenRepositoryDep = Annotated[TokenRepository, Depends(get_token_repository)]


def get_token_service(
  app_config: AppConfigDep,
  security_config: SecurityConfigDep,
  repository: TokenRepositoryDep,
) -> TokenService:
  return TokenService(app_config, security_config, repository)


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
