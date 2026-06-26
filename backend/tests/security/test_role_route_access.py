"""API route access denied for roles without required permissions."""

import pytest


@pytest.mark.integration
async def test_auditor_cannot_list_messages(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/messages",
        headers={"Authorization": f"Bearer {fx['token_auditor']}"},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_hokimiyat_cannot_list_messages(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/messages",
        headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_center_admin_cannot_list_teachers_for_write_ops(api_client, security_fixtures):
    """center_admin has teachers.read — verify they cannot create teachers."""
    fx = security_fixtures
    response = await api_client.post(
        "/api/v1/teachers",
        headers={"Authorization": f"Bearer {fx['token_admin_a']}"},
        json={"full_name": "Blocked", "phone": "+998901234567"},
    )
    assert response.status_code == 403
