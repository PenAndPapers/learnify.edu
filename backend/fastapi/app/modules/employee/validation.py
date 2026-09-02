from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from app.modules.user.validation import (
  CreateUser,
  UpdateUser,
  UserBaseResponse,
  UserInternalResponse,
  UserTypeEnum,
)


class EmploymentTypeEnum(StrEnum):
  FULL_TIME = "FULL_TIME"
  PART_TIME = "PART_TIME"
  CONTRACT = "CONTRACT"
  TEMPORARY = "TEMPORARY"
  PROBATIONARY = "PROBATIONARY"


class EmployeeStatusEnum(StrEnum):
  ACTIVE = "ACTIVE"
  ON_LEAVE = "ON_LEAVE"
  SUSPENDED = "SUSPENDED"
  RESIGNED = "RESIGNED"
  TERMINATED = "TERMINATED"
  RETIRED = "RETIRED"


class WorkArrangementEnum(StrEnum):
  ONSITE = "ONSITE"
  HYBRID = "HYBRID"
  REMOTE = "REMOTE"


class HighestEducationEnum(StrEnum):
  HIGH_SCHOOL = "HIGH_SCHOOL"
  BACHELORS = "BACHELORS"
  MASTERS = "MASTERS"
  DOCTORATE = "DOCTORATE"
  PROFESSIONAL = "PROFESSIONAL"


class BackgroundCheckStatusEnum(StrEnum):
  PENDING = "PENDING"
  CLEARED = "CLEARED"
  FAILED = "FAILED"
  NOT_APPLICABLE = "NOT_APPLICABLE"


class PayFrequencyEnum(StrEnum):
  MONTHLY = "MONTHLY"
  BI_MONTHLY = "BI_MONTHLY"
  WEEKLY = "WEEKLY"


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


class EmployeeFullResponse(UserInternalResponse):
  """Full employee details"""

  employee_id: str
  department: DepartmentEnum
  role: EmployeeRoleEnum
  date_hired: date | None = None
  employment_type: EmploymentTypeEnum | None = None
  employee_status: EmployeeStatusEnum
  probation_end_date: date | None = None
  date_regularized: date | None = None
  date_separated: date | None = None
  separation_reason: str | None = Field(default=None, max_length=250)
  work_arrangement: WorkArrangementEnum | None = None
  job_title: str | None = Field(default=None, max_length=150)
  reports_to_id: int | None = None
  office_location: str | None = Field(default=None, max_length=100)
  extension_number: str | None = Field(default=None, max_length=20)
  work_email: str | None = Field(default=None, max_length=255)
  teaching_load_units: int | None = None
  advisory_class_section: str | None = Field(default=None, max_length=50)
  highest_education: HighestEducationEnum | None = None
  alma_mater: str | None = Field(default=None, max_length=200)
  year_graduated: int | None = None
  field_of_study: str | None = Field(default=None, max_length=200)
  professional_license_number: str | None = Field(default=None, max_length=100)
  license_expiry: date | None = None
  years_of_prior_experience: int | None = None
  nda_signed: bool = False
  background_check_status: BackgroundCheckStatusEnum | None = None
  last_background_check_date: date | None = None
  basic_salary: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
  salary_grade: str | None = Field(default=None, max_length=50)
  pay_frequency: PayFrequencyEnum | None = None
  currency: str | None = Field(default=None, max_length=3)
  last_performance_review_date: date | None = None
  next_performance_review_date: date | None = None
  latest_performance_rating: str | None = Field(default=None, max_length=50)

  model_config = {"from_attributes": True}


class EmployeeResponse(UserBaseResponse):
  """Employee details"""

  employee_id: str
  department: DepartmentEnum
  role: EmployeeRoleEnum
  date_hired: date | None = None
  employment_type: EmploymentTypeEnum | None = None
  employee_status: EmployeeStatusEnum
  probation_end_date: date | None = None
  date_regularized: date | None = None
  date_separated: date | None = None
  separation_reason: str | None = Field(default=None, max_length=250)
  work_arrangement: WorkArrangementEnum | None = None
  job_title: str | None = Field(default=None, max_length=150)
  reports_to_id: int | None = None
  office_location: str | None = Field(default=None, max_length=100)
  extension_number: str | None = Field(default=None, max_length=20)
  work_email: str | None = Field(default=None, max_length=255)
  teaching_load_units: int | None = None
  advisory_class_section: str | None = Field(default=None, max_length=50)
  highest_education: HighestEducationEnum | None = None
  alma_mater: str | None = Field(default=None, max_length=200)
  year_graduated: int | None = None
  field_of_study: str | None = Field(default=None, max_length=200)
  professional_license_number: str | None = Field(default=None, max_length=100)
  license_expiry: date | None = None
  years_of_prior_experience: int | None = None
  nda_signed: bool = False
  background_check_status: BackgroundCheckStatusEnum | None = None
  last_background_check_date: date | None = None
  basic_salary: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
  salary_grade: str | None = Field(default=None, max_length=50)
  pay_frequency: PayFrequencyEnum | None = None
  currency: str | None = Field(default=None, max_length=3)
  last_performance_review_date: date | None = None
  next_performance_review_date: date | None = None
  latest_performance_rating: str | None = Field(default=None, max_length=50)

  model_config = {"from_attributes": True}


