from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from app.helpers.validators.string import is_valid_uuid

from .exception import (
  ExamAlreadyAssignedException,
  ExamAttemptAlreadyStartedException,
  ExamAttemptAlreadySubmittedException,
  ExamAttemptExpiredException,
  ExamAttemptNotFoundException,
  ExamNotActiveException,
  ExamNotFoundException,
  ExamQuestionNotFoundException,
  InvalidExamAnswerException,
)
from .repository import ExamRepository
from .table import ExamAttemptTable, ExamTable
from .validation import (
  CreateExam,
  ExamAttemptResponse,
  ExamAttemptStatusEnum,
  ExamListItemResponse,
  ExamQuestionResponse,
  ExamResponse,
  ExamStatusEnum,
  GradedExamAttemptResponse,
  QuestionTypeEnum,
  SubmitExamAttempt,
  UpdateExam,
)


class ExamService:
  def __init__(
    self,
    repository: ExamRepository,
    on_attempt_graded: Callable[[ExamAttemptTable], None] | None = None,
  ):
    self.repository = repository
    self.on_attempt_graded = on_attempt_graded

  # ---------- Exam template CRUD ----------

  def create_exam(self, payload: CreateExam) -> ExamTable:
    exam = self.repository.create(payload)
    return exam

  def get_exam(self, uuid: str) -> ExamTable:
    if not is_valid_uuid(uuid):
      raise ExamNotFoundException()
    exam = self.repository.get_by_uuid(uuid)
    if exam is None:
      raise ExamNotFoundException()
    return exam

  def list_active_exams(self) -> list[ExamTable]:
    return self.repository.list_active()

  def update_exam(self, uuid: str, payload: UpdateExam) -> ExamTable:
    exam = self.get_exam(uuid)
    return self.repository.update(exam, payload)

  def archive_exam(self, uuid: str) -> ExamTable:
    exam = self.get_exam(uuid)
    patch = UpdateExam(status=ExamStatusEnum.ARCHIVED)
    return self.repository.update(exam, patch)

  # ---------- Exam template → response helpers (avoid circular) ----------

  def to_response(self, exam: ExamTable) -> ExamResponse:
    q_count = len(exam.questions)
    _ = q_count
    return ExamResponse.model_validate(exam)

  def to_list_item(self, exam: ExamTable) -> ExamListItemResponse:
    item = ExamListItemResponse.model_validate(exam)
    item.question_count = self.repository.count_questions(exam.id)
    return item

  def question_response(
    self, question, show_correct: bool = False
  ) -> ExamQuestionResponse:
    data = {
      "id": question.id,
      "exam_id": question.exam_id,
      "question_text": question.question_text,
      "question_type": question.question_type,
      "points": question.points,
      "order_index": question.order_index,
      "options": [
        {
          "id": opt.id,
          "question_id": opt.question_id,
          "option_text": opt.option_text,
          "is_correct": opt.is_correct if show_correct else False,
        }
        for opt in question.options
      ],
    }
    return ExamQuestionResponse(**data)

  # ---------- Assignment & attempt lifecycle ----------

  def assign_to_enrollee(
    self,
    enrollee_id: int,
    exam_uuid: str,
    expires_in_hours: int = 72,
  ) -> ExamAttemptTable:
    """Create an exam attempt, returning the attempt row. Caller is responsible
    for writing the link UUID back onto the enrollee record.

    NOTE: This method intentionally does NOT import EnrolleeTable or touch
    enrollee columns — the enrollee module is the one that owns that side
    of the relationship (avoids circular imports).
    """

    exam = self.get_exam(exam_uuid)
    if exam.status != ExamStatusEnum.ACTIVE:
      raise ExamNotActiveException()

    existing = self.repository.get_active_attempt_for_enrollee(enrollee_id, exam.id)
    if existing is not None:
      raise ExamAlreadyAssignedException()

    attempt = self.repository.create_attempt(
      enrollee_id=enrollee_id,
      exam_id=exam.id,
      pass_score_snapshot=exam.pass_score,
    )
    _ = expires_in_hours
    return attempt

  def compute_expiry(self, created_at: datetime, hours: int) -> datetime:
    return created_at + timedelta(hours=hours)

  def get_attempt(self, attempt_uuid: str) -> ExamAttemptTable:
    if not is_valid_uuid(attempt_uuid):
      raise ExamAttemptNotFoundException()
    attempt = self.repository.get_attempt_by_uuid(attempt_uuid)
    if attempt is None:
      raise ExamAttemptNotFoundException()
    return attempt

  def get_attempt_for_link(
    self,
    attempt_uuid: str,
    expiry_check: Callable[[ExamAttemptTable], bool] | None = None,
  ) -> ExamAttemptTable:
    """Used by the public exam-link route to validate the attempt before
    allowing it to be started/submitted."""

    attempt = self.get_attempt(attempt_uuid)

    if attempt.status == ExamAttemptStatusEnum.ASSIGNED and expiry_check is not None:
      if not expiry_check(attempt):
        raise ExamAttemptExpiredException()

    return attempt

  def start_attempt(self, attempt_uuid: str) -> ExamAttemptTable:
    attempt = self.get_attempt(attempt_uuid)

    if attempt.status == ExamAttemptStatusEnum.IN_PROGRESS:
      raise ExamAttemptAlreadyStartedException()
    if attempt.status in {
      ExamAttemptStatusEnum.SUBMITTED,
      ExamAttemptStatusEnum.GRADED,
    }:
      raise ExamAttemptAlreadySubmittedException()
    if attempt.status != ExamAttemptStatusEnum.ASSIGNED:
      raise ExamAttemptAlreadyStartedException()

    return self.repository.start_attempt(attempt)

  def submit_attempt(
    self, attempt_uuid: str, payload: SubmitExamAttempt
  ) -> ExamAttemptTable:
    attempt = self.get_attempt(attempt_uuid)

    if attempt.status in {
      ExamAttemptStatusEnum.SUBMITTED,
      ExamAttemptStatusEnum.GRADED,
    }:
      raise ExamAttemptAlreadySubmittedException()

    if attempt.status not in {
      ExamAttemptStatusEnum.IN_PROGRESS,
      ExamAttemptStatusEnum.ASSIGNED,
    }:
      raise ExamAttemptAlreadyStartedException()

    self._validate_submission(attempt, payload)

    graded = self.repository.submit_attempt(attempt, payload)

    if self.on_attempt_graded is not None:
      self.on_attempt_graded(graded)

    return graded

  def _validate_submission(
    self, attempt: ExamAttemptTable, payload: SubmitExamAttempt
  ) -> None:
    """Sanity-check submissions before persisting them."""

    question_ids = {q.id for q in attempt.exam.questions}
    seen_qids: set[int] = set()

    for answer in payload.answers:
      if answer.question_id not in question_ids:
        raise ExamQuestionNotFoundException(
          f"Question id={answer.question_id} does not belong to this exam."
        )
      if answer.question_id in seen_qids:
        raise InvalidExamAnswerException(
          f"Duplicate answer for question id={answer.question_id}."
        )
      seen_qids.add(answer.question_id)

      question = next(q for q in attempt.exam.questions if q.id == answer.question_id)
      if answer.selected_option_id is not None:
        valid_option_ids = {opt.id for opt in question.options}
        if answer.selected_option_id not in valid_option_ids:
          raise InvalidExamAnswerException(
            f"Option id={answer.selected_option_id} is not valid for "
            f"question id={answer.question_id}."
          )
      if (
        question.question_type == QuestionTypeEnum.MCQ
        and answer.selected_option_id is None
        and not answer.text_answer
      ):
        continue

  # ---------- Graded result DTO builder ----------

  def to_graded_response(self, attempt: ExamAttemptTable) -> GradedExamAttemptResponse:
    base = ExamAttemptResponse.model_validate(attempt)
    total = sum(q.points for q in attempt.exam.questions)
    percentage = None
    passed = None
    if total > 0 and attempt.score is not None:
      percentage = round((attempt.score / total) * 100, 2)
      if attempt.pass_score_snapshot is not None:
        passed = percentage >= attempt.pass_score_snapshot

    return GradedExamAttemptResponse(
      **base.model_dump(),
      total_points_possible=float(total),
      percentage=percentage,
      passed=passed,
    )
