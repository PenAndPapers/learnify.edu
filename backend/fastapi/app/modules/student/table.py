from sqlalchemy import Column, ForeignKey, Integer, String

from app.modules.user.table import UserTable

from .validation import StudentAcademicStatusEnum


class StudentTable(UserTable):
  """Holds data strictly unique to ACTIVE ACADEMIC tracking."""

  __tablename__ = "students"

  id = Column(Integer, ForeignKey("users.id"), primary_key=True)

  # Unique to active students
  student_number = Column(String, unique=True, nullable=False)
  year_level = Column(Integer, default=1)
  academic_status = Column(String, default=StudentAcademicStatusEnum.ACTIVE)

  __mapper_args__ = {
    "polymorphic_identity": "STUDENT",
  }
