"""create_exam_tables

Revision ID: a1b2c3d4e5f6
Revises: 746da19874ea
Create Date: 2026-09-02 09:45:00.000000

Enum values are intentionally hardcoded here so migrations are self-contained,
replayable historical snapshots. They MUST match, in order and value, the
corresponding StrEnum members in app/modules/exam/validation.py:

  ExamStatusEnum        → ("DRAFT", "ACTIVE", "ARCHIVED")
  QuestionTypeEnum      → ("MCQ", "TRUE_FALSE", "SHORT_ANSWER")
  ExamAttemptStatusEnum → ("ASSIGNED", "IN_PROGRESS", "SUBMITTED", "GRADED")

To add a new enum value later, APPEND it to the validation enum first, then
write a NEW follow-up migration that runs ALTER TYPE ... ADD VALUE.
To remove/reorder values, write a NEW migration that recreates the type via
the rename-then-USING-cast dance. NEVER edit this file to change enum values.

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "746da19874ea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  op.create_table(
    "exams",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.Column(
      "uuid",
      sa.String(),
      nullable=False,
    ),
    sa.Column("title", sa.String(length=200), nullable=False),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("course_code", sa.String(length=50), nullable=True),
    sa.Column("duration_minutes", sa.Integer(), nullable=False),
    sa.Column("pass_score", sa.Float(), nullable=False),
    sa.Column(
      "status",
      sa.Enum("DRAFT", "ACTIVE", "ARCHIVED", name="examstatusenum"),
      nullable=False,
    ),
    sa.Column("created_by", sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(
      ["created_by"],
      ["employees.id"],
      name="fk_exams_created_by_employee",
      ondelete="SET NULL",
    ),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("uuid", name="uq_exams_uuid"),
  )

  op.create_table(
    "exam_questions",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.Column("exam_id", sa.Integer(), nullable=False),
    sa.Column("question_text", sa.Text(), nullable=False),
    sa.Column(
      "question_type",
      sa.Enum("MCQ", "TRUE_FALSE", "SHORT_ANSWER", name="questiontypeenum"),
      nullable=False,
    ),
    sa.Column("points", sa.Integer(), nullable=False),
    sa.Column("order_index", sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
      ["exam_id"],
      ["exams.id"],
      name="fk_exam_questions_exam_id",
      ondelete="CASCADE",
    ),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_index(
    "ix_exam_questions_exam_id",
    "exam_questions",
    ["exam_id"],
    unique=False,
  )

  op.create_table(
    "exam_options",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.Column("question_id", sa.Integer(), nullable=False),
    sa.Column("option_text", sa.String(length=500), nullable=False),
    sa.Column(
      "is_correct",
      sa.Boolean(),
      server_default=sa.text("false"),
      nullable=False,
    ),
    sa.ForeignKeyConstraint(
      ["question_id"],
      ["exam_questions.id"],
      name="fk_exam_options_question_id",
      ondelete="CASCADE",
    ),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_index(
    "ix_exam_options_question_id",
    "exam_options",
    ["question_id"],
    unique=False,
  )

  op.create_table(
    "exam_attempts",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.Column("uuid", sa.String(), nullable=False),
    sa.Column("enrollee_id", sa.Integer(), nullable=False),
    sa.Column("exam_id", sa.Integer(), nullable=False),
    sa.Column(
      "status",
      sa.Enum(
        "ASSIGNED",
        "IN_PROGRESS",
        "SUBMITTED",
        "GRADED",
        name="examattemptstatusenum",
      ),
      nullable=False,
    ),
    sa.Column("pass_score_snapshot", sa.Float(), nullable=True),
    sa.Column("started_at", sa.DateTime(), nullable=True),
    sa.Column("submitted_at", sa.DateTime(), nullable=True),
    sa.Column("score", sa.Float(), nullable=True),
    sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(
      ["enrollee_id"],
      ["enrollees.id"],
      name="fk_exam_attempts_enrollee_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["exam_id"],
      ["exams.id"],
      name="fk_exam_attempts_exam_id",
      ondelete="CASCADE",
    ),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("uuid", name="uq_exam_attempts_uuid"),
  )
  op.create_index(
    "ix_exam_attempts_enrollee_id",
    "exam_attempts",
    ["enrollee_id"],
    unique=False,
  )
  op.create_index(
    "ix_exam_attempts_exam_id",
    "exam_attempts",
    ["exam_id"],
    unique=False,
  )

  op.create_table(
    "exam_answers",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.Column("attempt_id", sa.Integer(), nullable=False),
    sa.Column("question_id", sa.Integer(), nullable=False),
    sa.Column("selected_option_id", sa.Integer(), nullable=True),
    sa.Column("text_answer", sa.Text(), nullable=True),
    sa.Column("is_correct", sa.Boolean(), nullable=True),
    sa.Column("points_awarded", sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(
      ["attempt_id"],
      ["exam_attempts.id"],
      name="fk_exam_answers_attempt_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["question_id"],
      ["exam_questions.id"],
      name="fk_exam_answers_question_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["selected_option_id"],
      ["exam_options.id"],
      name="fk_exam_answers_selected_option_id",
      ondelete="SET NULL",
    ),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_index(
    "ix_exam_answers_attempt_id",
    "exam_answers",
    ["attempt_id"],
    unique=False,
  )
  op.create_index(
    "ix_exam_answers_question_id",
    "exam_answers",
    ["question_id"],
    unique=False,
  )


def downgrade() -> None:
  op.drop_index("ix_exam_answers_question_id", table_name="exam_answers")
  op.drop_index("ix_exam_answers_attempt_id", table_name="exam_answers")
  op.drop_table("exam_answers")

  op.drop_index("ix_exam_attempts_exam_id", table_name="exam_attempts")
  op.drop_index("ix_exam_attempts_enrollee_id", table_name="exam_attempts")
  op.drop_table("exam_attempts")

  op.drop_index("ix_exam_options_question_id", table_name="exam_options")
  op.drop_table("exam_options")

  op.drop_index("ix_exam_questions_exam_id", table_name="exam_questions")
  op.drop_table("exam_questions")

  op.drop_table("exams")

  # Postgres enum types are not dropped when their referencing tables are.
  # Drop them explicitly so a downgrade leaves the schema clean and a
  # subsequent upgrade doesn't fail with "type already exists".
  # Dropping in reverse order of dependency is safest (innermost → outermost).
  for enum_name in (
    "examattemptstatusenum",
    "questiontypeenum",
    "examstatusenum",
  ):
    op.execute(f'DROP TYPE IF EXISTS "{enum_name}"')
