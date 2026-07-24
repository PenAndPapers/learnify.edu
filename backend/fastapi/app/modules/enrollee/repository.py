
from app.database import DatabaseDep

from .table import EnrolleeTable
from .validation import CreateEnrollee


class EnrolleeResitory:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = EnrolleeTable

  def create(self, data: CreateEnrollee) -> EnrolleeTable:
    """Store user info"""
    record = self.model(**data.model_dump())
    self.db.add(record)

    return record

  def get_enrollee(self, uuid: str) -> EnrolleeTable | None:
    """Get an enrollee by UUID."""
    enrollee = self.db.query(self.model).filter(self.model.uuid == uuid).first()

    return enrollee if enrollee else None
