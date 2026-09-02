from __future__ import annotations

from datetime import datetime

from app.database import DatabaseDep

from .table import (
  ExamAnswerTable,
  ExamAttemptTable,
  ExamOptionTable,
  ExamQuestionTable,
  ExamTable,
)
from .validation import (
  CreateExam,
  CreateExamQuestion,
  ExamAnswerSubmission,
  SubmitExamAttempt,
  UpdateExam,
)


class ExamRepository:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = ExamTable

  # ---------- Exam CRUD ----------

  def create(self, data: CreateExam) -> ExamTable:
    """Create an exam with its nested questions and options."""

    exam_data = data.model_dump(exclude={"questions"})
    exam = self.model(**exam_data)

    for q_data in data.questions:
      question = self._build_question(q_data)
      exam.questions.append(question)

    self.db.add(exam)
    self.db.flush()
    self.db.refresh(exam)
    return exam

  def get_by_uuid(self, uuid: str) -> ExamTable | None:
    return self.db.query(self.model).filter(self.model.uuid == uuid).first()

  def get_by_id(self, exam_id: int) -> ExamTable | None:
    return self.db.query(self.model).filter(self.model.id == exam_id).first()

  def list_active(self) -> list[ExamTable]:
    from .validation import ExamStatusEnum

    return (
      self.db.query(self.model)
      .filter(self.model.status == ExamStatusEnum.ACTIVE)
      .order_by(self.model.created_at.desc())
      .all()
    )

  def update(self, exam: ExamTable, data: UpdateExam) -> ExamTable:
    updated = data.model_dump(exclude_unset=True, exclude={"questions"})

    for key, value in updated.items():
      setattr(exam, key, value)

    if data.questions is not None:
      exam.questions.clear()
      for q_data in data.questions:
        question = self._build_question(q_data)
        exam.questions.append(question)

    self.db.add(exam)
    self.db.flush()
    self.db.refresh(exam)
    return exam

  @staticmethod
  def _build_question(q_data: CreateExamQuestion) -> ExamQuestionTable:
    question_data = q_data.model_dump(exclude={"options"})
    question = ExamQuestionTable(**question_data)

    for opt_data in q_data.options:
      option = ExamOptionTable(**opt_data.model_dump())
      question.options.append(option)

    return question

  # ---------- Exam Attempt ----------

  def create_attempt(
    self,
    enrollee_id: int,
    exam_id: int,
    pass_score_snapshot: float,
  ) -> ExamAttemptTable:
    attempt = ExamAttemptTable(
      enrollee_id=enrollee_id,
      exam_id=exam_id,
      pass_score_snapshot=pass_score_snapshot,
    )
    self.db.add(attempt)
    self.db.flush()
    self.db.refresh(attempt)
    return attempt

  def get_attempt_by_uuid(self, uuid: str) -> ExamAttemptTable | None:
    return self.db.query(ExamAttemptTable).filter(ExamAttemptTable.uuid == uuid).first()

  def get_active_attempt_for_enrollee(
    self, enrollee_id: int, exam_id: int
  ) -> ExamAttemptTable | None:
    from .validation import ExamAttemptStatusEnum

    terminal = {
      ExamAttemptStatusEnum.SUBMITTED,
      ExamAttemptStatusEnum.GRADED,
    }
    return (
      self.db.query(ExamAttemptTable)
      .filter(
        ExamAttemptTable.enrollee_id == enrollee_id,
        ExamAttemptTable.exam_id == exam_id,
        ~ExamAttemptTable.status.in_(terminal),
      )
      .first()
    )

  def start_attempt(self, attempt: ExamAttemptTable) -> ExamAttemptTable:
    from .validation import ExamAttemptStatusEnum

    attempt.status = ExamAttemptStatusEnum.IN_PROGRESS
    attempt.started_at = datetime.utcnow()
    self.db.add(attempt)
    self.db.flush()
    self.db.refresh(attempt)
    return attempt

  def submit_attempt(
    self,
    attempt: ExamAttemptTable,
    payload: SubmitExamAttempt,
  ) -> ExamAttemptTable:
    from .validation import ExamAttemptStatusEnum

    attempt.status = ExamAttemptStatusEnum.SUBMITTED
    attempt.submitted_at = datetime.utcnow()
    if attempt.started_at is not None:
      delta = attempt.submitted_at - attempt.started_at
      attempt.time_spent_seconds = int(delta.total_seconds())

    self._apply_answers(attempt, payload)
    self._grade_attempt(attempt)

    attempt.status = ExamAttemptStatusEnum.GRADED
    self.db.add(attempt)
    self.db.flush()
    self.db.refresh(attempt)
    return attempt

  def _apply_answers(
    self, attempt: ExamAttemptTable, payload: SubmitExamAttempt
  ) -> None:
    """Apply submitted answers to an attempt, clearing any previous ones."""

    attempt.answers.clear()
    by_qid = {a.question_id: a for a in payload.answers}

    for question in attempt.exam.questions:
      submission = by_qid.get(question.id)
      self._build_answer(attempt, question, submission)

  @staticmethod
  def _build_answer(
    attempt: ExamAttemptTable,
    question: ExamQuestionTable,
    submission: ExamAnswerSubmission | None,
  ) -> ExamAnswerTable:
    answer = ExamAnswerTable(
      attempt_id=attempt.id,
      question_id=question.id,
    )
    if submission is not None:
      answer.selected_option_id = submission.selected_option_id
      answer.text_answer = submission.text_answer
    attempt.answers.append(answer)
    return answer

  def _grade_attempt(self, attempt: ExamAttemptTable) -> None:
    """Auto-grade MCQ and TRUE_FALSE answers; leave SHORT_ANSWER as None correct."""

    total_awarded = 0.0
    total_possible = 0.0

    for answer in attempt.answers:
      question = next(
        (q for q in attempt.exam.questions if q.id == answer.question_id),
        None,
      )
      if question is None:
        continue

      total_possible += float(question.points)
      correct, awarded = self._grade_single(answer, question)
      if correct is not None:
        answer.is_correct = correct
        answer.points_awarded = awarded
        total_awarded += awarded or 0.0

    if total_possible > 0:
      attempt.score = round(total_awarded, 2)
    else:
      attempt.score = 0.0

  @staticmethod
  def _grade_single(
    answer: ExamAnswerTable, question: ExamQuestionTable
  ) -> tuple[bool | None, float | None]:
    from .validation import QuestionTypeEnum

    if question.question_type in {QuestionTypeEnum.MCQ, QuestionTypeEnum.TRUE_FALSE}:
      correct_options = {opt.id for opt in question.options if opt.is_correct}
      selected = answer.selected_option_id
      is_correct = (
        selected is not None
        and selected in correct_options
        and len(correct_options) == 1
      )
      awarded = float(question.points) if is_correct else 0.0
      return is_correct, awarded

    return None, None

  # ---------- Query helpers ----------

  def count_questions(self, exam_id: int) -> int:
    return (
      self.db.query(ExamQuestionTable)
      .filter(ExamQuestionTable.exam_id == exam_id)
      .count()
    )
