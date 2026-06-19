from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import EnrolleeResitory
from .service import EnrolleeService


# Enrollee service dependency
def get_enrollee_repository(db: DatabaseDep) -> EnrolleeResitory:
  return EnrolleeResitory(db)


EnrolleeRepositoryDep = Annotated[EnrolleeResitory, Depends(get_enrollee_repository)]


def get_enrolle_service(
  repository: EnrolleeResitory = Depends(get_enrollee_repository),
) -> EnrolleeService:
  return EnrolleeService(repository)


EnrolleeServiceDep = Annotated[EnrolleeService, Depends(get_enrolle_service)]
