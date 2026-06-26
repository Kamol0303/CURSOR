"""Group enroll / unenroll tests."""

import pytest


@pytest.mark.integration
async def test_director_can_enroll_and_unenroll_student(api_client, security_fixtures):
    fx = security_fixtures
    student_id = str(fx["student_a"].id)
    group_id = str(fx["group_a"].id)

    enroll = await api_client.post(
        f"/api/v1/groups/{group_id}/enroll",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        json={"student_id": student_id},
    )
    assert enroll.status_code == 200

    members = await api_client.get(
        f"/api/v1/groups/{group_id}/enrollments",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    assert members.status_code == 200
    ids = {m["student_id"] for m in members.json()["data"]}
    assert student_id in ids

    unenroll = await api_client.delete(
        f"/api/v1/groups/{group_id}/enroll/{student_id}",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    assert unenroll.status_code == 200

    members_after = await api_client.get(
        f"/api/v1/groups/{group_id}/enrollments",
        headers={"Authorization": f"Bearer {fx['token_director_a']}"},
    )
    ids_after = {m["student_id"] for m in members_after.json()["data"]}
    assert student_id not in ids_after


@pytest.mark.integration
async def test_teacher_cannot_enroll_student(api_client, security_fixtures):
    fx = security_fixtures
    response = await api_client.post(
        f"/api/v1/groups/{fx['group_a'].id}/enroll",
        headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        json={"student_id": str(fx["student_a"].id)},
    )
    assert response.status_code == 403


@pytest.mark.integration
async def test_batch_enroll_students(api_client, security_fixtures, db_session):
    from app.models.education import Student

    fx = security_fixtures
    extra = Student(center_id=fx["center_a"].id, full_name="Batch Student", grade="8")
    db_session.add(extra)
    await db_session.commit()
    await db_session.refresh(extra)

    response = await api_client.post(
        f"/api/v1/groups/{fx['group_a'].id}/enroll/batch",
        headers={"Authorization": f"Bearer {fx['token_admin_a']}"},
        json={"student_ids": [str(fx["student_a"].id), str(extra.id)]},
    )
    assert response.status_code == 200
    assert response.json()["data"]["enrolled"] == 2
