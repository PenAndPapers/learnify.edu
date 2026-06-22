from app.core import AppException


class TokenRequiredError(AppException):
  """An error when token is not passed as parameter"""
  status_code = 400
  error_code = "TOKEN_REQUIRED"

  def __init__(self, message: str = "Error: Token is required!"):
    super().__init__(message)


class TokenNotFoundError(AppException):
  """An error when a token does not exist in database"""
  status_code = 404
  error_code = "TOKEN_NOT_FOUND"

  def __init__(self, message: str = "Error: Token is not found!"):
    super().__init__(message)


class TokenExpiredError(AppException):
  """An error when a token exist in database but its expired"""
  status_code=400
  error_code="TOKEN_EXPIRED"

  def __init__(self, message: str = "Error: Token is expired!"):
    super().__init__(message)


class TokenTypeMismatchError(AppException):
  status_code=400
  error_code="TOKEN_MISMATCH"

  def __init__(self, message = "Error: Token type mismatch!"):
    super().__init__(message)


class TokenSessionMismatchError(AppException):
  status_code=400
  error_code="TOKEN_SESSION_MISMATCH"

  def __init__(self, message = "Error: Token session mismatch!"):
    super().__init__(message)


class TokenPairMismatchError(AppException):
  status_code=400
  error_code="TOKEN_SESSION_MISMATCH"

  def __init__(self, message = "Error: Token pair mismatch!"):
    super().__init__(message)


class TokenRevokedError(AppException):
  status_code=400
  error_code="TOKEN_REVOKED"

  def __init__(self, message: str = "Error: Token is revoked!"):
    super().__init__(message)


class TokenInvalidFormatError(AppException):
  status_code=400
  error_code="TOKEN_INVALID_FORMAT"

  def __init__(self, message: str = "Error: Token format is not valid!"):
    super().__init__(message)


class TokenInvalidError(AppException):
  status_code=500
  error_code="TOKEN_INVALID"

  def __init__(self, message: str = "Error: Token is not valid"):
    super().__init__(message)
