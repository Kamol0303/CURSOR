"""Canonical RBAC page definitions for admin and portal routes."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.permissions import NAV_PERMISSIONS, ROLE_PERMISSIONS

PORTAL_ONLY_ROLES = frozenset({"teacher", "student", "parent"})
STAFF_ROLES = frozenset(ROLE_PERMISSIONS.keys()) - PORTAL_ONLY_ROLES - {"external_api"}


@dataclass(frozen=True)
class PageDef:
    key: str
    path: str
    permission: str
    api_method: str
    api_path: str


ADMIN_DASHBOARD_PAGES: tuple[PageDef, ...] = (
    PageDef("dashboard", "/dashboard", NAV_PERMISSIONS["dashboard"], "GET", "/api/v1/dashboard/kpis"),
    PageDef(
        "operator_dashboard",
        "/dashboard",
        "dashboard.operator",
        "GET",
        "/api/v1/dashboard/operator-summary",
    ),
    PageDef("centers", "/dashboard/centers", NAV_PERMISSIONS["centers"], "GET", "/api/v1/centers"),
    PageDef("students", "/dashboard/students", NAV_PERMISSIONS["students"], "GET", "/api/v1/students"),
    PageDef("teachers", "/dashboard/teachers", NAV_PERMISSIONS["teachers"], "GET", "/api/v1/teachers"),
    PageDef("groups", "/dashboard/groups", NAV_PERMISSIONS["groups"], "GET", "/api/v1/groups"),
    PageDef("subjects", "/dashboard/subjects", NAV_PERMISSIONS["subjects"], "GET", "/api/v1/subjects"),
    PageDef("courses", "/dashboard/courses", NAV_PERMISSIONS["courses"], "GET", "/api/v1/courses"),
    PageDef("messages", "/dashboard/messages", NAV_PERMISSIONS["messages"], "GET", "/api/v1/messages"),
    PageDef("attendance", "/dashboard/attendance", NAV_PERMISSIONS["attendance"], "GET", "/api/v1/attendance"),
    PageDef("payments", "/dashboard/payments", NAV_PERMISSIONS["payments"], "GET", "/api/v1/payments"),
    PageDef("exams", "/dashboard/exams", NAV_PERMISSIONS["exams"], "GET", "/api/v1/exams"),
    PageDef("grades", "/dashboard/grades", NAV_PERMISSIONS["grades"], "GET", "/api/v1/grades"),
    PageDef("ratings", "/dashboard/ratings", NAV_PERMISSIONS["ratings"], "GET", "/api/v1/ratings"),
    PageDef(
        "certificates",
        "/dashboard/certificates",
        NAV_PERMISSIONS["certificates"],
        "GET",
        "/api/v1/certificates",
    ),
    PageDef("analytics", "/dashboard/analytics", NAV_PERMISSIONS["analytics"], "GET", "/api/v1/analytics/insights"),
    PageDef(
        "security",
        "/dashboard/security",
        NAV_PERMISSIONS["security"],
        "POST",
        "/api/v1/auth/admin/reset-password",
    ),
    PageDef("audit", "/dashboard/audit", NAV_PERMISSIONS["audit"], "GET", "/api/v1/audit-logs"),
)

TEACHER_PORTAL_PAGES: tuple[PageDef, ...] = (
    PageDef("dashboard", "/teacher/dashboard", "teacher.portal", "GET", "/api/v1/teacher/me"),
    PageDef("groups", "/teacher/groups", "teacher.portal", "GET", "/api/v1/teacher/groups"),
    PageDef("schedule", "/teacher/schedule", "teacher.portal", "GET", "/api/v1/teacher/schedule"),
)

PARENT_PORTAL_PAGES: tuple[PageDef, ...] = (
    PageDef("dashboard", "/parent/dashboard", "students.read", "GET", "/api/v1/parent/children"),
)

STUDENT_PORTAL_PAGES: tuple[PageDef, ...] = (
    PageDef("dashboard", "/student/dashboard", "students.read", "GET", "/api/v1/student/me"),
)


def role_can_access_admin_page(role: str, page: PageDef) -> bool:
    if role in PORTAL_ONLY_ROLES:
        return False
    return page.permission in ROLE_PERMISSIONS.get(role, [])


def build_admin_access_matrix() -> dict[str, dict[str, bool]]:
    matrix: dict[str, dict[str, bool]] = {}
    for role in sorted(STAFF_ROLES):
        matrix[role] = {page.key: role_can_access_admin_page(role, page) for page in ADMIN_DASHBOARD_PAGES}
    for role in sorted(PORTAL_ONLY_ROLES):
        matrix[role] = {page.key: False for page in ADMIN_DASHBOARD_PAGES}
    return matrix
