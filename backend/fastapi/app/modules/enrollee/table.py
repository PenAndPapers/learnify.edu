from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
  Boolean,
  DateTime,
  Enum,
  Float,
  ForeignKey,
  Integer,
  String,
  false,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.user.table import UserTable

from .validation import (
  EnrolleeApplicationStatusEnum,
  InterviewFormatEnum,
  LatestExamStatusEnum,
  LatestInterviewStatusEnum,
  SemesterEnum,
)


class EnrolleeTable(UserTable):
  __tablename__ = "enrollees"

  id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

  application_status: Mapped[EnrolleeApplicationStatusEnum | None] = mapped_column(
    Enum(EnrolleeApplicationStatusEnum),
    default=None,
  )
  previous_application_status: Mapped[EnrolleeApplicationStatusEnum | None] = (
    mapped_column(
      Enum(EnrolleeApplicationStatusEnum),
      default=None,
    )
  )
  chosen_course: Mapped[str | None] = mapped_column(String)
  previous_school: Mapped[str | None] = mapped_column(String)

  application_reference_number: Mapped[str] = mapped_column(
    String,
    default=lambda: str(uuid4()),
    unique=True,
  )
  academic_year: Mapped[str | None] = mapped_column(String)
  semester: Mapped[SemesterEnum | None] = mapped_column(Enum(SemesterEnum))

  strand_or_track: Mapped[str | None] = mapped_column(String)
  previous_school_graduated_year: Mapped[int | None] = mapped_column(Integer)
  general_weighted_average: Mapped[float | None] = mapped_column(Float)

  exam_link_uuid: Mapped[str | None] = mapped_column(
    String,
    default=None,
    unique=True,
  )
  exam_link_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
  latest_exam_status: Mapped[LatestExamStatusEnum | None] = mapped_column(
    Enum(LatestExamStatusEnum)
  )
  exam_score: Mapped[float | None] = mapped_column(Float)
  exam_pass_score: Mapped[float | None] = mapped_column(Float)

  interview_required: Mapped[bool] = mapped_column(Boolean, server_default=false())
  interview_format: Mapped[InterviewFormatEnum] = mapped_column(
    Enum(InterviewFormatEnum),
    default=InterviewFormatEnum.NONE,
  )
  interview_scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
  interviewed_by: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("employees.id", ondelete="SET NULL"),
  )
  interviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

  interview_link_uuid: Mapped[str | None] = mapped_column(
    String,
    default=None,
    unique=True,
  )
  interview_link_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
  latest_interview_status: Mapped[LatestInterviewStatusEnum | None] = mapped_column(
    Enum(LatestInterviewStatusEnum)
  )
  interview_score: Mapped[float | None] = mapped_column(Float)
  interview_pass_score: Mapped[float | None] = mapped_column(Float)

  approved_by: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("employees.id", ondelete="SET NULL"),
  )
  approved_at: Mapped[datetime | None] = mapped_column(DateTime)

  promoted_to_student_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("students.id", ondelete="SET NULL"),
  )
  promoted_at: Mapped[datetime | None] = mapped_column(DateTime)

  __mapper_args__ = {
    "polymorphic_identity": "ENROLLEE",
  }
