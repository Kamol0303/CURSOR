import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.education import Student, Teacher, TeacherSubject
from app.models.identity import SystemSetting, TrainingCenter
from app.models.ratings_certs import RatingFormulaVersion, RatingHistory

DEFAULT_WEIGHTS = {
    "total_students": 0.40,
    "certification_rate": 0.25,
    "graduates": 0.15,
    "monthly_growth": 0.10,
    "new_subjects": 0.05,
    "teacher_qualification": 0.05,
}


async def get_or_create_formula(db: AsyncSession, user_id: UUID | None = None) -> RatingFormulaVersion:
    result = await db.execute(
        select(RatingFormulaVersion).order_by(RatingFormulaVersion.version.desc()).limit(1)
    )
    formula = result.scalar_one_or_none()
    if formula:
        return formula

    formula = RatingFormulaVersion(
        version=1,
        weights=DEFAULT_WEIGHTS,
        created_by=user_id,
        notes="Default TaMoR v4.0 formula",
    )
    db.add(formula)
    await db.flush()

    setting = await db.get(SystemSetting, "rating_weights")
    if not setting:
        db.add(SystemSetting(key="rating_weights", value=DEFAULT_WEIGHTS))
    return formula


def _normalize(value: float, min_v: float, max_v: float) -> float:
    if max_v <= min_v:
        return 0.0
    return max(0.0, min(1.0, (value - min_v) / (max_v - min_v)))


def _inputs_hash(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


async def _center_metrics(db: AsyncSession, center_id: UUID) -> dict:
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    six_months_ago = now - timedelta(days=180)

    student_count = (
        await db.execute(
            select(func.count())
            .select_from(Student)
            .where(Student.center_id == center_id, Student.deleted_at.is_(None))
        )
    ).scalar() or 0

    prev_month_students = (
        await db.execute(
            select(func.count())
            .select_from(Student)
            .where(
                Student.center_id == center_id,
                Student.deleted_at.is_(None),
                Student.created_at < month_start,
                Student.created_at >= prev_month_start,
            )
        )
    ).scalar() or 0

    current_month_new = (
        await db.execute(
            select(func.count())
            .select_from(Student)
            .where(
                Student.center_id == center_id,
                Student.deleted_at.is_(None),
                Student.created_at >= month_start,
            )
        )
    ).scalar() or 0

    graduates = (
        await db.execute(
            select(func.count())
            .select_from(Student)
            .where(
                Student.center_id == center_id,
                Student.deleted_at.is_(None),
                Student.graduation_date.isnot(None),
            )
        )
    ).scalar() or 0

    from app.models.ratings_certs import Certificate

    certified = (
        await db.execute(
            select(func.count())
            .select_from(Certificate)
            .where(
                Certificate.center_id == center_id,
                Certificate.status == "valid",
                Certificate.deleted_at.is_(None),
            )
        )
    ).scalar() or 0

    cert_rate = (certified / graduates * 100) if graduates > 0 else 0.0

    if prev_month_students > 0:
        monthly_growth = (current_month_new - prev_month_students) / prev_month_students * 100
    elif current_month_new > 0:
        monthly_growth = 100.0
    else:
        monthly_growth = 0.0

    new_subjects = (
        await db.execute(
            select(func.count(func.distinct(TeacherSubject.subject_id)))
            .select_from(TeacherSubject)
            .join(Teacher, Teacher.id == TeacherSubject.teacher_id)
            .where(Teacher.center_id == center_id, Teacher.created_at >= six_months_ago)
        )
    ).scalar() or 0

    teacher_stats = (
        await db.execute(
            select(func.avg(Teacher.years_of_experience), func.count())
            .select_from(Teacher)
            .where(Teacher.center_id == center_id, Teacher.deleted_at.is_(None), Teacher.is_active.is_(True))
        )
    ).one()
    avg_exp = float(teacher_stats[0] or 0)
    teacher_count = teacher_stats[1] or 0
    teacher_qual = min(100.0, avg_exp * 10 + teacher_count * 2)

    return {
        "student_count": student_count,
        "graduates": graduates,
        "certified": certified,
        "certification_rate": cert_rate,
        "monthly_growth": monthly_growth,
        "new_subjects": new_subjects,
        "teacher_qualification": teacher_qual,
    }


async def compute_ratings(db: AsyncSession, *, user_id: UUID | None = None) -> list[RatingHistory]:
    formula = await get_or_create_formula(db, user_id)
    weights = formula.weights

    centers_result = await db.execute(
        select(TrainingCenter).where(TrainingCenter.deleted_at.is_(None), TrainingCenter.is_active.is_(True))
    )
    centers = list(centers_result.scalars().all())
    if not centers:
        return []

    all_metrics: dict[UUID, dict] = {}
    for center in centers:
        all_metrics[center.id] = await _center_metrics(db, center.id)

    max_students = max(m["student_count"] for m in all_metrics.values()) or 1
    max_graduates = max(m["graduates"] for m in all_metrics.values()) or 1

    period = date.today()
    scores: list[tuple[TrainingCenter, dict, float, dict, str, bool]] = []

    for center in centers:
        m = all_metrics[center.id]
        breakdown = {
            "total_students": _normalize(m["student_count"], 0, max_students) * weights["total_students"] * 100,
            "certification_rate": _normalize(m["certification_rate"], 0, 100) * weights["certification_rate"] * 100,
            "graduates": _normalize(m["graduates"], 0, max_graduates) * weights["graduates"] * 100,
            "monthly_growth": _normalize(max(m["monthly_growth"], 0), 0, 100) * weights["monthly_growth"] * 100,
            "new_subjects": _normalize(m["new_subjects"], 0, 10) * weights["new_subjects"] * 100,
            "teacher_qualification": _normalize(m["teacher_qualification"], 0, 100)
            * weights["teacher_qualification"]
            * 100,
        }
        total = sum(breakdown.values())
        inputs_hash = _inputs_hash(m)
        flagged = m["monthly_growth"] > 200
        scores.append((center, m, total, breakdown, inputs_hash, flagged))

    scores.sort(key=lambda x: x[2], reverse=True)

    prev_period = period.replace(day=1) - timedelta(days=1)
    prev_ranks: dict[UUID, int] = {}
    prev_result = await db.execute(
        select(RatingHistory).where(RatingHistory.period == prev_period.replace(day=1))
    )
    for rh in prev_result.scalars():
        if rh.rank:
            prev_ranks[rh.center_id] = rh.rank

    results: list[RatingHistory] = []
    for rank, (center, _m, total, breakdown, inputs_hash, flagged) in enumerate(scores, start=1):
        prev_rank = prev_ranks.get(center.id)
        rank_change = (prev_rank - rank) if prev_rank else None

        history = RatingHistory(
            center_id=center.id,
            formula_version_id=formula.id,
            period=period,
            total_score=round(total, 2),
            rank=rank,
            rank_change=rank_change,
            criteria_breakdown=breakdown,
            inputs_hash=inputs_hash,
            flagged_anomaly=flagged,
        )
        db.add(history)
        results.append(history)

    await db.flush()
    return results


async def get_latest_ratings(db: AsyncSession, limit: int = 10) -> list[RatingHistory]:
    latest_period = (
        await db.execute(select(func.max(RatingHistory.period)))
    ).scalar()
    if not latest_period:
        return []

    result = await db.execute(
        select(RatingHistory)
        .options(selectinload(RatingHistory.center))
        .where(RatingHistory.period == latest_period)
        .order_by(RatingHistory.rank)
        .limit(limit)
    )
    return list(result.scalars().all())
