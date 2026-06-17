from enum import StrEnum

from pydantic import Field

from app.modules.user.validation import CreateUser, UserBaseResponse, UserTypeEnum


class StudentAcademicStatusEnum(StrEnum):
  ACTIVE = "ACTIVE"
  INACTIVE = "INACTIVE"
  GRADUATED = "GRADUATED"
  ON_LEAVE = "ON_LEAVE"
  SUSPENDED = "SUSPENDED"
  WITHDRAWN = "WITHDRAWN"


class StudentResponse(UserBaseResponse):
  """Student details"""

  model_config = {"from_attributes": True}


class CreateStudent(CreateUser):
  student_number: int = Field(
    ...,
    ge=10000000,
    le=999999999999,
    description="Must be an integer between 8 and 12 digits",
  )
  year_level: int = Field(
    ..., ge=1, le=5, description="Year level must be between 1 and 5"
  )
  academic_status: StudentAcademicStatusEnum = Field(
    default=StudentAcademicStatusEnum.ACTIVE
  )
  user_type: UserTypeEnum = Field(default=UserTypeEnum.STUDENT)
