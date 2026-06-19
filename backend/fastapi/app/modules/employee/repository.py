import uuid

from app.database import DatabaseDep

from .table import EmployeeTable
from .validation import CreateEmployee, EmployeeFullResponse


class EmpoyeeResitory:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = EmployeeTable

  def _employee_id_generator(self) -> str:
    return str(uuid.uuid4())

  def create(self, employee: CreateEmployee) -> EmployeeFullResponse:
    """Store employee details in the database"""

    record = self.model(
      employee_id=self._employee_id_generator(), **employee.model_dump()
    )
    self.db.add(record)

    return record
