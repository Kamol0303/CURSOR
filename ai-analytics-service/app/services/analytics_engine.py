"""Read-only analytics engine — no PINFL column access."""

from __future__ import annotations

import time
import uuid
from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Tables queried without students.jshshir_encrypted
READONLY_TABLES = {
    "training_centers",
    "students",
    "teachers",
    "subjects",
    "teacher_subjects",
    "enrollments",
    "rating_history",
    "groups",
}


async def run_analysis(db: AsyncSession, triggered_by: str = "scheduler") -> dict:
    run_id = uuid.uuid4()
    started = time.monotonic()
    period_end = date.today()
    period_start = period_end - timedelta(days=30)

    try:
        predictions = []
        predictions.append(await _fastest_growing_center(db, period_start, period_end))
        predictions.append(await _declining_centers(db, period_start, period_end))
        predictions.append(await _high_demand_subjects(db))
        predictions.append(await _education_gap_index(db))

        duration_ms = int((time.monotonic() - started) * 1000)
        return {
            "run_id": str(run_id),
            "status": "completed",
            "triggered_by": triggered_by,
            "duration_ms": duration_ms,
            "predictions": predictions,
        }
    except Exception as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        return {
            "run_id": str(run_id),
            "status": "failed",
            "triggered_by": triggered_by,
            "duration_ms": duration_ms,
            "error": str(exc),
            "predictions": [],
        }


async def _fastest_growing_center(db: AsyncSession, period_start: date, period_end: date) -> dict:
    query = text("""
        SELECT tc.id, tc.name,
               COUNT(s.id) FILTER (WHERE s.created_at >= :start AND s.created_at <= :end) AS new_students,
               COUNT(s.id) AS total_students
        FROM training_centers tc
        LEFT JOIN students s ON s.center_id = tc.id AND s.deleted_at IS NULL
        WHERE tc.deleted_at IS NULL AND tc.is_active = true
        GROUP BY tc.id, tc.name
        ORDER BY new_students DESC NULLS LAST
        LIMIT 1
    """)
    row = (await db.execute(query, {"start": period_start, "end": period_end})).mappings().first()
    if not row or not row["new_students"]:
        return {
            "prediction_type": "fastest_growing_center",
            "confidence_score": 0.5,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "payload": {"message": "Insufficient enrollment data for growth analysis"},
        }

    growth_rate = (row["new_students"] / max(row["total_students"], 1)) * 100
    return {
        "prediction_type": "fastest_growing_center",
        "confidence_score": min(0.95, 0.6 + growth_rate / 100),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "payload": {
            "center_id": str(row["id"]),
            "center_name": row["name"],
            "new_students": row["new_students"],
            "total_students": row["total_students"],
            "growth_rate_pct": round(growth_rate, 2),
        },
    }


async def _declining_centers(db: AsyncSession, period_start: date, period_end: date) -> dict:
    query = text("""
        SELECT tc.id, tc.name,
               COALESCE(rh.rank_change, 0) AS rank_change,
               rh.total_score
        FROM training_centers tc
        LEFT JOIN LATERAL (
            SELECT rank_change, total_score
            FROM rating_history
            WHERE center_id = tc.id
            ORDER BY period DESC
            LIMIT 1
        ) rh ON true
        WHERE tc.deleted_at IS NULL AND tc.is_active = true
          AND COALESCE(rh.rank_change, 0) > 0
        ORDER BY rh.rank_change DESC
        LIMIT 5
    """)
    rows = (await db.execute(query)).mappings().all()
    centers = [
        {
            "center_id": str(r["id"]),
            "center_name": r["name"],
            "rank_drop": r["rank_change"],
            "current_score": r["total_score"],
        }
        for r in rows
    ]
    return {
        "prediction_type": "declining_centers",
        "confidence_score": 0.85 if centers else 0.4,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "payload": {"centers": centers, "count": len(centers)},
    }


