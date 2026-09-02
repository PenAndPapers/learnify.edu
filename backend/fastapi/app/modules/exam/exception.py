from app.core import AppException


class ExamNotFoundException(AppException):
  status_code = 404
  error_code = "EXAM_NOT_FOUND"

  def __init__(self, message: str = "Error: Exam not found."):
    super().__init__(message)


class ExamNotActiveException(AppException):
  status_code = 409
  error_code = "EXAM_NOT_ACTIVE"

  def __init__(
    self, message: str = "Error: Exam is not active and cannot be assigned."
  ):
    super().__init__(message)


class ExamAttemptNotFoundException(AppException):
  status_code = 404
  error_code = "EXAM_ATTEMPT_NOT_FOUND"

  def __init__(self, message: str = "Error: Exam attempt not found."):
    super().__init__(message)


class ExamAttemptAlreadyStartedException(AppException):
  status_code = 409
  error_code = "EXAM_ATTEMPT_ALREADY_STARTED"

  def __init__(self, message: str = "Error: Exam attempt has already been started."):
    super().__init__(message)


class ExamAttemptAlreadySubmittedException(AppException):
  status_code = 409
  error_code = "EXAM_ATTEMPT_ALREADY_SUBMITTED"

  def __init__(self, message: str = "Error: Exam attempt has already been submitted."):
    super().__init__(message)


class ExamAttemptNotSubmittedException(AppException):
  status_code = 409
  error_code = "EXAM_ATTEMPT_NOT_SUBMITTED"

  def __init__(self, message: str = "Error: Exam attempt has not been submitted yet."):
    super().__init__(message)


class ExamAttemptExpiredException(AppException):
  status_code = 409
  error_code = "EXAM_ATTEMPT_EXPIRED"

  def __init__(self, message: str = "Error: Exam link has expired."):
    super().__init__(message)


class ExamNotAssignedToEnrolleeException(AppException):
  status_code = 409
  error_code = "EXAM_NOT_ASSIGNED_TO_ENROLLEE"

  def __init__(
    self, message: str = "Error: This exam is not assigned to the specified enrollee."
  ):
    super().__init__(message)


class InvalidExamAnswerException(AppException):
  status_code = 400
  error_code = "INVALID_EXAM_ANSWER"

  def __init__(self, message: str = "Error: Invalid exam answer submitted."):
    super().__init__(message)


class ExamQuestionNotFoundException(AppException):
  status_code = 404
  error_code = "EXAM_QUESTION_NOT_FOUND"

  def __init__(self, message: str = "Error: Exam question not found."):
    super().__init__(message)


class ExamAlreadyAssignedException(AppException):
  status_code = 409
  error_code = "EXAM_ALREADY_ASSIGNED"

  def __init__(
    self,
    message: str = "Error: An active exam attempt already exists for this enrollee.",
  ):
    super().__init__(message)
