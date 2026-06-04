from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String

from app.database.session import Base


class UserTable(Base):
    """
    The Single Source of Truth for Identity & Core Biography.
    Every human in the system has a row here.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, default=lambda: str(uuid4()), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)

    # Polymorphism
    user_type = Column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_on": user_type,
        "polymorphic_identity": "user"
    }


class EnrolleeTable(UserTable):
    """Holds data strictly unique to the ADMISSIONS process."""
    __tablename__ = "enrollees"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # Unique to admissions
    application_status = Column(String, server_default="REGISTERED")  # e.g., EXAM_PENDING, PASSED
    chosen_course = Column(String, nullable=True)
    previous_school = Column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "enrollee",
    }


class StudentTable(UserTable):
    """Holds data strictly unique to ACTIVE ACADEMIC tracking."""
    __tablename__ = "students"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # Unique to active students
    student_number = Column(String, unique=True, nullable=False)
    year_level = Column(Integer, default=1)
    academic_status = Column(String, server_default="ACTIVE")  # e.g., ACTIVE, ON_LEAVE, GRADUATED

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }


class EmployeeTable(UserTable):
    """Holds data strictly unique to FACULTY and ADMINISTRATIVE staff."""
    __tablename__ = "employees"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # Unique to employees
    employee_number = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)  # e.g., "Admissions", "IT", "Mathematics"

    # Employee sub-roles (Crucial for guarding your FastAPI routes!)
    role = Column(String, nullable=False, server_default="STAFF")  # e.g., "TEACHER", "REGISTRAR", "ADMIN"

    date_hired = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    __mapper_args__ = {
        "polymorphic_identity": "employee",
    }
