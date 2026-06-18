from fastapi import APIRouter, Depends

from .dependency import get_student_service
from .service import StudentService
from .validation import CreateStudent, StudentResponse

router = APIRouter(prefix="/api/v1", tags=["Student"])


@router.get("/student/all", response_model=None)
def get_students() -> None:
  """Get list of students"""
  pass


@router.post("/student/login", response_model=None)
def login_student() -> None:
  """Login student"""
  pass


@router.post("/student/create", response_model=StudentResponse)
def create_student(
  student: CreateStudent, student_service: StudentService = Depends(get_student_service)
) -> StudentResponse:
  """Create student account"""
  new_student = student_service.create(student)

  return new_student


@router.get("/student/{uuid}", response_model=None)
def get_student() -> None:
  """Get student account information"""
  pass


@router.patch("/student/{uuid}", response_model=None)
def update_student() -> None:
  """Update student account information"""
  pass


@router.delete("/student/{uuid}", response_model=None)
def delete_student() -> None:
  """Delete student account"""
  pass
