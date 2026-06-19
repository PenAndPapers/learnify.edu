from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class BaseTable(Base):
  """
  The modern base schema using SQLAlchemy 2.0 Mapped attributes.
  """

  __abstract__ = True

  # primary_key=True keeps nullable=False implicitly
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

  # We use server_default expressions, but explicitly map to standard datetime
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(
    DateTime, server_default=func.now(), onupdate=func.now()
  )

  # Optional typing (str | None) cleanly flags nullable=True automatically
  deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
