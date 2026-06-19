from fastapi import APIRouter

from .dependency import EmployeeServiceDep
from .validation import CreateEmployee, EmployeeResponse

router = APIRouter(prefix="/api/v1/employee", tags=["Employee"])


@router.get("/", response_model=None)
def get_employees() -> None:
  """Get all employee list"""
  pass


@router.post("/login", response_model=None)
def login_employee() -> None:
  """Login an employee account"""
  pass


@router.post("/", response_model=EmployeeResponse)
def create_employee(
  employee: CreateEmployee,
  employee_service: EmployeeServiceDep,
) -> EmployeeResponse:
  """Create an employee account"""
  new_employee = employee_service.create(employee)

  return EmployeeResponse.model_validate(new_employee)


@router.get("/{uuid}", response_model=None)
def get_employee() -> None:
  """Get an employee account"""
  pass


@router.patch("/{uuid}", response_model=None)
def update_employee() -> None:
  """Update an employee account"""
  pass


@router.delete("/{uuid}", response_model=None)
def delete_employee() -> None:
  """Delete an employee account"""
  pass
