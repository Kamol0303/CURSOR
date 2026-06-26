from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExamQuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=1)
    options_json: list[str] | None = None
    correct_answer: str = Field(min_length=1)
    points: float = Field(default=1.0, ge=0.1)
    order_index: int = Field(default=0, ge=0)


class ExamGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_id: UUID
    topic: str = Field(min_length=2, max_length=255)
    question_count: int = Field(default=5, ge=1, le=30)
    difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
    locale: str = Field(default="uz", pattern=r"^(uz|ru|en)$")
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    center_id: UUID | None = None
    group_id: UUID | None = None
    pass_score: float = Field(default=60.0, ge=0, le=100)
    duration_minutes: int = Field(default=60, ge=15, le=240)


class ExamCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center_id: UUID | None = None
    subject_id: UUID
    group_id: UUID | None = None
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    pass_score: float = Field(default=60.0, ge=0, le=100)
    duration_minutes: int = Field(default=60, ge=15, le=240)
    questions: list[ExamQuestionCreate] = Field(default_factory=list)


class ExamUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    pass_score: float | None = Field(default=None, ge=0, le=100)
    duration_minutes: int | None = Field(default=None, ge=15, le=240)
    is_published: bool | None = None


class ExamSubmitAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: UUID
    answer: str = Field(min_length=1)


class ExamSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: UUID | None = None
    answers: list[ExamSubmitAnswer] = Field(min_length=1)


class ExamQuestionResponse(BaseModel):
    id: UUID
    question_text: str
    options_json: list[str] | None
    correct_answer: str | None = None
    points: float
    order_index: int


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


class ExamDetailResponse(ExamResponse):
    questions: list[ExamQuestionResponse] = Field(default_factory=list)


class ExamResultResponse(BaseModel):
    id: UUID
    exam_id: UUID
    student_id: UUID
    score: float
    max_score: float
    passed: bool
    submitted_at: date | None = None
