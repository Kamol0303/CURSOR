from fastapi import FastAPI

app = FastAPI(title="TaMoR AI Analytics", version="0.0.1-phase0")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-analytics", "phase": 0}
