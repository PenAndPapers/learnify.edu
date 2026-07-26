import jwt

from app.core.config import env_config
from app.helpers.security.jwt import (
  decode_jwt,
  encode_jwt,
  get_jwt_claims,
  get_token_family_id,
)
from app.modules.user.exception import UserNotFoundError
from app.modules.user.service import UserService
from app.utils.email.email import render_email_template, send_email

from .exception import (
  TokenExpiredError,
  TokenInvalidError,
  TokenPairMismatchError,
  TokenRevokedError,
  TokenSessionMismatchError,
  TokenTypeMismatchError,
  VerificationLinkNotSentError,
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


class AuthService:
  def __init__(self, repository: TokenRepository):
    self.repository = repository

  def get_token(self, token_str: str) -> UserToken | None:
    """Get a token from the database by its token string."""
    return self.repository.get_by_token(token_str)

  def revoke_tokens(self, tokens: list[str] | None = None) -> None:
    """Revoke the given tokens by updating their is_revoked field in the database."""
    self.repository.revoke_tokens(tokens)

  def generate_token(self, payload: JWTInputParams) -> Token:
    """Generates a JWT token with the given audience, jti, and token type."""

    claims = get_jwt_claims(payload)
    token = encode_jwt(claims)

    return Token(token=token, expires_at=claims.exp)

  def save_token(
    self,
    audience: TokenAudience,
    family_id: str,
    tokens: list[tuple[Token, TokenTypeEnum]],
  ) -> list[UserToken]:
    token_records = [
      UserToken(
        **token_obj.model_dump(),
        is_revoked=False,
        user_id=audience.id,
        token_type=token_type,
        family_id=family_id,
      )
      for token_obj, token_type in tokens
    ]

    db_tokens = self.repository.create(token_records)
    self.repository.db.flush()

    return db_tokens

  def verify_account(self, token_code: str) -> UserToken | None:
    """Verifies the account of the user by checking the token code and returning the corresponding UserToken if valid."""

    validated_token = self.validate_token(TokenValidateRequest(token=token_code, token_type=TokenTypeEnum.EMAIL_VERIFICATION))

    if validated_token.token_type != TokenTypeEnum.EMAIL_VERIFICATION:
      raise TokenInvalidError()

    return validated_token

  def validate_token(self, token: TokenValidateRequest) -> UserToken | None:
    """Validates the given JWT token and returns the corresponding UserToken from the database if valid."""

    try:
      payload = decode_jwt(token.token)

    except jwt.ExpiredSignatureError as e:
      raise TokenExpiredError() from e

    except jwt.InvalidTokenError as e:
      raise TokenInvalidError() from e

    if payload.get("type") != token.token_type:
      raise TokenTypeMismatchError()

    db_token = self.get_token(token.token)

    if db_token.is_revoked:
      raise TokenRevokedError()

    return db_token

  def refresh_token(
    self, token: TokenRefreshRequest, user_service: UserService
  ) -> TokenResponse:
    """Refereshes the given access and refresh tokens and returns new tokens if valid."""

    db_tokens = self.repository.get_by_tokens(token.access_token, token.refresh_token)
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

    db_user = user_service.filter_user({"id": access_token.user_id})

    if db_user is None:
      raise UserNotFoundError()

    new_token = self.create_auth_tokens(
      TokenAudience(id=access_token.user_id, uuid=db_user.uuid)
    )

    self.revoke_tokens([access_token.token, refresh_token.token])
    self.repository.db.flush()

    return new_token

  def create_auth_tokens(self, audience: TokenAudience) -> TokenResponse:
    """Creates a new pair of access and refresh tokens for the given audience and stores them in the database."""

    payload = {
      "jti": get_token_family_id(),
      "aud": audience.uuid,
    }

    access_token = self.generate_token(
      JWTInputParams(**payload, type=TokenTypeEnum.ACCESS)
    )
    refresh_token = self.generate_token(
      JWTInputParams(**payload, type=TokenTypeEnum.REFRESH)
    )

    self.save_token(
      audience,
      payload["jti"],
      [(access_token, TokenTypeEnum.ACCESS), (refresh_token, TokenTypeEnum.REFRESH)],
    )

    return TokenResponse(
      access_token=access_token.token,
      refresh_token=refresh_token.token,
      expires_at=access_token.expires_at,
    )

  def create_email_verification_token(self, audience: TokenAudience) -> Token:
    """Creates a new email verification token for the given audience and stores it in the database."""

    payload = {
      "jti": get_token_family_id(),
      "aud": audience.uuid,
    }

    email_verification_token = self.generate_token(
      JWTInputParams(**payload, type=TokenTypeEnum.EMAIL_VERIFICATION)
    )

    self.save_token(
      audience,
      payload["jti"],
      [(email_verification_token, TokenTypeEnum.EMAIL_VERIFICATION)],
    )

    return email_verification_token

  async def send_verification_email(self, email: str, token: str) -> None:
    """Sends a verification email to the user with the given audience."""

    if not email or not token:
      raise VerificationLinkNotSentError()

    verification_url = (
      f"{env_config.base_url}/api/v1/authentication/token/verify/{token}"
    )

    html_template = render_email_template(
      template_name="account_verification.html",
      context={"verification_url": verification_url},
    )

    await send_email(to=email, subject="Verify your account", content=html_template)
