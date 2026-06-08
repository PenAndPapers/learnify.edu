from .repository import (
  EmpoyeeResitory,
  EnrolleeResitory,
  StudentResitory,
  UserInternalResponse,
)
from .validation import CreateEnrollee, EnrolleeApplicationStatusEnum, UserTypeEnum


class EnrolleeService:
  def __init__(self, repository: EnrolleeResitory):
    self.repository = repository

  def create(self, enrollee: CreateEnrollee) -> UserInternalResponse:
    """
    TODO: validate if email already exist
    """
    converted_data = CreateEnrollee(
      email=enrollee.email,
      password=enrollee.password,
      first_name=enrollee.first_name,
      last_name=enrollee.last_name,
      phone_number=enrollee.phone_number,
      gender=enrollee.gender,
      date_of_birth=enrollee.date_of_birth,
      address=enrollee.address,
      chosen_course=enrollee.chosen_course,
      previous_school=enrollee.previous_school,
      application_status=EnrolleeApplicationStatusEnum.REGISTERED,
      user_type=UserTypeEnum.ENROLLEE,
      is_verified=False,
    )
    return self.repository.create(converted_data)

  def get_enrollee(self, filter: dict) -> UserInternalResponse | None:
    return self.repository.get_enrollee(filter, False)


class StudentService:
  def __init__(self, repository: StudentResitory):
    self.repository = repository


class EmployeeService:
  def __init__(self, repository: EmpoyeeResitory):
    self.repository = repository
