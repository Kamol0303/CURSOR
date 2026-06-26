from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name_uz: str = Field(min_length=1, max_length=100)
    name_ru: str = Field(min_length=1, max_length=100)
    name_en: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class SubjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name_uz: str | None = Field(default=None, min_length=1, max_length=100)
    name_ru: str | None = Field(default=None, min_length=1, max_length=100)
    name_en: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name_uz: str
    name_ru: str
    name_en: str
    is_active: bool
