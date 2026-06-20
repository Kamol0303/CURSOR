from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.centers import router as centers_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.students import router as students_router
from app.api.v1.teachers import router as teachers_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(centers_router)
api_router.include_router(students_router)
api_router.include_router(teachers_router)
api_router.include_router(dashboard_router)
