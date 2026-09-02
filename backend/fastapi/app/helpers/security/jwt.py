from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from app.core import get_app_config, get_security_config
from app.helpers.validators.token import is_valid_jwt_token_format
from app.modules.authentication.validation import (
  JWTClaims,
  JWTInputParams,
  TokenTypeEnum,
)

app_config = get_app_config()
jwt_config = get_security_config()


def get_token_family_id() -> str:
  """Generate a token family id used for pairing access and refresh token"""
  return str(uuid4())


def get_jwt_expiration(type: TokenTypeEnum, time: datetime) -> datetime:
  """Get JWT expiration based on token type"""

  match type:
    case TokenTypeEnum.ACCESS:
      return time + timedelta(minutes=jwt_config.access_token_expire_minutes)
    case TokenTypeEnum.REFRESH:
      return time + timedelta(days=jwt_config.refresh_token_expire_days)
    case TokenTypeEnum.EMAIL_VERIFICATION:
      return time + timedelta(hours=jwt_config.email_verification_token_expire_hours)
    case TokenTypeEnum.PASSWORD_RESET:
      return time + timedelta(minutes=jwt_config.password_reset_expire_minutes)
    case _:
      raise ValueError("Error: Unhandled token type. Token generation is aborted!")


def get_jwt_claims(claims: JWTInputParams) -> JWTClaims:
  """Get JWT claims"""

  current_time = datetime.now(UTC)

  return JWTClaims(
    iss=app_config.name,
    iat=current_time.timestamp(),
    exp=get_jwt_expiration(claims.type, current_time),
    **claims.model_dump(),
  )


def encode_jwt(claims: JWTClaims) -> str:
  """Encode JWT"""

  payload = claims.model_dump()

  if isinstance(payload.get("exp"), datetime):
    payload["exp"] = int(payload["exp"].timestamp())

  token = jwt.encode(payload, jwt_config.secret_key, algorithm=jwt_config.algorithm)

  return token


def decode_jwt(token: str) -> dict[str, Any]:
  """Decode JWT"""

  if not is_valid_jwt_token_format(token):
    raise ValueError("Error: Token provided is not valid")

  decoded_token = jwt.decode(
    token,
    jwt_config.secret_key,
    algorithms=[jwt_config.algorithm],
    options={"verify_aud": False},
  )

  return decoded_token
