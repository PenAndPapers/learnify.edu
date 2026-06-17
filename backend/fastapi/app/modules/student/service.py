from .repository import StudentResitory


class StudentService:
  def __init__(self, repository: StudentResitory):
    self.repository = repository
