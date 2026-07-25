from app.core import AppException


class UserNotFoundError(AppException):
  """An error when a user does not exist in database"""
  status_code = 404
  error_code = "USER_NOT_FOUND"

  def __init__(self, message: str = "Error: User is not found!"):
    super().__init__(message)

class UserAlreadyVerifiedError(AppException):
  """An error when a user is already verified"""
  status_code = 400
  error_code = "USER_ALREADY_VERIFIED"

  def __init__(self, message: str = "Error: User is already verified!"):
    super().__init__(message)
