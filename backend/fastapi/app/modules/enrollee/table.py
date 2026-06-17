from sqlalchemy import Column, ForeignKey, Integer, String

from app.modules.user.table import UserTable

from .validation import EnrolleeApplicationStatusEnum


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
