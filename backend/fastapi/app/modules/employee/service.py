from .repository import EmpoyeeResitory
from .validation import CreateEmployee, EmployeeFullResponse


class EmployeeService:
  def __init__(self, repository: EmpoyeeResitory):
    self.repository = repository

  def create(self, employee: CreateEmployee) -> EmployeeFullResponse:
    validated_employee = CreateEmployee.model_validate(employee)

    new_employee = self.repository.create(validated_employee)

    self.repository.db.flush()

    return new_employee
