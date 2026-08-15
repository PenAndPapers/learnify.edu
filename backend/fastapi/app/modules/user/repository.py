
from sqlalchemy import select

from app.database import DatabaseDep
from app.helpers.types import NonEmptyStr, PositiveInt

from .table import UserTable


class UserRepository:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = UserTable

  def filter_user(self, filter: dict) -> UserTable | None:
    """Filter a user by the given filter criteria and return the corresponding UserTable if found."""

    user = self.db.query(self.model).filter_by(**filter).first()

    return user

  def get_by_id(self, id: PositiveInt) -> UserTable | None:
    """Get a user by their ID and return the corresponding UserTable if found."""

    query = select(self.model).where(self.model.id == id)
    db_user = self.db.scalar(query)

    return db_user

  def update(self, user: UserTable) -> UserTable | None:
    """Update"""

    if not user:
      return None

    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)

    return user

  def verify_user(self, user: UserTable) -> UserTable | None:
    """Verify the user by updating the is_verified field"""

    user.is_verified = True
    return self.update(user)

  def update_password(self, user: UserTable, password: NonEmptyStr) -> UserTable | None:
    """Update user password"""

    user.password = password
    return self.update(user)