async def _high_demand_subjects(db: AsyncSession) -> dict:
    query = text("""
        SELECT sub.id, sub.name_uz, sub.name_ru, sub.name_en,
               COUNT(DISTINCT ts.teacher_id) AS teacher_count,
               COUNT(DISTINCT g.id) AS group_count
        FROM subjects sub
        LEFT JOIN teacher_subjects ts ON ts.subject_id = sub.id
        LEFT JOIN groups g ON g.subject_id = sub.id AND g.deleted_at IS NULL
        WHERE sub.is_active = true
        GROUP BY sub.id, sub.name_uz, sub.name_ru, sub.name_en
        ORDER BY teacher_count DESC, group_count DESC
        LIMIT 5
    """)
    rows = (await db.execute(query)).mappings().all()
    subjects = [
        {
            "subject_id": str(r["id"]),
            "name_uz": r["name_uz"],
            "name_ru": r["name_ru"],
            "name_en": r["name_en"],
            "teacher_count": r["teacher_count"],
            "group_count": r["group_count"],
            "demand_score": r["teacher_count"] * 2 + r["group_count"],
        }
        for r in rows
    ]
    return {
        "prediction_type": "high_demand_subjects",
        "confidence_score": 0.9 if subjects else 0.3,
        "period_start": date.today().isoformat(),
        "period_end": date.today().isoformat(),
        "payload": {"subjects": subjects},
    }


async def _education_gap_index(db: AsyncSession) -> dict:
    total_centers = (
        await db.execute(
            text("SELECT COUNT(*) FROM training_centers WHERE deleted_at IS NULL AND is_active = true")
        )
    ).scalar() or 0
    total_students = (
        await db.execute(text("SELECT COUNT(*) FROM students WHERE deleted_at IS NULL"))
    ).scalar() or 0
    total_teachers = (
        await db.execute(text("SELECT COUNT(*) FROM teachers WHERE deleted_at IS NULL AND is_active = true"))
    ).scalar() or 0
    certified = (
        await db.execute(
            text("SELECT COUNT(*) FROM students WHERE graduation_date IS NOT NULL AND deleted_at IS NULL")
        )
    ).scalar() or 0

    student_teacher_ratio = total_students / max(total_teachers, 1)
    certification_rate = certified / max(total_students, 1)
    coverage_score = min(1.0, total_centers / 10)
    gap_index = round((1 - certification_rate) * 0.4 + min(student_teacher_ratio / 25, 1) * 0.4 + (1 - coverage_score) * 0.2, 3)

    return {
        "prediction_type": "education_gap_index",
        "confidence_score": 0.88,
        "period_start": date.today().isoformat(),
        "period_end": date.today().isoformat(),
        "payload": {
            "gap_index": gap_index,
            "interpretation": "lower_is_better" if gap_index < 0.5 else "needs_attention",
            "total_centers": total_centers,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "certification_rate_pct": round(certification_rate * 100, 1),
            "student_teacher_ratio": round(student_teacher_ratio, 1),
        },
    }


async def get_cached_insights(db: AsyncSession) -> list[dict]:
    """Return latest prediction per type from ai_predictions if available."""
    query = text("""
        SELECT DISTINCT ON (prediction_type)
            prediction_type, payload, confidence_score, period_start, period_end, computed_at
        FROM ai_predictions
        ORDER BY prediction_type, computed_at DESC
    """)
    try:
        rows = (await db.execute(query)).mappings().all()
    except Exception:
        return []

    return [
        {
            "prediction_type": r["prediction_type"],
            "payload": r["payload"],
            "confidence_score": r["confidence_score"],
            "period_start": r["period_start"].isoformat() if r["period_start"] else None,
            "period_end": r["period_end"].isoformat() if r["period_end"] else None,
            "computed_at": r["computed_at"].isoformat() if r["computed_at"] else None,
        }
        for r in rows
    ]
