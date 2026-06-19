
from app.helpers.security.password import hash_password

from .repository import EmpoyeeResitory
from .validation import CreateEmployee, EmployeeFullResponse


class EmployeeService:
  def __init__(self, repository: EmpoyeeResitory):
    self.repository = repository

  def create(self, employee: CreateEmployee) -> EmployeeFullResponse:
    """Create an employee account."""

    hash_pwd = hash_password(employee.password)

    employee_data = employee.model_copy(update={"password": hash_pwd})
    new_employee = self.repository.create(employee_data)

    self.repository.db.flush()

    return new_employee
