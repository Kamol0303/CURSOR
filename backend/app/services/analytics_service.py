"""Backend proxy to AI analytics microservice and local prediction cache."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.analytics_notifications import AiAnalysisLog, AiPrediction


async def get_latest_predictions(db: AsyncSession) -> list[AiPrediction]:
    result = await db.execute(
        select(AiPrediction).order_by(AiPrediction.computed_at.desc()).limit(20)
    )
    return list(result.scalars().all())


async def get_latest_analysis_log(db: AsyncSession) -> AiAnalysisLog | None:
    result = await db.execute(
        select(AiAnalysisLog).order_by(AiAnalysisLog.created_at.desc()).limit(1)
    )
    return result.scalar_one_or_none()


async def fetch_insights_from_service(access_token: str) -> dict:
    url = f"{settings.AI_ANALYTICS_URL.rstrip('/')}/analytics/insights"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


async def trigger_analytics_run(access_token: str, triggered_by: str = "api") -> dict:
    url = f"{settings.AI_ANALYTICS_URL.rstrip('/')}/analytics/run"
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            json={"triggered_by": triggered_by},
        )
        response.raise_for_status()
        return response.json()


def serialize_prediction(p: AiPrediction) -> dict:
    return {
        "id": str(p.id),
        "prediction_type": p.prediction_type,
        "payload": p.payload,
        "confidence_score": p.confidence_score,
        "period_start": p.period_start.isoformat(),
        "period_end": p.period_end.isoformat(),
        "computed_at": p.computed_at.isoformat() if p.computed_at else None,
    }


async def store_predictions_from_run(db: AsyncSession, run_payload: dict) -> int:
    """Persist predictions returned by AI service into main DB cache."""
    predictions = run_payload.get("predictions", [])
    count = 0
    now = datetime.now(UTC)
    for item in predictions:
        pred = AiPrediction(
            prediction_type=item["prediction_type"],
            payload=item["payload"],
            confidence_score=item.get("confidence_score", 0.8),
            period_start=datetime.fromisoformat(item["period_start"]).date()
            if isinstance(item["period_start"], str)
            else item["period_start"],
            period_end=datetime.fromisoformat(item["period_end"]).date()
            if isinstance(item["period_end"], str)
            else item["period_end"],
            expires_at=now + timedelta(days=7),
        )
        db.add(pred)
        count += 1

    log = AiAnalysisLog(
        run_id=UUID(run_payload["run_id"]) if isinstance(run_payload.get("run_id"), str) else run_payload.get("run_id"),
        status=run_payload.get("status", "completed"),
        metrics_count=count,
        duration_ms=run_payload.get("duration_ms"),
        triggered_by=run_payload.get("triggered_by", "api"),
    )
    db.add(log)
    await db.flush()
    return count
