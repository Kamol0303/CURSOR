from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import get_user_center_filter
from app.models.education import Student, Subject, Teacher
from app.models.identity import TrainingCenter, User
from app.schemas.dashboard import DashboardKpi, DashboardResponse


async def get_dashboard(db: AsyncSession, user: User) -> DashboardResponse:
    center_filter = get_user_center_filter(user)
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    expiry_threshold = now + timedelta(days=30)

    centers_q = select(func.count()).select_from(TrainingCenter).where(TrainingCenter.deleted_at.is_(None))
    if center_filter:
        centers_q = centers_q.where(TrainingCenter.id == center_filter)
    total_centers = (await db.execute(centers_q)).scalar() or 0

    active_q = centers_q.where(TrainingCenter.is_active.is_(True))
    active_centers = (await db.execute(active_q)).scalar() or 0

    students_q = select(func.count()).select_from(Student).where(Student.deleted_at.is_(None))
    if center_filter:
        students_q = students_q.where(Student.center_id == center_filter)
    total_students = (await db.execute(students_q)).scalar() or 0

    teachers_q = select(func.count()).select_from(Teacher).where(
        Teacher.deleted_at.is_(None), Teacher.is_active.is_(True)
    )
    if center_filter:
        teachers_q = teachers_q.where(Teacher.center_id == center_filter)
    total_teachers = (await db.execute(teachers_q)).scalar() or 0

    subjects_q = select(func.count()).select_from(Subject).where(
        Subject.deleted_at.is_(None), Subject.is_active.is_(True)
    )
    total_subjects = (await db.execute(subjects_q)).scalar() or 0

    new_reg_q = select(func.count()).select_from(Student).where(
        Student.deleted_at.is_(None), Student.created_at >= month_start
    )
    if center_filter:
        new_reg_q = new_reg_q.where(Student.center_id == center_filter)
    new_registrations = (await db.execute(new_reg_q)).scalar() or 0

    expiring_q = select(func.count()).select_from(TrainingCenter).where(
        TrainingCenter.deleted_at.is_(None),
        TrainingCenter.license_expiry.isnot(None),
        TrainingCenter.license_expiry <= expiry_threshold,
        TrainingCenter.license_expiry >= now,
    )
    if center_filter:
        expiring_q = expiring_q.where(TrainingCenter.id == center_filter)
    license_expiring = (await db.execute(expiring_q)).scalar() or 0

    kpis = [
        DashboardKpi(key="total_centers", value=total_centers),
        DashboardKpi(key="total_students", value=total_students),
        DashboardKpi(key="total_teachers", value=total_teachers),
        DashboardKpi(key="total_subjects", value=total_subjects),
        DashboardKpi(key="active_centers", value=active_centers),
        DashboardKpi(key="new_registrations_month", value=new_registrations),
        DashboardKpi(key="license_expiring_30_days", value=license_expiring),
    ]

    return DashboardResponse(
        total_centers=total_centers,
        total_students=total_students,
        total_teachers=total_teachers,
        total_subjects=total_subjects,
        active_centers=active_centers,
        new_registrations_month=new_registrations,
        license_expiring_30_days=license_expiring,
        kpis=kpis,
    )
