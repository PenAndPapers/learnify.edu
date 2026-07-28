from fastapi import APIRouter

from app.modules.user.dependency import UserServiceDep
from app.modules.user.exception import UserNotFoundError

from .dependency import AuthServiceDep
from .exception import (
  TokenInvalidFormatError,
  TokenNotFoundError,
)
from .validation import (
  PasswordResetRequest,
  PasswordUpdateRequest,
  TokenRefreshRequest,
  TokenResponse,
  TokenTypeEnum,
  TokenValidateRequest,
)

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/validate_token", response_model=bool)
def validate_token(token: TokenValidateRequest, auth_service: AuthServiceDep) -> bool:
  token = auth_service.validate_token(token)

  return token is not None


@router.post("/refresh_token", response_model=TokenResponse)
def refresh_token(
  token: TokenRefreshRequest,
  auth_service: AuthServiceDep,
  user_service: UserServiceDep,
) -> TokenResponse:
  token = auth_service.refresh_token(token, user_service)

  return token


@router.get("/verify_token/{token_code}", response_model=None)
def verify_account(token_code: str, auth_service: AuthServiceDep, user_service: UserServiceDep) -> None:
  """User verify their account by clicking the verification link sent to their email."""

  token = auth_service.verify_account(token_code)

  user_id = token.user_id if token else None

  if not user_id:
    raise TokenInvalidFormatError()

  user = user_service.verify_user(user_id)

  if not user:
    raise UserNotFoundError()

  auth_service.revoke_tokens([token.token])

  return {
    "message": "Account has been successfully activated. You can now log in to your account."
  }


@router.post("/password/reset", response_model=None)
async def password_reset(payload: PasswordResetRequest, auth_service: AuthServiceDep, user_service: UserServiceDep) -> None:
  """Request a password reset link"""

  token = auth_service.password_reset(payload, user_service)

  user_id = token.user_id if token else None

  if not user_id:
    raise TokenInvalidFormatError()

  await auth_service.send_password_reset_email(token, user_service)

  return {
    "message": "Password reset link has been sent to your email."
  }


@router.post("/password/update", response_model=None)
def password_update(payload: PasswordUpdateRequest, auth_service: AuthServiceDep, user_service: UserServiceDep) -> None:
  """Update user's password
  
  TODO:
    - validate the token is valid and not used or expired
    - validate user password input
    - password and confirm password should match
    - encrypt the new password
    - update user password in database using user's uuid from the token
    - send email to user with message that email has been updated
    - revoke the password reset token
  """

  db_token = auth_service.validate_token(
    TokenValidateRequest(token=payload.token, token_type=TokenTypeEnum.PASSWORD_RESET)
  )

  if not db_token:
    raise TokenNotFoundError()

  user_service.update_password(db_token.user_id, payload.new_password)
  auth_service.revoke_tokens([payload.token])

  return {
    "message": "Password has been successfully updated!"
  }

