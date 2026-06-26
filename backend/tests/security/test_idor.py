"""Security tests for horizontal/vertical privilege escalation (Section 2A.4, 16.5)."""

import pytest

from app.core.permissions import MANDATORY_MFA_ROLES


@pytest.mark.integration
async def test_idor_center_director_cannot_read_other_center_student(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        f"/api/v1/students/{fx['student_b'].id}",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


@pytest.mark.integration
async def test_teacher_cannot_reveal_pinfl(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.post(
        f"/api/v1/students/{fx['student_a'].id}/reveal-pinfl",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_auditor_can_reveal_pinfl(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.post(
        f"/api/v1/students/{fx['student_b'].id}/reveal-pinfl",
        headers={"Authorization": f"Bearer {fx['token_auditor']}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["jshshir"] == "12345678901234"


@pytest.mark.integration
async def test_parent_sees_only_linked_children(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/parent/children",
        headers={"Authorization": f"Bearer {fx['token_parent']}"},
    )
    assert response.status_code == 200
    children = response.json()["data"]
    ids = {c["id"] for c in children}
    assert str(fx["student_a"].id) in ids
    assert str(fx["student_b"].id) not in ids


@pytest.mark.integration
async def test_student_list_masks_pinfl(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {fx['token_auditor']}"},
    )
    assert response.status_code == 200
    for student in response.json()["data"]:
        masked = student.get("jshshir_masked")
        if masked:
            assert "12345678901234" not in masked


def test_mfa_mandatory_roles_defined():
    assert "super_admin" in MANDATORY_MFA_ROLES
    assert "center_director" in MANDATORY_MFA_ROLES
