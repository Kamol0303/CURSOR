from pydantic import BaseModel


class CenterCertificateStat(BaseModel):
    center_id: str
    center_name: str
    certificate_count: int


class TrendPoint(BaseModel):
    label: str
    value: int
    is_forecast: bool = False


class OperatorDashboardResponse(BaseModel):
    active_centers: int
    total_teachers: int
    total_students: int
    certificates_ytd: int
    total_courses: int
    certificates_by_center: list[CenterCertificateStat]
    certificates_by_center_total: int
    student_trend: list[TrendPoint]
    certificate_trend: list[TrendPoint]


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
