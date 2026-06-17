from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String

from app.modules.user.table import UserTable

from .validation import DepartmentEnum, EmployeeRoleEnum


class EmployeeTable(UserTable):
  """Holds data strictly unique to FACULTY and ADMINISTRATIVE staff."""

  __tablename__ = "employees"

  id = Column(Integer, ForeignKey("users.id"), primary_key=True)

  # Unique to employees
  employee_number = Column(String, unique=True, nullable=False)
  department = Column(String, nullable=False, default=DepartmentEnum.ADMISSIONS)

  # Employee sub-roles (Crucial for guarding your FastAPI routes!)
  role = Column(String, nullable=False, default=EmployeeRoleEnum.TEACHING_STAFF)

  date_hired = Column(Date, nullable=True)
  is_active = Column(Boolean, default=True)

  __mapper_args__ = {
    "polymorphic_identity": "EMPLOYEE",
  }
