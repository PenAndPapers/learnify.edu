"""expand_enrollee_table_add_admissions_fields

Revision ID: 746da19874ea
Revises: 380e59bad4e5
Create Date: 2026-09-02 07:44:55.251883

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.modules.enrollee.validation import (
  InterviewFormatEnum,
  LatestExamStatusEnum,
  SemesterEnum,
)

# revision identifiers, used by Alembic.
revision: str = "746da19874ea"
down_revision: str | Sequence[str] | None = "380e59bad4e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  """Upgrade schema."""

  sa_semester_enum = sa.Enum(SemesterEnum, name="semesterenum")
  sa_semester_enum.create(op.get_bind(), checkfirst=True)

  sa_latest_exam_status_enum = sa.Enum(
    LatestExamStatusEnum, name="latestexamstatusenum"
  )
  sa_latest_exam_status_enum.create(op.get_bind(), checkfirst=True)

  sa_interview_format_enum = sa.Enum(InterviewFormatEnum, name="interviewformatenum")
  sa_interview_format_enum.create(op.get_bind(), checkfirst=True)

  op.add_column(
    "enrollees",
    sa.Column("application_reference_number", sa.String(), nullable=True),
  )
  op.execute(
    "UPDATE enrollees SET application_reference_number = "
    "gen_random_uuid()::text WHERE application_reference_number IS NULL"
  )
  op.alter_column("enrollees", "application_reference_number", nullable=False)

  op.add_column("enrollees", sa.Column("academic_year", sa.String(), nullable=True))
  op.add_column(
    "enrollees",
    sa.Column("semester", sa_semester_enum, nullable=True),
  )
  op.add_column("enrollees", sa.Column("strand_or_track", sa.String(), nullable=True))
  op.add_column(
    "enrollees",
    sa.Column("previous_school_graduated_year", sa.Integer(), nullable=True),
  )
  op.add_column(
    "enrollees",
    sa.Column("general_weighted_average", sa.Float(), nullable=True),
  )
  op.add_column("enrollees", sa.Column("exam_link_uuid", sa.String(), nullable=True))
  op.add_column(
    "enrollees",
    sa.Column("exam_link_expires_at", sa.DateTime(), nullable=True),
  )
  op.add_column(
    "enrollees",
    sa.Column("latest_exam_status", sa_latest_exam_status_enum, nullable=True),
  )
  op.add_column("enrollees", sa.Column("exam_score", sa.Float(), nullable=True))
  op.add_column("enrollees", sa.Column("exam_pass_score", sa.Float(), nullable=True))

  op.add_column(
    "enrollees",
    sa.Column(
      "interview_required",
      sa.Boolean(),
      server_default=sa.text("false"),
      nullable=True,
    ),
  )
  op.execute(
    "UPDATE enrollees SET interview_required = false WHERE interview_required IS NULL"
  )
  op.alter_column(
    "enrollees",
    "interview_required",
    nullable=False,
    server_default=sa.text("false"),
  )
  op.add_column(
    "enrollees",
    sa.Column("interview_format", sa_interview_format_enum, nullable=True),
  )
  op.execute(
    "UPDATE enrollees SET interview_format = 'NONE' WHERE interview_format IS NULL"
  )
  op.alter_column(
    "enrollees", "interview_format", nullable=False, server_default="NONE"
  )
  op.add_column(
    "enrollees",
    sa.Column("interview_scheduled_at", sa.DateTime(), nullable=True),
  )
  op.add_column("enrollees", sa.Column("interviewed_by", sa.Integer(), nullable=True))
  op.add_column("enrollees", sa.Column("interviewed_at", sa.DateTime(), nullable=True))
  op.add_column("enrollees", sa.Column("approved_by", sa.Integer(), nullable=True))
  op.add_column("enrollees", sa.Column("approved_at", sa.DateTime(), nullable=True))
  op.add_column(
    "enrollees",
    sa.Column("promoted_to_student_id", sa.Integer(), nullable=True),
  )
  op.add_column("enrollees", sa.Column("promoted_at", sa.DateTime(), nullable=True))

  op.create_unique_constraint(
    "uq_enrollees_application_reference_number",
    "enrollees",
    ["application_reference_number"],
  )
  op.create_unique_constraint(
    "uq_enrollees_exam_link_uuid", "enrollees", ["exam_link_uuid"]
  )

  op.create_foreign_key(
    "fk_enrollees_interviewed_by_id",
    "enrollees",
    "employees",
    ["interviewed_by"],
    ["id"],
    ondelete="SET NULL",
  )
  op.create_foreign_key(
    "fk_enrollees_approved_by_id",
    "enrollees",
    "employees",
    ["approved_by"],
    ["id"],
    ondelete="SET NULL",
  )
  op.create_foreign_key(
    "fk_enrollees_promoted_to_student_id",
    "enrollees",
    "students",
    ["promoted_to_student_id"],
    ["id"],
    ondelete="SET NULL",
  )


def downgrade() -> None:
  """Downgrade schema."""

  op.drop_constraint(
    "fk_enrollees_promoted_to_student_id", "enrollees", type_="foreignkey"
  )
  op.drop_constraint("fk_enrollees_approved_by_id", "enrollees", type_="foreignkey")
  op.drop_constraint("fk_enrollees_interviewed_by_id", "enrollees", type_="foreignkey")

  op.drop_constraint("uq_enrollees_exam_link_uuid", "enrollees", type_="unique")
  op.drop_constraint(
    "uq_enrollees_application_reference_number", "enrollees", type_="unique"
  )

  op.drop_column("enrollees", "promoted_at")
  op.drop_column("enrollees", "promoted_to_student_id")
  op.drop_column("enrollees", "approved_at")
  op.drop_column("enrollees", "approved_by")
  op.drop_column("enrollees", "interviewed_at")
  op.drop_column("enrollees", "interviewed_by")
  op.drop_column("enrollees", "interview_scheduled_at")
  op.alter_column("enrollees", "interview_format", nullable=True)
  op.alter_column("enrollees", "interview_format", server_default=None)
  op.drop_column("enrollees", "interview_format")
  op.alter_column("enrollees", "interview_required", server_default=None)
  op.alter_column("enrollees", "interview_required", nullable=True)
  op.drop_column("enrollees", "interview_required")
  op.drop_column("enrollees", "exam_pass_score")
  op.drop_column("enrollees", "exam_score")
  op.drop_column("enrollees", "latest_exam_status")
  op.drop_column("enrollees", "exam_link_expires_at")
  op.drop_column("enrollees", "exam_link_uuid")
  op.drop_column("enrollees", "general_weighted_average")
  op.drop_column("enrollees", "previous_school_graduated_year")
  op.drop_column("enrollees", "strand_or_track")
  op.drop_column("enrollees", "semester")
  op.drop_column("enrollees", "academic_year")
  op.drop_column("enrollees", "application_reference_number")

  sa_semester_enum = sa.Enum(SemesterEnum, name="semesterenum")
  sa_semester_enum.drop(op.get_bind(), checkfirst=True)

  sa_latest_exam_status_enum = sa.Enum(
    LatestExamStatusEnum, name="latestexamstatusenum"
  )
  sa_latest_exam_status_enum.drop(op.get_bind(), checkfirst=True)

  sa_interview_format_enum = sa.Enum(InterviewFormatEnum, name="interviewformatenum")
  sa_interview_format_enum.drop(op.get_bind(), checkfirst=True)
