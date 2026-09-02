from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
  Boolean,
  DateTime,
  Enum,
  Float,
  ForeignKey,
  Integer,
  String,
  Text,
  false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import BaseTable

from .validation import (
  InterviewQuestionTypeEnum,
  InterviewSessionStatusEnum,
  InterviewStatusEnum,
)


class InterviewTemplateTable(BaseTable):
  __tablename__ = "interview_templates"

  uuid: Mapped[str] = mapped_column(
    String,
    default=lambda: str(uuid4()),
    unique=True,
  )
  title: Mapped[str] = mapped_column(String(200))
  description: Mapped[str | None] = mapped_column(Text, default=None)
  course_code: Mapped[str | None] = mapped_column(String(50), default=None)
  duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
  pass_score: Mapped[float] = mapped_column(Float, default=50.0)
  status: Mapped[InterviewStatusEnum] = mapped_column(
    Enum(InterviewStatusEnum),
    default=InterviewStatusEnum.ACTIVE,
  )
  created_by: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("employees.id", ondelete="SET NULL"),
    default=None,
  )

  questions: Mapped[list[InterviewQuestionTable]] = relationship(
    "InterviewQuestionTable",
    back_populates="interview",
    cascade="all, delete-orphan",
    order_by="InterviewQuestionTable.order_index.asc()",
  )
  sessions: Mapped[list[InterviewSessionTable]] = relationship(
    "InterviewSessionTable",
    back_populates="interview",
    cascade="all, delete-orphan",
  )


class InterviewQuestionTable(BaseTable):
  __tablename__ = "interview_questions"

  interview_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("interview_templates.id", ondelete="CASCADE"),
  )
  question_text: Mapped[str] = mapped_column(Text)
  question_type: Mapped[InterviewQuestionTypeEnum] = mapped_column(
    Enum(InterviewQuestionTypeEnum),
    default=InterviewQuestionTypeEnum.MCQ,
  )
  points: Mapped[int] = mapped_column(Integer, default=1)
  order_index: Mapped[int] = mapped_column(Integer, default=0)

  interview: Mapped[InterviewTemplateTable] = relationship(
    "InterviewTemplateTable",
    back_populates="questions",
  )
  options: Mapped[list[InterviewOptionTable]] = relationship(
    "InterviewOptionTable",
    back_populates="question",
    cascade="all, delete-orphan",
  )
  answers: Mapped[list[InterviewAnswerTable]] = relationship(
    "InterviewAnswerTable",
    back_populates="question",
    cascade="all, delete-orphan",
  )


class InterviewOptionTable(BaseTable):
  __tablename__ = "interview_options"

  question_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("interview_questions.id", ondelete="CASCADE"),
  )
  option_text: Mapped[str] = mapped_column(String(500))
  is_correct: Mapped[bool] = mapped_column(Boolean, server_default=false())

  question: Mapped[InterviewQuestionTable] = relationship(
    "InterviewQuestionTable",
    back_populates="options",
  )


class InterviewSessionTable(BaseTable):
  __tablename__ = "interview_sessions"

  uuid: Mapped[str] = mapped_column(
    String,
    default=lambda: str(uuid4()),
    unique=True,
  )
  enrollee_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("enrollees.id", ondelete="CASCADE"),
  )
  interview_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("interview_templates.id", ondelete="CASCADE"),
  )
  status: Mapped[InterviewSessionStatusEnum] = mapped_column(
    Enum(InterviewSessionStatusEnum),
    default=InterviewSessionStatusEnum.SCHEDULED,
  )
  pass_score_snapshot: Mapped[float | None] = mapped_column(Float, default=None)
  scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
  completed_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
  score: Mapped[float | None] = mapped_column(Float, default=None)
  time_spent_seconds: Mapped[int | None] = mapped_column(Integer, default=None)
  conducted_by: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("employees.id", ondelete="SET NULL"),
    default=None,
  )
  notes: Mapped[str | None] = mapped_column(Text, default=None)

  interview: Mapped[InterviewTemplateTable] = relationship(
    "InterviewTemplateTable",
    back_populates="sessions",
  )
  answers: Mapped[list[InterviewAnswerTable]] = relationship(
    "InterviewAnswerTable",
    back_populates="session",
    cascade="all, delete-orphan",
  )


class InterviewAnswerTable(BaseTable):
  __tablename__ = "interview_answers"

  session_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("interview_sessions.id", ondelete="CASCADE"),
  )
  question_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("interview_questions.id", ondelete="CASCADE"),
  )
  selected_option_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("interview_options.id", ondelete="SET NULL"),
    default=None,
  )
  text_answer: Mapped[str | None] = mapped_column(Text, default=None)
  rating_value: Mapped[int | None] = mapped_column(Integer, default=None)
  is_correct: Mapped[bool | None] = mapped_column(Boolean, default=None)
  points_awarded: Mapped[float | None] = mapped_column(Float, default=None)
  rater_note: Mapped[str | None] = mapped_column(Text, default=None)

  session: Mapped[InterviewSessionTable] = relationship(
    "InterviewSessionTable",
    back_populates="answers",
  )
  question: Mapped[InterviewQuestionTable] = relationship(
    "InterviewQuestionTable",
    back_populates="answers",
  )
