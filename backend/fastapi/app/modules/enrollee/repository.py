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
