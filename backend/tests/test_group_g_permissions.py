"""Group G — role-based UI restrictions and credential issuance."""

from __future__ import annotations

import pytest

from app.core.permissions import ROLE_PERMISSIONS


class TestGroupGPaymentsAccess:
    def test_teacher_cannot_read_payments(self):
        assert "payments.read" not in ROLE_PERMISSIONS["teacher"]

    def test_parent_cannot_read_payments(self):
        assert "payments.read" not in ROLE_PERMISSIONS["parent"]

    def test_auditor_cannot_read_payments(self):
        assert "payments.read" not in ROLE_PERMISSIONS["auditor"]

    def test_hokimiyat_cannot_read_payments(self):
        assert "payments.read" not in ROLE_PERMISSIONS["hokimiyat_operator"]

    def test_director_can_read_payments(self):
        assert "payments.read" in ROLE_PERMISSIONS["center_director"]

    def test_accountant_can_read_payments(self):
        assert "payments.read" in ROLE_PERMISSIONS["accountant"]


class TestGroupGAttendanceAccess:
    def test_hokimiyat_cannot_mark_attendance(self):
        assert "attendance.mark" not in ROLE_PERMISSIONS["hokimiyat_operator"]

    def test_hokimiyat_can_read_attendance(self):
        assert "attendance.read" in ROLE_PERMISSIONS["hokimiyat_operator"]

    def test_teacher_can_mark_attendance(self):
        assert "attendance.mark" in ROLE_PERMISSIONS["teacher"]


class TestGroupGCredentialIssuance:
    def test_super_admin_can_issue_credentials(self):
        assert "security.credentials.issue" in ROLE_PERMISSIONS["super_admin"]

    def test_director_can_issue_credentials(self):
        assert "security.credentials.issue" in ROLE_PERMISSIONS["center_director"]

    def test_center_admin_cannot_issue_credentials(self):
        assert "security.credentials.issue" not in ROLE_PERMISSIONS["center_admin"]

    def test_teacher_cannot_issue_credentials(self):
        assert "security.credentials.issue" not in ROLE_PERMISSIONS["teacher"]


@pytest.mark.integration
class TestGroupGApiEnforcement:
    async def test_hokimiyat_cannot_list_payments(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/payments",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_teacher_cannot_list_payments(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/payments",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert response.status_code == 403

    async def test_hokimiyat_cannot_mark_attendance(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/attendance/mark",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
            json={
                "student_id": str(fx["student_a"].id),
                "group_id": str(fx["group_a"].id),
                "session_date": "2026-01-15",
                "status": "present",
            },
        )
        assert response.status_code == 403

    async def test_hokimiyat_can_read_attendance(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            f"/api/v1/attendance?group_id={fx['group_a'].id}&session_date=2026-01-15",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 200

    async def test_hokimiyat_cannot_create_qr_session(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            f"/api/v1/attendance/qr-session?group_id={fx['group_a'].id}&session_date=2026-01-15",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert response.status_code == 403

    async def test_director_can_issue_credentials(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/auth/admin/issue-credentials",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"target_user_id": str(fx["teacher_a"].id)},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["temporary_password"]
        assert data["must_change_password"] is True

    async def test_teacher_cannot_issue_credentials(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/auth/admin/issue-credentials",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={"target_user_id": str(fx["admin_a"].id)},
        )
        assert response.status_code == 403
