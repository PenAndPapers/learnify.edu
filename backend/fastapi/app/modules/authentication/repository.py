from datetime import UTC, datetime

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from .exceptions import TokenNotFoundError, TokenRequiredError
from .table import TokenTable
from .validation import TokenTypeEnum, UserPairToken, UserToken


class TokenRepository:
  def __init__(self, db: Session):
    self.db = db
    self.model = TokenTable

  def create(self, tokens: list[UserToken]) -> list[UserToken]:
    """Store authentication tokens in the database"""

    records = [self.model(**token.model_dump()) for token in tokens]

    self.db.add_all(records)

    return [UserToken.model_validate(record) for record in records]

  def get_by_token(self, token: str) -> UserToken:
    """Get a token record from the database by token string"""

    if not token:
      raise TokenRequiredError()

    db_token = self.db.query(self.model).filter(self.model.token == token).first()

    if not db_token:
      raise TokenNotFoundError()

    return UserToken.model_validate(db_token)

  def get_by_tokens(self, access_token: str, refresh_token: str) -> UserPairToken:
    """Get multiple token records from the database by a list of token strings"""

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

  def revoke_tokens(self, tokens: list[str] | None = None) -> None:
    """Update token to a revoke state"""

    if tokens is None or len(tokens) != 2:
      raise TokenRequiredError()

    self.db.execute(
      update(self.model)
      .where(self.model.token.in_(tokens))
      .values(is_revoked=True, deleted_at=datetime.now(UTC))
    )
