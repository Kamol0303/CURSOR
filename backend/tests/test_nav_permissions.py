"""Role × route permission matrix alignment tests."""

from app.core.permissions import NAV_PERMISSIONS, ROLE_PERMISSIONS


def test_nav_permissions_used_by_at_least_one_role():
    for perm in NAV_PERMISSIONS.values():
        assert any(perm in perms for perms in ROLE_PERMISSIONS.values()), (
            f"No role has nav permission {perm!r}"
        )


def test_security_nav_requires_password_reset():
    assert NAV_PERMISSIONS["security"] == "users.password_reset"


def test_auditor_cannot_access_messages():
    assert "messages.read" not in ROLE_PERMISSIONS["auditor"]


def test_accountant_cannot_access_teachers():
    assert "teachers.read" not in ROLE_PERMISSIONS["accountant"]


def test_accountant_cannot_access_certificates_nav():
    assert "ratings.view" not in ROLE_PERMISSIONS["accountant"]


def test_center_admin_cannot_reset_passwords():
    assert "users.password_reset" not in ROLE_PERMISSIONS["center_admin"]


def test_teacher_has_portal_not_dashboard():
    teacher = ROLE_PERMISSIONS["teacher"]
    assert "teacher.portal" in teacher
    assert "dashboard.view" not in teacher
