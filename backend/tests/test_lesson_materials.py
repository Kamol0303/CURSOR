"""Lesson material generation and teacher subject assignment tests."""

from __future__ import annotations

import pytest

from app.core.permissions import ROLE_PERMISSIONS
from app.models.education import Group, Subject, TeacherSubject


class TestLessonPermissions:
    def test_center_admin_can_generate_reports(self):
        assert "reports.generate" in ROLE_PERMISSIONS["center_admin"]

    def test_teacher_cannot_generate_reports(self):
        assert "reports.generate" not in ROLE_PERMISSIONS["teacher"]


@pytest.mark.integration
class TestTeacherSubjects:
    async def test_teacher_subjects_from_assigned_group(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/teacher/subjects",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert response.status_code == 200
        subject_ids = {s["id"] for s in response.json()["data"]}
        assert str(fx["group_a"].subject_id) in subject_ids

    async def test_teacher_subjects_from_teacher_subject_table(
        self, api_client, security_fixtures, db_session
    ):
        fx = security_fixtures
        extra_subject = Subject(
            name_uz="Ingliz tili",
            name_ru="Английский",
            name_en="English",
            is_active=True,
        )
        db_session.add(extra_subject)
        await db_session.flush()
        db_session.add(TeacherSubject(teacher_id=fx["teacher_record_a"].id, subject_id=extra_subject.id))
        await db_session.commit()

        response = await api_client.get(
            "/api/v1/teacher/subjects",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert response.status_code == 200
        subject_ids = {s["id"] for s in response.json()["data"]}
        assert str(extra_subject.id) in subject_ids
        assert str(fx["group_a"].subject_id) in subject_ids


@pytest.mark.integration
class TestLessonMaterialGenerate:
    async def test_generate_with_assigned_subject(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/teacher/lesson-materials/generate",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "subject_id": str(fx["group_a"].subject_id),
                "topic": "Test mavzu",
                "content_type": "presentation",
                "locale": "uz",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["topic"] == "Test mavzu"
        assert data["status"] == "draft"

    async def test_generate_rejects_unassigned_subject(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        other_subject = Subject(
            name_uz="Fizika",
            name_ru="Физика",
            name_en="Physics",
            is_active=True,
        )
        db_session.add(other_subject)
        await db_session.commit()

        response = await api_client.post(
            "/api/v1/teacher/lesson-materials/generate",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "subject_id": str(other_subject.id),
                "topic": "Test mavzu",
                "content_type": "presentation",
            },
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "SUBJECT_NOT_ASSIGNED"

    async def test_generate_rejects_invalid_locale(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.post(
            "/api/v1/teacher/lesson-materials/generate",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "subject_id": str(fx["group_a"].subject_id),
                "topic": "Test mavzu",
                "content_type": "presentation",
                "locale": "fr",
            },
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestLessonMaterialStart:
    async def test_start_draft_material(self, api_client, security_fixtures):
        fx = security_fixtures
        create = await api_client.post(
            "/api/v1/teacher/lesson-materials/generate",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "subject_id": str(fx["group_a"].subject_id),
                "topic": "Start test",
                "content_type": "game",
            },
        )
        material_id = create.json()["data"]["id"]

        start = await api_client.post(
            f"/api/v1/teacher/lesson-materials/{material_id}/start",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert start.status_code == 200
        assert start.json()["data"]["status"] == "started"

    async def test_start_already_started_fails(self, api_client, security_fixtures):
        fx = security_fixtures
        create = await api_client.post(
            "/api/v1/teacher/lesson-materials/generate",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "subject_id": str(fx["group_a"].subject_id),
                "topic": "Double start",
                "content_type": "presentation",
            },
        )
        material_id = create.json()["data"]["id"]
        headers = {"Authorization": f"Bearer {fx['token_teacher_a']}"}

        first = await api_client.post(f"/api/v1/teacher/lesson-materials/{material_id}/start", headers=headers)
        assert first.status_code == 200

        second = await api_client.post(f"/api/v1/teacher/lesson-materials/{material_id}/start", headers=headers)
        assert second.status_code == 422
        assert second.json()["detail"]["code"] == "LESSON_ALREADY_STARTED"


@pytest.mark.integration
class TestRatingsReportAccess:
    async def test_center_admin_can_download_ratings_pdf(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/reports/ratings?format=pdf",
            headers={"Authorization": f"Bearer {fx['token_admin_a']}"},
        )
        assert response.status_code == 200
        assert "pdf" in response.headers.get("content-type", "").lower()

    async def test_teacher_cannot_download_ratings(self, api_client, security_fixtures):
        fx = security_fixtures
        response = await api_client.get(
            "/api/v1/reports/ratings?format=pdf",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert response.status_code == 403
