from fastapi import APIRouter

from app.modules.user.dependency import UserServiceDep
from app.modules.user.exception import UserNotFoundError

from .dependency import AuthServiceDep
from .exception import TokenInvalidFormatError
from .validation import (
  PasswordResetRequest,
  TokenRefreshRequest,
  TokenResponse,
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
  """User has requested to update their password and system will send a link to update password
  
  TODO:
    - validate user input email
    - validate if email exist
    - generate a jwt token with type of RESET_PASSWORD
    - set token validity for 15mins
    - prevent user to flood sending of email when they have unused and not expired RESET_PASSWORD token
    - send email to user with password update link
  """
  token = auth_service.password_reset(payload, user_service)

  user_id = token.user_id if token else None

  if not user_id:
    raise TokenInvalidFormatError()

  await auth_service.send_password_reset_email(token, user_service)

  return {
    "message": "Password reset link has been sent to your email."
  }


@router.post("/password/update", response_model=None)
def password_update() -> None:
  """Update user's password
  
  TODO:
    - validate the token is valid and not used or expired
    - validate user password input
    - password and confirm password should match
    - update user password in database using user's uuid from the token
    - send email to user with message that email has been updated
    - remove the password reset token
  """
  pass
