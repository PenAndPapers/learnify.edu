import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .table import EmployeeTable, EnrolleeTable, StudentTable, UserTable
from .validation import CreateEnrollee, UserInternalResponse


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


class EnrolleeResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = EnrolleeTable

  def create(self, data: CreateEnrollee) -> UserInternalResponse:
    """Store user info"""
    try:
      record = self.model(**data.model_dump())
      self.db.add(record)
      self.db.commit()
      self.db.refresh(record)
      return record
    except Exception as e:
      self.db.rollback()

      logging.exception(
        f"Database error occurred while creating enrollee for email: {data.email}"
      )

      raise RuntimeError("Failed to create enrollee") from e

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


class StudentResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = StudentTable


class EmpoyeeResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = EmployeeTable
