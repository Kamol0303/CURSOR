from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    meta: dict | None = None
    error: dict | None = None


class PaginationParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
