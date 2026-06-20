from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.deps import require_analytics_access
from app.services.analytics_engine import get_cached_insights, run_analysis

scheduler = AsyncIOScheduler()


async def _scheduled_run():
    async with SessionLocal() as db:
        result = await run_analysis(db, triggered_by="scheduler")
        if result["status"] == "completed":
            await _persist_predictions(db, result)
        await db.commit()


async def _persist_predictions(db: AsyncSession, result: dict):
    import json
    import uuid as uuid_mod

    from sqlalchemy import text

    for item in result.get("predictions", []):
        await db.execute(
            text("""
                INSERT INTO ai_predictions
                (id, prediction_type, payload, confidence_score, period_start, period_end)
                VALUES (:id, :type, CAST(:payload AS jsonb), :confidence, :start, :end)
            """),
            {
                "id": str(uuid_mod.uuid4()),
                "type": item["prediction_type"],
                "payload": json.dumps(item["payload"]),
                "confidence": item["confidence_score"],
                "start": item["period_start"],
                "end": item["period_end"],
            },
        )

    await db.execute(
        text("""
            INSERT INTO ai_analysis_logs (id, run_id, status, metrics_count, duration_ms, triggered_by)
            VALUES (:id, CAST(:run_id AS uuid), :status, :count, :duration, :triggered_by)
        """),
        {
            "id": str(uuid_mod.uuid4()),
            "run_id": result["run_id"],
            "status": result["status"],
            "count": len(result.get("predictions", [])),
            "duration": result.get("duration_ms"),
            "triggered_by": result.get("triggered_by", "scheduler"),
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT != "test":
        scheduler.add_job(_scheduled_run, "cron", hour=settings.SCHEDULE_CRON_HOUR, id="daily_analytics")
        scheduler.start()
    yield
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(title="TaMoR AI Analytics", version="0.3.0-phase3", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-analytics", "phase": 3}


class RunRequest(BaseModel):
    triggered_by: str = "api"


@app.get("/analytics/insights")
async def insights(
    _payload: dict = Depends(require_analytics_access),
    db: AsyncSession = Depends(get_db),
):
    cached = await get_cached_insights(db)
    if cached:
        return {"predictions": cached, "source": "cache"}
    result = await run_analysis(db, triggered_by="on_demand")
    return {"predictions": result["predictions"], "source": "live", "run_id": result["run_id"]}


@app.post("/analytics/run")
async def run(
    body: RunRequest,
    _payload: dict = Depends(require_analytics_access),
    db: AsyncSession = Depends(get_db),
):
    result = await run_analysis(db, triggered_by=body.triggered_by)
    if result["status"] == "completed":
        await _persist_predictions(db, result)
    await db.commit()
    return result
