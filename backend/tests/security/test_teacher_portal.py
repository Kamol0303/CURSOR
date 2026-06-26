"""Teacher portal API access tests."""

import pytest


@pytest.mark.integration
async def test_teacher_can_access_portal_me(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/teacher/me",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["full_name"] == fx["teacher_record_a"].full_name
    assert data["center_id"] == str(fx["center_a"].id)


@pytest.mark.integration
async def test_teacher_can_list_own_groups(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/teacher/groups",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert response.status_code == 200
    group_ids = {g["id"] for g in response.json()["data"]}
    assert str(fx["group_a"].id) in group_ids
    assert str(fx["group_b"].id) not in group_ids


@pytest.mark.integration
async def test_teacher_can_list_group_students(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        f"/api/v1/teacher/groups/{fx['group_a'].id}/students",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert response.status_code == 200
    student_ids = {m["student_id"] for m in response.json()["data"]}
    assert str(fx["student_a"].id) in student_ids


@pytest.mark.integration
async def test_teacher_cannot_access_other_center_group_students(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        f"/api/v1/teacher/groups/{fx['group_b'].id}/students",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_teacher_cannot_access_dashboard_kpis(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/dashboard/kpis",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_non_teacher_cannot_access_teacher_portal(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.get(
        "/api/v1/teacher/me",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    assert response.status_code == 403
