import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.orm import Session
from typing import List

from .table import TokenTable
from .validation import UserToken


class TokenRepository:
  def __init__(self, db: Session):
    self.db = db
    self.model = TokenTable

  def store_auth_tokens(self, tokens: list[UserToken]) -> list[UserToken]:
    try:
      records = [self.model(**token.model_dump()) for token in tokens]

      self.db.add_all(records)
      self.db.commit()

      for record in records:
        self.db.refresh(record)

      return records
    except Exception as e:
      self.db.rollback()

      logging.exception("Error: Database error occurred while storing token")
      raise RuntimeError("Failed to store token") from e
  

  def get_by_token(self, token: str) -> UserToken | None:
    if not token:
      raise ValueError(f"Error: Missing token")

    db_token = self.db.query(self.model).filter(self.model.token == token).first()

    if not token:
      raise HTTPException(status_code=404, detail="Error: Token not found")

    return UserToken.model_validate(db_token)
  

  def get_by_tokens(self, tokens: List[str] | None = None) -> List[UserToken] | None:
    if tokens is None:
      raise ValueError(f"Error: Invalid set of tokens. Provide at least one token.")
    
    try:
      query = select(self.model).where(self.model.token.in_(tokens)).order_by(self.model.id.asc())
      db_tokens = self.db.scalars(query).all()

      return [UserToken.model_validate(token) for token in db_tokens]
    except Exception as e:
      raise RuntimeError("Error: Failed to fetch token") from e


  def revoke_tokens(self, tokens: List[str] = []) -> None:
    if len(tokens) < 1:
      raise ValueError(f"Error: Missing tokens")
    
    try:
      self.db.execute(
        update(self.model)
        .where(self.model.token.in_(tokens))
        .values(
          is_revoked=True,
          deleted_at=datetime.now(timezone.utc)
        )
      )

      self.db.commit()
    except Exception as e:
      self.db.rollback()
      raise RuntimeError("Error: Failed to revoke token") from e
