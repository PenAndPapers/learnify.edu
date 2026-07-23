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

  def read(self, uuid: str) -> EmployeeFullResponse:
    """Get an employee by UUID"""

    record = self.db.query(self.model).filter(self.model.employee_id == uuid).first()

    return record

  def delete(self, uuid: str) -> bool:
    """Delete an employee by UUID"""

    record = self.db.query(self.model).filter(self.model.employee_id == uuid).first()

    if not record:
      return False

    self.db.delete(record)
    return True
