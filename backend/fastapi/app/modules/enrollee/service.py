from app.modules.user.validation import UserInternalResponse, UserTypeEnum

from .repository import EnrolleeResitory
from .validation import CreateEnrollee, EnrolleeApplicationStatusEnum


class EnrolleeService:
  def __init__(self, repository: EnrolleeResitory):
    self.repository = repository

  def create(self, enrollee: CreateEnrollee) -> UserInternalResponse:
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
    new_enrollee = self.repository.create(converted_data)

    self.repository.db.flush()

    return new_enrollee

  def get_enrollee(self, filter: dict) -> UserInternalResponse | None:
    return self.repository.get_enrollee(filter, False)
