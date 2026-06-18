"""update_student_employee_number

Revision ID: 624c9363288c
Revises: 58df2002f79b
Create Date: 2026-06-18 00:13:38.863799

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '624c9363288c'
down_revision: str | Sequence[str] | None = '58df2002f79b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  """Upgrade schema."""
  # 1. Rename employee column and its unique constraint
  op.alter_column('employees', 'employee_number', new_column_name='employee_id')
  op.execute('ALTER TABLE employees RENAME CONSTRAINT employees_employee_number_key TO employees_employee_id_key')

  # 2. Rename student column and its unique constraint
  op.alter_column('students', 'student_number', new_column_name='student_id')
  op.execute('ALTER TABLE students RENAME CONSTRAINT students_student_number_key TO students_student_id_key')


def downgrade() -> None:
  """Downgrade schema."""
  # 1. Reverse student rename
  op.execute('ALTER TABLE students RENAME CONSTRAINT students_student_id_key TO students_student_number_key')
  op.alter_column('students', 'student_id', new_column_name='student_number')

  # 2. Reverse employee rename
  op.execute('ALTER TABLE employees RENAME CONSTRAINT employees_employee_id_key TO employees_employee_number_key')
  op.alter_column('employees', 'employee_id', new_column_name='employee_number')
