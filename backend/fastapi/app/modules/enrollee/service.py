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
  ):
    self.repository = repository
    self.student_repository = student_repository

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
