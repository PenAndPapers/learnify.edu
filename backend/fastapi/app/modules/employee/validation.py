from datetime import date
from enum import StrEnum

from pydantic import Field

from app.modules.user.validation import (
  CreateUser,
  UserBaseResponse,
  UserInternalResponse,
)


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

  employee_number: int
  department: DepartmentEnum
  role: EmployeeRoleEnum
  date_hired: date
  is_active: bool

  model_config = {"from_attributes": True}


class EmployeeResponse(UserBaseResponse):
  """Employee details"""

  employee_number: int
  department: DepartmentEnum
  role: EmployeeRoleEnum
  date_hired: date
  is_active: bool

  model_config = {"from_attributes": True}


class CreateEmployee(CreateUser):
  department: DepartmentEnum = Field(default=DepartmentEnum.ADMISSIONS)
  role: EmployeeRoleEnum = Field(default=EmployeeRoleEnum.TEACHING_STAFF)
  date_hired: date | None = None
  is_active: bool = True
  is_verified: bool = True
