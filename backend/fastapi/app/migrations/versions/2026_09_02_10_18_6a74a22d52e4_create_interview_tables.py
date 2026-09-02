"""create_interview_tables

Revision ID: 6a74a22d52e4
Revises: a1b2c3d4e5f6
Create Date: 2026-09-02 10:18:52.516871

Enum values are intentionally hardcoded here so migrations are self-contained,
replayable historical snapshots. They MUST match, in order and value, the
corresponding StrEnum members in app/modules/interview/validation.py and
app/modules/enrollee/validation.py:

  InterviewStatusEnum        → ("DRAFT", "ACTIVE", "ARCHIVED")
  InterviewSessionStatusEnum → ("SCHEDULED", "IN_PROGRESS", "COMPLETED",
                                "GRADED", "CANCELLED")
  InterviewQuestionTypeEnum  → ("MCQ", "SHORT_ANSWER", "RATING_SCALE")
  LatestInterviewStatusEnum  → ("NOT_SCHEDULED", "SCHEDULED", "IN_PROGRESS",
                                "COMPLETED", "GRADED", "CANCELLED")
  EnrolleeApplicationStatusEnum new values appended:
      INTERVIEW_PENDING, INTERVIEW_FAILED, INTERVIEW_PASSED

To add a new enum value later, APPEND it to the validation enum first, then
write a NEW follow-up migration that runs ALTER TYPE ... ADD VALUE.
To remove/reorder values, write a NEW migration that recreates the type via
the rename-then-USING-cast dance. NEVER edit this file to change enum values.

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6a74a22d52e4"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _postgres_enum_type_ref(
  type_name: str, values: tuple[str, ...]
) -> sa.types.TypeEngine:
  """Return a Postgres ENUM type REFERENCE (no side effects on DDL emit).

  Alembic + SQLAlchemy 2.0's vanilla :class:`sqlalchemy.Enum` constructor still
  triggers ``CREATE TYPE`` emission even with ``create_constraint=False`` when
  used on Postgres. To avoid this after we've already materialised the type
  via ``_create_postgres_enum_safely``, we construct a
  :class:`sqlalchemy.dialects.postgresql.ENUM` with ``create_type=False``.
  ``values`` is kept here purely for documentation/repr.
  """
  return postgresql.ENUM(
    *values,
    name=type_name,
    create_type=False,
  )


def _create_postgres_enum_safely(type_name: str, values: tuple[str, ...]) -> None:
  """Create a Postgres ENUM type idempotently.

  Postgres does not support ``CREATE TYPE ... IF NOT EXISTS``, so we wrap
  the statement in a small PL/pgSQL block that swallows the
  ``duplicate_object`` error. This lets us re-run the migration without
  manually cleaning up partially-applied DDL state from earlier failed
  attempts (Alembic rolls back the transaction, but partially-created
  Postgres enum types sometimes leak across transactional DDL in testing).
  """
  labels_sql = ", ".join(f"'{v}'" for v in values)
  op.execute(
    f"""
    DO $$
    BEGIN
      CREATE TYPE {type_name} AS ENUM ({labels_sql});
    EXCEPTION WHEN duplicate_object THEN
      NULL;
    END $$;
    """
  )


def upgrade() -> None:
  # ---------------------------------------------------------------------------
  # 0. Enrollee: Rename the existing Postgres enum type to match the name the
  #    ORM currently generates (SQLAlchemy auto-generates a name for the
  #    Enum(EnrolleeApplicationStatusEnum) column when no explicit `name=`
  #    is given). Previous migrations created it as `applicationstatusenum`;
  #    standardize to `enrolleeapplicationstatusenum` now so later ADD VALUEs
  #    and SQLAlchemy queries line up.
  # ---------------------------------------------------------------------------
  op.execute("ALTER TYPE applicationstatusenum RENAME TO enrolleeapplicationstatusenum")

  # ---------------------------------------------------------------------------
  # 1. Enrollee: append INTERVIEW_* status values to the renamed
  #    enrolleeapplicationstatusenum type. Existing values:
  #    REGISTERED, PENDING_ACTIVATION, PROFILE_COMPLETE,
  #    EXAM_PENDING, EXAM_FAILED, EXAM_PASSED,
  #    APPROVED, ENROLLED, REJECTED
  # ---------------------------------------------------------------------------
  for new_status in (
    "INTERVIEW_PENDING",
    "INTERVIEW_FAILED",
    "INTERVIEW_PASSED",
  ):
    op.execute(
      f"ALTER TYPE enrolleeapplicationstatusenum ADD VALUE IF NOT EXISTS '{new_status}'"
    )

  # ---------------------------------------------------------------------------
  # 2. Explicitly create the new Postgres enum types needed by both enrollee
  #    and interview tables. Postgres lacks CREATE TYPE ... IF NOT EXISTS so
  #    we wrap each in a safe PL/pgSQL block that swallows the "already
  #    exists" error. Column definitions later use create_constraint=False so
  #    SQLAlchemy does NOT re-emit a bare CREATE TYPE per column.
  # ---------------------------------------------------------------------------
  _create_postgres_enum_safely(
    "interviewstatusenum",
    ("DRAFT", "ACTIVE", "ARCHIVED"),
  )
  _create_postgres_enum_safely(
    "interviewsessionstatusenum",
    ("SCHEDULED", "IN_PROGRESS", "COMPLETED", "GRADED", "CANCELLED"),
  )
  _create_postgres_enum_safely(
    "interviewquestiontypeenum",
    ("MCQ", "SHORT_ANSWER", "RATING_SCALE"),
  )
  _create_postgres_enum_safely(
    "latestinterviewstatusenum",
    (
      "NOT_SCHEDULED",
      "SCHEDULED",
      "IN_PROGRESS",
      "COMPLETED",
      "GRADED",
      "CANCELLED",
    ),
  )

  # Construct Postgres ENUM type REFERENCEs (create_type=False ensures SA does
  # NOT emit duplicate CREATE TYPE DDL for each column we attach these to).
  _INTERVIEW_STATUS_VALUES: tuple[str, ...] = ("DRAFT", "ACTIVE", "ARCHIVED")
  _INTERVIEW_SESSION_STATUS_VALUES: tuple[str, ...] = (
    "SCHEDULED",
    "IN_PROGRESS",
    "COMPLETED",
    "GRADED",
    "CANCELLED",
  )
  _INTERVIEW_QUESTION_TYPE_VALUES: tuple[str, ...] = (
    "MCQ",
    "SHORT_ANSWER",
    "RATING_SCALE",
  )
  _LATEST_INTERVIEW_STATUS_VALUES: tuple[str, ...] = (
    "NOT_SCHEDULED",
    "SCHEDULED",
    "IN_PROGRESS",
    "COMPLETED",
    "GRADED",
    "CANCELLED",
  )
  interview_status_enum = _postgres_enum_type_ref(
    "interviewstatusenum",
    _INTERVIEW_STATUS_VALUES,
  )
  interview_session_status_enum = _postgres_enum_type_ref(
    "interviewsessionstatusenum",
    _INTERVIEW_SESSION_STATUS_VALUES,
  )
  interview_question_type_enum = _postgres_enum_type_ref(
    "interviewquestiontypeenum",
    _INTERVIEW_QUESTION_TYPE_VALUES,
  )
  latest_interview_status_enum = _postgres_enum_type_ref(
    "latestinterviewstatusenum",
    _LATEST_INTERVIEW_STATUS_VALUES,
  )

  # ---------------------------------------------------------------------------
  # 3. Enrollee: 5 new interview-gate columns (mirrors exam pattern)
  # ---------------------------------------------------------------------------
  op.add_column(
    "enrollees",
    sa.Column("interview_link_uuid", sa.String(), nullable=True),
  )
  op.add_column(
    "enrollees",
    sa.Column("interview_link_expires_at", sa.DateTime(), nullable=True),
  )
  op.add_column(
    "enrollees",
    sa.Column(
      "latest_interview_status",
      latest_interview_status_enum,
      nullable=True,
    ),
  )
  op.add_column(
    "enrollees",
    sa.Column("interview_score", sa.Float(), nullable=True),
  )
  op.add_column(
    "enrollees",
    sa.Column("interview_pass_score", sa.Float(), nullable=True),
  )
  op.create_unique_constraint(
    "uq_enrollees_interview_link_uuid",
    "enrollees",
    ["interview_link_uuid"],
  )

  # ---------------------------------------------------------------------------
  # 4. Backfill: fix pre-existing gaps on existing exam tables.
  #    - Add the missing `deleted_at` column (BaseTable declares it but the
  #      original 2026-09-02 09:45 `create_exam_tables` migration omitted it).
  #    - Attach `server_default = now()` to `created_at` / `updated_at`. The
  #      ORM's BaseTable declares these as server_default=func.now(), so the
  #      ORM deliberately omits them from INSERT projections and expects the
  #      DB to populate them. Without the server-side default, inserts fail
  #      with a NotNullViolation.
  # ---------------------------------------------------------------------------
  for table_name in (
    "exams",
    "exam_questions",
    "exam_options",
    "exam_attempts",
    "exam_answers",
  ):
    op.add_column(
      table_name,
      sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.alter_column(
      table_name,
      "created_at",
      existing_type=sa.DateTime(),
      server_default=sa.text("now()"),
      existing_nullable=False,
    )
    op.alter_column(
      table_name,
      "updated_at",
      existing_type=sa.DateTime(),
      server_default=sa.text("now()"),
      existing_nullable=False,
    )

  # ---------------------------------------------------------------------------
  # 5. interview_templates  (root table; analogous to exams)
  # ---------------------------------------------------------------------------
  op.create_table(
    "interview_templates",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column(
      "created_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column(
      "updated_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    sa.Column("uuid", sa.String(), nullable=False),
    sa.Column("title", sa.String(length=200), nullable=False),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("course_code", sa.String(length=50), nullable=True),
    sa.Column("duration_minutes", sa.Integer(), nullable=False),
    sa.Column("pass_score", sa.Float(), nullable=False),
    sa.Column("status", interview_status_enum, nullable=False),
    sa.Column("created_by", sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(
      ["created_by"],
      ["employees.id"],
      name="fk_interview_templates_created_by_employee",
      ondelete="SET NULL",
    ),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("uuid", name="uq_interview_templates_uuid"),
  )

  # ---------------------------------------------------------------------------
  # 6. interview_questions  (child of interview_templates)
  # ---------------------------------------------------------------------------
  op.create_table(
    "interview_questions",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column(
      "created_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column(
      "updated_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    sa.Column("interview_id", sa.Integer(), nullable=False),
    sa.Column("question_text", sa.Text(), nullable=False),
    sa.Column(
      "question_type",
      interview_question_type_enum,
      nullable=False,
    ),
    sa.Column("points", sa.Integer(), nullable=False),
    sa.Column("order_index", sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
      ["interview_id"],
      ["interview_templates.id"],
      name="fk_interview_questions_interview_id",
      ondelete="CASCADE",
    ),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_index(
    "ix_interview_questions_interview_id",
    "interview_questions",
    ["interview_id"],
    unique=False,
  )

  # ---------------------------------------------------------------------------
  # 7. interview_options  (child of interview_questions)
  # ---------------------------------------------------------------------------
  op.create_table(
    "interview_options",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column(
      "created_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column(
      "updated_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
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
      ["interview_questions.id"],
      name="fk_interview_options_question_id",
      ondelete="CASCADE",
    ),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_index(
    "ix_interview_options_question_id",
    "interview_options",
    ["question_id"],
    unique=False,
  )

  # ---------------------------------------------------------------------------
  # 8. interview_sessions  (enrollee + template join; analogous to exam_attempts)
  # ---------------------------------------------------------------------------
  op.create_table(
    "interview_sessions",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column(
      "created_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column(
      "updated_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    sa.Column("uuid", sa.String(), nullable=False),
    sa.Column("enrollee_id", sa.Integer(), nullable=False),
    sa.Column("interview_id", sa.Integer(), nullable=False),
    sa.Column(
      "status",
      interview_session_status_enum,
      nullable=False,
    ),
    sa.Column("pass_score_snapshot", sa.Float(), nullable=True),
    sa.Column("scheduled_at", sa.DateTime(), nullable=True),
    sa.Column("started_at", sa.DateTime(), nullable=True),
    sa.Column("completed_at", sa.DateTime(), nullable=True),
    sa.Column("score", sa.Float(), nullable=True),
    sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
    sa.Column("conducted_by", sa.Integer(), nullable=True),
    sa.Column("notes", sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(
      ["enrollee_id"],
      ["enrollees.id"],
      name="fk_interview_sessions_enrollee_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["interview_id"],
      ["interview_templates.id"],
      name="fk_interview_sessions_interview_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["conducted_by"],
      ["employees.id"],
      name="fk_interview_sessions_conducted_by_employee",
      ondelete="SET NULL",
    ),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("uuid", name="uq_interview_sessions_uuid"),
  )
  op.create_index(
    "ix_interview_sessions_enrollee_id",
    "interview_sessions",
    ["enrollee_id"],
    unique=False,
  )
  op.create_index(
    "ix_interview_sessions_interview_id",
    "interview_sessions",
    ["interview_id"],
    unique=False,
  )

  # ---------------------------------------------------------------------------
  # 9. interview_answers  (child of session + question; analogous to exam_answers)
  # ---------------------------------------------------------------------------
  op.create_table(
    "interview_answers",
    sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
    sa.Column(
      "created_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column(
      "updated_at",
      sa.DateTime(),
      server_default=sa.text("now()"),
      nullable=False,
    ),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    sa.Column("session_id", sa.Integer(), nullable=False),
    sa.Column("question_id", sa.Integer(), nullable=False),
    sa.Column("selected_option_id", sa.Integer(), nullable=True),
    sa.Column("text_answer", sa.Text(), nullable=True),
    sa.Column("rating_value", sa.Integer(), nullable=True),
    sa.Column("is_correct", sa.Boolean(), nullable=True),
    sa.Column("points_awarded", sa.Float(), nullable=True),
    sa.Column("rater_note", sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(
      ["session_id"],
      ["interview_sessions.id"],
      name="fk_interview_answers_session_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["question_id"],
      ["interview_questions.id"],
      name="fk_interview_answers_question_id",
      ondelete="CASCADE",
    ),
    sa.ForeignKeyConstraint(
      ["selected_option_id"],
      ["interview_options.id"],
      name="fk_interview_answers_selected_option_id",
      ondelete="SET NULL",
    ),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_index(
    "ix_interview_answers_session_id",
    "interview_answers",
    ["session_id"],
    unique=False,
  )
  op.create_index(
    "ix_interview_answers_question_id",
    "interview_answers",
    ["question_id"],
    unique=False,
  )


def downgrade() -> None:
  # Drop tables in reverse-dependency order (children before parents)
  op.drop_index(
    "ix_interview_answers_question_id",
    table_name="interview_answers",
  )
  op.drop_index(
    "ix_interview_answers_session_id",
    table_name="interview_answers",
  )
  op.drop_table("interview_answers")

  op.drop_index(
    "ix_interview_sessions_interview_id",
    table_name="interview_sessions",
  )
  op.drop_index(
    "ix_interview_sessions_enrollee_id",
    table_name="interview_sessions",
  )
  op.drop_table("interview_sessions")

  op.drop_index(
    "ix_interview_options_question_id",
    table_name="interview_options",
  )
  op.drop_table("interview_options")

  op.drop_index(
    "ix_interview_questions_interview_id",
    table_name="interview_questions",
  )
  op.drop_table("interview_questions")

  op.drop_table("interview_templates")

  # Drop enrollee columns + unique constraint
  op.drop_constraint(
    "uq_enrollees_interview_link_uuid",
    "enrollees",
    type_="unique",
  )
  op.drop_column("enrollees", "interview_pass_score")
  op.drop_column("enrollees", "interview_score")
  op.drop_column("enrollees", "latest_interview_status")
  op.drop_column("enrollees", "interview_link_expires_at")
  op.drop_column("enrollees", "interview_link_uuid")

  # Drop the backfilled deleted_at columns on existing exam tables AND
  # revert the created_at / updated_at server_default we attached so a
  # downgrade restores the pre-migration schema exactly.
  for table_name in (
    "exam_answers",
    "exam_attempts",
    "exam_options",
    "exam_questions",
    "exams",
  ):
    op.drop_column(table_name, "deleted_at")
    op.alter_column(
      table_name,
      "created_at",
      existing_type=sa.DateTime(),
      server_default=None,
      existing_nullable=False,
    )
    op.alter_column(
      table_name,
      "updated_at",
      existing_type=sa.DateTime(),
      server_default=None,
      existing_nullable=False,
    )

  # Postgres enum types are not dropped when their referencing tables are.
  # Drop them explicitly so a downgrade leaves the schema clean and a
  # subsequent upgrade doesn't fail with "type already exists".
  # Dropping in reverse order of dependency is safest (innermost → outermost).
  for enum_name in (
    "interviewsessionstatusenum",
    "interviewquestiontypeenum",
    "interviewstatusenum",
    "latestinterviewstatusenum",
  ):
    op.execute(f'DROP TYPE IF EXISTS "{enum_name}"')

  # Reverse the rename of applicationstatusenum → enrolleeapplicationstatusenum
  # so the previous migration's expected type name is restored. We intentionally
  # do NOT remove the appended INTERVIEW_* labels from the type (Postgres has
  # no safe ALTER TYPE DROP VALUE); they are harmless as unused variants.
  op.execute("ALTER TYPE enrolleeapplicationstatusenum RENAME TO applicationstatusenum")
