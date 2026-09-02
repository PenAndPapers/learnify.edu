from __future__ import annotations

from datetime import datetime

from app.database import DatabaseDep

from .table import (
  InterviewAnswerTable,
  InterviewOptionTable,
  InterviewQuestionTable,
  InterviewSessionTable,
  InterviewTemplateTable,
)
from .validation import (
  CreateInterview,
  CreateInterviewQuestion,
  GradeInterviewAnswer,
  GradeInterviewSession,
  InterviewAnswerSubmission,
  SubmitInterviewSession,
  UpdateInterview,
)


class InterviewRepository:
  def __init__(self, db: DatabaseDep):
    self.db = db
    self.model = InterviewTemplateTable

  # ---------- Interview template CRUD ----------

  def create(self, data: CreateInterview) -> InterviewTemplateTable:
    interview_data = data.model_dump(exclude={"questions"})
    interview = self.model(**interview_data)

    for q_data in data.questions:
      question = self._build_question(q_data)
      interview.questions.append(question)

    self.db.add(interview)
    self.db.flush()
    self.db.refresh(interview)
    return interview

  def get_by_uuid(self, uuid: str) -> InterviewTemplateTable | None:
    return self.db.query(self.model).filter(self.model.uuid == uuid).first()

  def get_by_id(self, interview_id: int) -> InterviewTemplateTable | None:
    return self.db.query(self.model).filter(self.model.id == interview_id).first()

  def list_active(self) -> list[InterviewTemplateTable]:
    from .validation import InterviewStatusEnum

    return (
      self.db.query(self.model)
      .filter(self.model.status == InterviewStatusEnum.ACTIVE)
      .order_by(self.model.created_at.desc())
      .all()
    )

  def update(
    self, interview: InterviewTemplateTable, data: UpdateInterview
  ) -> InterviewTemplateTable:
    updated = data.model_dump(exclude_unset=True, exclude={"questions"})

    for key, value in updated.items():
      setattr(interview, key, value)

    if data.questions is not None:
      interview.questions.clear()
      for q_data in data.questions:
        question = self._build_question(q_data)
        interview.questions.append(question)

    self.db.add(interview)
    self.db.flush()
    self.db.refresh(interview)
    return interview

  @staticmethod
  def _build_question(
    q_data: CreateInterviewQuestion,
  ) -> InterviewQuestionTable:
    question_data = q_data.model_dump(exclude={"options"})
    question = InterviewQuestionTable(**question_data)

    for opt_data in q_data.options:
      option = InterviewOptionTable(**opt_data.model_dump())
      question.options.append(option)

    return question

  # ---------- Session lifecycle ----------

  def create_session(
    self,
    enrollee_id: int,
    interview_id: int,
    pass_score_snapshot: float,
    scheduled_at: datetime | None = None,
  ) -> InterviewSessionTable:
    session = InterviewSessionTable(
      enrollee_id=enrollee_id,
      interview_id=interview_id,
      pass_score_snapshot=pass_score_snapshot,
      scheduled_at=scheduled_at,
    )
    self.db.add(session)
    self.db.flush()
    self.db.refresh(session)
    return session

  def get_session_by_uuid(self, uuid: str) -> InterviewSessionTable | None:
    return (
      self.db.query(InterviewSessionTable)
      .filter(InterviewSessionTable.uuid == uuid)
      .first()
    )

  def get_active_session_for_enrollee(
    self, enrollee_id: int, interview_id: int
  ) -> InterviewSessionTable | None:
    from .validation import InterviewSessionStatusEnum

    terminal = {
      InterviewSessionStatusEnum.COMPLETED,
      InterviewSessionStatusEnum.GRADED,
      InterviewSessionStatusEnum.CANCELLED,
    }
    return (
      self.db.query(InterviewSessionTable)
      .filter(
        InterviewSessionTable.enrollee_id == enrollee_id,
        InterviewSessionTable.interview_id == interview_id,
        ~InterviewSessionTable.status.in_(terminal),
      )
      .first()
    )

  def start_session(self, session: InterviewSessionTable) -> InterviewSessionTable:
    from .validation import InterviewSessionStatusEnum

    session.status = InterviewSessionStatusEnum.IN_PROGRESS
    session.started_at = datetime.utcnow()
    self.db.add(session)
    self.db.flush()
    self.db.refresh(session)
    return session

  def submit_session(
    self,
    session: InterviewSessionTable,
    payload: SubmitInterviewSession,
  ) -> InterviewSessionTable:
    from .validation import InterviewSessionStatusEnum

    session.status = InterviewSessionStatusEnum.COMPLETED
    session.completed_at = datetime.utcnow()
    if session.started_at is not None:
      delta = session.completed_at - session.started_at
      session.time_spent_seconds = int(delta.total_seconds())

    self._apply_answers(session, payload)
    self._auto_grade_mcq_and_rating(session)

    self.db.add(session)
    self.db.flush()
    self.db.refresh(session)
    return session

  def grade_session(
    self,
    session: InterviewSessionTable,
    payload: GradeInterviewSession,
  ) -> InterviewSessionTable:
    from .validation import InterviewSessionStatusEnum

    if payload.conducted_by is not None:
      session.conducted_by = payload.conducted_by
    if payload.notes is not None:
      session.notes = payload.notes

    by_answer_id = {g.answer_id: g for g in payload.answer_grades}
    for answer in session.answers:
      grade: GradeInterviewAnswer | None = by_answer_id.get(answer.id)
      if grade is not None:
        if grade.is_correct is not None:
          answer.is_correct = grade.is_correct
        if grade.points_awarded is not None:
          answer.points_awarded = grade.points_awarded
        if grade.rater_note is not None:
          answer.rater_note = grade.rater_note

    if payload.override_score is not None:
      session.score = payload.override_score
    else:
      total_awarded = 0.0
      for answer in session.answers:
        if answer.points_awarded is not None:
          total_awarded += answer.points_awarded
      session.score = round(total_awarded, 2)

    session.status = InterviewSessionStatusEnum.GRADED
    self.db.add(session)
    self.db.flush()
    self.db.refresh(session)
    return session

  def cancel_session(self, session: InterviewSessionTable) -> InterviewSessionTable:
    from .validation import InterviewSessionStatusEnum

    session.status = InterviewSessionStatusEnum.CANCELLED
    self.db.add(session)
    self.db.flush()
    self.db.refresh(session)
    return session

  def _apply_answers(
    self, session: InterviewSessionTable, payload: SubmitInterviewSession
  ) -> None:
    session.answers.clear()
    by_qid = {a.question_id: a for a in payload.answers}

    for question in session.interview.questions:
      submission = by_qid.get(question.id)
      self._build_answer(session, question, submission)

  @staticmethod
  def _build_answer(
    session: InterviewSessionTable,
    question: InterviewQuestionTable,
    submission: InterviewAnswerSubmission | None,
  ) -> InterviewAnswerTable:
    answer = InterviewAnswerTable(
      session_id=session.id,
      question_id=question.id,
    )
    if submission is not None:
      answer.selected_option_id = submission.selected_option_id
      answer.text_answer = submission.text_answer
      answer.rating_value = submission.rating_value
    session.answers.append(answer)
    return answer

  def _auto_grade_mcq_and_rating(self, session: InterviewSessionTable) -> None:
    from .validation import InterviewQuestionTypeEnum

    total_awarded = 0.0
    has_ungraded = False

    for answer in session.answers:
      question = next(
        (q for q in session.interview.questions if q.id == answer.question_id),
        None,
      )
      if question is None:
        continue

      if question.question_type == InterviewQuestionTypeEnum.MCQ:
        correct_options = {opt.id for opt in question.options if opt.is_correct}
        selected = answer.selected_option_id
        is_correct = (
          selected is not None
          and selected in correct_options
          and len(correct_options) == 1
        )
        awarded = float(question.points) if is_correct else 0.0
        answer.is_correct = is_correct
        answer.points_awarded = awarded
        total_awarded += awarded
      elif question.question_type == InterviewQuestionTypeEnum.RATING_SCALE:
        if answer.rating_value is not None and question.points > 0:
          normalized = max(0.0, min(10.0, float(answer.rating_value))) / 10.0
          awarded = round(normalized * question.points, 2)
          answer.points_awarded = awarded
          answer.is_correct = normalized >= 0.5
          total_awarded += awarded
      else:
        has_ungraded = True

    if not has_ungraded:
      session.score = round(total_awarded, 2)

  # ---------- Query helpers ----------

  def count_questions(self, interview_id: int) -> int:
    return (
      self.db.query(InterviewQuestionTable)
      .filter(InterviewQuestionTable.interview_id == interview_id)
      .count()
    )
