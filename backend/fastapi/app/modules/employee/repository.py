import logging
import uuid

from sqlalchemy.orm import Session

from .table import EmployeeTable
from .validation import CreateEmployee, EmployeeFullResponse


class EmpoyeeResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = EmployeeTable

  def _employee_id_generator(self) -> str:
    return str(uuid.uuid4())

  def create(self, employee: CreateEmployee) -> EmployeeFullResponse:
    """Store employee details"""
    try:
      record = self.model(
        employee_id=self._employee_id_generator(), **employee.model_dump()
      )
      self.db.add(record)
      self.db.commit()
      self.db.refresh(record)

      return EmployeeFullResponse.model_validate(record)

    except Exception as e:
      self.db.rollback()
      error_message = f"Error: Database error occurred while creating student for email - {employee.email}"
      logging.exception(error_message)
      raise RuntimeError(error_message) from e
