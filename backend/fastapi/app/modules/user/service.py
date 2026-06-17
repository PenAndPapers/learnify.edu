from .repository import UserRepository
from .validation import UserInternalResponse


class UserService:
  def __init__(self, repository: UserRepository):
    self.repository = repository

  def get_user(self, filter: dict) -> UserInternalResponse | None:
    return self.repository.get_user(filter, False)
