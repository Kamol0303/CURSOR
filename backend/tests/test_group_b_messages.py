"""Group B — internal messages recipient selection and monitoring."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.core.permissions import ROLE_PERMISSIONS
from app.core.security import hash_password
from app.models.identity import Role, User


class TestGroupBPermissions:
    def test_only_super_admin_can_monitor_messages(self):
        assert "messages.monitor" in ROLE_PERMISSIONS["super_admin"]
        assert "messages.monitor" not in ROLE_PERMISSIONS["center_director"]
        assert "messages.monitor" not in ROLE_PERMISSIONS["teacher"]

    def test_director_can_send_messages(self):
        assert "messages.send" in ROLE_PERMISSIONS["center_director"]
        assert "messages.read" in ROLE_PERMISSIONS["center_director"]


@pytest.mark.integration
class TestGroupBMessagesApi:
    async def test_list_recipients_scoped_to_center(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/messages/recipients",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert response.status_code == 200
        ids = {item["id"] for item in response.json()["data"]}
        assert str(fx["teacher_a"].id) in ids
        assert str(fx["admin_a"].id) in ids

    async def test_recipients_search_by_teacher_name(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/messages/recipients?search=SecTest Teacher",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert any("SecTest Teacher" in item["display_name"] for item in data)

    async def test_cross_center_send_forbidden(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        role_result = await db_session.execute(select(Role).where(Role.code == "teacher"))
        teacher_role = role_result.scalar_one()

        other_teacher_user = User(
            username=f"other_center_teacher_{fx['center_b'].id.hex[:8]}",
            password_hash=hash_password("Test#OtherTeacher1"),
            role_id=teacher_role.id,
            center_id=fx["center_b"].id,
            is_active=True,
        )
        db_session.add(other_teacher_user)
        await db_session.commit()

        response = await api_client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "recipient_id": str(other_teacher_user.id),
                "title": "Test",
                "body": "Cross center attempt",
            },
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "CROSS_CENTER_FORBIDDEN"

    async def test_send_message_within_center(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "recipient_id": str(fx["teacher_a"].id),
                "title": "Hello",
                "body": "Center message",
            },
        )
        assert response.status_code == 201
        assert response.json()["data"]["recipient_name"] == "SecTest Teacher A"

    async def test_super_admin_can_monitor_messages(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/messages/monitor",
            headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json()["data"], list)

    async def test_director_cannot_monitor_messages(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/messages/monitor",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert response.status_code == 403

    async def test_teacher_cannot_monitor_messages(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/messages/monitor",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert response.status_code == 403
