from fastapi import APIRouter

from app.modules.user.dependency import UserServiceDep
from app.modules.user.exception import UserNotFoundError

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


@router.get("/verify/{token_code}", response_model=None)
def verify_account(token_code: str, auth_service: AuthServiceDep, user_service: UserServiceDep) -> None:
  """Enrollee verify their account by clicking the verification link sent to their email."""

  token = auth_service.verify_account(token_code)

  user_id = token.user_id if token else None

  if user_id:
    user = user_service.verify_user(user_id)

    if not user:
      raise UserNotFoundError()

    auth_service.revoke_tokens([token.token])

  return {
    "message": "Account has been successfully activated. You can now log in to your account."
  }