class CreateEmployee(CreateUser):
  user_type: UserTypeEnum = Field(default=UserTypeEnum.EMPLOYEE)
  department: DepartmentEnum = Field(default=DepartmentEnum.ADMISSIONS)
  role: EmployeeRoleEnum = Field(default=EmployeeRoleEnum.TEACHING_STAFF)
  date_hired: date | None = None
  employment_type: EmploymentTypeEnum | None = None
  employee_status: EmployeeStatusEnum = Field(default=EmployeeStatusEnum.ACTIVE)
  probation_end_date: date | None = None
  date_regularized: date | None = None
  date_separated: date | None = None
  separation_reason: str | None = Field(default=None, max_length=250)
  work_arrangement: WorkArrangementEnum | None = None
  job_title: str | None = Field(default=None, max_length=150)
  reports_to_id: int | None = None
  office_location: str | None = Field(default=None, max_length=100)
  extension_number: str | None = Field(default=None, max_length=20)
  work_email: str | None = Field(default=None, max_length=255)
  teaching_load_units: int | None = None
  advisory_class_section: str | None = Field(default=None, max_length=50)
  highest_education: HighestEducationEnum | None = None
  alma_mater: str | None = Field(default=None, max_length=200)
  year_graduated: int | None = None
  field_of_study: str | None = Field(default=None, max_length=200)
  professional_license_number: str | None = Field(default=None, max_length=100)
  license_expiry: date | None = None
  years_of_prior_experience: int | None = None
  nda_signed: bool = False
  background_check_status: BackgroundCheckStatusEnum | None = None
  last_background_check_date: date | None = None
  basic_salary: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
  salary_grade: str | None = Field(default=None, max_length=50)
  pay_frequency: PayFrequencyEnum | None = None
  currency: str | None = Field(default="PHP", max_length=3)
  last_performance_review_date: date | None = None
  next_performance_review_date: date | None = None
  latest_performance_rating: str | None = Field(default=None, max_length=50)
  is_verified: bool = True

  model_config = {"from_attributes": True}


class UpdateEmployee(UpdateUser):
  department: DepartmentEnum | None = Field(default=None)
  role: EmployeeRoleEnum | None = Field(default=None)
  date_hired: date | None = None
  employment_type: EmploymentTypeEnum | None = Field(default=None)
  employee_status: EmployeeStatusEnum | None = Field(default=None)
  probation_end_date: date | None = Field(default=None)
  date_regularized: date | None = Field(default=None)
  date_separated: date | None = Field(default=None)
  separation_reason: str | None = Field(default=None, max_length=250)
  work_arrangement: WorkArrangementEnum | None = Field(default=None)
  job_title: str | None = Field(default=None, max_length=150)
  reports_to_id: int | None = Field(default=None)
  office_location: str | None = Field(default=None, max_length=100)
  extension_number: str | None = Field(default=None, max_length=20)
  work_email: str | None = Field(default=None, max_length=255)
  teaching_load_units: int | None = Field(default=None)
  advisory_class_section: str | None = Field(default=None, max_length=50)
  highest_education: HighestEducationEnum | None = Field(default=None)
  alma_mater: str | None = Field(default=None, max_length=200)
  year_graduated: int | None = Field(default=None)
  field_of_study: str | None = Field(default=None, max_length=200)
  professional_license_number: str | None = Field(default=None, max_length=100)
  license_expiry: date | None = Field(default=None)
  years_of_prior_experience: int | None = Field(default=None)
  nda_signed: bool | None = Field(default=None)
  background_check_status: BackgroundCheckStatusEnum | None = Field(default=None)
  last_background_check_date: date | None = Field(default=None)
  basic_salary: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
  salary_grade: str | None = Field(default=None, max_length=50)
  pay_frequency: PayFrequencyEnum | None = Field(default=None)
  currency: str | None = Field(default=None, max_length=3)
  last_performance_review_date: date | None = Field(default=None)
  next_performance_review_date: date | None = Field(default=None)
  latest_performance_rating: str | None = Field(default=None, max_length=50)

  model_config = {"from_attributes": True}
