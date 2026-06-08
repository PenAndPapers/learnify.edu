import logging

from sqlalchemy.orm import Session

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

      logging.exception("Database error occurred while storing token")
      raise RuntimeError("Failed to store token") from e
