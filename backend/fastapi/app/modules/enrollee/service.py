from datetime import datetime, timedelta
from typing import Any

from app.helpers.security import hash_password
from app.helpers.validators.string import is_valid_uuid
from app.modules.enrollee.exception import (
  EnrolleeAlreadyPromotedException,
  EnrolleeExamNotPassedException,
  EnrolleeIDNotValidException,
  EnrolleeNotApprovedException,
  EnrolleeNotFoundException,
  InvalidEnrolleeStatusTransitionException,
)
from app.modules.student.repository import StudentRepository
from app.modules.student.table import StudentTable

from .repository import EnrolleeRepository
from .table import EnrolleeTable
from .validation import (
  ALLOWED_STATUS_TRANSITIONS,
  AssignEnrolleeExam,
  CreateEnrollee,
  EnrolleeApplicationStatusEnum,
  UpdateEnrollee,
  UpdateEnrolleeStatus,
)


class EnrolleeService:
  def __init__(
    self,
    repository: EnrolleeRepository,
    student_repository: StudentRepository | None = None,
    exam_service_factory: Any = None,
  ):
    """EnrolleeService is the orchestrator.

    - exam_service_factory: a callable (callback) -> ExamService.
      The factory is responsible for wiring the enrollee's sync_graded_exam
      hook as the `on_attempt_graded` callback so that whenever ExamService
      grades a submission, the enrollee row is atomically kept in sync.
      Injected by the enrollee.dependency module to avoid circular imports.
    """

    self.repository = repository
    self.student_repository = student_repository
    self._exam_service_factory = exam_service_factory
    self._exam_service = None

  def _get_exam_service(self):
    """Lazily construct the wired ExamService on first use."""

    if self._exam_service is None:
      if self._exam_service_factory is None:
        msg = (
          "assign_exam called but ExamService factory was not injected. "
          "Wire EnrolleeService via dependency.get_enrollee_service()."
        )
        raise RuntimeError(msg)
      self._exam_service = self._exam_service_factory(
        self._build_graded_attempt_callback()
      )
    return self._exam_service

  def _build_graded_attempt_callback(self):
    """Return a closure that ExamService calls after grading an attempt."""

    def callback(attempt):
      self._sync_graded_attempt_to_enrollee(attempt)

    return callback

  def _sync_graded_attempt_to_enrollee(self, attempt) -> None:
    """Sync enrollee row after an exam attempt is graded."""

    enrollee = (
      self.repository.db.query(EnrolleeTable)
      .filter(EnrolleeTable.id == attempt.enrollee_id)
      .first()
    )
    if enrollee is None:
      return
    self.repository.sync_graded_exam(
      enrollee,
      score=attempt.score,
      pass_score=attempt.pass_score_snapshot,
    )

  @staticmethod
  def is_transition_allowed(
    current: EnrolleeApplicationStatusEnum | None,
    target: EnrolleeApplicationStatusEnum,
  ) -> bool:
    if current is None:
      return target in {
        EnrolleeApplicationStatusEnum.REGISTERED,
        EnrolleeApplicationStatusEnum.PENDING_ACTIVATION,
      }
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current, set())
    return target in allowed

  def create(self, enrollee: CreateEnrollee) -> EnrolleeTable:
    """Create a new enrollee application record in the database."""
    hash_pwd = hash_password(enrollee.password)

    enrollee_data = enrollee.model_copy(
      update={
        "password": hash_pwd,
        "application_status": EnrolleeApplicationStatusEnum.REGISTERED,
        "is_verified": False,
      }
    )
    new_enrollee = self.repository.create(enrollee_data)
    return new_enrollee

  def get_enrollee(self, uuid: str) -> EnrolleeTable:
    """Get an enrollee by UUID."""

    if not is_valid_uuid(uuid):
      raise EnrolleeIDNotValidException()

    enrollee = self.repository.get_enrollee(uuid)

    if not enrollee:
      raise EnrolleeNotFoundException()

    return enrollee

  def update_enrollee(self, uuid: str, payload: UpdateEnrollee) -> EnrolleeTable:
    """Partial edit of enrollee fields."""
    enrollee = self.get_enrollee(uuid)
    return self.repository.update(enrollee, payload)

  def update_enrollee_status(
    self, uuid: str, payload: UpdateEnrolleeStatus
  ) -> EnrolleeTable:
    """Update the application status of an enrollee by UUID with legal-transition guard."""

    enrollee = self.get_enrollee(uuid)

    if not self.is_transition_allowed(enrollee.application_status, payload.status):
      raise InvalidEnrolleeStatusTransitionException(
        f"Cannot transition enrollee status from "
        f"{enrollee.application_status.value if enrollee.application_status else None} "
        f"to {payload.status.value}."
      )

    return self.repository.update_enrollee_status(enrollee, payload.status, payload)

  def is_eligible_for_promotion(self, uuid: str) -> tuple[bool, Exception | None]:
    """Return (True, None) if the enrollee satisfies the promotion guard, else (False, exception)."""

    try:
      enrollee = self.get_enrollee(uuid)
    except Exception as exc:
      return False, exc

    if enrollee.promoted_to_student_id is not None:
      return False, EnrolleeAlreadyPromotedException()

    approved_states = {
      EnrolleeApplicationStatusEnum.APPROVED,
      EnrolleeApplicationStatusEnum.EXAM_PASSED,
      EnrolleeApplicationStatusEnum.ENROLLED,
    }
    if (
      enrollee.application_status is None
      or enrollee.application_status not in approved_states
    ):
      return False, EnrolleeNotApprovedException()

    if enrollee.application_status != EnrolleeApplicationStatusEnum.EXAM_PASSED:
      passed = (
        enrollee.exam_score is not None
        and enrollee.exam_pass_score is not None
        and enrollee.exam_score >= enrollee.exam_pass_score
      )
      if not passed:
        return False, EnrolleeExamNotPassedException()

    return True, None

  def promote_to_student(
    self, uuid: str, by_employee_id: int | None = None
  ) -> StudentTable:
    """Convert an APPROVED + exam-passed enrollee into an ACTIVE year-1 student.

    Returns the newly created StudentTable row (ORM entity, not Pydantic).
    """

    if self.student_repository is None:
      msg = (
        "promote_to_student called but StudentRepository was not injected. "
        "Wire EnrolleeService with a StudentRepository instance first."
      )
      raise RuntimeError(msg)

    enrollee = self.get_enrollee(uuid)

    eligible, reason = self.is_eligible_for_promotion(uuid)
    if not eligible:
      assert reason is not None
      raise reason

    student = self.student_repository.promote_from_enrollee(enrollee)
    self.repository.mark_promoted(enrollee, student_id=student.id, promoted_at=None)
    _ = by_employee_id

    return student

  # ---------- Exam module integration (orchestration side) ----------

  def assign_exam(
    self,
    enrollee_uuid: str,
    payload: AssignEnrolleeExam,
  ):
    """Assign an exam template to this enrollee.

    Orchestrates:
      1. validate enrollee + exam exist
      2. delegate to ExamService to create the ExamAttempt row
      3. write back exam_link_uuid, expires_at, pass_score snapshot + EXAM_PENDING status
    """

    enrollee = self.get_enrollee(enrollee_uuid)
    exam_service = self._get_exam_service()

    attempt = exam_service.assign_to_enrollee(
      enrollee_id=enrollee.id,
      exam_uuid=str(payload.exam_uuid),
      expires_in_hours=payload.expires_in_hours,
    )

    created_at = (
      attempt.created_at if hasattr(attempt, "created_at") else datetime.utcnow()
    )
    expiry = created_at + timedelta(hours=payload.expires_in_hours)

    synced = self.repository.sync_exam_assignment(
      enrollee=enrollee,
      exam_link_uuid=attempt.uuid,
      exam_link_expires_at=expiry,
      exam_pass_score=attempt.pass_score_snapshot or 0.0,
      by_employee_id=payload.by_employee_id,
    )
    _ = synced

    return attempt

  def get_enrollee_by_exam_link(self, exam_link_uuid: str) -> EnrolleeTable:
    """Lookup an enrollee by their stored exam_link_uuid (used by public link route)."""

    if not is_valid_uuid(exam_link_uuid):
      raise EnrolleeNotFoundException()

    enrollee = self.repository.get_by_exam_link_uuid(exam_link_uuid)
    if enrollee is None:
      raise EnrolleeNotFoundException()
    return enrollee

  def is_exam_link_expired(self, exam_link_uuid: str) -> bool:
    """Check if the exam link (exam attempt) has expired based on enrollee snapshot."""

    enrollee = self.get_enrollee_by_exam_link(exam_link_uuid)
    if enrollee.exam_link_expires_at is None:
      return False
    return datetime.utcnow() > enrollee.exam_link_expires_at
