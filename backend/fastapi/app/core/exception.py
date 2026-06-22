class AppException(Exception):
  status_code = 500
  error_code = "INTERNAL_SERVER_ERROR"

  def __init__(self, message: str | None):
    self.message = message or "Error: An unexpected error occured"
    super().__init__(self.message)

