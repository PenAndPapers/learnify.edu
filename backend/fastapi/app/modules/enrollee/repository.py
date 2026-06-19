from fastapi import HTTPException, status

from app.database import DatabaseDep
from app.modules.user.validation import UserInternalResponse

from .table import EnrolleeTable
from .validation import CreateEnrollee


class EnrolleeResitory:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = EnrolleeTable

  def create(self, data: CreateEnrollee) -> UserInternalResponse:
    """Store user info"""
    record = self.model(**data.model_dump())
    self.db.add(record)

    return record

  def get_enrollee(
    self, filter: dict, raise_error: bool = True
  ) -> UserInternalResponse | None:
    enrollee = self.db.query(self.model).filter_by(**filter).first()

    if enrollee:
      return UserInternalResponse.model_validate(enrollee)

    if raise_error:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Enrollee not found"
      )

    return None
