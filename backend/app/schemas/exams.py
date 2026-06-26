from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class ExamQuestionCreate(BaseModel):
    question_text: str
    options_json: list[str] | None = None
    correct_answer: str
    points: float = 1.0
    order_index: int = 0


class ExamCreate(BaseModel):
    center_id: UUID | None = None
    subject_id: UUID
    group_id: UUID | None = None
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    pass_score: float = 60.0
    duration_minutes: int = 60
    questions: list[ExamQuestionCreate] = []


class ExamUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    pass_score: float | None = None
    duration_minutes: int | None = None
    is_published: bool | None = None


class ExamSubmitAnswer(BaseModel):
    question_id: UUID
    answer: str


class ExamSubmitRequest(BaseModel):
    student_id: UUID
    answers: list[ExamSubmitAnswer]


class ExamResponse(BaseModel):
    id: UUID
    center_id: UUID
    subject_id: UUID
    group_id: UUID | None
    title: str
    description: str | None
    pass_score: float
    duration_minutes: int
    is_published: bool
    question_count: int = 0


class ExamResultResponse(BaseModel):
    id: UUID
    exam_id: UUID
    student_id: UUID
    score: float
    max_score: float
    passed: bool
    submitted_at: date | None = None
