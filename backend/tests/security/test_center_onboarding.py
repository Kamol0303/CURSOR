"""Center onboarding flow tests."""

import pytest

from app.core.security import hash_password


@pytest.mark.integration
async def test_super_admin_can_onboard_center(api_client, security_fixtures):
    fx = security_fixtures
    suffix = fx["center_a"].name[-8:]
    response = await api_client.post(
        "/api/v1/centers/onboard",
        headers={"Authorization": f"Bearer {fx['token_super_admin']}"},
        json={
            "name": f"Onboard Test {suffix}",
            "director_username": f"dir_new_{suffix}",
            "director_full_name": "Yangi Direktor",
            "director_email": f"dir_{suffix}@example.com",
            "director_phone": "+998901234567",
        },
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["director_username"] == f"dir_new_{suffix}"
    assert len(data["temporary_password"]) >= 12
    assert data["center"]["profile_completed"] is False


@pytest.mark.integration
async def test_hokimiyat_cannot_onboard_center(api_client, security_fixtures):
    fx = security_fixtures
    suffix = fx["center_a"].name[-8:]
    response = await api_client.post(
        "/api/v1/centers/onboard",
        headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        json={
            "name": f"Onboard Blocked {suffix}",
            "director_username": f"dir_blk_{suffix}",
            "director_full_name": "Blocked",
            "director_email": f"blk_{suffix}@example.com",
            "director_phone": "+998901234567",
        },
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_hokimiyat_cannot_update_center(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.patch(
        f"/api/v1/centers/{fx['center_a'].id}",
        headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        json={"phone": "+998909999999"},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_director_must_complete_profile(api_client, security_fixtures, db_session):
    from app.models.identity import Role, TrainingCenter, User
    from sqlalchemy import select

    fx = security_fixtures
    roles = await db_session.execute(select(Role).where(Role.code == "center_director"))
    role = roles.scalar_one()

    center = TrainingCenter(name="Incomplete Center", profile_completed=False, is_active=True)
    db_session.add(center)
    await db_session.flush()

    director = User(
        username="incomplete_dir",
        password_hash=hash_password("Test#Incomplete1"),
        role_id=role.id,
        center_id=center.id,
        is_active=True,
        must_change_password=False,
    )
    db_session.add(director)
    await db_session.commit()
    await db_session.refresh(director, attribute_names=["role"])

    from app.core.security import create_access_token
    from app.core.permissions import ROLE_PERMISSIONS

    token, _, _ = create_access_token(
        user_id=director.id,
        role=director.role.code,
        center_id=director.center_id,
        permissions=ROLE_PERMISSIONS["center_director"],
        locale="uz",
    )

    status = await api_client.get(
        "/api/v1/centers/onboarding/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert status.status_code == 200
    assert status.json()["data"]["profile_completed"] is False

    complete = await api_client.post(
        "/api/v1/centers/onboarding/complete",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "stir": "123456789",
            "director_name": "Direktor Test",
            "phone": "+998901112233",
            "address": "Toshkent sh., Test ko'chasi 1",
            "center_type": "private",
        },
    )
    assert complete.status_code == 200
    assert complete.json()["data"]["profile_completed"] is True
