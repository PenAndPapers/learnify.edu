from datetime import date
from decimal import Decimal

from sqlalchemy import (
  Boolean,
  Date,
  Enum,
  ForeignKey,
  Integer,
  Numeric,
  String,
  false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.user.table import UserTable

from .validation import (
  BackgroundCheckStatusEnum,
  DepartmentEnum,
  EmployeeRoleEnum,
  EmployeeStatusEnum,
  EmploymentTypeEnum,
  HighestEducationEnum,
  PayFrequencyEnum,
  WorkArrangementEnum,
)


class EmployeeTable(UserTable):
  __tablename__ = "employees"

  id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

  employee_id: Mapped[str] = mapped_column(String, unique=True)
  department: Mapped[DepartmentEnum] = mapped_column(
    Enum(DepartmentEnum), default=DepartmentEnum.ADMISSIONS
  )
  role: Mapped[EmployeeRoleEnum] = mapped_column(
    Enum(EmployeeRoleEnum), default=EmployeeRoleEnum.TEACHING_STAFF
  )

  date_hired: Mapped[date | None] = mapped_column(Date)

  employment_type: Mapped[EmploymentTypeEnum | None] = mapped_column(
    Enum(EmploymentTypeEnum)
  )
  employee_status: Mapped[EmployeeStatusEnum] = mapped_column(
    Enum(EmployeeStatusEnum), default=EmployeeStatusEnum.ACTIVE
  )
  probation_end_date: Mapped[date | None] = mapped_column(Date)
  date_regularized: Mapped[date | None] = mapped_column(Date)
  date_separated: Mapped[date | None] = mapped_column(Date)
  separation_reason: Mapped[str | None] = mapped_column(String(250))
  work_arrangement: Mapped[WorkArrangementEnum | None] = mapped_column(
    Enum(WorkArrangementEnum)
  )

  job_title: Mapped[str | None] = mapped_column(String(150))
  reports_to_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey(
      "employees.id",
      use_alter=True,
      name="fk_employees_reports_to_id",
    ),
  )
  office_location: Mapped[str | None] = mapped_column(String(100))
  extension_number: Mapped[str | None] = mapped_column(String(20))
  work_email: Mapped[str | None] = mapped_column(String(255))
  teaching_load_units: Mapped[int | None] = mapped_column(Integer)
  advisory_class_section: Mapped[str | None] = mapped_column(String(50))

  highest_education: Mapped[HighestEducationEnum | None] = mapped_column(
    Enum(HighestEducationEnum)
  )
  alma_mater: Mapped[str | None] = mapped_column(String(200))
  year_graduated: Mapped[int | None] = mapped_column(Integer)
  field_of_study: Mapped[str | None] = mapped_column(String(200))
  professional_license_number: Mapped[str | None] = mapped_column(String(100))
  license_expiry: Mapped[date | None] = mapped_column(Date)
  years_of_prior_experience: Mapped[int | None] = mapped_column(Integer)

  nda_signed: Mapped[bool] = mapped_column(Boolean, server_default=false())
  background_check_status: Mapped[BackgroundCheckStatusEnum | None] = mapped_column(
    Enum(BackgroundCheckStatusEnum)
  )
  last_background_check_date: Mapped[date | None] = mapped_column(Date)

  basic_salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
  salary_grade: Mapped[str | None] = mapped_column(String(50))
  pay_frequency: Mapped[PayFrequencyEnum | None] = mapped_column(Enum(PayFrequencyEnum))
  currency: Mapped[str | None] = mapped_column(String(3), default="PHP")

  last_performance_review_date: Mapped[date | None] = mapped_column(Date)
  next_performance_review_date: Mapped[date | None] = mapped_column(Date)
  latest_performance_rating: Mapped[str | None] = mapped_column(String(50))

  reports_to: Mapped["EmployeeTable | None"] = relationship(
    "EmployeeTable", remote_side="EmployeeTable.id"
  )

  __mapper_args__ = {
    "polymorphic_identity": "EMPLOYEE",
  }
