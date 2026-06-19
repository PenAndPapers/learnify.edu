from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import EmpoyeeResitory
from .service import EmployeeService


# Employee service dependency
def get_employee_repository(db: DatabaseDep) -> EmpoyeeResitory:
  return EmpoyeeResitory(db)


EmployeeRepositoryDep = Annotated[EmpoyeeResitory, Depends(get_employee_repository)]


def get_employee_service(
  repository: EmployeeService = Depends(get_employee_repository),
) -> EmployeeService:
  return EmployeeService(repository)


EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
