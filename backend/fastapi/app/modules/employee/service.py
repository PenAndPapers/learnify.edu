from .repository import EmpoyeeResitory


class EmployeeService:
  def __init__(self, repository: EmpoyeeResitory):
    self.repository = repository
