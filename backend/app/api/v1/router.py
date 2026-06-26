from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.auth import router as auth_router
from app.api.v1.centers import router as centers_router
from app.api.v1.certificates import router as certificates_router
from app.api.v1.courses import router as courses_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.external import router as external_router
from app.api.v1.exams import router as exams_router
from app.api.v1.geography import router as geography_router
from app.api.v1.files import router as files_router
from app.api.v1.grades import router as grades_router
from app.api.v1.groups import groups_router, payments_router
from app.api.v1.subjects import router as subjects_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.messages import router as messages_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.parent import router as parent_router
from app.api.v1.public import router as public_router
from app.api.v1.ratings import router as ratings_router
from app.api.v1.reports import router as reports_router
from app.api.v1.students import router as students_router
from app.api.v1.student import router as student_router
from app.api.v1.teacher import router as teacher_router
from app.api.v1.teachers import router as teachers_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(centers_router)
api_router.include_router(students_router)
api_router.include_router(teachers_router)
api_router.include_router(groups_router)
api_router.include_router(subjects_router)
api_router.include_router(attendance_router)
api_router.include_router(payments_router)
api_router.include_router(dashboard_router)
api_router.include_router(exams_router)
api_router.include_router(grades_router)
api_router.include_router(courses_router)
api_router.include_router(geography_router)
api_router.include_router(files_router)
api_router.include_router(ratings_router)
api_router.include_router(certificates_router)
api_router.include_router(reports_router)
api_router.include_router(analytics_router)
api_router.include_router(notifications_router)
api_router.include_router(messages_router)
api_router.include_router(parent_router)
api_router.include_router(student_router)
api_router.include_router(teacher_router)
api_router.include_router(external_router)
api_router.include_router(integrations_router)
api_router.include_router(public_router)
