"""Group H — assign primary teacher to a group."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.core.permissions import ROLE_PERMISSIONS
from app.models.education import Group, Subject


class TestGroupHPermissions:
    def test_director_can_update_groups(self):
        assert "groups.update" in ROLE_PERMISSIONS["center_director"]

    def test_center_admin_can_update_groups(self):
        assert "groups.update" in ROLE_PERMISSIONS["center_admin"]

    def test_teacher_cannot_update_groups(self):
        assert "groups.update" not in ROLE_PERMISSIONS["teacher"]


@pytest.mark.integration
class TestGroupHTeacherAssignment:
    async def test_assign_teacher_to_group(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        subject = (await db_session.execute(select(Subject).limit(1))).scalar_one()

        create_res = await api_client.post(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "subject_id": str(subject.id),
                "name": "Group H Test",
            },
        )
        assert create_res.status_code == 201
        group_id = create_res.json()["data"]["id"]

        assign_res = await api_client.patch(
            f"/api/v1/groups/{group_id}/assign-teacher",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"teacher_id": str(fx["teacher_record_a"].id)},
        )
        assert assign_res.status_code == 200
        assert assign_res.json()["data"]["teacher_name"] == fx["teacher_record_a"].full_name

        teacher_groups = await api_client.get(
            "/api/v1/teacher/groups",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert teacher_groups.status_code == 200
        assert group_id in {g["id"] for g in teacher_groups.json()["data"]}

    async def test_cannot_assign_teacher_from_other_center(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        subject = (await db_session.execute(select(Subject).limit(1))).scalar_one()

        create_res = await api_client.post(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "subject_id": str(subject.id),
                "name": "Group H Cross Center",
            },
        )
        group_id = create_res.json()["data"]["id"]

        assign_res = await api_client.patch(
            f"/api/v1/groups/{group_id}/assign-teacher",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"teacher_id": str(fx["teacher_record_b"].id)},
        )
        assert assign_res.status_code == 422
        assert assign_res.json()["detail"]["code"] == "CENTER_MISMATCH"

    async def test_teacher_cannot_assign_teacher(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.patch(
            f"/api/v1/groups/{fx['group_a'].id}/assign-teacher",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={"teacher_id": str(fx["teacher_record_a"].id)},
        )
        assert response.status_code == 403

    async def test_search_teachers_by_name(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/teachers?search=SecTest Teacher",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert response.status_code == 200
        names = [t["full_name"] for t in response.json()["data"]]
        assert any("SecTest Teacher" in name for name in names)

    async def test_reassign_teacher_updates_group(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        group = await db_session.get(Group, fx["group_a"].id)
        assert group is not None
        group.teacher_id = None
        await db_session.commit()

        assign_res = await api_client.patch(
            f"/api/v1/groups/{fx['group_a'].id}/assign-teacher",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"teacher_id": str(fx["teacher_record_a"].id)},
        )
        assert assign_res.status_code == 200
        assert assign_res.json()["data"]["teacher_id"] == str(fx["teacher_record_a"].id)
