from fastapi import APIRouter, Depends

from app.modules.user.dependency import get_user_service
from app.modules.user.service import UserService

from .dependency import get_token_service
from .service import TokenService
from .validation import TokenRefreshRequest, TokenResponse, TokenValidateRequest

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
  token: TokenRefreshRequest,
  token_service: TokenService = Depends(get_token_service),
  user_service: UserService = Depends(get_user_service),
) -> TokenResponse:
  token = token_service.refresh_token(token, user_service)

  return token


@router.post("/token/validate", response_model=bool)
async def validate_token(
  token: TokenValidateRequest, token_service: TokenService = Depends(get_token_service)
) -> bool:
  token = token_service.validate_token(token)

  return token is not None
