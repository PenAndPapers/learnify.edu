"""update_columns_to_use_enums

Revision ID: a7b21fc1b25b
Revises: 624c9363288c
Create Date: 2026-06-18 01:23:05.398192

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.modules.authentication.validation import TokenTypeEnum
from app.modules.employee.validation import DepartmentEnum, EmployeeRoleEnum
from app.modules.enrollee.validation import EnrolleeApplicationStatusEnum
from app.modules.student.validation import StudentAcademicStatusEnum
from app.modules.user.validation import UserTypeEnum

# revision identifiers, used by Alembic.
revision: str = 'a7b21fc1b25b'
down_revision: str | Sequence[str] | None = '624c9363288c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Manually create the custom Enum types in the database context
    sa_department_enum = sa.Enum(DepartmentEnum, name='departmentenum')
    sa_role_enum = sa.Enum(EmployeeRoleEnum, name='employeeroleenum')
    sa_department_enum.create(op.get_bind(), checkfirst=True)
    sa_role_enum.create(op.get_bind(), checkfirst=True)

    sa_application_status_enum = sa.Enum(EnrolleeApplicationStatusEnum, name="applicationstatusenum")
    sa_application_status_enum.create(op.get_bind(), checkfirst=True)

    sa_acedemic_status_enum = sa.Enum(StudentAcademicStatusEnum, name="academicstatusenum")
    sa_acedemic_status_enum.create(op.get_bind(), checkfirst=True)

    sa_token_type_enum = sa.Enum(TokenTypeEnum, name="tokentypeenum")
    sa_token_type_enum.create(op.get_bind(), checkfirst=True)

    sa_user_type_enum = sa.Enum(UserTypeEnum, name="usertypeenum")
    sa_user_type_enum.create(op.get_bind(), checkfirst=True)


    # 2. Alter columns with an explicit PostgreSQL USING clause cast
    op.alter_column(
        'employees',
        'department',
        existing_type=sa.String(),
        type_=sa_department_enum,
        existing_nullable=False,
        postgresql_using="department::departmentenum"
    )
    op.alter_column(
        'employees',
        'role',
        existing_type=sa.String(),
        type_=sa_role_enum,
        existing_nullable=False,
        postgresql_using="role::employeeroleenum"
    )

    op.alter_column(
        'enrollees',
        'application_status',
        existing_type=sa.String(),
        type_=sa_application_status_enum,
        existing_nullable=False,
        postgresql_using="application_status::applicationstatusenum"
    )

    op.alter_column(
        'students',
        'academic_status',
        existing_type=sa.String(),
        type_=sa_acedemic_status_enum,
        existing_nullable=False,
        postgresql_using="academic_status::academicstatusenum"
    )

    op.alter_column(
        'tokens',
        'token_type',
        existing_type=sa.String(),
        type_=sa_token_type_enum,
        existing_nullable=False,
        postgresql_using="token_type::tokentypeenum"
    )

    op.alter_column(
        'users',
        'user_type',
        existing_type=sa.String(),
        type_=sa_user_type_enum,
        existing_nullable=False,
        postgresql_using="user_type::usertypeenum"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Revert columns back to standard String/Varchar type
    op.alter_column(
        'employees',
        'department',
        existing_type=sa.Enum(DepartmentEnum, name='departmentenum'),
        type=sa.String(),
        existing_nullable=False
    )
    op.alter_column(
        'employees',
        'role',
        existing_type=sa.Enum(EmployeeRoleEnum, name='employeeroleenum'),
        type=sa.String(),
        existing_nullable=False
    )

    op.alter_column(
        'enrollees',
        'application_status',
        existing_type=sa.Enum(EnrolleeApplicationStatusEnum, name='applicationstatusenum'),
        type=sa.String(),
        existing_nullable=False
    )

    op.alter_column(
        'students',
        'academic_status',
        existing_type=sa.Enum(StudentAcademicStatusEnum, name='academicstatusenum'),
        type=sa.String(),
        existing_nullable=False
    )

    op.alter_column(
        'tokens',
        'token_type',
        existing_type=sa.Enum(TokenTypeEnum, name='tokentypeenum'),
        type=sa.String(),
        existing_nullable=False
    )

    op.alter_column(
        'users',
        'user_type',
        existing_type=sa.Enum(UserTypeEnum, name='usertypeenum'),
        type=sa.String(),
        existing_nullable=False
    )

    # 2. Drop the custom types from PostgreSQL completely
    sa.Enum(name='departmentenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='employeeroleenum').drop(op.get_bind(), checkfirst=True)

    sa.Enum(name='applicationstatusenum').drop(op.get_bind(), checkfirst=True)

    sa.Enum(name='academicstatusenum').drop(op.get_bind(), checkfirst=True)

    sa.Enum(name='tokentypeenum').drop(op.get_bind(), checkfirst=True)

    sa.Enum(name='usertypeenum').drop(op.get_bind(), checkfirst=True)
