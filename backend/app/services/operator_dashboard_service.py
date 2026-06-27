"""District-wide operator dashboard aggregates (Hokimiyat / Super Admin preview)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_redis
from app.models.academics import Course
from app.models.education import Enrollment, Student, Teacher
from app.models.identity import TrainingCenter, User
from app.models.ratings_certs import Certificate
from app.schemas.dashboard import CenterCertificateStat, OperatorDashboardResponse, TrendPoint

logger = logging.getLogger(__name__)

_CACHE_KEY = "dashboard:operator_summary:v1"
_CACHE_TTL_SECONDS = 300


async def get_operator_summary(db: AsyncSession, user: User) -> OperatorDashboardResponse:
    if user.role.code not in {"hokimiyat_operator", "super_admin"}:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Operator dashboard only")

    try:
        r = await get_redis()
        cached = await r.get(_CACHE_KEY)
        if cached:
            return OperatorDashboardResponse.model_validate(json.loads(cached))
    except Exception:
        logger.warning("Operator dashboard cache read failed", exc_info=True)

    payload = await _compute_operator_summary(db)
    try:
        r = await get_redis()
        await r.setex(_CACHE_KEY, _CACHE_TTL_SECONDS, payload.model_dump_json())
    except Exception:
        logger.warning("Operator dashboard cache write failed", exc_info=True)
    return payload


async def _compute_operator_summary(db: AsyncSession) -> OperatorDashboardResponse:
    now = datetime.now(UTC)
    year_start = date(now.year, 1, 1)

    active_centers = (
        await db.execute(
            select(func.count())
            .select_from(TrainingCenter)
            .where(TrainingCenter.deleted_at.is_(None), TrainingCenter.is_active.is_(True))
        )
    ).scalar() or 0

    total_teachers = (
        await db.execute(
            select(func.count())
            .select_from(Teacher)
            .where(Teacher.deleted_at.is_(None), Teacher.is_active.is_(True))
        )
    ).scalar() or 0

    total_students = (
        await db.execute(
            select(func.count(func.distinct(Enrollment.student_id)))
            .select_from(Enrollment)
            .join(Student, Student.id == Enrollment.student_id)
            .where(
                Enrollment.status == "active",
                Enrollment.deleted_at.is_(None),
                Student.deleted_at.is_(None),
            )
        )
    ).scalar() or 0

    certificates_ytd = (
        await db.execute(
            select(func.count())
            .select_from(Certificate)
            .where(
                Certificate.status == "valid",
                Certificate.issue_date >= year_start,
            )
        )
    ).scalar() or 0

    total_courses = (
        await db.execute(
            select(func.count())
            .select_from(Course)
            .where(Course.deleted_at.is_(None), Course.is_active.is_(True))
        )
    ).scalar() or 0

    cert_rows = (
        await db.execute(
            select(
                TrainingCenter.id,
                TrainingCenter.name,
                func.count(Certificate.id).label("cnt"),
            )
            .join(Certificate, Certificate.center_id == TrainingCenter.id)
            .where(
                TrainingCenter.deleted_at.is_(None),
                Certificate.deleted_at.is_(None),
                Certificate.status == "valid",
                Certificate.issue_date >= year_start,
            )
            .group_by(TrainingCenter.id, TrainingCenter.name)
            .order_by(func.count(Certificate.id).desc())
        )
    ).all()

    certificates_by_center = [
        CenterCertificateStat(
            center_id=str(row.id),
            center_name=row.name,
            certificate_count=int(row.cnt),
        )
        for row in cert_rows
    ]

    student_trend = await _monthly_student_trend(db, months=12, forecast_months=2)
    certificate_trend = await _monthly_certificate_trend(db, months=12, forecast_months=1)

    return OperatorDashboardResponse(
        active_centers=active_centers,
        total_teachers=total_teachers,
        total_students=total_students,
        certificates_ytd=certificates_ytd,
        total_courses=total_courses,
        certificates_by_center=certificates_by_center,
        certificates_by_center_total=len(certificates_by_center),
        student_trend=student_trend,
        certificate_trend=certificate_trend,
    )


async def _monthly_student_trend(
    db: AsyncSession,
    *,
    months: int,
    forecast_months: int,
) -> list[TrendPoint]:
    points = await _monthly_enrollment_counts(db, months)
    return _append_linear_forecast(points, forecast_months)


async def _monthly_certificate_trend(
    db: AsyncSession,
    *,
    months: int,
    forecast_months: int,
) -> list[TrendPoint]:
    points = await _monthly_certificate_counts(db, months)
    return _append_linear_forecast(points, forecast_months)


async def _monthly_enrollment_counts(db: AsyncSession, months: int) -> list[TrendPoint]:
    now = datetime.now(UTC)
    points: list[TrendPoint] = []
    for offset in range(months - 1, -1, -1):
        month_dt = _shift_month(now, -offset)
        start = month_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = _shift_month(start, 1)
        count = (
            await db.execute(
                select(func.count(func.distinct(Enrollment.student_id)))
                .select_from(Enrollment)
                .join(Student, Student.id == Enrollment.student_id)
                .where(
                    Enrollment.deleted_at.is_(None),
                    Enrollment.status == "active",
                    Enrollment.created_at < end,
                    Student.deleted_at.is_(None),
                )
            )
        ).scalar() or 0
        points.append(TrendPoint(label=start.strftime("%Y-%m"), value=int(count)))
    return points


async def _monthly_certificate_counts(db: AsyncSession, months: int) -> list[TrendPoint]:
    now = datetime.now(UTC)
    points: list[TrendPoint] = []
    for offset in range(months - 1, -1, -1):
        month_dt = _shift_month(now, -offset)
        start = month_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = _shift_month(start, 1)
        count = (
            await db.execute(
                select(func.count())
                .select_from(Certificate)
                .where(
                    Certificate.deleted_at.is_(None),
                    Certificate.status == "valid",
                    Certificate.issue_date >= start.date(),
                    Certificate.issue_date < end.date(),
                )
            )
        ).scalar() or 0
        points.append(TrendPoint(label=start.strftime("%Y-%m"), value=int(count)))
    return points


def _shift_month(dt: datetime, delta: int) -> datetime:
    month = dt.month - 1 + delta
    year = dt.year + month // 12
    month = month % 12 + 1
    return dt.replace(year=year, month=month)


def _append_linear_forecast(points: list[TrendPoint], forecast_months: int) -> list[TrendPoint]:
    if not points or forecast_months <= 0:
        return points

    n = len(points)
    if n < 2:
        return points

    xs = list(range(n))
    ys = [p.value for p in points]
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    denom = sum((x - x_mean) ** 2 for x in xs) or 1.0
    slope = sum((x - x_mean) * (y - ys[i]) for i, x in enumerate(xs)) / denom
    intercept = y_mean - slope * x_mean

    result = list(points)
    last_label = points[-1].label
    year, month = (int(last_label[:4]), int(last_label[5:7]))
    for i in range(1, forecast_months + 1):
        month += 1
        if month > 12:
            month = 1
            year += 1
        x_future = n - 1 + i
        predicted = max(0, round(intercept + slope * x_future))
        result.append(
            TrendPoint(
                label=f"{year:04d}-{month:02d}",
                value=predicted,
                is_forecast=True,
            )
        )
    return result
