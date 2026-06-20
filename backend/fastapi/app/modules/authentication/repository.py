from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

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

    return records

  def get_by_token(self, token: str) -> UserToken | None:
    """Get a token record from the database by token string"""

    if not token:
      raise HTTPException(status_code=400, detail="Error: Token is required")

    db_token = self.db.query(self.model).filter(self.model.token == token).first()

    if not db_token:
      raise HTTPException(status_code=404, detail="Error: Token not found")

    return UserToken.model_validate(db_token)

  def get_by_tokens(self, tokens: list[str] | None = None) -> list[UserToken] | None:
    """Get multiple token records from the database by a list of token strings"""
    if tokens is None:
      raise HTTPException(
        status_code=400,
        detail="Error: Invalid set of tokens. Provide at least one token.",
      )

    try:
      query = (
        select(self.model)
        .where(self.model.token.in_(tokens))
        .order_by(self.model.id.asc())
      )
      db_tokens = self.db.scalars(query).all()

      if not db_tokens or len(db_tokens) != len(tokens):
        raise HTTPException(
          status_code=404, detail="Error: One or more tokens not found"
        )

      return [UserToken.model_validate(token) for token in db_tokens]
    except Exception as e:
      raise HTTPException(status_code=500, detail="Error: Token is not valid") from e

  def revoke_tokens(self, tokens: list[str] | None = None) -> None:
    if tokens is None or len(tokens) != 2:
      raise HTTPException(status_code=400, detail="Error: Missing tokens")

    self.db.execute(
      update(self.model)
      .where(self.model.token.in_(tokens))
      .values(is_revoked=True, deleted_at=datetime.now(UTC))
    )
