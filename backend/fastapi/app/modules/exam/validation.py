from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionTypeEnum(StrEnum):
  MCQ = "MCQ"
  TRUE_FALSE = "TRUE_FALSE"
  SHORT_ANSWER = "SHORT_ANSWER"


class ExamStatusEnum(StrEnum):
  DRAFT = "DRAFT"
  ACTIVE = "ACTIVE"
  ARCHIVED = "ARCHIVED"


class ExamAttemptStatusEnum(StrEnum):
  ASSIGNED = "ASSIGNED"
  IN_PROGRESS = "IN_PROGRESS"
  SUBMITTED = "SUBMITTED"
  GRADED = "GRADED"


class ExamOptionBase(BaseModel):
  option_text: str = Field(..., min_length=1, max_length=500)
  is_correct: bool = False

  model_config = {"from_attributes": True}


class CreateExamOption(ExamOptionBase):
  pass


class UpdateExamOption(BaseModel):
  option_text: str | None = Field(default=None, min_length=1, max_length=500)
  is_correct: bool | None = None

  model_config = {"from_attributes": True}


class ExamOptionResponse(ExamOptionBase):
  id: int
  question_id: int


class ExamQuestionBase(BaseModel):
  question_text: str = Field(..., min_length=1, max_length=2000)
  question_type: QuestionTypeEnum = QuestionTypeEnum.MCQ
  points: int = Field(default=1, ge=1)
  order_index: int = Field(default=0, ge=0)

  model_config = {"from_attributes": True}


class CreateExamQuestion(ExamQuestionBase):
  options: list[CreateExamOption] = Field(default_factory=list)


class UpdateExamQuestion(BaseModel):
  question_text: str | None = Field(default=None, min_length=1, max_length=2000)
  question_type: QuestionTypeEnum | None = None
  points: int | None = Field(default=None, ge=1)
  order_index: int | None = Field(default=None, ge=0)
  options: list[UpdateExamOption] | None = None

  model_config = {"from_attributes": True}


class ExamQuestionResponse(ExamQuestionBase):
  id: int
  exam_id: int
  options: list[ExamOptionResponse] = Field(default_factory=list)


class ExamBase(BaseModel):
  title: str = Field(..., min_length=2, max_length=200)
  description: str | None = Field(default=None, max_length=2000)
  course_code: str | None = Field(default=None, max_length=50)
  duration_minutes: int = Field(default=120, ge=1, le=720)
  pass_score: float = Field(default=50.0, ge=0.0, le=100.0)
  status: ExamStatusEnum = ExamStatusEnum.ACTIVE

  model_config = {"from_attributes": True}


class CreateExam(ExamBase):
  questions: list[CreateExamQuestion] = Field(default_factory=list)
  created_by: int | None = None


class UpdateExam(BaseModel):
  title: str | None = Field(default=None, min_length=2, max_length=200)
  description: str | None = Field(default=None, max_length=2000)
  course_code: str | None = Field(default=None, max_length=50)
  duration_minutes: int | None = Field(default=None, ge=1, le=720)
  pass_score: float | None = Field(default=None, ge=0.0, le=100.0)
  status: ExamStatusEnum | None = None
  questions: list[CreateExamQuestion] | None = None

  model_config = {"from_attributes": True}


class ExamResponse(ExamBase):
  id: int
  uuid: UUID
  created_by: int | None = None
  created_at: datetime
  updated_at: datetime
  questions: list[ExamQuestionResponse] = Field(default_factory=list)


class ExamListItemResponse(ExamBase):
  id: int
  uuid: UUID
  created_by: int | None = None
  created_at: datetime
  updated_at: datetime
  question_count: int = 0


class ExamAnswerSubmission(BaseModel):
  question_id: int
  selected_option_id: int | None = None
  text_answer: str | None = Field(default=None, max_length=1000)


class SubmitExamAttempt(BaseModel):
  answers: list[ExamAnswerSubmission] = Field(default_factory=list)


class ExamAnswerResponse(BaseModel):
  id: int
  attempt_id: int
  question_id: int
  selected_option_id: int | None = None
  text_answer: str | None = None
  is_correct: bool | None = None
  points_awarded: float | None = None

  model_config = {"from_attributes": True}


class ExamAttemptBase(BaseModel):
  status: ExamAttemptStatusEnum = ExamAttemptStatusEnum.ASSIGNED
  pass_score_snapshot: float | None = None

  model_config = {"from_attributes": True}


class ExamAttemptResponse(ExamAttemptBase):
  id: int
  uuid: UUID
  enrollee_id: int
  exam_id: int
  started_at: datetime | None = None
  submitted_at: datetime | None = None
  score: float | None = None
  time_spent_seconds: int | None = None
  answers: list[ExamAnswerResponse] = Field(default_factory=list)


class AssignExamRequest(BaseModel):
  enrollee_uuid: UUID
  exam_uuid: UUID
  expires_in_hours: int = Field(default=72, ge=1, le=24 * 30)
  by_employee_id: int | None = None


class GradedExamAttemptResponse(ExamAttemptResponse):
  total_points_possible: float = 0.0
  percentage: float | None = None
  passed: bool | None = None
