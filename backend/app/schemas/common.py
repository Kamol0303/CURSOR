<<<<<<< HEAD
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

=======
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field
>>>>>>> main

T = TypeVar("T")


<<<<<<< HEAD
class ErrorPayload(BaseModel):
    code: str
    field: str | None = None
    detail: str | None = None


class MetaPayload(BaseModel):
    page: int | None = None
    per_page: int | None = None
    total: int | None = None


class Envelope(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    meta: MetaPayload | None = None
    error: ErrorPayload | None = None


def success_response(data: Any) -> dict[str, Any]:
    return {"success": True, "data": data, "meta": None, "error": None}


def error_response(code: str, field: str | None = None, detail: str | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "meta": None,
        "error": {"code": code, "field": field, "detail": detail},
    }
=======
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
>>>>>>> main
