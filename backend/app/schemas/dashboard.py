from pydantic import BaseModel


class DashboardKpi(BaseModel):
    key: str
    value: int
    change_percent: float | None = None


class DashboardResponse(BaseModel):
    total_centers: int
    total_students: int
    total_teachers: int
    total_subjects: int
    active_centers: int
    new_registrations_month: int
    license_expiring_30_days: int
    kpis: list[DashboardKpi]
