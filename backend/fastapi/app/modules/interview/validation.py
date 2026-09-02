from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class InterviewStatusEnum(StrEnum):
  DRAFT = "DRAFT"
  ACTIVE = "ACTIVE"
  ARCHIVED = "ARCHIVED"


class InterviewSessionStatusEnum(StrEnum):
  SCHEDULED = "SCHEDULED"
  IN_PROGRESS = "IN_PROGRESS"
  COMPLETED = "COMPLETED"
  GRADED = "GRADED"
  CANCELLED = "CANCELLED"


class InterviewQuestionTypeEnum(StrEnum):
  MCQ = "MCQ"
  SHORT_ANSWER = "SHORT_ANSWER"
  RATING_SCALE = "RATING_SCALE"


class InterviewOptionBase(BaseModel):
  option_text: str = Field(..., min_length=1, max_length=500)
  is_correct: bool = False

  model_config = {"from_attributes": True}


class CreateInterviewOption(InterviewOptionBase):
  pass


class UpdateInterviewOption(BaseModel):
  option_text: str | None = Field(default=None, min_length=1, max_length=500)
  is_correct: bool | None = None

  model_config = {"from_attributes": True}


class InterviewOptionResponse(InterviewOptionBase):
  id: int
  question_id: int


class InterviewQuestionBase(BaseModel):
  question_text: str = Field(..., min_length=1, max_length=2000)
  question_type: InterviewQuestionTypeEnum = InterviewQuestionTypeEnum.MCQ
  points: int = Field(default=1, ge=1)
  order_index: int = Field(default=0, ge=0)

  model_config = {"from_attributes": True}


class CreateInterviewQuestion(InterviewQuestionBase):
  options: list[CreateInterviewOption] = Field(default_factory=list)


class UpdateInterviewQuestion(BaseModel):
  question_text: str | None = Field(default=None, min_length=1, max_length=2000)
  question_type: InterviewQuestionTypeEnum | None = None
  points: int | None = Field(default=None, ge=1)
  order_index: int | None = Field(default=None, ge=0)
  options: list[UpdateInterviewOption] | None = None

  model_config = {"from_attributes": True}


class InterviewQuestionResponse(InterviewQuestionBase):
  id: int
  interview_id: int
  options: list[InterviewOptionResponse] = Field(default_factory=list)


class InterviewBase(BaseModel):
  title: str = Field(..., min_length=2, max_length=200)
  description: str | None = Field(default=None, max_length=2000)
  course_code: str | None = Field(default=None, max_length=50)
  duration_minutes: int = Field(default=30, ge=1, le=480)
  pass_score: float = Field(default=50.0, ge=0.0, le=100.0)
  status: InterviewStatusEnum = InterviewStatusEnum.ACTIVE

  model_config = {"from_attributes": True}


class CreateInterview(InterviewBase):
  questions: list[CreateInterviewQuestion] = Field(default_factory=list)
  created_by: int | None = None


class UpdateInterview(BaseModel):
  title: str | None = Field(default=None, min_length=2, max_length=200)
  description: str | None = Field(default=None, max_length=2000)
  course_code: str | None = Field(default=None, max_length=50)
  duration_minutes: int | None = Field(default=None, ge=1, le=480)
  pass_score: float | None = Field(default=None, ge=0.0, le=100.0)
  status: InterviewStatusEnum | None = None
  questions: list[CreateInterviewQuestion] | None = None

  model_config = {"from_attributes": True}


class InterviewResponse(InterviewBase):
  id: int
  uuid: UUID
  created_by: int | None = None
  created_at: datetime
  updated_at: datetime
  questions: list[InterviewQuestionResponse] = Field(default_factory=list)


class InterviewListItemResponse(InterviewBase):
  id: int
  uuid: UUID
  created_by: int | None = None
  created_at: datetime
  updated_at: datetime
  question_count: int = 0


class InterviewAnswerSubmission(BaseModel):
  question_id: int
  selected_option_id: int | None = None
  text_answer: str | None = Field(default=None, max_length=2000)
  rating_value: int | None = Field(default=None, ge=1, le=10)


class SubmitInterviewSession(BaseModel):
  answers: list[InterviewAnswerSubmission] = Field(default_factory=list)


class InterviewAnswerResponse(BaseModel):
  id: int
  session_id: int
  question_id: int
  selected_option_id: int | None = None
  text_answer: str | None = None
  rating_value: int | None = None
  is_correct: bool | None = None
  points_awarded: float | None = None
  rater_note: str | None = None

  model_config = {"from_attributes": True}


class InterviewSessionBase(BaseModel):
  status: InterviewSessionStatusEnum = InterviewSessionStatusEnum.SCHEDULED
  pass_score_snapshot: float | None = None

  model_config = {"from_attributes": True}


class InterviewSessionResponse(InterviewSessionBase):
  id: int
  uuid: UUID
  enrollee_id: int
  interview_id: int
  scheduled_at: datetime | None = None
  started_at: datetime | None = None
  completed_at: datetime | None = None
  score: float | None = None
  time_spent_seconds: int | None = None
  conducted_by: int | None = None
  notes: str | None = None
  answers: list[InterviewAnswerResponse] = Field(default_factory=list)


class ScheduleInterviewRequest(BaseModel):
  enrollee_id: int
  interview_uuid: UUID
  scheduled_at: datetime | None = Field(
    default=None,
    description="When the interview is scheduled to occur (optional; None = immediate).",
  )
  expires_in_hours: int = Field(
    default=24 * 7,
    ge=1,
    le=24 * 60,
    description="How long the generated session link remains valid (hours).",
  )
  by_employee_id: int | None = Field(
    default=None,
    description="Employee FK of the admin scheduling the interview.",
  )


class AssignInterviewRequest(BaseModel):
  interview_uuid: UUID = Field(
    ...,
    description="UUID of the interview template to schedule.",
  )
  scheduled_at: datetime | None = Field(
    default=None,
    description="When the interview is scheduled to occur (optional; None = immediate).",
  )
  expires_in_hours: int = Field(
    default=24 * 7,
    ge=1,
    le=24 * 60,
    description="How long the generated session link remains valid (hours).",
  )
  by_employee_id: int | None = Field(
    default=None,
    description="Employee FK of the admin scheduling the interview.",
  )


class GradeInterviewAnswer(BaseModel):
  answer_id: int
  is_correct: bool | None = None
  points_awarded: float | None = Field(default=None, ge=0.0)
  rater_note: str | None = Field(default=None, max_length=500)


class GradeInterviewSession(BaseModel):
  conducted_by: int | None = Field(
    default=None,
    description="Employee FK of the rater conducting the interview/rating.",
  )
  notes: str | None = Field(default=None, max_length=1000)
  answer_grades: list[GradeInterviewAnswer] = Field(default_factory=list)
  override_score: float | None = Field(default=None, ge=0.0, le=100.0)


class GradedInterviewSessionResponse(InterviewSessionResponse):
  total_points_possible: float = 0.0
  percentage: float | None = None
  passed: bool | None = None
