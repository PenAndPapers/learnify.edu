from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

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


class UserToken(BaseModel):
  user_id: int
  token: str
  token_type: TokenTypeEnum
  expires_at: datetime
  is_revoked: bool
  family_id: str | None

  model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  expires_at: datetime


class TokenRefreshRequest(BaseModel):
  access_token: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC...")
  refresh_token: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC...")

class TokenValidateRequest(BaseModel):
  token: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC...")
  token_type: TokenTypeEnum = Field(default=TokenTypeEnum.ACCESS)