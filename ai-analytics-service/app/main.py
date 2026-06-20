"""TaMoR AI Analytics Microservice — Phase 0 skeleton."""

from fastapi import FastAPI

app = FastAPI(
    title="TaMoR AI Analytics",
    description="Decoupled analytics microservice for trend forecasting and anomaly detection",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "tamor-ai-analytics", "version": "0.1.0"}


@app.get("/api/v1/predictions")
async def list_predictions():
    """Placeholder — full implementation in Phase 3."""
    return {
        "success": True,
        "data": [],
        "meta": {"message": "AI analytics module — Phase 3"},
        "error": None,
    }
