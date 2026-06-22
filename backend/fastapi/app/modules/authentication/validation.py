from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.helpers.validators.token import is_valid_jwt_token_format


class TokenTypeEnum(StrEnum):
  EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
  PASSWORD_RESET = "PASSWORD_RESET"
  ACCESS = "ACCESS"
  BEARER = "BEARER"
  REFRESH = "REFRESH"


class JWTInputParams(BaseModel):
  jti: str
  aud: str
  type: TokenTypeEnum


class JWTClaims(BaseModel):
    iss: str
    iat: float
    jti: str
    aud: str
    type: str
    exp: datetime


class Token(BaseModel):
  token: str
  expires_at: datetime


class TokenAudience(BaseModel):
  id: int
  uuid: str


class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  expires_at: datetime


class TokenRefreshRequest(BaseModel):
  access_token: str = Field(
    ..., # ... means the field is strictly REQUIRED
    min_length=1,
    description="The expired or current JWT access token.",
    examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
  )
  refresh_token: str = Field(
    ...,
    min_length=1,
    description="The valid cryptographically signed refresh token.",
    examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
  )

  @field_validator("access_token", "refresh_token")
  @classmethod
  def validate_token(cls, value: str) -> str:
    if not is_valid_jwt_token_format(value):
      raise ValueError("Invalid JWT token format")
    return value


class TokenValidateRequest(BaseModel):
  token: str = Field(
    ...,
    min_length=1,
    description="The token payload string to evaluate.",
    examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
  )
  token_type: TokenTypeEnum = Field(
    ...,
    description="The type category of the token being validated.",
    examples=[TokenTypeEnum.REFRESH.value]
  )

  @field_validator("token")
  @classmethod
  def validate_token(cls, value: str) -> str:
    if not is_valid_jwt_token_format(value):
      raise ValueError("Invalid JWT token format")
    return value


class UserToken(BaseModel):
  user_id: int
  token: str
  is_revoked: bool
  family_id: str
  token_type: TokenTypeEnum
  expires_at: datetime

  model_config = {"from_attributes": True}


class UserPairToken(BaseModel):
  access_token: UserToken
  refresh_token: UserToken
