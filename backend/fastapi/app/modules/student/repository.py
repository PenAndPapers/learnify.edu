import uuid

from app.database import DatabaseDep

from .table import StudentTable
from .validation import CreateStudent, StudentFullResponse


class StudentResitory:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = StudentTable

  def _student_id_generator(self) -> str:
    return str(uuid.uuid4())

  def create(self, student: CreateStudent) -> StudentFullResponse:
    """Store student information in the database"""

    record = self.model(student_id=self._student_id_generator(), **student.model_dump())
    self.db.add(record)

    return record
