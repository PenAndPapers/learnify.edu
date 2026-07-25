
from app.database import DatabaseDep

from .table import UserTable


class UserRepository:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = UserTable

  def filter_user(self, filter: dict) -> UserTable | None:
    """Filter a user by the given filter criteria and return the corresponding UserTable if found."""

    user = self.db.query(self.model).filter_by(**filter).first()

    return user

  def get_by_id(self, user_id: int) -> UserTable | None:
    """Get a user by their ID and return the corresponding UserTable if found."""

    user = self.db.query(self.model).filter_by(id=user_id).first()

    return user

  def verify_user(self, user: UserTable) -> UserTable | None:
    """Verify the user by updating the is_verified field"""

    user.is_verified = True
    self.db.commit()
    self.db.refresh(user)

    return user
