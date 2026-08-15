from datetime import UTC, datetime

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.helpers.types import NonEmptyStr, PositiveInt

from .exception import TokenNotFoundError, TokenRequiredError
from .table import TokenTable
from .validation import TokenTypeEnum, UserPairToken, UserToken


class TokenRepository:
  def __init__(self, db: Session):
    self.db = db
    self.model = TokenTable

  def get_active_user_tokens(
      self,
      user_id: PositiveInt,
      token_type: TokenTypeEnum,
      limit: int | None = None,
  ) -> list[TokenTable]:
    """Get active user tokens with optional limit."""
    query = (
        select(self.model)
        .where(
            self.model.user_id == user_id,
            self.model.token_type == token_type,
            self.model.is_revoked.is_(False),
        )
        .order_by(self.model.created_at.desc())
    )

    if limit is not None:
      query = query.limit(limit)

    return list(self.db.scalars(query).all())

  def create(self, tokens: list[UserToken]) -> list[UserToken]:
    """Store authentication tokens in the database"""

    records = [self.model(**token.model_dump()) for token in tokens]

    self.db.add_all(records)

    return [UserToken.model_validate(record) for record in records]

  def get_by_token(self, token: NonEmptyStr) -> TokenTable | None:
    """Get a token record from the database by token string"""

    if not token:
      raise TokenRequiredError()

    query = select(self.model).where(self.model.token == token)
    db_token = self.db.scalar(query)

    return db_token

  def get_user_token_by_type(self, user_id: PositiveInt, token_type: TokenTypeEnum) -> TokenTable | None:
    """Get user lastest active token by type"""
    query = self.get_active_user_tokens(user_id, token_type, limit=1)
    return query[0] if query else None


  def get_user_tokens_by_type(self, user_id: PositiveInt, token_type: TokenTypeEnum) -> list[TokenTable] | None:
    """Get user active tokens by type"""
    return self.get_active_user_tokens(user_id, token_type)

  def get_auth_token_pair(self, access_token: NonEmptyStr, refresh_token: NonEmptyStr) -> UserPairToken:
    """Get authentication pair token"""

    query = (
      select(self.model)
      .where(
        or_(
          (self.model.token == access_token) & (self.model.token_type == TokenTypeEnum.ACCESS),
          (self.model.token == refresh_token) & (self.model.token_type == TokenTypeEnum.REFRESH),
        )
      )
    )
    db_tokens = self.db.scalars(query).all()

    if not db_tokens or len(db_tokens) != 2:
        raise TokenNotFoundError()

    db_access_token = next((token for token in db_tokens if token.token_type == TokenTypeEnum.ACCESS), None)
    db_refresh_token = next((token for token in db_tokens if token.token_type == TokenTypeEnum.REFRESH), None)

    # Ensures that both tokens are found otherwise we raise error
    if not db_access_token or not db_refresh_token:
      raise TokenNotFoundError()

    return UserPairToken(access_token=db_access_token, refresh_token=db_refresh_token)

  def revoke_tokens(self, tokens: list[NonEmptyStr] | None = None) -> list[NonEmptyStr]:
    """Update token to a revoke state"""

    if not tokens:
      raise TokenRequiredError()

    query = (
      update(self.model)
      .where(self.model.token.in_(tokens))
      .values(is_revoked=True, deleted_at=datetime.now(UTC))
      .returning(self.model.token)
    )

    return list(self.db.scalars(query).all())
