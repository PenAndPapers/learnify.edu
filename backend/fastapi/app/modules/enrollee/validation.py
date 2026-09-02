from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.user.validation import CreateUser, UserBaseResponse, UserTypeEnum


class EnrolleeApplicationStatusEnum(StrEnum):
  REGISTERED = "REGISTERED"
  PENDING_ACTIVATION = "PENDING_ACTIVATION"
  PROFILE_COMPLETE = "PROFILE_COMPLETE"
  EXAM_PENDING = "EXAM_PENDING"
  EXAM_FAILED = "EXAM_FAILED"
  EXAM_PASSED = "EXAM_PASSED"
  APPROVED = "APPROVED"
  ENROLLED = "ENROLLED"
  REJECTED = "REJECTED"


ALLOWED_STATUS_TRANSITIONS: dict[
  EnrolleeApplicationStatusEnum, set[EnrolleeApplicationStatusEnum]
] = {
  EnrolleeApplicationStatusEnum.REGISTERED: {
    EnrolleeApplicationStatusEnum.PENDING_ACTIVATION,
    EnrolleeApplicationStatusEnum.PROFILE_COMPLETE,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.PENDING_ACTIVATION: {
    EnrolleeApplicationStatusEnum.PROFILE_COMPLETE,
    EnrolleeApplicationStatusEnum.REGISTERED,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.PROFILE_COMPLETE: {
    EnrolleeApplicationStatusEnum.EXAM_PENDING,
    EnrolleeApplicationStatusEnum.APPROVED,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.EXAM_PENDING: {
    EnrolleeApplicationStatusEnum.EXAM_PASSED,
    EnrolleeApplicationStatusEnum.EXAM_FAILED,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.EXAM_FAILED: {
    EnrolleeApplicationStatusEnum.EXAM_PENDING,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.EXAM_PASSED: {
    EnrolleeApplicationStatusEnum.APPROVED,
    EnrolleeApplicationStatusEnum.ENROLLED,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.APPROVED: {
    EnrolleeApplicationStatusEnum.EXAM_PENDING,
    EnrolleeApplicationStatusEnum.EXAM_PASSED,
    EnrolleeApplicationStatusEnum.ENROLLED,
    EnrolleeApplicationStatusEnum.REJECTED,
  },
  EnrolleeApplicationStatusEnum.ENROLLED: set(),
  EnrolleeApplicationStatusEnum.REJECTED: {
    EnrolleeApplicationStatusEnum.PENDING_ACTIVATION,
    EnrolleeApplicationStatusEnum.PROFILE_COMPLETE,
    EnrolleeApplicationStatusEnum.EXAM_PENDING,
  },
}


class SemesterEnum(StrEnum):
  FIRST = "FIRST"
  SECOND = "SECOND"
  SUMMER = "SUMMER"


class LatestExamStatusEnum(StrEnum):
  NOT_ASSIGNED = "NOT_ASSIGNED"
  ASSIGNED = "ASSIGNED"
  IN_PROGRESS = "IN_PROGRESS"
  SUBMITTED = "SUBMITTED"
  GRADED = "GRADED"


class InterviewFormatEnum(StrEnum):
  NONE = "NONE"
  VIRTUAL_SYNC = "VIRTUAL_SYNC"
  VIRTUAL_ASYNC = "VIRTUAL_ASYNC"


class CoursesEnum(StrEnum):
  COMPUTER_SCIENCE = "BACHELOR_OF_SCIENCE_IN_COMPUTER_SCIENCE"
  INFORMATION_TECHNOLOGY = "BACHELOR_OF_SCIENCE_IN_FORMATION_TECHNOLOGY"
  SOFTWARE_ENGINEERING = "BACHELOR_OF_SCIENCE_IN_SOFTWARE_ENGINEERING"
  DATA_SCIENCE = "BACHELOR_OF_SCIENCE_IN_DATA_SCIENCE"
  CYBER_SECURITY = "BACHELOR_OF_SCIENCE_IN_CYBER_SECURITY"
  NETWORKING = "BACHELOR_OF_SCIENCE_IN_NETWORKING"
  ARTIFICIAL_INTELLIGENCE = "BACHELOR_OF_SCIENCE_IN_ARTIFICIAL_INTELLIGENCE"
  CLOUD_COMPUTING = "BACHELOR_OF_SCIENCE_IN_CLOUD_COMPUTING"
  WEB_DEVELOPMENT = "BACHELOR_OF_SCIENCE_IN_WEB_DEVELOPMENT"
  MOBILE_APP_DEVELOPMENT = "BACHELOR_OF_SCIENCE_IN_MOBILE_APP_DEVELOPMENT"
  EDUCATION = "BACHELOR_OF_SCIENCE_IN_EDUCATION"
  PSYCHOLOGY = "BACHELOR_OF_SCIENCE_IN_PSYCHOLOGY"
  BUSINESS_ADMINISTRATION = "BACHELOR_OF_SCIENCE_IN_BUSINESS_ADMINISTRATION"
  ACCOUNTING = "BACHELOR_OF_SCIENCE_IN_ACCOUNTING"
  FINANCE = "BACHELOR_OF_SCIENCE_IN_FINANCE"
  MARKETING = "BACHELOR_OF_SCIENCE_IN_MARKETING"
  HUMAN_RESOURCE_MANAGEMENT = "BACHELOR_OF_SCIENCE_IN_HUMAN_RESOURCE_MANAGEMENT"
  CRIMINOLOGY = "BACHELOR_OF_SCIENCE_IN_CRIMINOLOGY"
  NURSING = "BACHELOR_OF_SCIENCE_IN_NURSING"
  PUBLIC_HEALTH = "BACHELOR_OF_SCIENCE_IN_PUBLIC_HEALTH"
  ENVIRONMENTAL_SCIENCE = "BACHELOR_OF_SCIENCE_IN_ENVIRONMENTAL_SCIENCE"
  BIOLOGY = "BACHELOR_OF_SCIENCE_IN_BIOLOGY"
  CHEMISTRY = "BACHELOR_OF_SCIENCE_IN_CHEMISTRY"
  PHYSICS = "BACHELOR_OF_SCIENCE_IN_PHYSICS"
  MATHEMATICS = "BACHELOR_OF_SCIENCE_IN_MATHEMATICS"
  ECONOMICS = "BACHELOR_OF_SCIENCE_IN_ECONOMICS"
  POLITICAL_SCIENCE = "BACHELOR_OF_SCIENCE_IN_POLITICAL_SCIENCE"
  SOCIOLOGY = "BACHELOR_OF_SCIENCE_IN_SOCIOLOGY"
  PHILOSOPHY = "BACHELOR_OF_SCIENCE_IN_PHILOSOPHY"
  HISTORY = "BACHELOR_OF_SCIENCE_IN_HISTORY"
  LITERATURE = "BACHELOR_OF_SCIENCE_IN_LITERATURE"
  ART = "BACHELOR_OF_SCIENCE_IN_ART"
  MUSIC = "BACHELOR_OF_SCIENCE_IN_MUSIC"
  THEATER = "BACHELOR_OF_SCIENCE_IN_THEATER"
  OTHER = "OTHER"


class EnrolleeResponse(UserBaseResponse):
  """Enrollee details"""

  application_reference_number: str
  academic_year: str | None = None
  semester: SemesterEnum | None = None

  previous_school: str | None = None
  strand_or_track: str | None = None
  previous_school_graduated_year: int | None = None
  general_weighted_average: float | None = None

  chosen_course: CoursesEnum | str | None = None

  application_status: EnrolleeApplicationStatusEnum | None = None
  previous_application_status: EnrolleeApplicationStatusEnum | None = None

  exam_link_uuid: UUID | str | None = None
  exam_link_expires_at: datetime | None = None
  latest_exam_status: LatestExamStatusEnum | None = None
  exam_score: float | None = None
  exam_pass_score: float | None = None

  interview_required: bool = False
  interview_format: InterviewFormatEnum = InterviewFormatEnum.NONE
  interview_scheduled_at: datetime | None = None
  interviewed_by: int | None = None
  interviewed_at: datetime | None = None

  approved_by: int | None = None
  approved_at: datetime | None = None

  promoted_to_student_id: int | None = None
  promoted_at: datetime | None = None

  is_verified: bool

  model_config = {"from_attributes": True}


class CreateEnrollee(CreateUser):
  previous_school: str = Field(
    ..., min_length=2, max_length=150, examples=["Farrell-Shields University"]
  )
  chosen_course: CoursesEnum = Field(
    ...,
    description="The course the enrollee is applying for.",
    examples=[CoursesEnum.INFORMATION_TECHNOLOGY.value],
  )

  academic_year: str | None = Field(
    default=None,
    max_length=20,
    description="Academic year the enrollee is applying for, e.g. '2026-2027'.",
    examples=["2026-2027"],
  )
  semester: SemesterEnum | None = Field(
    default=None,
    description="Intake semester for the application.",
  )
  strand_or_track: str | None = Field(
    default=None,
    max_length=100,
    description="K-12 strand or previous educational track.",
    examples=["STEM", "ABM", "TVL-ICT"],
  )
  previous_school_graduated_year: int | None = Field(
    default=None,
    ge=1950,
    le=2200,
    description="Year the enrollee graduated from their previous school.",
    examples=[2025],
  )
  general_weighted_average: float | None = Field(
    default=None,
    ge=0.0,
    le=5.0,
    description="General Weighted Average from the previous school.",
    examples=[1.5],
  )

  application_status: EnrolleeApplicationStatusEnum | None = None
  previous_application_status: EnrolleeApplicationStatusEnum | None = None
  user_type: UserTypeEnum = UserTypeEnum.ENROLLEE
  is_verified: bool = False

  model_config = {"from_attributes": True}


class UpdateEnrollee(BaseModel):
  """Partial edit of enrollee application fields (enrollee self-service + admin)."""

  previous_school: str | None = Field(default=None, min_length=2, max_length=150)
  chosen_course: CoursesEnum | None = Field(default=None)

  academic_year: str | None = Field(default=None, max_length=20)
  semester: SemesterEnum | None = None
  strand_or_track: str | None = Field(default=None, max_length=100)
  previous_school_graduated_year: int | None = Field(default=None, ge=1950, le=2200)
  general_weighted_average: float | None = Field(default=None, ge=0.0, le=5.0)

  exam_pass_score: float | None = Field(default=None, ge=0.0, le=100.0)

  interview_required: bool | None = None
  interview_format: InterviewFormatEnum | None = None
  interview_scheduled_at: datetime | None = None
  interviewed_by: int | None = None
  interviewed_at: datetime | None = None

  model_config = {"from_attributes": True}


class UpdateEnrolleeStatus(BaseModel):
  """Admin payload used to transition an enrollee from one application status to another."""

  status: EnrolleeApplicationStatusEnum
  by_employee_id: int | None = Field(
    default=None,
    description="Employee FK of the admin performing the change.",
  )
  note: str | None = Field(
    default=None,
    max_length=500,
    description="Free-text reason or comment for the status change.",
  )


class AssignEnrolleeExam(BaseModel):
  """Payload to assign an online entrance exam to an enrollee."""

  exam_uuid: UUID = Field(
    ...,
    description="UUID of the exam template to assign.",
  )
  expires_in_hours: int = Field(
    default=72,
    ge=1,
    le=24 * 30,
    description="How long the generated exam link remains valid (hours).",
  )
  by_employee_id: int | None = Field(
    default=None,
    description="Employee FK of the admin assigning the exam.",
  )
