from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.user.table import UserTable

from .validation import StudentAcademicStatusEnum


class StudentTable(UserTable):
  __tablename__ = "students"

  # Explicit foreign key linking for joined table inheritance
  id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

  student_number: Mapped[str] = mapped_column(String(18), CheckConstraint("length(student_number) = 18", name="ck_student_number_length"), unique=True)
  year_level: Mapped[int] = mapped_column(Integer, default=1)
  academic_status: Mapped[str] = mapped_column(
    String, default=StudentAcademicStatusEnum.ACTIVE
  )

  __mapper_args__ = {
    "polymorphic_identity": "STUDENT",
  }
