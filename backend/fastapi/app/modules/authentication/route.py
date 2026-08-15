from fastapi import APIRouter

from app.helpers.types import MessageResponse
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
  RefreshTokenRequest,
  TokenResponse,
  TokenTypeEnum,
  ValidateTokenRequest,
  ValidTokenResponse,
)

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/validate_token", response_model=ValidTokenResponse)
def validate_token(token: ValidateTokenRequest, auth_service: AuthServiceDep) -> ValidTokenResponse:
  token = auth_service.validate_token(token)

  if not token:
    raise TokenNotFoundError()

  return ValidTokenResponse(is_valid=True, token_type=token.token_type, token=token.token, expires_at=token.expires_at)


@router.post("/refresh_token", response_model=TokenResponse)
def refresh_token(
  token: RefreshTokenRequest,
  auth_service: AuthServiceDep,
  user_service: UserServiceDep,
) -> TokenResponse:
  token = auth_service.refresh_token(token, user_service)

  return token


@router.get("/verify/{token_code}", response_model=MessageResponse)
def verify_account(token_code: str, auth_service: AuthServiceDep, user_service: UserServiceDep) -> MessageResponse:
  """User verify their account by clicking the verification link sent to their email."""

  token = auth_service.verify_account(token_code)

  user_id = token.user_id if token else None

  if not user_id:
    raise TokenInvalidFormatError()

  user = user_service.verify_user(user_id)

  if not user:
    raise UserNotFoundError()

  revoked_tokens = auth_service.revoke_tokens([token.token])

  if not revoked_tokens:
    raise TokenNotFoundError()

  return MessageResponse(
    message="Account has been successfully activated. You can now log in to your account."
  )


@router.post("/password/reset", response_model=MessageResponse)
async def password_reset(payload: PasswordResetRequest, auth_service: AuthServiceDep, user_service: UserServiceDep) -> MessageResponse:
  """Request a password reset link"""

  token = auth_service.password_reset(payload, user_service)

  user_id = token.user_id if token else None

  if not user_id:
    raise TokenInvalidFormatError()

  await auth_service.send_password_reset_email(token, user_service)

  return MessageResponse(
    message="Password reset link has been sent to your email."
  )


@router.post("/password/update", response_model=MessageResponse)
async def password_update(payload: PasswordUpdateRequest, auth_service: AuthServiceDep, user_service: UserServiceDep) -> MessageResponse:
  """Update user's password"""

  db_token = auth_service.validate_token(
    ValidateTokenRequest(token=payload.token, token_type=TokenTypeEnum.PASSWORD_RESET)
  )

  if not db_token:
    raise TokenNotFoundError()

  db_user = user_service.update_password(db_token.user_id, payload.new_password)

  password_reset_tokens = auth_service.get_user_tokens_by_type(db_token.user_id, TokenTypeEnum.PASSWORD_RESET)
  unused_tokens = [token.token for token in password_reset_tokens if not token.is_revoked]

  revoked_tokens = auth_service.revoke_tokens(unused_tokens)

  if not revoked_tokens:
    raise TokenNotFoundError()

  await auth_service.send_password_updated_email(db_user)

  return MessageResponse(
    message="Password has been successfully updated!"
  )

