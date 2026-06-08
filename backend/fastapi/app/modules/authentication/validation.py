from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from app.modules.user.validation import UserTypeEnum


class TokenTypeEnum(StrEnum):
  EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
  PASSWORD_RESET = "PASSWORD_RESET"
  ACCESS = "ACCESS"
  BEARER = "BEARER"
  REFRESH = "REFRESH"


class Token(BaseModel):
  token: str
  expires_at: datetime


class TokenAudience(BaseModel):
  id: int
  uuid: str
  user_type: UserTypeEnum


class UserToken(BaseModel):
  user_id: int
  token: str
  token_type: TokenTypeEnum
  expires_at: datetime
  is_revoked: bool


class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  expires_at: datetime
