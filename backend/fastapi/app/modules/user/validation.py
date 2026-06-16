from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, AwareDatetime


class UserTypeEnum(StrEnum):
  ENROLLEE = "ENROLLEE"
  STUDENT = "STUDENT"
  EMPLOYEE = "EMPLOYEE"


class StudentAcademicStatusEnum(StrEnum):
  ACTIVE = "ACTIVE"
  INACTIVE = "INACTIVE"
  GRADUATED = "GRADUATED"
  ON_LEAVE = "ON_LEAVE"
  SUSPENDED = "SUSPENDED"
  WITHDRAWN = "WITHDRAWN"


class EnrolleeApplicationStatusEnum(StrEnum):
  REGISTERED = "REGISTERED"
  PROFILE_COMPLETE = "PROFILE_COMPLETE"
  EXAM_PENDING = "EXAM_PENDING"
  EXAM_FAILED = "EXAM_FAILED"
  EXAM_PASSED = "EXAM_PASSED"
  APPROVED = "APPROVED"
  ENROLLED = "ENROLLED"


class EmployeeRoleEnum(StrEnum):
  SYSTEM_ADMIN = "SYSTEM_ADMIN"
  IT_STAFF = "IT_STAFF"
  HUMAN_RESOURCE = "HUMAN_RESOURCE"
  FINANCE = "FINANCE"
  INVENTORY_MANAGER = "INVENTORY_MANAGER"
  REGISTRAR = "REGISTRAR"
  ACADEMIC_LEAD = "ACADEMIC_LEAD"
  TEACHING_STAFF = "TEACHING_STAFF"
  LIBRARIAN = "LIBRARIAN"
  ADMINISTRATIVE_STAFF = "ADMINISTRATIVE_STAFF"
  EXECUTIVE = "EXECUTIVE"


class DepartmentEnum(StrEnum):
  ADMISSIONS = "ADMISSIONS"
  INFORMATION_TECHNOLOGY = "INFORMATION_TECHNOLOGY"
  HUMAN_RESOURCES = "HUMAN_RESOURCES"
  FINANCE_AND_ACCOUNTING = "FINANCE_AND_ACCOUNTING"
  REGISTRAR_OFFICE = "REGISTRAR_OFFICE"
  FACILITIES_AND_OPERATIONS = "FACILITIES_AND_OPERATIONS"
  MATHEMATICS = "MATHEMATICS"
  SCIENCE = "SCIENCE"
  COMPUTING_AND_INFORMATION_SCIENCES = "COMPUTING_AND_INFORMATION_SCIENCES"
  ENGINEERING = "ENGINEERING"
  BUSINESS_AND_MANAGEMENT = "BUSINESS_AND_MANAGEMENT"
  HUMANITIES_AND_SOCIAL_SCIENCES = "HUMANITIES_AND_SOCIAL_SCIENCES"
  LANGUAGES = "LANGUAGES"


class UserBaseSchema(BaseModel):
  """User schema containing shared details"""

  uuid: str
  email: EmailStr
  first_name: str | None = None
  last_name: str | None = None
  phone_number: str | None = None
  gender: str | None = None
  date_of_birth: date | None = None
  address: str | None = None
  user_type: UserTypeEnum
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None

  model_config = {"from_attributes": True}


class UserInternalResponse(UserBaseSchema):
  """
  User schema containing sensitive user details
  Note:
    Avoid using this for returning a response
  """

  id: int

  model_config = {"from_attributes": True}


class EnrolleeResponse(UserBaseSchema):
  """Enrollee details"""

  model_config = {"from_attributes": True}


class StudentResponse(UserBaseSchema):
  """Student details"""

  model_config = {"from_attributes": True}


class EmployeeResponse(UserBaseSchema):
  """Employee details"""

  model_config = {"from_attributes": True}


class CreateUser(BaseModel):
  """The data required for creating a user"""

  email: EmailStr
  password: str = Field(..., min_length=8)
  first_name: str | None = Field(default=None, max_length=100)
  last_name: str | None = Field(default=None, max_length=100)
  phone_number: str | None = Field(default=None, max_length=50)
  gender: str | None = Field(default=None, max_length=50)
  date_of_birth: date | None = None
  address: str | None = Field(default=None, max_length=250)
  is_verified: bool = Field(default=False)
  user_type: UserTypeEnum | None = Field(default=None)


class CreateEnrollee(CreateUser):
  application_status: EnrolleeApplicationStatusEnum | None = Field(default=None)
  chosen_course: str = Field(default=None, max_length=150)
  previous_school: str = Field(default=None, max_length=150)
  user_type: UserTypeEnum = Field(default=UserTypeEnum.ENROLLEE)


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
