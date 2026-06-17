from sqlalchemy.orm import Session

from .table import StudentTable


class StudentResitory:
  def __init__(self, db: Session):
    self.db = db
    self.model = StudentTable
