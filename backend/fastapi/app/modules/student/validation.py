from enum import StrEnum

from pydantic import Field

from app.modules.user.validation import (
  CreateUser,
  UserBaseResponse,
  UserInternalResponse,
  UserTypeEnum,
)


class StudentAcademicStatusEnum(StrEnum):
  ACTIVE = "ACTIVE"
  INACTIVE = "INACTIVE"
  GRADUATED = "GRADUATED"
  ON_LEAVE = "ON_LEAVE"
  SUSPENDED = "SUSPENDED"
  WITHDRAWN = "WITHDRAWN"


class StudentFullResponse(UserInternalResponse):
  """Student full detail response"""

  studen_number: int
  year_level: int
  academic_status: StudentAcademicStatusEnum

  model_config = {"from_attributes": True}


class StudentResponse(UserBaseResponse):
  """Student details"""

  student_number: int
  year_level: int
  academic_status: StudentAcademicStatusEnum

  model_config = {"from_attributes": True}


class CreateStudent(CreateUser):
  year_level: int = Field(
    ..., ge=1, le=5, description="Year level must be between 1 and 5"
  )
  user_type: UserTypeEnum = Field(default=UserTypeEnum.STUDENT)
  is_verified: int = True
