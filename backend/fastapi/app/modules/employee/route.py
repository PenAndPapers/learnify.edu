from fastapi import APIRouter, Depends

from .dependency import get_employee_service
from .service import EmployeeService
from .validation import CreateEmployee, EmployeeResponse

router = APIRouter(prefix="/api/v1", tags=["Employee"])


@router.get("/employee/all", response_model=None)
async def get_employees() -> None:
  """Get all employee list"""
  pass


@router.post("/employee/login", response_model=None)
async def login_employee() -> None:
  """Login an employee account"""
  pass


@router.post("/employee/create", response_model=EmployeeResponse)
async def create_employee(
  employee: CreateEmployee,
  employee_service: EmployeeService = Depends(get_employee_service)
) -> EmployeeResponse:
  """Create an employee account"""
  new_employee = employee_service.create(employee)

  return EmployeeResponse.model_validate(new_employee)



@router.get("/employee/{uuid}", response_model=None)
async def get_employee() -> None:
  """Get an employee account"""
  pass


@router.patch("/employee/{uuid}", response_model=None)
async def update_employee() -> None:
  """Update an employee account"""
  pass


@router.delete("/employee/{uuid}", response_model=None)
async def delete_employee() -> None:
  """Delete an employee account"""
  pass
