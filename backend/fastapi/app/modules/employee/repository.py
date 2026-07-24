import uuid

from app.database import DatabaseDep

from .table import EmployeeTable
from .validation import CreateEmployee, UpdateEmployee


class EmpoyeeResitory:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = EmployeeTable

  def _employee_id_generator(self) -> str:
    return str(uuid.uuid4())

  def create(self, employee: CreateEmployee) -> EmployeeTable:
    """Store employee details in the database"""

    record = self.model(
      employee_id=self._employee_id_generator(), **employee.model_dump()
    )
    self.db.add(record)

    return record

  def read(self, uuid: str) -> EmployeeTable | None:
    """Get an employee by UUID"""

    record = self.db.query(self.model).filter(self.model.uuid == uuid).first()

    return record

  def update(self, uuid: str, employee: UpdateEmployee) -> EmployeeTable | None:
    """Update an employee by UUID"""

    record = self.read(uuid)

    if not record:
      return None

    updated_data = employee.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
      setattr(record, key, value)

    self.db.commit()
    self.db.refresh(record)

    return record

  def delete(self, uuid: str) -> bool:
    """Delete an employee by UUID"""

    record = self.read(uuid)

    if not record:
      return False

    self.db.delete(record)
    return True
