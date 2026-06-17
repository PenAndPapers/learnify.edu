from .repository import StudentResitory
from .validation import CreateStudent, StudentFullResponse


class StudentService:
  def __init__(self, repository: StudentResitory):
    self.repository = repository


  def create(self, student: CreateStudent) -> StudentFullResponse:
    validated_student = CreateStudent.model_validate(student)

    new_student = self.repository.create(validated_student)

    return new_student
