from app.helpers.security import hash_password

from .repository import StudentResitory
from .validation import CreateStudent, StudentFullResponse


class StudentService:
  def __init__(self, repository: StudentResitory):
    self.repository = repository

  def create(self, student: CreateStudent) -> StudentFullResponse:
    """Create a new student record in the database with hashed password."""

    hashed_pwd = hash_password(student.password)
    updated_student = student.model_copy(update={"password": hashed_pwd})

    new_student = self.repository.create(updated_student)

    self.repository.db.flush()

    return new_student
