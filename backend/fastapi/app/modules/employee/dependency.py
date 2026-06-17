from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import EmpoyeeResitory
from .service import EmployeeService


# User service dependency
def get_employee_repository(db: Session = Depends(get_db)) -> EmpoyeeResitory:
  return EmpoyeeResitory(db)


def get_employee_service(
  repository: EmployeeService = Depends(get_employee_repository),
) -> EmployeeService:
  return EmployeeService(repository)
