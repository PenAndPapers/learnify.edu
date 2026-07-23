from app.core import AppException

class StudentNotFoundException(AppException):
  """Exception raised when a student is not found in the database."""
  status_code = 404
  error_code = "STUDENT_NOT_FOUND"

  def __init__(self, message: str = "Error: Student not found!"):
    super().__init__(message)

class StudentIDNotValidException(AppException):
  """Exception raised when a student ID is not valid."""
  status_code = 400
  error_code = "STUDENT_ID_NOT_VALID"

  def __init__(self, message: str = "Error: Student ID is not valid!"):
    super().__init__(message)