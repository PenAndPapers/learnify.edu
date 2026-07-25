from fastapi import APIRouter

from app.modules.user.dependency import UserServiceDep

from .dependency import AuthServiceDep
from .validation import TokenRefreshRequest, TokenResponse, TokenValidateRequest

router = APIRouter(prefix="/api/v1/authentication/token", tags=["Authentication"])


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
  token: TokenRefreshRequest,
  auth_service: AuthServiceDep,
  user_service: UserServiceDep,
) -> TokenResponse:
  token = auth_service.refresh_token(token, user_service)

  return token


@router.post("/validate", response_model=bool)
def validate_token(token: TokenValidateRequest, auth_service: AuthServiceDep) -> bool:
  token = auth_service.validate_token(token)

  return token is not None
