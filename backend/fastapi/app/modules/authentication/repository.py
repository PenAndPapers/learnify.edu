from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.helpers.types import NonEmptyStr, PositiveInt

from .exception import TokenRequiredError
from .table import TokenTable
from .validation import TokenTypeEnum, UserToken


class TokenRepository:
  def __init__(self, db: Session):
    self.db = db
    self.model = TokenTable

  def add(self, tokens: list[UserToken]) -> list[TokenTable]:
    """Store authentication tokens in the database"""

    records = [self.model(**token.model_dump()) for token in tokens]

    self.db.add_all(records)

    return records

  def get_active_user_tokens(
      self,
      user_id: PositiveInt,
      token_type: TokenTypeEnum,
      limit: PositiveInt | None = None,
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

  def get_token(self, token: NonEmptyStr) -> TokenTable | None:
    """Get a token record from the database by token string"""

    if not token:
      raise TokenRequiredError()

    query = select(self.model).where(self.model.token == token)
    db_token = self.db.scalar(query)

    return db_token

  def get_token_by_values(self, tokens: list[NonEmptyStr]) -> list[TokenTable] | None:
    """Get a list of token records from the database by token strings"""

    if not tokens:
      raise TokenRequiredError()

    query = (select(self.model)
      .where(self.model.token.in_(tokens))
      .limit(len(tokens))
    )
    db_tokens = self.db.scalars(query).all()

    return db_tokens

  def get_user_token_by_type(self, user_id: PositiveInt, token_type: TokenTypeEnum) -> TokenTable | None:
    """Get user lastest active token by type"""
    query = self.get_active_user_tokens(user_id, token_type, limit=1)
    return query[0] if query else None

  def get_user_tokens_by_type(self, user_id: PositiveInt, token_type: TokenTypeEnum) -> list[TokenTable] | None:
    """Get user active tokens by type"""
    return self.get_active_user_tokens(user_id, token_type)

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
