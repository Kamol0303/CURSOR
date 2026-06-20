from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.centers import router as centers_router
from app.api.v1.certificates import router as certificates_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.public import router as public_router
from app.api.v1.ratings import router as ratings_router
from app.api.v1.reports import router as reports_router
from app.api.v1.students import router as students_router
from app.api.v1.teachers import router as teachers_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(centers_router)
api_router.include_router(students_router)
api_router.include_router(teachers_router)
api_router.include_router(dashboard_router)
api_router.include_router(ratings_router)
api_router.include_router(certificates_router)
api_router.include_router(reports_router)
api_router.include_router(analytics_router)
api_router.include_router(notifications_router)
api_router.include_router(integrations_router)
api_router.include_router(public_router)
