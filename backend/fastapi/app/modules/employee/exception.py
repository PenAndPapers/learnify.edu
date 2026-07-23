from app.core import AppException


class EmployeeNotFoundException(AppException):
  """Exception raised when an employee is not found in the database."""
  status_code = 404
  error_code = "EMPLOYEE_NOT_FOUND"

  def __init__(self, message: str = "Error: Employee not found!"):
    super().__init__(message)


class EmployeeIDNotValidException(AppException):
  """Exception raised when an employee ID is not valid."""
  status_code = 400
  error_code = "EMPLOYEE_ID_NOT_VALID"

  def __init__(self, message: str = "Error: Employee ID is not valid!"):
    super().__init__(message)
