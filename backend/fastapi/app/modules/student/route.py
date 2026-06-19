from fastapi import APIRouter

from .dependency import StudentServiceDep
from .validation import CreateStudent, StudentResponse

router = APIRouter(prefix="/api/v1/student", tags=["Student"])


@router.get("/", response_model=None)
def get_students() -> None:
  """Get all student list"""
  pass


@router.post("/login", response_model=None)
def login_student() -> None:
  """Login a student account"""
  pass


@router.post("/", response_model=StudentResponse)
def create_student(
  student: CreateStudent, student_service: StudentServiceDep
) -> StudentResponse:
  """Create a student account"""
  new_student = student_service.create(student)

  return new_student


@router.get("/{uuid}", response_model=None)
def get_student() -> None:
  """Get student account information"""
  pass


@router.patch("/{uuid}", response_model=None)
def update_student() -> None:
  """Update student account information"""
  pass


@router.delete("/{uuid}", response_model=None)
def delete_student() -> None:
  """Delete student account"""
  pass
