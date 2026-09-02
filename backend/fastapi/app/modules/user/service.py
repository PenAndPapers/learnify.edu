from app.helpers.security.password import hash_password
from app.helpers.types import NonEmptyStr, PositiveInt
from app.modules.user.exception import UserAlreadyVerifiedError, UserNotFoundError
from app.modules.user.table import UserTable

from .repository import UserRepository


class UserService:
  def __init__(self, repository: UserRepository):
    self.repository = repository

  def filter_user(self, filter: dict) -> UserTable | None:
    return self.repository.filter_user(filter)

  def get_by_id(self, user_id: int) -> UserTable | None:
    return self.repository.get_by_id(user_id)

  def verify_user(self, user_id: int) -> UserTable | None:
    """Verify the user by updating the is_verified field in the database."""

    user = self.get_by_id(user_id)

    if not user:
      raise UserNotFoundError()

    if user.is_verified:
      raise UserAlreadyVerifiedError()

    return self.repository.verify_user(user)

  def update_password(self, id: PositiveInt, password: NonEmptyStr) -> UserTable | None:
    """Update and employee account by UUID."""

    db_user = self.get_by_id(id)

    if not db_user:
      raise UserNotFoundError()

    return self.repository.update_password(db_user, hash_password(str(password)))
