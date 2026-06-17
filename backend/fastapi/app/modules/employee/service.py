from .validation import CreateEmployee, EmployeeFullResponse
from .repository import EmpoyeeResitory


class EmployeeService:
  def __init__(self, repository: EmpoyeeResitory):
    self.repository = repository


  def create(self, employee: CreateEmployee) -> EmployeeFullResponse:
    validated_employee = CreateEmployee.model_validate(employee)

    new_employee = self.repository.create(validated_employee)

    return new_employee
