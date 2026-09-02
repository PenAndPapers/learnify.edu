from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
  Boolean,
  Date,
  DateTime,
  Enum,
  ForeignKey,
  Index,
  Integer,
  Numeric,
  String,
  Text,
  UniqueConstraint,
  false,
  func,
  text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.table import BaseTable
from app.modules.user.table import UserTable

from .validation import (
  BackgroundCheckStatusEnum,
  BankAccountTypeEnum,
  CompensationChangeReasonEnum,
  DepartmentEnum,
  EmployeeDocumentTypeEnum,
  EmployeeRoleEnum,
  EmployeeStatusEnum,
  EmploymentTypeEnum,
  HighestEducationEnum,
  LeaveTypeEnum,
  PayFrequencyEnum,
  PerformanceRatingEnum,
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
    "EmployeeTable",
    remote_side="EmployeeTable.id",
    foreign_keys="EmployeeTable.reports_to_id",
  )

  # 1:N related tables — owned rows vanish if employee is removed
  compensation_history: Mapped[list["EmployeeCompensationHistoryTable"]] = relationship(
    "EmployeeCompensationHistoryTable",
    back_populates="employee",
    cascade="all, delete-orphan",
  )
  leave_credits: Mapped[list["EmployeeLeaveCreditsTable"]] = relationship(
    "EmployeeLeaveCreditsTable",
    back_populates="employee",
    cascade="all, delete-orphan",
  )
  documents: Mapped[list["EmployeeDocumentsTable"]] = relationship(
    "EmployeeDocumentsTable",
    back_populates="employee",
    cascade="all, delete-orphan",
    foreign_keys="EmployeeDocumentsTable.employee_id",
  )
  performance_reviews: Mapped[list["EmployeePerformanceReviewsTable"]] = relationship(
    "EmployeePerformanceReviewsTable",
    back_populates="employee",
    cascade="all, delete-orphan",
    foreign_keys="EmployeePerformanceReviewsTable.employee_id",
  )
  education_history: Mapped[list["EmployeeEducationHistoryTable"]] = relationship(
    "EmployeeEducationHistoryTable",
    back_populates="employee",
    cascade="all, delete-orphan",
  )
  bank_accounts: Mapped[list["EmployeeBankAccountsTable"]] = relationship(
    "EmployeeBankAccountsTable",
    back_populates="employee",
    cascade="all, delete-orphan",
  )

  __mapper_args__ = {
    "polymorphic_identity": "EMPLOYEE",
  }


class EmployeeCompensationHistoryTable(BaseTable):
  __tablename__ = "employee_compensation_history"

  employee_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("employees.id", ondelete="CASCADE")
  )
  effective_date: Mapped[date] = mapped_column(Date)
  end_date: Mapped[date | None] = mapped_column(Date)
  basic_salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
  salary_grade: Mapped[str | None] = mapped_column(String(50))
  pay_frequency: Mapped[PayFrequencyEnum | None] = mapped_column(Enum(PayFrequencyEnum))
  currency: Mapped[str | None] = mapped_column(String(3), default="PHP")
  change_reason: Mapped[CompensationChangeReasonEnum | None] = mapped_column(
    Enum(CompensationChangeReasonEnum)
  )
  notes: Mapped[str | None] = mapped_column(String(500))

  employee: Mapped["EmployeeTable"] = relationship(
    "EmployeeTable", back_populates="compensation_history"
  )

  __table_args__ = (
    UniqueConstraint(
      "employee_id",
      "effective_date",
      name="uq_emp_comp_history_employee_effective_date",
    ),
    Index(
      "ix_emp_comp_history_employee_id",
      "employee_id",
    ),
    Index(
      "ix_emp_comp_history_effective_date",
      "effective_date",
    ),
  )


class EmployeeLeaveCreditsTable(BaseTable):
  __tablename__ = "employee_leave_credits"

  employee_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("employees.id", ondelete="CASCADE")
  )
  leave_type: Mapped[LeaveTypeEnum] = mapped_column(Enum(LeaveTypeEnum))
  fiscal_year: Mapped[str] = mapped_column(String(20))
  total_credited: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0)
  used: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0)
  balance: Mapped[Decimal] = mapped_column(Numeric(5, 1), default=0)
  as_of_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())
  notes: Mapped[str | None] = mapped_column(String(500))

  employee: Mapped["EmployeeTable"] = relationship(
    "EmployeeTable", back_populates="leave_credits"
  )

  __table_args__ = (
    UniqueConstraint(
      "employee_id",
      "leave_type",
      "fiscal_year",
      name="uq_emp_leave_credits_employee_type_fiscal_year",
    ),
    Index(
      "ix_emp_leave_credits_employee_id",
      "employee_id",
    ),
  )


