from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.user.table import UserTable

from .validation import DepartmentEnum, EmployeeRoleEnum


class EmployeeTable(UserTable):
  __tablename__ = "employees"

  id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

  employee_id: Mapped[str] = mapped_column(String, unique=True)
  department: Mapped[DepartmentEnum] = mapped_column(Enum(DepartmentEnum), default=DepartmentEnum.ADMISSIONS)
  role: Mapped[EmployeeRoleEnum] = mapped_column(Enum(EmployeeRoleEnum), default=EmployeeRoleEnum.TEACHING_STAFF)

  date_hired: Mapped[date | None] = mapped_column(Date)
  is_active: Mapped[bool] = mapped_column(Boolean, default=True)

  __mapper_args__ = {
    "polymorphic_identity": "EMPLOYEE",
  }
