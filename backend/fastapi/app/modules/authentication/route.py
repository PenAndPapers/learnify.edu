from fastapi import APIRouter

from app.modules.user.dependency import UserServiceDep

from .dependency import TokenServiceDep
from .validation import TokenRefreshRequest, TokenResponse, TokenValidateRequest

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token(
  token: TokenRefreshRequest,
  token_service: TokenServiceDep,
  user_service: UserServiceDep,
) -> TokenResponse:
  token = token_service.refresh_token(token, user_service)

  return token


@router.post("/token/validate", response_model=bool)
def validate_token(token: TokenValidateRequest, token_service: TokenServiceDep) -> bool:
  token = token_service.validate_token(token)

  return token is not None
