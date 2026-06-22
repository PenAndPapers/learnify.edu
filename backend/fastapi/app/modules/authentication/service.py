
import jwt
from fastapi import HTTPException

from app.core.config import AppConfig, SecurityConfig
from app.helpers.security.jwt import (
  decode_jwt,
  encode_jwt,
  get_jwt_claims,
  get_token_family_id,
)
from app.helpers.validators import is_valid_jwt_token_format
from app.modules.user.service import UserService

from .exceptions import (
  TokenInvalidFormatError,
  TokenPairMismatchError,
  TokenRevokedError,
  TokenSessionMismatchError,
)
from .repository import TokenRepository
from .validation import (
  JWTInputParams,
  Token,
  TokenAudience,
  TokenRefreshRequest,
  TokenResponse,
  TokenTypeEnum,
  TokenValidateRequest,
  UserToken,
)


class TokenService:
  def __init__(
    self,
    app_config: AppConfig,
    security_config: SecurityConfig,
    repository: TokenRepository,
  ):
    self.app_config = app_config
    self.security_config = security_config
    self.repository = repository

  def generate(self, payload: JWTInputParams) -> Token:
    """Generates a JWT token with the given audience, jti, and token type."""

    if not isinstance(payload.type, TokenTypeEnum):
      raise HTTPException(
        status_code=400,
        detail="Error: Invalid or missing token type. Token generation is aborted!",
      )

    claims = get_jwt_claims(payload)
    token = encode_jwt(claims)

    return Token(token=token, expires_at=claims.exp)

  def validate_token(self, token: TokenValidateRequest) -> UserToken | None:
    """Validates the given JWT token and returns the corresponding UserToken from the database if valid."""

    try:
      payload = decode_jwt(token.token)

      if payload.get("type") != token.token_type:
        raise HTTPException(status_code=400, detail="Error: Token type mismatch")

      db_token = self.repository.get_by_token(token.token)

      if db_token and db_token.is_revoked:
        raise HTTPException(status_code=400, detail="Error: Token is revoked")

      return db_token

    except jwt.ExpiredSignatureError as e:
      raise HTTPException(status_code=400, detail="Error: Token is expired") from e

    except jwt.InvalidTokenError as e:
      raise HTTPException(
        status_code=400, detail="Error: Token signature is invalid"
      ) from e

  def refresh_token(
    self, token: TokenRefreshRequest, user_service: UserService
  ) -> TokenResponse:
    """Refereshes the given access and refresh tokens and returns new tokens if valid."""

    if not is_valid_jwt_token_format(token.access_token) or not is_valid_jwt_token_format(token.refresh_token):
      raise TokenInvalidFormatError()

    validated_token = TokenRefreshRequest.model_validate(token)

    db_tokens = self.repository.get_by_tokens(
      [validated_token.access_token, validated_token.refresh_token]
    )
    access_token = db_tokens.access_token
    refresh_token = db_tokens.refresh_token

    # check that token are not revoked before creating a new one
    if access_token.is_revoked or refresh_token.is_revoked:
      raise TokenRevokedError()

    # check that both access and refresh token user_id is match
    if access_token.user_id != refresh_token.user_id:
      raise TokenSessionMismatchError()

    # check that both access and refresh token family_id is match
    if access_token.family_id != refresh_token.family_id:
      raise TokenPairMismatchError()

    db_user = user_service.get_user({"id": access_token.user_id})

    if db_user is None:
      raise HTTPException(status_code=400, detail="Error: User not found")

    new_token = self.create_auth_tokens(
      TokenAudience(id=access_token.user_id, uuid=db_user.uuid)
    )

    self.repository.revoke_tokens([access_token.token, refresh_token.token])
    self.repository.db.flush()

    return new_token

  def create_auth_tokens(self, audience: TokenAudience) -> TokenResponse:
    """Creates a new pair of access and refresh tokens for the given audience and stores them in the database."""

    if audience is None:
      raise HTTPException(status_code=400, detail="Error: Audience cannot be empty")

    payload = {
      "jti": get_token_family_id(),
      "aud": audience.uuid,
    }

    access_token = self.generate(JWTInputParams(**payload, type=TokenTypeEnum.ACCESS))
    refresh_token = self.generate(JWTInputParams(**payload, type=TokenTypeEnum.REFRESH))
    tokens = [
      UserToken(
        **token_obj.model_dump(),
        is_revoked=False,
        user_id=audience.id,
        token_type=token_type,
        family_id=payload["jti"]
      )
      for token_obj, token_type in [
        (access_token, TokenTypeEnum.ACCESS),
        (refresh_token, TokenTypeEnum.REFRESH),
      ]
    ]

    self.repository.create(tokens)
    self.repository.db.flush()

    return TokenResponse(
      access_token=access_token.token,
      refresh_token=refresh_token.token,
      expires_at=access_token.expires_at,
    )


class AuthService:
  def __init__(self):
    pass
