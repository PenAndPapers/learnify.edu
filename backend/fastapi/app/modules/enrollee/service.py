from app.helpers.security import hash_password
from app.modules.enrollee.exception import EnrolleeNotFoundException, EnrolleeIDNotValidException
from app.modules.user.validation import UserInternalResponse
from app.helpers.validators.string import is_valid_uuid

from .repository import EnrolleeResitory
from .table import EnrolleeTable
from .validation import CreateEnrollee, EnrolleeApplicationStatusEnum


class EnrolleeService:
  def __init__(self, repository: EnrolleeResitory):
    self.repository = repository

  def create(self, enrollee: CreateEnrollee) -> UserInternalResponse:
    """Create a new enrollee application record in the database with default values for application status, user type, and verification status."""
    hash_pwd = hash_password(enrollee.password)

    enrollee_data = enrollee.model_copy(update={
      "password": hash_pwd,
      "application_status": EnrolleeApplicationStatusEnum.REGISTERED,
      "is_verified": False,
    })
    new_enrollee = self.repository.create(enrollee_data)

    self.repository.db.flush()

    return new_enrollee

  def get_enrollee(self, uuid: str) -> EnrolleeTable | None:
    """Get an enrollee by UUID."""

    if not is_valid_uuid(uuid):
      raise EnrolleeIDNotValidException()

    enrollee =  self.repository.get_enrollee(uuid)

    if not enrollee:
      raise EnrolleeNotFoundException()

    return enrollee


  def activate_account(self, token: str) -> EnrolleeTable | None:
    """Activate an enrollee account by verifying the activation token."""
    pass