from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


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
