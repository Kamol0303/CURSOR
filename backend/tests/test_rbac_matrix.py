"""Parametrized RBAC matrix unit tests (no database required)."""

import pytest

from app.core.permissions import ROLE_PERMISSIONS
from app.core.rbac_pages import (
    ADMIN_DASHBOARD_PAGES,
    PARENT_PORTAL_PAGES,
    PORTAL_ONLY_ROLES,
    STUDENT_PORTAL_PAGES,
    TEACHER_PORTAL_PAGES,
    build_admin_access_matrix,
    role_can_access_admin_page,
)


@pytest.mark.parametrize("page", ADMIN_DASHBOARD_PAGES, ids=lambda p: p.key)
@pytest.mark.parametrize(
    "role",
    [
        "super_admin",
        "hokimiyat_operator",
        "center_director",
        "center_admin",
        "accountant",
        "auditor",
        "teacher",
        "parent",
        "student",
    ],
)
def test_admin_page_access_matches_permissions(role: str, page) -> None:
    perms = ROLE_PERMISSIONS.get(role, [])
    if role in PORTAL_ONLY_ROLES:
        assert role_can_access_admin_page(role, page) is False
    else:
        assert role_can_access_admin_page(role, page) == (page.permission in perms)


def test_super_admin_has_full_admin_nav() -> None:
    matrix = build_admin_access_matrix()["super_admin"]
    assert all(matrix.values()), "super_admin must access every admin dashboard page"


def test_teacher_portal_pages_require_teacher_portal_permission() -> None:
    assert "teacher.portal" in ROLE_PERMISSIONS["teacher"]
    for page in TEACHER_PORTAL_PAGES:
        assert page.permission == "teacher.portal"


def test_portal_only_roles_blocked_from_admin_dashboard() -> None:
    for role in PORTAL_ONLY_ROLES:
        matrix = build_admin_access_matrix()[role]
        assert not any(matrix.values())


def test_parent_portal_permission_present() -> None:
    assert "students.read" in ROLE_PERMISSIONS["parent"]
    assert len(PARENT_PORTAL_PAGES) >= 1


def test_student_portal_permission_present() -> None:
    assert "students.read" in ROLE_PERMISSIONS["student"]
    assert len(STUDENT_PORTAL_PAGES) >= 1
