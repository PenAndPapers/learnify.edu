from enum import StrEnum

from pydantic import Field

from app.modules.user.validation import CreateUser, UserBaseResponse, UserTypeEnum


class EnrolleeApplicationStatusEnum(StrEnum):
  REGISTERED = "REGISTERED"
  PROFILE_COMPLETE = "PROFILE_COMPLETE"
  EXAM_PENDING = "EXAM_PENDING"
  EXAM_FAILED = "EXAM_FAILED"
  EXAM_PASSED = "EXAM_PASSED"
  APPROVED = "APPROVED"
  ENROLLED = "ENROLLED"


class EnrolleeResponse(UserBaseResponse):
  """Enrollee details"""

  model_config = {"from_attributes": True}


class CreateEnrollee(CreateUser):
  application_status: EnrolleeApplicationStatusEnum | None = Field(default=None)
  chosen_course: str = Field(default=None, max_length=150)
  previous_school: str = Field(default=None, max_length=150)
  user_type: UserTypeEnum = Field(default=UserTypeEnum.ENROLLEE)
