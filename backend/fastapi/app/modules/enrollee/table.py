from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.user.table import UserTable

from .validation import EnrolleeApplicationStatusEnum


class EnrolleeTable(UserTable):
    __tablename__ = "enrollees"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

    application_status: Mapped[str] = mapped_column(String, default=EnrolleeApplicationStatusEnum.REGISTERED)
    chosen_course: Mapped[str | None] = mapped_column(String)
    previous_school: Mapped[str | None] = mapped_column(String)

    __mapper_args__ = {
        "polymorphic_identity": "ENROLLEE",
    }
