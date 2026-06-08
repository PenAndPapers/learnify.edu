from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.get("/employee/all", response_model=None)
async def get_employees() -> None:
  pass


@router.post("/employee/create", response_model=None)
async def create_employee() -> None:
  """
  Create an employee account

  Args:
      user_data: An object containing the employee initial data

  Returns:
      user_data: An object containing the employee data
  """
  pass


@router.get("/employee/{uuid}", response_model=None)
async def get_employee() -> None:
  """
  Get an employee account

  Args:
      uuid: A user system generated uuid

  Returns:
      user_data: An object containing the employee data
  """
  pass


@router.patch("/employee/{uuid}", response_model=None)
async def update_employee() -> None:
  """
  Update an employee account

  Args:
      uuid: A user system generated uuid

  Returns:
      user_data: An object containing the employee updated data
  """
  pass


@router.delete("/employee/{uuid}", response_model=None)
async def delete_employee() -> None:
  """
  Delete an employee account

  Args:
      uuid: A user system generated uuid

  Returns:
      Boolean value
  """
  pass
