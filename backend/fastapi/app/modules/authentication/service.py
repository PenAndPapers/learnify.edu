import logging
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_app_config, get_security_config

from .repository import TokenRepository
from .validation import Token, TokenAudience, TokenResponse, TokenTypeEnum, UserToken


class TokenService:
  def __init__(self, repository: TokenRepository):
    security_config = get_security_config()

    self.repository = repository

    self.app_config = get_app_config()
    self.secret_key = security_config.secret_key
    self.algorith = security_config.algorithm
    self.access_token_expires_min = security_config.access_token_expire_minutes
    self.refresh_token_expire_days = security_config.refresh_token_expire_days

  def _generate(self, audience: TokenAudience, token_type: TokenTypeEnum) -> Token:
    """
    Generates a token
    Params:
      audience: the audience (user details)
      token_type: the type of token to be generated
    Returns:
      Token: object containing the token string and expiration time
    """
    if not isinstance(token_type, TokenTypeEnum):
      error_message = (
        f"Invalid or missing token type {token_type}. Token generation is aborted!"
      )
      logging.error(error_message)
      raise ValueError(error_message)

    now = datetime.now(UTC)
    claims = {
      "iat": now.timestamp(),
      "jti": str(uuid.uuid4()),
      "iss": self.app_config.name,
      "aud": audience.uuid,
      "user_type": audience.user_type,
      "type": token_type.value,
    }

    match token_type:
      case TokenTypeEnum.ACCESS:
        expires_at = now + timedelta(minutes=self.access_token_expires_min)
      case TokenTypeEnum.REFRESH:
        expires_at = now + timedelta(days=self.refresh_token_expire_days)
      case _:
        error_message = f"Error: Unhandled token type {token_type}"
        logging.critical(error_message)
        raise NotImplementedError(error_message)

    claims["exp"] = expires_at.timestamp()

    token = jwt.encode(claims, self.secret_key, algorithm=self.algorith)

    return Token(token=token, expires_at=expires_at)

  def _validate(self):
    """
    TODO: implement later
    """
    pass

  def create_auth_tokens(self, audience: TokenAudience) -> TokenResponse:
    """
    Create access and refresh token and store them in database
    Args:
      audience: the audience (user details)
    Returns:
      TokenResponse: contains the access and refresh token and expiration time of access token
    """
    access_token = self._generate(audience, TokenTypeEnum.ACCESS)
    refresh_token = self._generate(audience, TokenTypeEnum.REFRESH)

    self.repository.store_auth_tokens(
      [
        UserToken(
          **access_token.model_dump(),
          user_id=audience.id,
          token_type=TokenTypeEnum.ACCESS,
          is_revoked=False,
        ),
        UserToken(
          **refresh_token.model_dump(),
          user_id=audience.id,
          token_type=TokenTypeEnum.REFRESH,
          is_revoked=False,
        ),
      ]
    )

    return TokenResponse(
      access_token=access_token.token,
      refresh_token=refresh_token.token,
      expires_at=access_token.expires_at,
    )
