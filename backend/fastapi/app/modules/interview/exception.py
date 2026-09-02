from app.core import AppException


class InterviewTemplateNotFoundException(AppException):
  status_code = 404
  error_code = "INTERVIEW_TEMPLATE_NOT_FOUND"

  def __init__(self, message: str = "Error: Interview template not found."):
    super().__init__(message)


class InterviewTemplateNotActiveException(AppException):
  status_code = 409
  error_code = "INTERVIEW_TEMPLATE_NOT_ACTIVE"

  def __init__(
    self,
    message: str = "Error: Interview template is not active and cannot be scheduled.",
  ):
    super().__init__(message)


class InterviewSessionNotFoundException(AppException):
  status_code = 404
  error_code = "INTERVIEW_SESSION_NOT_FOUND"

  def __init__(self, message: str = "Error: Interview session not found."):
    super().__init__(message)


class InterviewSessionAlreadyScheduledException(AppException):
  status_code = 409
  error_code = "INTERVIEW_SESSION_ALREADY_SCHEDULED"

  def __init__(
    self,
    message: str = "Error: An active interview session already exists for this enrollee.",
  ):
    super().__init__(message)


class InterviewTemplateAlreadyScheduledException(
  InterviewSessionAlreadyScheduledException
):
  """Alias kept for symmetry with ExamAlreadyAssignedException naming pattern."""

  pass


class InterviewSessionAlreadyStartedException(AppException):
  status_code = 409
  error_code = "INTERVIEW_SESSION_ALREADY_STARTED"

  def __init__(
    self, message: str = "Error: Interview session has already been started."
  ):
    super().__init__(message)


class InterviewSessionAlreadyConductedException(AppException):
  status_code = 409
  error_code = "INTERVIEW_SESSION_ALREADY_CONDUCTED"

  def __init__(
    self, message: str = "Error: Interview session has already been conducted."
  ):
    super().__init__(message)


class InterviewSessionNotConductedException(AppException):
  status_code = 409
  error_code = "INTERVIEW_SESSION_NOT_CONDUCTED"

  def __init__(
    self, message: str = "Error: Interview session has not been conducted yet."
  ):
    super().__init__(message)


class InterviewSessionExpiredException(AppException):
  status_code = 409
  error_code = "INTERVIEW_SESSION_EXPIRED"

  def __init__(self, message: str = "Error: Interview session link has expired."):
    super().__init__(message)


class InterviewSessionCancelledException(AppException):
  status_code = 409
  error_code = "INTERVIEW_SESSION_CANCELLED"

  def __init__(self, message: str = "Error: Interview session has been cancelled."):
    super().__init__(message)


class InterviewQuestionNotFoundException(AppException):
  status_code = 404
  error_code = "INTERVIEW_QUESTION_NOT_FOUND"

  def __init__(self, message: str = "Error: Interview question not found."):
    super().__init__(message)


class InvalidInterviewAnswerException(AppException):
  status_code = 400
  error_code = "INVALID_INTERVIEW_ANSWER"

  def __init__(self, message: str = "Error: Invalid interview answer submitted."):
    super().__init__(message)
