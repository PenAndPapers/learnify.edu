from app.modules.user.validation import UserInternalResponse, UserTypeEnum

from .repository import EnrolleeResitory
from .validation import CreateEnrollee, EnrolleeApplicationStatusEnum


class EnrolleeService:
  def __init__(self, repository: EnrolleeResitory):
    self.repository = repository

  def create(self, enrollee: CreateEnrollee) -> UserInternalResponse:
    """Create a new enrollee application record in the database with default values for application status, user type, and verification status."""

    enrollee_data = enrollee.model_copy(update={
      "application_status": EnrolleeApplicationStatusEnum.REGISTERED,
      "user_type": UserTypeEnum.ENROLLEE,
      "is_verified": False,
    })
    new_enrollee = self.repository.create(enrollee_data)

    self.repository.db.flush()

    return new_enrollee

  def get_enrollee(self, filter: dict) -> UserInternalResponse | None:
    """Get an enrollee by filter."""
    return self.repository.get_enrollee(filter, False)
