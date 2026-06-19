import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException

from app.core.config import AppConfig, SecurityConfig
from app.helpers.validators import is_valid_jwt_token_format
from app.modules.user.service import UserService

from .repository import TokenRepository
from .validation import (
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

  def _generate(
    self, audience: TokenAudience, jti: str, token_type: TokenTypeEnum
  ) -> Token:
    """Generates a token
    Params:
      audience: the audience (user details)
      token_type: the type of token to be generated
    Returns:
      Token: object containing the token string and expiration time
    """

    if not isinstance(token_type, TokenTypeEnum):
      raise HTTPException(
        status_code=400,
        detail="Error: Invalid or missing token type. Token generation is aborted!",
      )

    now = datetime.now(UTC)
    claims = {
      "iat": now.timestamp(),
      "jti": jti,
      "iss": self.app_config.name,
      "aud": str(audience.uuid),
      "type": token_type.value,
    }

    match token_type:
      case TokenTypeEnum.ACCESS:
        expires_at = now + timedelta(
          minutes=self.security_config.access_token_expire_minutes
        )
      case TokenTypeEnum.REFRESH:
        expires_at = now + timedelta(
          days=self.security_config.refresh_token_expire_days
        )
      case _:
        raise HTTPException(
          status_code=400,
          detail="Error: Unhandled token type. Token generation is aborted!",
        )

    claims["exp"] = expires_at.timestamp()

    token = jwt.encode(
      claims, self.security_config.secret_key, algorithm=self.security_config.algorithm
    )

    return Token(token=token, expires_at=expires_at)

  def validate_token(self, token: TokenValidateRequest) -> UserToken | None:
    """Validates a token by cheking the database if data exist and token is not revoked
    Args:
      token: the token string
      token_type: the type of token
    """

    try:
      payload = jwt.decode(
        token.token,
        self.security_config.secret_key,
        algorithms=[self.security_config.algorithm],
        options={"verify_aud": False},
      )

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
    """
    Refresh user token
    """

    if not is_valid_jwt_token_format(
      token.access_token
    ) or not is_valid_jwt_token_format(token.refresh_token):
      raise HTTPException(status_code=400, detail="Error: Token is not valid")

    validated_token = TokenRefreshRequest.model_validate(token)

    db_tokens = self.repository.get_by_tokens(
      [validated_token.access_token, validated_token.refresh_token]
    )

    # check that both access token and refresh token is in database
    if not db_tokens or len(db_tokens) != 2:
      raise HTTPException(status_code=400, detail="Error: Token does not exist.")

    access_token = next(
      (token for token in db_tokens if token.token_type == TokenTypeEnum.ACCESS.value),
      None,
    )
    refresh_token = next(
      (token for token in db_tokens if token.token_type == TokenTypeEnum.REFRESH.value),
      None,
    )

    # check that access and refresh token has value
    if access_token is None or refresh_token is None:
      raise HTTPException(status_code=400, detail="Error: Missing token")

    # check that token are not revoked before creating a new one
    if access_token.is_revoked or refresh_token.is_revoked:
      raise HTTPException(
        status_code=400, detail="Error: Attempt to use a revoked token"
      )

    # check that both access and refresh token user_id is match
    if access_token.user_id != refresh_token.user_id:
      raise HTTPException(status_code=400, detail="Error: Token session mismatch")

    if access_token.family_id != refresh_token.family_id:
      raise HTTPException(status_code=400, detail="Error: Token pair mismatch")

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
    """
    Create access and refresh token and store them in database
    Args:
      audience: the audience (user details)
    Returns:
      TokenResponse: contains the access and refresh token and expiration time of access token
    """

    if audience is None:
      raise HTTPException(status_code=400, detail="Error: Audience cannot be None")

    validated_audience = TokenAudience.model_validate(audience)

    jti = str(uuid.uuid4())

    access_token = self._generate(validated_audience, jti, TokenTypeEnum.ACCESS)
    refresh_token = self._generate(validated_audience, jti, TokenTypeEnum.REFRESH)

    self.repository.create(
      [
        UserToken(
          **token_obj.model_dump(),
          user_id=validated_audience.id,
          is_revoked=False,
          token_type=token_type,
          family_id=jti,
        )
        for token_obj, token_type in [
          (access_token, TokenTypeEnum.ACCESS),
          (refresh_token, TokenTypeEnum.REFRESH),
        ]
      ]
    )

    self.repository.db.flush()

    return TokenResponse(
      access_token=access_token.token,
      refresh_token=refresh_token.token,
      expires_at=access_token.expires_at,
    )


class AuthService:
  def __init__(self):
    pass
