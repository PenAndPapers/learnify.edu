from sqlalchemy import Column, DateTime, Integer, func

from app.database.session import Base


class AppBaseModel(Base):
  """
  This will be the base schema of the application
  other schema will extend this schema to apply the columns
  it's not necessary to apply this schema to all table

  """

  __abstract__ = True  # prevents sqlalchemy to create a "basemodel" table

  id = Column(Integer, primary_key=True, index=True)
  created_at = Column(DateTime, server_default=func.now(), nullable=False)
  updated_at = Column(
    DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
  )
  deleted_at = Column(DateTime, nullable=True)
