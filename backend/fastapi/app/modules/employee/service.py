from .repository import EmpoyeeResitory
from .validation import CreateEmployee, EmployeeFullResponse


class EmployeeService:
  def __init__(self, repository: EmpoyeeResitory):
    self.repository = repository

  def create(self, employee: CreateEmployee) -> EmployeeFullResponse:
    """Create an employee account."""

    new_employee = self.repository.create(employee)

    self.repository.db.flush()

    return new_employee
