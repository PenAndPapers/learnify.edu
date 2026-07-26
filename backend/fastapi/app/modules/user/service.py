
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

    user = self.repository.get_by_id(user_id)

    if not user:
      raise UserNotFoundError()

    if user.is_verified:
      raise UserAlreadyVerifiedError()

    return self.repository.verify_user(user)
