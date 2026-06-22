from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .exceptions import TokenInvalidError, TokenNotFoundError, TokenRequiredError
from .table import TokenTable
from .validation import UserToken


class TokenRepository:
  def __init__(self, db: Session):
    self.db = db
    self.model = TokenTable

  def create(self, tokens: list[UserToken]) -> list[UserToken]:
    """Store authentication tokens in the database"""

    records = [self.model(**token.model_dump()) for token in tokens]

    self.db.add_all(records)

    return [UserToken.model_validate(record) for record in records]

  def get_by_token(self, token: str) -> UserToken | None:
    """Get a token record from the database by token string"""

    if not token:
      raise TokenRequiredError()

    db_token = self.db.query(self.model).filter(self.model.token == token).first()

    if not db_token:
      raise TokenNotFoundError()

    return UserToken.model_validate(db_token)

  def get_by_tokens(self, tokens: list[str] | None = None) -> list[UserToken] | None:
    """Get multiple token records from the database by a list of token strings"""
    if tokens is None:
      raise TokenRequiredError()

    try:
      query = (
        select(self.model)
        .where(self.model.token.in_(tokens))
        .order_by(self.model.id.asc())
      )
      db_tokens = self.db.scalars(query).all()

      if not db_tokens or len(db_tokens) != len(tokens):
        raise TokenNotFoundError()

      return [UserToken.model_validate(token) for token in db_tokens]
    except Exception as e:
      # TODO evaluate:
      # - Is this a valid way of checking?
      # - Is the error message means anything if model_validate fails?
      raise TokenInvalidError() from e

  def revoke_tokens(self, tokens: list[str] | None = None) -> None:
    if tokens is None or len(tokens) != 2:
      raise TokenRequiredError()

    self.db.execute(
      update(self.model)
      .where(self.model.token.in_(tokens))
      .values(is_revoked=True, deleted_at=datetime.now(UTC))
    )
