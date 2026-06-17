from sqlalchemy.orm import Session

from .table import EmployeeTable


class EmpoyeeResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = EmployeeTable
