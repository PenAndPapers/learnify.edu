from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, false
from sqlalchemy.orm import relationship

from app.core.base_model import AppBaseModel

from .validation import (
  EmployeeRoleEnum,
  EnrolleeApplicationStatusEnum,
  StudentAcademicStatusEnum,
)


class UserTable(AppBaseModel):
  """
  The Single Source of Truth for Identity & Core Biography.
  Every human in the system has a row here.
  """

  __tablename__ = "users"

  uuid = Column(String, default=lambda: str(uuid4()), unique=True, nullable=False)
  email = Column(String, unique=True, nullable=False)
  password = Column(String, nullable=False)
  first_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)
  phone_number = Column(String, nullable=True)
  gender = Column(String, nullable=True)
  date_of_birth = Column(Date, nullable=True)
  address = Column(String, nullable=True)
  is_verified = Column(Boolean, server_default=false(), nullable=False)

  # Polymorphism
  user_type = Column(String, nullable=False)

  tokens = relationship(
    "TokenTable", back_populates="user", cascade="all, delete-orphan"
  )

  __mapper_args__ = {"polymorphic_on": user_type, "polymorphic_identity": "user"}


class EnrolleeTable(UserTable):
  """Holds data strictly unique to the ADMISSIONS process."""

  __tablename__ = "enrollees"

  id = Column(Integer, ForeignKey("users.id"), primary_key=True)

  # Unique to admissions
  application_status = Column(String, default=EnrolleeApplicationStatusEnum.REGISTERED)
  chosen_course = Column(String, nullable=True)
  previous_school = Column(String, nullable=True)

  __mapper_args__ = {
    "polymorphic_identity": "ENROLLEE",
  }


class StudentTable(UserTable):
  """Holds data strictly unique to ACTIVE ACADEMIC tracking."""

  __tablename__ = "students"

  id = Column(Integer, ForeignKey("users.id"), primary_key=True)

  # Unique to active students
  student_number = Column(String, unique=True, nullable=False)
  year_level = Column(Integer, default=1)
  academic_status = Column(
    String, default=StudentAcademicStatusEnum.ACTIVE
  )  # e.g., ACTIVE, ON_LEAVE, GRADUATED

  __mapper_args__ = {
    "polymorphic_identity": "STUDENT",
  }


class EmployeeTable(UserTable):
  """Holds data strictly unique to FACULTY and ADMINISTRATIVE staff."""

  __tablename__ = "employees"

  id = Column(Integer, ForeignKey("users.id"), primary_key=True)

  # Unique to employees
  employee_number = Column(String, unique=True, nullable=False)
  department = Column(String, nullable=False)

  # Employee sub-roles (Crucial for guarding your FastAPI routes!)
  role = Column(String, nullable=False, default=EmployeeRoleEnum.TEACHING_STAFF)

  date_hired = Column(Date, nullable=True)
  is_active = Column(Boolean, default=True)

  __mapper_args__ = {
    "polymorphic_identity": "EMPLOYEE",
  }
