from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)

health_router = APIRouter()


@health_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tamor-backend", "version": "0.1.0"}
