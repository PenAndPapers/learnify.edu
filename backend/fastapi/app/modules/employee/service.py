
from app.helpers.security.password import hash_password
from app.helpers.validators.string import is_valid_uuid

from .exception import EmployeeIDNotValidException, EmployeeNotFoundException
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

  def read(self, uuid: str) -> EmployeeFullResponse:
    """Get an employee account by UUID."""

    if not is_valid_uuid(uuid):
      raise EmployeeIDNotValidException()

    employee = self.repository.read(uuid)

    if not employee:
      raise EmployeeNotFoundException()

    return employee


  def delete(self, uuid: str) -> None:
    """Delete an employee account by UUID."""

    if not is_valid_uuid(uuid):
      raise EmployeeIDNotValidException()

    is_employee_deleted = self.repository.delete(uuid)

    if not is_employee_deleted:
      raise EmployeeNotFoundException()
