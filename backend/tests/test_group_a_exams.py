"""Group A — AI exam generator and exam workflow."""

from __future__ import annotations

import pytest

from app.core.permissions import ROLE_PERMISSIONS
from app.services.llm_service import generate_questions_mock, _parse_questions_payload


class TestGroupAPermissions:
    def test_teacher_can_create_exams(self):
        assert "exams.create" in ROLE_PERMISSIONS["teacher"]

    def test_center_admin_can_publish_exams(self):
        assert "exams.update" in ROLE_PERMISSIONS["center_admin"]

    def test_student_can_submit_exams(self):
        assert "exams.submit" in ROLE_PERMISSIONS["student"]


class TestGroupALLMHelpers:
    def test_mock_generator_returns_requested_count(self):
        questions = generate_questions_mock(topic="Algebra", question_count=3, difficulty="easy")
        assert len(questions) == 3
        assert questions[0].correct_answer in questions[0].options_json

    def test_parse_questions_payload(self):
        raw = """
        {
          "questions": [
            {
              "question_text": "2+2?",
              "options_json": ["3", "4", "5"],
              "correct_answer": "4",
              "points": 1,
              "order_index": 0
            }
          ]
        }
        """
        questions = _parse_questions_payload(raw)
        assert len(questions) == 1
        assert questions[0].correct_answer == "4"


@pytest.mark.integration
class TestGroupAExamApi:
    async def test_generate_exam_creates_draft(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        from sqlalchemy import select
        from app.models.education import Subject

        subject = (await db_session.execute(select(Subject).limit(1))).scalar_one()
        response = await api_client.post(
            "/api/v1/exams/generate",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
            json={
                "subject_id": str(subject.id),
                "topic": "Group A Topic",
                "question_count": 3,
                "difficulty": "medium",
            },
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["question_count"] == 3
        assert data["is_published"] is False

        detail = await api_client.get(
            f"/api/v1/exams/{data['id']}",
            headers={"Authorization": f"Bearer {fx['token_teacher_a']}"},
        )
        assert detail.status_code == 200
        assert len(detail.json()["data"]["questions"]) == 3
        assert detail.json()["data"]["questions"][0]["correct_answer"]

    async def test_student_cannot_see_correct_answers(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        from sqlalchemy import select
        from app.models.education import Subject

        subject = (await db_session.execute(select(Subject).limit(1))).scalar_one()
        create_res = await api_client.post(
            "/api/v1/exams/generate",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "subject_id": str(subject.id),
                "topic": "Student View",
                "question_count": 2,
            },
        )
        exam_id = create_res.json()["data"]["id"]
        await api_client.patch(
            f"/api/v1/exams/{exam_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"is_published": True},
        )

        student_view = await api_client.get(
            f"/api/v1/exams/{exam_id}",
            headers={"Authorization": f"Bearer {fx['token_student']}"},
        )
        assert student_view.status_code == 200
        for q in student_view.json()["data"]["questions"]:
            assert q["correct_answer"] is None

    async def test_publish_and_submit_exam(self, api_client, security_fixtures, db_session):
        fx = security_fixtures
        from sqlalchemy import select
        from app.models.education import Subject

        subject = (await db_session.execute(select(Subject).limit(1))).scalar_one()
        create_res = await api_client.post(
            "/api/v1/exams/generate",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={
                "subject_id": str(subject.id),
                "topic": "Submit Flow",
                "question_count": 1,
            },
        )
        exam_id = create_res.json()["data"]["id"]
        detail = await api_client.get(
            f"/api/v1/exams/{exam_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
        )
        question = detail.json()["data"]["questions"][0]

        await api_client.patch(
            f"/api/v1/exams/{exam_id}",
            headers={"Authorization": f"Bearer {fx['token_director_a']}"},
            json={"is_published": True},
        )

        submit_res = await api_client.post(
            f"/api/v1/exams/{exam_id}/submit",
            headers={"Authorization": f"Bearer {fx['token_student']}"},
            json={
                "answers": [{"question_id": question["id"], "answer": question["correct_answer"]}],
            },
        )
        assert submit_res.status_code == 200
        assert submit_res.json()["data"]["passed"] is True
