import uuid

from app.database import DatabaseDep

from .table import StudentTable
from .validation import CreateStudent, UpdateStudent


class StudentRepository:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = StudentTable

  def _student_id_generator(self) -> str:
    return str(uuid.uuid4())

  def create(self, student: CreateStudent) -> StudentTable:
    """Store student information in the database"""

    record = self.model(student_id=self._student_id_generator(), **student.model_dump())
    self.db.add(record)
    self.db.flush()
    self.db.refresh(record)

    return record

  def read(self, uuid: str) -> StudentTable | None:
    """Get a student by UUID"""

    record = self.db.query(self.model).filter(self.model.uuid == uuid).first()

    return record

  def update(self, uuid: str, student: UpdateStudent) -> StudentTable | None:
    """Update a student by UUID"""

    record = self.read(uuid)

    if not record:
      return None

    updated_data = student.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
      setattr(record, key, value)

    self.db.flush()
    self.db.refresh(record)

    return record

  def delete(self, uuid: str) -> bool:
    """Delete a student by UUID"""

    record = self.read(uuid)

    if not record:
      return False

    self.db.delete(record)
    self.db.flush()
    return True
