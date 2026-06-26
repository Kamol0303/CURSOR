"""Group D — teacher/student onboarding and parent SMS provisioning."""

from __future__ import annotations

import pytest

from app.services.credential_service import generate_temp_password, suggest_teacher_username


class TestGroupDCredentialHelpers:
    def test_generate_temp_password_meets_policy(self):
        from app.core.security import validate_password_policy

        password = generate_temp_password()
        assert not validate_password_policy(password)

    def test_suggest_teacher_username_uses_phone(self):
        assert suggest_teacher_username("Dilnoza Karimova", "+998901234567") == "+998901234567"

    def test_suggest_teacher_username_from_name(self):
        username = suggest_teacher_username("Dilnoza Karimova", None)
        assert "dilnoza" in username


@pytest.mark.integration
class TestGroupDOnboardingApi:
    async def test_create_teacher_returns_credentials(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/teachers",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "full_name": "Group D Teacher",
                "phone": "+998909999001",
                "specialization": "English",
            },
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["credentials"]["login"]
        assert data["credentials"]["temporary_password"]
        assert data["teacher"]["full_name"] == "Group D Teacher"

    async def test_create_student_with_parent_provisions_account(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        from sqlalchemy import select
        from app.models.identity import User

        phone = "+998909999002"
        response = await api_client.post(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "full_name": "Group D Student",
                "guardian_name": "Group D Parent",
                "guardian_phone": phone,
            },
        )
        assert response.status_code == 201
        parent = response.json()["data"]["parent"]
        assert parent["created"] is True
        assert parent["sms_sent"] is True

        parent_user = (
            await db_session.execute(
                select(User).where(User.phone == phone, User.role.has(code="parent"))
            )
        ).scalar_one_or_none()
        assert parent_user is not None

    async def test_second_child_links_existing_parent_without_sms(self, api_client, security_fixtures):
        fx = security_fixtures
        phone = "+998909999003"
        first = await api_client.post(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "full_name": "Child One",
                "guardian_name": "Shared Parent",
                "guardian_phone": phone,
            },
        )
        assert first.status_code == 201

        second = await api_client.post(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "full_name": "Child Two",
                "guardian_name": "Shared Parent",
                "guardian_phone": phone,
            },
        )
        assert second.status_code == 201
        parent = second.json()["data"]["parent"]
        assert parent["created"] is False
        assert parent["sms_sent"] is False

    async def test_student_no_passport_requires_photo(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "full_name": "No Photo Student",
                "no_passport": True,
            },
        )
        assert response.status_code == 422
