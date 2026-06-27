"""Hokimiyat operator dashboard and restricted RBAC."""

from __future__ import annotations

import pytest

from app.core.permissions import ROLE_PERMISSIONS


class TestHokimiyatSidebarPermissions:
    perms = ROLE_PERMISSIONS["hokimiyat_operator"]

    def test_can_view_dashboard_and_analytics(self):
        assert "dashboard.view" in self.perms
        assert "dashboard.operator" in self.perms
        assert "analytics.view" in self.perms

    def test_read_only_monitoring_modules(self):
        assert "centers.read" in self.perms
        assert "students.read" in self.perms
        assert "teachers.read" in self.perms
        assert "certificates.read" in self.perms

    def test_operational_modules_removed(self):
        for perm in (
            "groups.read",
            "attendance.read",
            "payments.read",
            "exams.read",
            "grades.read",
            "ratings.view",
            "courses.read",
            "subjects.read",
            "centers.create",
            "messages.read",
        ):
            assert perm not in self.perms


@pytest.mark.integration
class TestHokimiyatApiRestrictions:
    async def test_hokimiyat_cannot_list_attendance(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            f"/api/v1/attendance?group_id={fx['group_a'].id}&session_date=2026-01-15",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_hokimiyat_cannot_list_groups(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_hokimiyat_cannot_list_exams(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/exams",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_hokimiyat_cannot_list_grades(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/grades",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_hokimiyat_cannot_list_ratings(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/ratings",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_hokimiyat_can_list_centers(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/centers",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 200

    async def test_hokimiyat_cannot_onboard_center(self, api_client, security_fixtures):
        fx = security_fixtures
        suffix = fx["center_a"].name[-8:]
        response = await api_client.post(
            "/api/v1/centers/onboard",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
            json={
                "name": f"Blocked Onboard {suffix}",
                "director_username": f"dir_blk_{suffix}",
                "director_full_name": "Blocked",
                "director_email": f"blk_{suffix}@example.com",
                "director_phone": "+998901234567",
            },
        )
        assert response.status_code == 403


@pytest.mark.integration
class TestOperatorDashboardEndpoint:
    async def test_hokimiyat_operator_summary(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/dashboard/operator-summary",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "active_centers" in data
        assert "total_students" in data
        assert "certificates_by_center" in data
        assert "student_trend" in data
        assert "monthly_revenue" not in data
        assert "debtors_count" not in data

    async def test_director_cannot_access_operator_summary(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/dashboard/operator-summary",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert response.status_code == 403

    async def test_super_admin_can_access_operator_summary(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/dashboard/operator-summary",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 200
