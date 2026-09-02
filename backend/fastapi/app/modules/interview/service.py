from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from app.helpers.validators.string import is_valid_uuid

from .exception import (
  InterviewQuestionNotFoundException,
  InterviewSessionAlreadyConductedException,
  InterviewSessionAlreadyStartedException,
  InterviewSessionCancelledException,
  InterviewSessionExpiredException,
  InterviewSessionNotConductedException,
  InterviewSessionNotFoundException,
  InterviewTemplateAlreadyScheduledException,
  InterviewTemplateNotActiveException,
  InterviewTemplateNotFoundException,
  InvalidInterviewAnswerException,
)
from .repository import InterviewRepository
from .table import InterviewSessionTable, InterviewTemplateTable
from .validation import (
  CreateInterview,
  GradeInterviewSession,
  InterviewListItemResponse,
  InterviewQuestionResponse,
  InterviewQuestionTypeEnum,
  InterviewResponse,
  InterviewSessionResponse,
  InterviewSessionStatusEnum,
  InterviewStatusEnum,
  SubmitInterviewSession,
  UpdateInterview,
)


class InterviewService:
  def __init__(
    self,
    repository: InterviewRepository,
    on_session_graded: Callable[[InterviewSessionTable], None] | None = None,
  ):
    self.repository = repository
    self.on_session_graded = on_session_graded

  # ---------- Interview template CRUD ----------

  def create_interview(self, payload: CreateInterview) -> InterviewTemplateTable:
    interview = self.repository.create(payload)
    return interview

  def get_interview(self, uuid: str) -> InterviewTemplateTable:
    if not is_valid_uuid(uuid):
      raise InterviewTemplateNotFoundException()
    interview = self.repository.get_by_uuid(uuid)
    if interview is None:
      raise InterviewTemplateNotFoundException()
    return interview

  def list_active_interviews(self) -> list[InterviewTemplateTable]:
    return self.repository.list_active()

  def update_interview(
    self, uuid: str, payload: UpdateInterview
  ) -> InterviewTemplateTable:
    interview = self.get_interview(uuid)
    return self.repository.update(interview, payload)

  def archive_interview(self, uuid: str) -> InterviewTemplateTable:
    interview = self.get_interview(uuid)
    patch = UpdateInterview(status=InterviewStatusEnum.ARCHIVED)
    return self.repository.update(interview, patch)

  # ---------- Response builders ----------

  def to_response(self, interview: InterviewTemplateTable) -> InterviewResponse:
    _ = len(interview.questions)
    return InterviewResponse.model_validate(interview)

  def to_list_item(
    self, interview: InterviewTemplateTable
  ) -> InterviewListItemResponse:
    item = InterviewListItemResponse.model_validate(interview)
    item.question_count = self.repository.count_questions(interview.id)
    return item

  def question_response(
    self, question, show_correct: bool = False
  ) -> InterviewQuestionResponse:
    data = {
      "id": question.id,
      "interview_id": question.interview_id,
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
    return InterviewQuestionResponse(**data)

  # ---------- Session scheduling & lifecycle ----------

  def schedule_for_enrollee(
    self,
    enrollee_id: int,
    interview_uuid: str,
    scheduled_at: datetime | None = None,
    expires_in_hours: int = 24 * 7,
  ) -> InterviewSessionTable:
    """Create an interview session for an enrollee.

    NOTE: This method intentionally does NOT import EnrolleeTable or touch
    enrollee columns — the enrollee module owns that side of the relationship.
    """

    interview = self.get_interview(interview_uuid)
    if interview.status != InterviewStatusEnum.ACTIVE:
      raise InterviewTemplateNotActiveException()

    existing = self.repository.get_active_session_for_enrollee(
      enrollee_id, interview.id
    )
    if existing is not None:
      raise InterviewTemplateAlreadyScheduledException()

    session = self.repository.create_session(
      enrollee_id=enrollee_id,
      interview_id=interview.id,
      pass_score_snapshot=interview.pass_score,
      scheduled_at=scheduled_at,
    )
    _ = expires_in_hours
    return session

  def get_session(self, session_uuid: str) -> InterviewSessionTable:
    if not is_valid_uuid(session_uuid):
      raise InterviewSessionNotFoundException()
    session = self.repository.get_session_by_uuid(session_uuid)
    if session is None:
      raise InterviewSessionNotFoundException()
    return session

  def get_session_for_link(
    self,
    session_uuid: str,
    expiry_check: Callable[[InterviewSessionTable], bool] | None = None,
  ) -> InterviewSessionTable:
    session = self.get_session(session_uuid)

    if session.status == InterviewSessionStatusEnum.CANCELLED:
      raise InterviewSessionCancelledException()

    if (
      session.status == InterviewSessionStatusEnum.SCHEDULED
      and expiry_check is not None
    ):
      if not expiry_check(session):
        raise InterviewSessionExpiredException()

    return session

  def start_session(self, session_uuid: str) -> InterviewSessionTable:
    session = self.get_session(session_uuid)

    if session.status == InterviewSessionStatusEnum.CANCELLED:
      raise InterviewSessionCancelledException()
    if session.status == InterviewSessionStatusEnum.IN_PROGRESS:
      raise InterviewSessionAlreadyStartedException()
    if session.status in {
      InterviewSessionStatusEnum.COMPLETED,
      InterviewSessionStatusEnum.GRADED,
    }:
      raise InterviewSessionAlreadyConductedException()
    if session.status != InterviewSessionStatusEnum.SCHEDULED:
      raise InterviewSessionAlreadyStartedException()

    return self.repository.start_session(session)

  def submit_session(
    self, session_uuid: str, payload: SubmitInterviewSession
  ) -> InterviewSessionTable:
    session = self.get_session(session_uuid)

    if session.status == InterviewSessionStatusEnum.CANCELLED:
      raise InterviewSessionCancelledException()
    if session.status in {
      InterviewSessionStatusEnum.COMPLETED,
      InterviewSessionStatusEnum.GRADED,
    }:
      raise InterviewSessionAlreadyConductedException()
    if session.status not in {
      InterviewSessionStatusEnum.IN_PROGRESS,
      InterviewSessionStatusEnum.SCHEDULED,
    }:
      raise InterviewSessionAlreadyStartedException()

    self._validate_submission(session, payload)

    submitted = self.repository.submit_session(session, payload)
    return submitted

  def grade_session(
    self, session_uuid: str, payload: GradeInterviewSession
  ) -> InterviewSessionTable:
    session = self.get_session(session_uuid)

    if session.status == InterviewSessionStatusEnum.CANCELLED:
      raise InterviewSessionCancelledException()
    if session.status == InterviewSessionStatusEnum.GRADED:
      raise InterviewSessionAlreadyConductedException()
    if session.status not in {
      InterviewSessionStatusEnum.COMPLETED,
      InterviewSessionStatusEnum.IN_PROGRESS,
    }:
      raise InterviewSessionNotConductedException()

    graded = self.repository.grade_session(session, payload)

    if self.on_session_graded is not None:
      self.on_session_graded(graded)

    return graded

  def cancel_session(self, session_uuid: str) -> InterviewSessionTable:
    session = self.get_session(session_uuid)

    if session.status in {
      InterviewSessionStatusEnum.COMPLETED,
      InterviewSessionStatusEnum.GRADED,
      InterviewSessionStatusEnum.CANCELLED,
    }:
      raise InterviewSessionAlreadyConductedException()

    return self.repository.cancel_session(session)

  def _validate_submission(
    self, session: InterviewSessionTable, payload: SubmitInterviewSession
  ) -> None:
    question_ids = {q.id for q in session.interview.questions}
    seen_qids: set[int] = set()

    for answer in payload.answers:
      if answer.question_id not in question_ids:
        raise InterviewQuestionNotFoundException(
          f"Question id={answer.question_id} does not belong to this interview."
        )
      if answer.question_id in seen_qids:
        raise InvalidInterviewAnswerException(
          f"Duplicate answer for question id={answer.question_id}."
        )
      seen_qids.add(answer.question_id)

      question = next(
        q for q in session.interview.questions if q.id == answer.question_id
      )
      if answer.selected_option_id is not None:
        valid_option_ids = {opt.id for opt in question.options}
        if answer.selected_option_id not in valid_option_ids:
          raise InvalidInterviewAnswerException(
            f"Option id={answer.selected_option_id} is not valid for "
            f"question id={answer.question_id}."
          )
      if answer.rating_value is not None and (
        answer.rating_value < 1 or answer.rating_value > 10
      ):
        raise InvalidInterviewAnswerException(
          f"Rating value {answer.rating_value} for question "
          f"id={answer.question_id} is outside 1-10 range."
        )
      if (
        question.question_type == InterviewQuestionTypeEnum.MCQ
        and answer.selected_option_id is None
        and not answer.text_answer
      ):
        continue

  # ---------- Graded result builder ----------

  def to_graded_response(self, session: InterviewSessionTable):
    from .validation import GradedInterviewSessionResponse

    base = InterviewSessionResponse.model_validate(session)
    total = sum(q.points for q in session.interview.questions)
    percentage = None
    passed = None
    if total > 0 and session.score is not None:
      percentage = round((session.score / total) * 100, 2)
      if session.pass_score_snapshot is not None:
        passed = percentage >= session.pass_score_snapshot

    return GradedInterviewSessionResponse(
      **base.model_dump(),
      total_points_possible=float(total),
      percentage=percentage,
      passed=passed,
    )
