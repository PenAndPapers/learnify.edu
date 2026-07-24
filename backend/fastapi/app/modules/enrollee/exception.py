from app.core import AppException


class EnrolleeNotFoundException(AppException):
  """Exception raised when an enrollee is not found in the database."""
  status_code = 404
  error_code = "ENROLLEE_NOT_FOUND"

  def __init__(self, message: str = "Error: Enrollee not found!"):
    super().__init__(message)
