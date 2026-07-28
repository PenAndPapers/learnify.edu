from datetime import UTC, datetime

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.core.validation import NonEmptyStr, PositiveInt

from .exception import TokenNotFoundError, TokenRequiredError
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

  def get_by_token(self, token: NonEmptyStr) -> TokenTable | None:
    """Get a token record from the database by token string"""

    if not token:
      raise TokenRequiredError()

    query = select(self.model).where(self.model.token == token)
    db_token = self.db.scalar(query)

    return db_token

  def get_active_user_token_by_type(self, user_id: PositiveInt, token_type: TokenTypeEnum) -> TokenTable | None:
    """Get lastest user active token by type"""
    query = (
      select(self.model)
        .where(
          self.model.user_id == user_id,
          self.model.token_type == token_type,
          self.model.is_revoked == False
        )
        .order_by(self.model.created_at.desc())
    )

    result = self.db.scalars(query).first()

    return result


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

  def revoke_tokens(self, tokens: list[NonEmptyStr] | None = None) -> None:
    """Update token to a revoke state"""

    if tokens is None or len(tokens) == 0:
      raise TokenRequiredError()

    self.db.execute(
      update(self.model)
      .where(self.model.token.in_(tokens))
      .values(is_revoked=True, deleted_at=datetime.now(UTC))
    )
