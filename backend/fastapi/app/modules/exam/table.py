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
  ExamAttemptStatusEnum,
  ExamStatusEnum,
  QuestionTypeEnum,
)


class ExamTable(BaseTable):
  __tablename__ = "exams"

  uuid: Mapped[str] = mapped_column(
    String,
    default=lambda: str(uuid4()),
    unique=True,
  )
  title: Mapped[str] = mapped_column(String(200))
  description: Mapped[str | None] = mapped_column(Text, default=None)
  course_code: Mapped[str | None] = mapped_column(String(50), default=None)
  duration_minutes: Mapped[int] = mapped_column(Integer, default=120)
  pass_score: Mapped[float] = mapped_column(Float, default=50.0)
  status: Mapped[ExamStatusEnum] = mapped_column(
    Enum(ExamStatusEnum),
    default=ExamStatusEnum.ACTIVE,
  )
  created_by: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("employees.id", ondelete="SET NULL"),
    default=None,
  )

  questions: Mapped[list[ExamQuestionTable]] = relationship(
    "ExamQuestionTable",
    back_populates="exam",
    cascade="all, delete-orphan",
    order_by="ExamQuestionTable.order_index.asc()",
  )
  attempts: Mapped[list[ExamAttemptTable]] = relationship(
    "ExamAttemptTable",
    back_populates="exam",
    cascade="all, delete-orphan",
  )


class ExamQuestionTable(BaseTable):
  __tablename__ = "exam_questions"

  exam_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("exams.id", ondelete="CASCADE"),
  )
  question_text: Mapped[str] = mapped_column(Text)
  question_type: Mapped[QuestionTypeEnum] = mapped_column(
    Enum(QuestionTypeEnum),
    default=QuestionTypeEnum.MCQ,
  )
  points: Mapped[int] = mapped_column(Integer, default=1)
  order_index: Mapped[int] = mapped_column(Integer, default=0)

  exam: Mapped[ExamTable] = relationship("ExamTable", back_populates="questions")
  options: Mapped[list[ExamOptionTable]] = relationship(
    "ExamOptionTable",
    back_populates="question",
    cascade="all, delete-orphan",
  )
  answers: Mapped[list[ExamAnswerTable]] = relationship(
    "ExamAnswerTable",
    back_populates="question",
    cascade="all, delete-orphan",
  )


class ExamOptionTable(BaseTable):
  __tablename__ = "exam_options"

  question_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("exam_questions.id", ondelete="CASCADE"),
  )
  option_text: Mapped[str] = mapped_column(String(500))
  is_correct: Mapped[bool] = mapped_column(Boolean, server_default=false())

  question: Mapped[ExamQuestionTable] = relationship(
    "ExamQuestionTable",
    back_populates="options",
  )


class ExamAttemptTable(BaseTable):
  __tablename__ = "exam_attempts"

  uuid: Mapped[str] = mapped_column(
    String,
    default=lambda: str(uuid4()),
    unique=True,
  )
  enrollee_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("enrollees.id", ondelete="CASCADE"),
  )
  exam_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("exams.id", ondelete="CASCADE"),
  )
  status: Mapped[ExamAttemptStatusEnum] = mapped_column(
    Enum(ExamAttemptStatusEnum),
    default=ExamAttemptStatusEnum.ASSIGNED,
  )
  pass_score_snapshot: Mapped[float | None] = mapped_column(Float, default=None)
  started_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
  submitted_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
  score: Mapped[float | None] = mapped_column(Float, default=None)
  time_spent_seconds: Mapped[int | None] = mapped_column(Integer, default=None)

  exam: Mapped[ExamTable] = relationship("ExamTable", back_populates="attempts")
  answers: Mapped[list[ExamAnswerTable]] = relationship(
    "ExamAnswerTable",
    back_populates="attempt",
    cascade="all, delete-orphan",
  )


class ExamAnswerTable(BaseTable):
  __tablename__ = "exam_answers"

  attempt_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("exam_attempts.id", ondelete="CASCADE"),
  )
  question_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("exam_questions.id", ondelete="CASCADE"),
  )
  selected_option_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("exam_options.id", ondelete="SET NULL"),
    default=None,
  )
  text_answer: Mapped[str | None] = mapped_column(Text, default=None)
  is_correct: Mapped[bool | None] = mapped_column(Boolean, default=None)
  points_awarded: Mapped[float | None] = mapped_column(Float, default=None)

  attempt: Mapped[ExamAttemptTable] = relationship(
    "ExamAttemptTable",
    back_populates="answers",
  )
  question: Mapped[ExamQuestionTable] = relationship(
    "ExamQuestionTable",
    back_populates="answers",
  )