class EmployeeDocumentsTable(BaseTable):
  __tablename__ = "employee_documents"

  employee_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("employees.id", ondelete="CASCADE")
  )
  document_type: Mapped[EmployeeDocumentTypeEnum] = mapped_column(
    Enum(EmployeeDocumentTypeEnum)
  )
  document_title: Mapped[str] = mapped_column(String(200))
  file_name: Mapped[str | None] = mapped_column(String(255))
  file_path: Mapped[str | None] = mapped_column(String(500))
  file_url: Mapped[str | None] = mapped_column(String(1000))
  mime_type: Mapped[str | None] = mapped_column(String(100))
  uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  expiry_date: Mapped[date | None] = mapped_column(Date)
  verified_by_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey(
      "employees.id",
      ondelete="SET NULL",
      use_alter=True,
      name="fk_emp_docs_verified_by_id",
    ),
  )
  notes: Mapped[str | None] = mapped_column(String(500))

  employee: Mapped["EmployeeTable"] = relationship(
    "EmployeeTable",
    back_populates="documents",
    foreign_keys=[employee_id],
  )
  verified_by: Mapped["EmployeeTable | None"] = relationship(
    "EmployeeTable", foreign_keys=[verified_by_id]
  )

  __table_args__ = (
    Index(
      "ix_emp_documents_employee_id",
      "employee_id",
    ),
    Index(
      "ix_emp_documents_verified_by_id",
      "verified_by_id",
    ),
    Index(
      "ix_emp_documents_expiry_date",
      "expiry_date",
    ),
  )


class EmployeePerformanceReviewsTable(BaseTable):
  __tablename__ = "employee_performance_reviews"

  employee_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("employees.id", ondelete="CASCADE")
  )
  review_date: Mapped[date] = mapped_column(Date)
  review_period: Mapped[str] = mapped_column(String(50))
  reviewer_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey(
      "employees.id",
      ondelete="SET NULL",
      use_alter=True,
      name="fk_emp_perf_reviewer_id",
    ),
  )
  rating: Mapped[PerformanceRatingEnum | None] = mapped_column(
    Enum(PerformanceRatingEnum)
  )
  score_numeric: Mapped[int | None] = mapped_column(Integer)
  overall_comments: Mapped[str | None] = mapped_column(Text)
  goals_next_period: Mapped[str | None] = mapped_column(Text)
  employee_sign_off_date: Mapped[date | None] = mapped_column(Date)
  reviewer_sign_off_date: Mapped[date | None] = mapped_column(Date)
  next_review_date: Mapped[date | None] = mapped_column(Date)
  attachments_path: Mapped[str | None] = mapped_column(String(500))

  employee: Mapped["EmployeeTable"] = relationship(
    "EmployeeTable",
    back_populates="performance_reviews",
    foreign_keys=[employee_id],
  )
  reviewer: Mapped["EmployeeTable | None"] = relationship(
    "EmployeeTable", foreign_keys=[reviewer_id]
  )

  __table_args__ = (
    Index(
      "ix_emp_perf_reviews_employee_id",
      "employee_id",
    ),
    Index(
      "ix_emp_perf_reviews_reviewer_id",
      "reviewer_id",
    ),
    Index(
      "ix_emp_perf_reviews_review_date",
      "review_date",
    ),
  )


class EmployeeEducationHistoryTable(BaseTable):
  __tablename__ = "employee_education_history"

  employee_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("employees.id", ondelete="CASCADE")
  )
  degree: Mapped[HighestEducationEnum] = mapped_column(Enum(HighestEducationEnum))
  field_of_study: Mapped[str] = mapped_column(String(200))
  institution_name: Mapped[str] = mapped_column(String(200))
  institution_location: Mapped[str | None] = mapped_column(String(200))
  year_started: Mapped[int | None] = mapped_column(Integer)
  year_completed: Mapped[int | None] = mapped_column(Integer)
  is_incomplete: Mapped[bool] = mapped_column(Boolean, server_default=false())
  honors: Mapped[str | None] = mapped_column(String(200))
  thesis_title: Mapped[str | None] = mapped_column(String(500))
  diploma_document_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey(
      "employee_documents.id",
      ondelete="SET NULL",
      use_alter=True,
      name="fk_emp_edu_diploma_doc_id",
    ),
  )

  employee: Mapped["EmployeeTable"] = relationship(
    "EmployeeTable", back_populates="education_history"
  )
  diploma_document: Mapped["EmployeeDocumentsTable | None"] = relationship(
    "EmployeeDocumentsTable", foreign_keys=[diploma_document_id]
  )

  __table_args__ = (
    Index(
      "ix_emp_edu_history_employee_id",
      "employee_id",
    ),
    Index(
      "ix_emp_edu_history_year_completed",
      "year_completed",
    ),
    Index(
      "ix_emp_edu_history_diploma_document_id",
      "diploma_document_id",
    ),
  )


class EmployeeBankAccountsTable(BaseTable):
  __tablename__ = "employee_bank_accounts"

  employee_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("employees.id", ondelete="CASCADE")
  )
  bank_name: Mapped[str] = mapped_column(String(100))
  bank_branch: Mapped[str | None] = mapped_column(String(100))
  routing_code: Mapped[str | None] = mapped_column(String(50))
  account_number: Mapped[str] = mapped_column(String(100))
  account_type: Mapped[BankAccountTypeEnum] = mapped_column(Enum(BankAccountTypeEnum))
  account_holder_name: Mapped[str | None] = mapped_column(String(200))
  currency: Mapped[str] = mapped_column(String(3), default="PHP")
  is_primary: Mapped[bool] = mapped_column(Boolean, server_default=false())
  is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
  verified_at: Mapped[date | None] = mapped_column(Date)
  notes: Mapped[str | None] = mapped_column(String(500))

  employee: Mapped["EmployeeTable"] = relationship(
    "EmployeeTable", back_populates="bank_accounts"
  )

  __table_args__ = (
    Index(
      "ix_emp_bank_accounts_employee_id",
      "employee_id",
    ),
    Index(
      "ix_emp_bank_accounts_primary",
      "is_primary",
    ),
  )
