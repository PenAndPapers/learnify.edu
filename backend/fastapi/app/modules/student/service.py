from app.helpers.security import hash_password
from app.helpers.validators.string import is_valid_uuid
from app.modules.student.exception import (
  StudentIDNotValidException,
  StudentNotFoundException,
)

from .repository import StudentResitory
from .validation import CreateStudent, StudentFullResponse, UpdateStudent


class StudentService:
  def __init__(self, repository: StudentResitory):
    self.repository = repository

  def get_students(self) -> None:
    """Get list of students"""
    pass

  def create(self, student: CreateStudent) -> StudentFullResponse:
    """Create a new student record in the database with hashed password."""

    hash_pwd = hash_password(student.password)
    updated_student = student.model_copy(update={"password": hash_pwd})

    new_student = self.repository.create(updated_student)

    self.repository.db.flush()

    return new_student

  def read(self, uuid: str) -> StudentFullResponse:
    """Get a student by UUID."""

    if not is_valid_uuid(uuid):
      raise StudentIDNotValidException()

    student = self.repository.read(uuid)

    if not student:
      raise StudentNotFoundException()

    return student

  def update(self, uuid: str, student: UpdateStudent) -> StudentFullResponse:
    """Update a student record in the database by UUID."""

    updated_student = self.repository.update(uuid, student)

    if not updated_student:
      raise StudentNotFoundException()

    return updated_student

  def delete(self, uuid: str) -> None:
    """Delete a student record in the database by UUID."""

    if not is_valid_uuid(uuid):
      raise StudentIDNotValidException()

    is_student_deleted = self.repository.delete(uuid)

    if not is_student_deleted:
      raise StudentNotFoundException()

    return None
