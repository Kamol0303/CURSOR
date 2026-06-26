"""Stage 6 — Super Admin regression and per-role API access tests."""

from __future__ import annotations

import pytest

from app.core.rbac_pages import (
    ADMIN_DASHBOARD_PAGES,
    PARENT_PORTAL_PAGES,
    PORTAL_ONLY_ROLES,
    STUDENT_PORTAL_PAGES,
    TEACHER_PORTAL_PAGES,
    role_can_access_admin_page,
)

ROLE_TOKEN_KEYS: list[tuple[str, str]] = [
    ("super_admin", "token_super_admin"),
    ("hokimiyat_operator", "token_hokimiyat"),
    ("center_director", "token_director_a"),
    ("center_admin", "token_admin_a"),
    ("accountant", "token_accountant"),
    ("auditor", "token_auditor"),
    ("teacher", "token_teacher_a"),
    ("parent", "token_parent"),
    ("student", "token_student"),
]


async def _api_call(client, page, token: str):
    if page.api_method == "GET":
        return await client.get(page.api_path, headers={"Authorization": f"Bearer {token}"})
    if page.api_method == "POST":
        return await client.post(
            page.api_path,
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "nobody_exists", "new_password": "Test#ResetPass1!"},
        )
    raise ValueError(f"Unsupported method {page.api_method}")


@pytest.mark.integration
class TestSuperAdminRegression:
    async def test_super_admin_lists_all_centers(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/centers",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 200
        center_ids = {c["id"] for c in response.json()["data"]}
        assert str(fx["center_a"].id) in center_ids
        assert str(fx["center_b"].id) in center_ids

    async def test_super_admin_lists_cross_center_students(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 200
        student_ids = {s["id"] for s in response.json()["data"]}
        assert str(fx["student_a"].id) in student_ids
        assert str(fx["student_b"].id) in student_ids

    async def test_super_admin_dashboard_kpis_global(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/dashboard/kpis",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_centers"] >= 2

    async def test_super_admin_can_reveal_pinfl(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            f"/api/v1/students/{fx['student_b'].id}/reveal-pinfl",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 200

    async def test_super_admin_cannot_access_teacher_portal(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/teacher/me",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.parametrize("role,token_key", ROLE_TOKEN_KEYS, ids=lambda x: x[0])
@pytest.mark.parametrize("page", ADMIN_DASHBOARD_PAGES, ids=lambda p: p.key)
async def test_admin_page_api_access_by_role(api_client, security_fixtures, role, token_key, page):
    fx = security_fixtures
    token = fx[token_key]
    expected = role_can_access_admin_page(role, page)
    response = await _api_call(api_client, page, token)

    if expected:
        assert response.status_code != 403, f"{role} should access {page.key}"
    else:
        assert response.status_code == 403, f"{role} must not access {page.key}"


@pytest.mark.integration
@pytest.mark.parametrize("role,token_key", ROLE_TOKEN_KEYS, ids=lambda x: x[0])
async def test_teacher_portal_access(api_client, security_fixtures, role, token_key):
    fx = security_fixtures
    token = fx[token_key]
    for page in TEACHER_PORTAL_PAGES:
        response = await api_client.get(page.api_path, headers={"Authorization": f"Bearer {token}"})
        if role == "teacher":
            assert response.status_code == 200, f"teacher should access {page.key}"
        else:
            assert response.status_code == 403, f"{role} must not access teacher {page.key}"


@pytest.mark.integration
async def test_parent_portal_access(api_client, security_fixtures):
    fx = security_fixtures
    page = PARENT_PORTAL_PAGES[0]
    allowed = await api_client.get(
        page.api_path,
        headers={"Authorization": f"Bearer {fx['token_parent']}"},
    )
    assert allowed.status_code == 200

    denied = await api_client.get(
        page.api_path,
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    assert denied.status_code == 403


@pytest.mark.integration
async def test_student_portal_access(api_client, security_fixtures):
    fx = security_fixtures
    page = STUDENT_PORTAL_PAGES[0]
    allowed = await api_client.get(
        page.api_path,
        headers={"Authorization": f"Bearer {fx['token_student']}"},
    )
    assert allowed.status_code == 200

    denied = await api_client.get(
        page.api_path,
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert denied.status_code == 403


@pytest.mark.integration
async def test_portal_roles_denied_admin_dashboard(api_client, security_fixtures):
    fx = security_fixtures
    for role in PORTAL_ONLY_ROLES:
        token_key = {
            "teacher": "token_teacher_a",
            "parent": "token_parent",
            "student": "token_student",
        }[role]
        response = await api_client.get(
            "/api/v1/dashboard/kpis",
            headers={"Authorization": f"Bearer {fx[token_key]}"},
        )
        assert response.status_code == 403
