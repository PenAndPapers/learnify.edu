import uuid

from app.database import DatabaseDep
from app.modules.enrollee.table import EnrolleeTable

from .table import StudentTable
from .validation import (
  CreateStudent,
  StudentAcademicStatusEnum,
  UpdateStudent,
)


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

  def promote_from_enrollee(self, enrollee: EnrolleeTable) -> StudentTable:
    """Create a Student row sharing the existing users.id of an already-approved enrollee.

    Does NOT duplicate the user row. This uses the SQLAlchemy joined-table inheritance
    pattern: a row in `students` with the same `id` as the enrollee's user row extends
    that user into the STUDENT polymorphic identity. After promotion, the same account
    login works for both the originating enrollee record and the new student record.
    """

    record = self.model(
      id=enrollee.id,
      student_id=self._student_id_generator(),
      year_level=1,
      academic_status=StudentAcademicStatusEnum.ACTIVE,
    )
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
