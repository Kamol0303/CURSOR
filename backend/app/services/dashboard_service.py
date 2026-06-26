from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import get_user_center_filter
from app.models.academics import Course
from app.models.education import Enrollment, Student, Subject, Teacher
from app.models.identity import TrainingCenter, User
from app.models.operations import StudentPayment
from app.schemas.dashboard import DashboardKpi, DashboardResponse, TimeSeriesPoint


async def get_dashboard(db: AsyncSession, user: User) -> DashboardResponse:
    center_filter = get_user_center_filter(user)
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    expiry_threshold = now + timedelta(days=30)

    def _center_clause(model, column):
        if center_filter:
            return column == center_filter
        return True

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

    active_students_q = (
        select(func.count(func.distinct(Enrollment.student_id)))
        .select_from(Enrollment)
        .join(Student, Student.id == Enrollment.student_id)
        .where(Enrollment.status == "active", Student.deleted_at.is_(None))
    )
    if center_filter:
        active_students_q = active_students_q.where(Enrollment.center_id == center_filter)
    active_students = (await db.execute(active_students_q)).scalar() or 0

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

    courses_q = select(func.count()).select_from(Course).where(Course.deleted_at.is_(None), Course.is_active.is_(True))
    if center_filter:
        courses_q = courses_q.where(Course.center_id == center_filter)
    total_courses = (await db.execute(courses_q)).scalar() or 0

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

    revenue_q = select(func.coalesce(func.sum(StudentPayment.amount), 0)).where(
        StudentPayment.status == "paid",
        StudentPayment.paid_at.isnot(None),
        StudentPayment.paid_at >= month_start,
    )
    if center_filter:
        revenue_q = revenue_q.where(StudentPayment.center_id == center_filter)
    monthly_revenue = float((await db.execute(revenue_q)).scalar() or 0)

    debtors_q = select(func.count(func.distinct(StudentPayment.student_id))).where(
        StudentPayment.status.in_(["pending", "overdue"])
    )
    if center_filter:
        debtors_q = debtors_q.where(StudentPayment.center_id == center_filter)
    debtors_count = (await db.execute(debtors_q)).scalar() or 0

    daily_stats = await _registration_series(db, center_filter, days=7)
    weekly_stats = await _registration_series(db, center_filter, days=28, bucket_days=7)
    monthly_stats = await _registration_series(db, center_filter, days=180, bucket_days=30)

    kpis = [
        DashboardKpi(key="total_centers", value=total_centers),
        DashboardKpi(key="total_students", value=total_students),
        DashboardKpi(key="active_students", value=active_students),
        DashboardKpi(key="total_teachers", value=total_teachers),
        DashboardKpi(key="total_subjects", value=total_subjects),
        DashboardKpi(key="total_courses", value=total_courses),
        DashboardKpi(key="active_centers", value=active_centers),
        DashboardKpi(key="new_registrations_month", value=new_registrations),
        DashboardKpi(key="license_expiring_30_days", value=license_expiring),
        DashboardKpi(key="monthly_revenue", value=monthly_revenue),
        DashboardKpi(key="debtors_count", value=debtors_count),
    ]

    return DashboardResponse(
        total_centers=total_centers,
        total_students=total_students,
        active_students=active_students,
        total_teachers=total_teachers,
        total_subjects=total_subjects,
        total_courses=total_courses,
        active_centers=active_centers,
        new_registrations_month=new_registrations,
        license_expiring_30_days=license_expiring,
        monthly_revenue=monthly_revenue,
        debtors_count=debtors_count,
        kpis=kpis,
        daily_stats=daily_stats,
        weekly_stats=weekly_stats,
        monthly_stats=monthly_stats,
    )


async def _registration_series(
    db: AsyncSession,
    center_filter,
    *,
    days: int,
    bucket_days: int = 1,
) -> list[TimeSeriesPoint]:
    now = datetime.now(UTC)
    points: list[TimeSeriesPoint] = []
    for i in range(days // bucket_days):
        end = now - timedelta(days=i * bucket_days)
        start = end - timedelta(days=bucket_days)
        q = select(func.count()).select_from(Student).where(
            Student.deleted_at.is_(None),
            Student.created_at >= start,
            Student.created_at < end,
        )
        if center_filter:
            q = q.where(Student.center_id == center_filter)
        count = (await db.execute(q)).scalar() or 0
        points.append(TimeSeriesPoint(label=start.strftime("%m-%d"), value=count))
    points.reverse()
    return points
