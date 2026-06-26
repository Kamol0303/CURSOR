"""Group C — courses and subjects full CRUD."""

from __future__ import annotations

import pytest

from app.core.permissions import ROLE_PERMISSIONS
from app.services import file_service


class TestGroupCPermissions:
    def test_hokimiyat_can_manage_subjects(self):
        perms = ROLE_PERMISSIONS["hokimiyat_operator"]
        assert "subjects.create" in perms
        assert "subjects.delete" in perms

    def test_director_can_read_subjects_not_create(self):
        perms = ROLE_PERMISSIONS["center_director"]
        assert "subjects.read" in perms
        assert "subjects.create" not in perms

    def test_center_admin_can_manage_courses(self):
        perms = ROLE_PERMISSIONS["center_admin"]
        assert "courses.create" in perms
        assert "courses.update" in perms
        assert "courses.delete" in perms

    def test_teacher_cannot_manage_courses(self):
        perms = ROLE_PERMISSIONS["teacher"]
        assert "courses.read" in perms
        assert "courses.create" not in perms


class TestGroupCFilePolicyUnchanged:
    def test_certificate_mimes_still_defined(self):
        assert "application/pdf" in file_service.CERTIFICATE_MIMES


@pytest.mark.integration
class TestGroupCSubjectsApi:
    async def test_create_list_update_delete_subject(self, api_client, security_fixtures):
        fx = security_fixtures
        create_res = await api_client.post(
            "/api/v1/subjects",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
            json={
                "name_uz": "Group C Fan",
                "name_ru": "Group C Fan RU",
                "name_en": "Group C Subject",
            },
        )
        assert create_res.status_code == 201
        subject_id = create_res.json()["data"]["id"]

        list_res = await api_client.get(
            "/api/v1/subjects",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert list_res.status_code == 200
        ids = [item["id"] for item in list_res.json()["data"]]
        assert subject_id in ids

        update_res = await api_client.patch(
            f"/api/v1/subjects/{subject_id}",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
            json={"name_uz": "Group C Fan Updated"},
        )
        assert update_res.status_code == 200
        assert update_res.json()["data"]["name_uz"] == "Group C Fan Updated"

        delete_res = await api_client.delete(
            f"/api/v1/subjects/{subject_id}",
            headers={"Authorization": f"Bearer {fx['token_hokimiyat']}"},
        )
        assert delete_res.status_code == 200

    async def test_director_cannot_create_subject(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/subjects",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"name_uz": "Blocked", "name_ru": "Blocked", "name_en": "Blocked"},
        )
        assert response.status_code == 403


@pytest.mark.integration
class TestGroupCCoursesApi:
    async def test_course_crud_with_lessons(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        from sqlalchemy import select
        from app.models.education import Subject

        subject = (await db_session.execute(select(Subject).limit(1))).scalar_one()

        create_res = await api_client.post(
            "/api/v1/courses",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "center_id": str(fx["center_a"].id),
                "subject_id": str(subject.id),
                "name": "Group C Course",
                "description": "Test course",
                "price": 500000,
                "duration_weeks": 12,
            },
        )
        assert create_res.status_code == 201
        course_id = create_res.json()["data"]["id"]

        get_res = await api_client.get(
            f"/api/v1/courses/{course_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert get_res.status_code == 200
        assert get_res.json()["data"]["name"] == "Group C Course"

        patch_res = await api_client.patch(
            f"/api/v1/courses/{course_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"name": "Group C Course Updated", "is_active": False},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["data"]["is_active"] is False

        lesson_res = await api_client.post(
            f"/api/v1/courses/{course_id}/lessons",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"title": "Lesson 1"},
        )
        assert lesson_res.status_code == 201
        lesson_id = lesson_res.json()["data"]["id"]

        lesson_patch = await api_client.patch(
            f"/api/v1/courses/{course_id}/lessons/{lesson_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"title": "Lesson 1 Updated"},
        )
        assert lesson_patch.status_code == 200

        delete_lesson = await api_client.delete(
            f"/api/v1/courses/{course_id}/lessons/{lesson_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert delete_lesson.status_code == 200

        delete_course = await api_client.delete(
            f"/api/v1/courses/{course_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        assert delete_course.status_code == 200
