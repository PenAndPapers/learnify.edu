from app.core import AppException


class EnrolleeNotFoundException(AppException):
  """Exception raised when an enrollee is not found in the database."""

  status_code = 404
  error_code = "ENROLLEE_NOT_FOUND"

  def __init__(self, message: str = "Error: Enrollee not found!"):
    super().__init__(message)


class EnrolleeIDNotValidException(AppException):
  """Exception raised when an enrollee ID is not valid."""

  status_code = 400
  error_code = "ENROLLEE_ID_NOT_VALID"

  def __init__(self, message: str = "Error: Enrollee ID is not valid!"):
    super().__init__(message)


class InvalidEnrolleeStatusTransitionException(AppException):
  """Raised when the requested enrollee application status transition is not allowed."""

  status_code = 409
  error_code = "INVALID_ENROLLEE_STATUS_TRANSITION"

  def __init__(self, message: str = "Error: Invalid enrollee status transition."):
    super().__init__(message)


class EnrolleeAlreadyPromotedException(AppException):
  """Raised when promotion is attempted on an enrollee that has already been enrolled."""

  status_code = 409
  error_code = "ENROLLEE_ALREADY_PROMOTED"

  def __init__(
    self, message: str = "Error: Enrollee has already been promoted to student."
  ):
    super().__init__(message)


class EnrolleeNotApprovedException(AppException):
  """Raised when promotion is attempted on an enrollee whose application has not been approved."""

  status_code = 409
  error_code = "ENROLLEE_NOT_APPROVED"

  def __init__(
    self, message: str = "Error: Enrollee application must be approved first."
  ):
    super().__init__(message)


class EnrolleeExamNotPassedException(AppException):
  """Raised when promotion is attempted on an enrollee who has not passed the entrance exam."""

  status_code = 409
  error_code = "ENROLLEE_EXAM_NOT_PASSED"

  def __init__(
    self, message: str = "Error: Enrollee must pass the entrance examination first."
  ):
    super().__init__(message)
