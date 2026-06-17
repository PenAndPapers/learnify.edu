import logging
import uuid

from sqlalchemy.orm import Session

from .table import StudentTable
from .validation import CreateStudent, StudentFullResponse


class StudentResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = StudentTable

  def _student_number_generator(self) -> int:
    return uuid.uuid4().int

  def create(self, student: CreateStudent) -> StudentFullResponse:
    """Store student info"""
    try:
      record = self.model(
        student_number=self._student_number_generator(), **student.model_dump()
      )
      self.db.add(record)
      self.db.commit()
      self.db.refresh(record)
      return record

    except Exception as e:
      self.db.rollback()
      error_message = f"Error: Database error occurred while creating student for email - {student.email}"
      logging.exception(error_message)
      raise RuntimeError(error_message) from e
