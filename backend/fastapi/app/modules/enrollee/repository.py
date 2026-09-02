from datetime import datetime

from app.database import DatabaseDep

from .table import EnrolleeTable
from .validation import (
  CreateEnrollee,
  EnrolleeApplicationStatusEnum,
  UpdateEnrollee,
  UpdateEnrolleeStatus,
)


class EnrolleeRepository:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = EnrolleeTable

  def create(self, data: CreateEnrollee) -> EnrolleeTable:
    """Store user info"""
    record = self.model(**data.model_dump())
    self.db.add(record)
    self.db.flush()
    self.db.refresh(record)

    return record

  def get_enrollee(self, uuid: str) -> EnrolleeTable | None:
    """Get an enrollee by UUID."""
    enrollee = self.db.query(self.model).filter(self.model.uuid == uuid).first()

    return enrollee if enrollee else None

  def get_by_promoted_student_id(self, student_id: int) -> EnrolleeTable | None:
    """Look up the originating enrollee row for a promoted student id."""
    enrollee = (
      self.db.query(self.model)
      .filter(self.model.promoted_to_student_id == student_id)
      .first()
    )
    return enrollee if enrollee else None

  def update(self, enrollee: EnrolleeTable, data: UpdateEnrollee) -> EnrolleeTable:
    """Apply a partial PATCH payload to an enrollee row."""
    updated_fields = data.model_dump(exclude_unset=True)

    for key, value in updated_fields.items():
      setattr(enrollee, key, value)

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)
    return enrollee

  def update_enrollee_status(
    self,
    enrollee: EnrolleeTable,
    status: EnrolleeApplicationStatusEnum,
    payload: UpdateEnrolleeStatus | None = None,
  ) -> EnrolleeTable:
    """Update enrollee application status, preserving previous status and setting audit fields."""

    if not enrollee:
      return enrollee

    enrollee.previous_application_status = enrollee.application_status
    enrollee.application_status = status

    if payload is not None and payload.by_employee_id is not None:
      if status == EnrolleeApplicationStatusEnum.APPROVED:
        enrollee.approved_by = payload.by_employee_id
        enrollee.approved_at = datetime.utcnow()
      if (
        status == EnrolleeApplicationStatusEnum.EXAM_PASSED
        and enrollee.interview_required
        and enrollee.interviewed_by is None
      ):
        enrollee.interviewed_by = payload.by_employee_id
        enrollee.interviewed_at = datetime.utcnow()

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)

    return enrollee

  def mark_promoted(
    self,
    enrollee: EnrolleeTable,
    student_id: int,
    promoted_at: datetime | None = None,
  ) -> EnrolleeTable:
    """Backfill the enrollee promotion audit columns after a successful student row create."""

    now = promoted_at or datetime.utcnow()

    enrollee.previous_application_status = enrollee.application_status
    enrollee.application_status = EnrolleeApplicationStatusEnum.ENROLLED
    enrollee.promoted_to_student_id = student_id
    enrollee.promoted_at = now

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)
    return enrollee

  def sync_exam_assignment(
    self,
    enrollee: EnrolleeTable,
    exam_link_uuid: str,
    exam_link_expires_at: datetime,
    exam_pass_score: float,
    by_employee_id: int | None = None,
  ) -> EnrolleeTable:
    """After an exam attempt is created, persist the link UUID, expiry, pass
    score snapshot onto the enrollee and transition status to EXAM_PENDING."""

    from .validation import LatestExamStatusEnum

    enrollee.previous_application_status = enrollee.application_status
    enrollee.application_status = EnrolleeApplicationStatusEnum.EXAM_PENDING
    enrollee.exam_link_uuid = exam_link_uuid
    enrollee.exam_link_expires_at = exam_link_expires_at
    enrollee.exam_pass_score = exam_pass_score
    enrollee.latest_exam_status = LatestExamStatusEnum.ASSIGNED

    _ = by_employee_id

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)
    return enrollee

  def sync_graded_exam(
    self,
    enrollee: EnrolleeTable,
    score: float | None,
    pass_score: float | None,
  ) -> EnrolleeTable:
    """After an exam attempt is graded, sync score + latest status + transition
    the application status to EXAM_PASSED or EXAM_FAILED."""

    from .validation import LatestExamStatusEnum

    enrollee.latest_exam_status = LatestExamStatusEnum.GRADED
    enrollee.exam_score = score
    if pass_score is not None:
      enrollee.exam_pass_score = pass_score

    passed = (
      score is not None
      and enrollee.exam_pass_score is not None
      and score >= enrollee.exam_pass_score
    )
    target = (
      EnrolleeApplicationStatusEnum.EXAM_PASSED
      if passed
      else EnrolleeApplicationStatusEnum.EXAM_FAILED
    )

    enrollee.previous_application_status = enrollee.application_status
    enrollee.application_status = target

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)
    return enrollee

  def get_by_exam_link_uuid(self, exam_link_uuid: str) -> EnrolleeTable | None:
    """Look up an enrollee row by the shared exam link UUID stored on it."""

    enrollee = (
      self.db.query(self.model)
      .filter(self.model.exam_link_uuid == exam_link_uuid)
      .first()
    )
    return enrollee if enrollee else None

  def sync_interview_scheduling(
    self,
    enrollee: EnrolleeTable,
    interview_link_uuid: str,
    interview_link_expires_at: datetime,
    interview_pass_score: float,
    scheduled_at: datetime | None = None,
    by_employee_id: int | None = None,
  ) -> EnrolleeTable:
    """After an interview session is created, persist the link UUID, expiry,
    pass score snapshot onto the enrollee and transition status to INTERVIEW_PENDING."""

    from .validation import LatestInterviewStatusEnum

    enrollee.previous_application_status = enrollee.application_status
    enrollee.application_status = EnrolleeApplicationStatusEnum.INTERVIEW_PENDING
    enrollee.interview_required = True
    enrollee.interview_link_uuid = interview_link_uuid
    enrollee.interview_link_expires_at = interview_link_expires_at
    enrollee.interview_pass_score = interview_pass_score
    enrollee.latest_interview_status = LatestInterviewStatusEnum.SCHEDULED
    if scheduled_at is not None:
      enrollee.interview_scheduled_at = scheduled_at
    if by_employee_id is not None and enrollee.interviewed_by is None:
      enrollee.interviewed_by = by_employee_id

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)
    return enrollee

  def sync_graded_interview(
    self,
    enrollee: EnrolleeTable,
    score: float | None,
    pass_score: float | None,
    passed: bool | None,
    conducted_by: int | None = None,
  ) -> EnrolleeTable:
    """After an interview session is graded, sync score + latest status + transition
    the application status to INTERVIEW_PASSED or INTERVIEW_FAILED."""

    from .validation import LatestInterviewStatusEnum

    enrollee.latest_interview_status = LatestInterviewStatusEnum.GRADED
    enrollee.interview_score = score
    if pass_score is not None:
      enrollee.interview_pass_score = pass_score
    if conducted_by is not None:
      enrollee.interviewed_by = conducted_by
      enrollee.interviewed_at = datetime.utcnow()

    target = (
      EnrolleeApplicationStatusEnum.INTERVIEW_PASSED
      if passed
      else EnrolleeApplicationStatusEnum.INTERVIEW_FAILED
    )

    enrollee.previous_application_status = enrollee.application_status
    enrollee.application_status = target

    self.db.add(enrollee)
    self.db.flush()
    self.db.refresh(enrollee)
    return enrollee

  def get_by_interview_link_uuid(
    self, interview_link_uuid: str
  ) -> EnrolleeTable | None:
    """Look up an enrollee row by the shared interview session link UUID stored on it."""

    enrollee = (
      self.db.query(self.model)
      .filter(self.model.interview_link_uuid == interview_link_uuid)
      .first()
    )
    return enrollee if enrollee else None
