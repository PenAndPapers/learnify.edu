class AppException(Exception):
  status_code = 500
  error_code = "INTERNAL_SERVER_ERROR"

  def __init__(self, message: str | None):
    self.message = message or "Error: An unexpected error occured"
    super().__init__(self.message)

class RateLimitException(AppException):
  status_code=429
  error_code="RATE_LIMIT_EXCEEDED"

  def __init__(self, message: str = "Please wait before making another request."):
    super().__init__(message)
