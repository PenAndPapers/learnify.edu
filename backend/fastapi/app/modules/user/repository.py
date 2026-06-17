from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .table import UserTable
from .validation import UserInternalResponse


class UserRepository:
  def __init__(self, db: Session):
    self.db = db
    self.model = UserTable

  def get_user(
    self, filter: dict, raise_error: bool = True
  ) -> UserInternalResponse | None:
    user = self.db.query(self.model).filter_by(**filter).first()

    if user:
      return UserInternalResponse.model_validate(user)

    if raise_error:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
      )

    return None
