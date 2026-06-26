from pydantic import BaseModel


class DashboardKpi(BaseModel):
    key: str
    value: int | float
    change_percent: float | None = None


class TimeSeriesPoint(BaseModel):
    label: str
    value: int | float


class DashboardResponse(BaseModel):
    total_centers: int
    total_students: int
    active_students: int
    total_teachers: int
    total_subjects: int
    total_courses: int
    active_centers: int
    new_registrations_month: int
    license_expiring_30_days: int
    monthly_revenue: float
    debtors_count: int
    kpis: list[DashboardKpi]
    daily_stats: list[TimeSeriesPoint]
    weekly_stats: list[TimeSeriesPoint]
    monthly_stats: list[TimeSeriesPoint]
