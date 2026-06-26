from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Region(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "regions"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)


class Mahalla(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "mahallas"

    region_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
