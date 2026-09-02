from fastapi import APIRouter, Response, status

from .dependency import EmployeeServiceDep
from .validation import CreateEmployee, EmployeeResponse, UpdateEmployee

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


@router.get("/{uuid}", response_model=EmployeeResponse)
def get_employee(uuid: str, employee_service: EmployeeServiceDep) -> EmployeeResponse:
  """Get an employee account"""

  employee = employee_service.read(uuid)

  return EmployeeResponse.model_validate(employee)


@router.patch("/{uuid}", response_model=EmployeeResponse)
def update_employee(
  uuid: str, employee: UpdateEmployee, employee_service: EmployeeServiceDep
) -> EmployeeResponse:
  """Update an employee account"""

  updated_employee = employee_service.update(uuid, employee)

  return EmployeeResponse.model_validate(updated_employee)


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(uuid: str, employee_service: EmployeeServiceDep) -> Response:
  """Delete an employee account"""

  employee_service.delete(uuid)

  return Response(status_code=status.HTTP_204_NO_CONTENT)
