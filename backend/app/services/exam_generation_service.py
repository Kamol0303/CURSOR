"""AI-powered exam generation — draft exams for teacher review."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.education import Subject
from app.models.identity import User
from app.schemas.exams import ExamCreate, ExamGenerateRequest, ExamResponse
from app.services import exam_service, llm_service
from app.services.audit_service import write_audit_log


async def generate_exam(
    db: AsyncSession,
    user: User,
    body: ExamGenerateRequest,
    *,
    ip_address: str | None = None,
) -> ExamResponse:
    if user.role.code not in {"super_admin", "center_director", "center_admin", "teacher"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    subject = (
        await db.execute(select(Subject).where(Subject.id == body.subject_id, Subject.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "SUBJECT_NOT_FOUND"})

    locale = body.locale if body.locale in {"uz", "ru", "en"} else (user.locale_preference or "uz")
    subject_name = getattr(subject, f"name_{locale}", subject.name_uz)
    questions = await llm_service.generate_exam_questions(
        subject_name=subject_name,
        topic=body.topic,
        question_count=body.question_count,
        difficulty=body.difficulty,
        locale=locale,
    )

    title = body.title or f"{subject_name}: {body.topic}"
    exam_body = ExamCreate(
        center_id=body.center_id,
        subject_id=body.subject_id,
        group_id=body.group_id,
        title=title[:200],
        description=body.description or f"AI generated ({body.difficulty})",
        pass_score=body.pass_score,
        duration_minutes=body.duration_minutes,
        questions=questions,
    )
    exam = await exam_service.create_exam(db, user, exam_body)

    await write_audit_log(
        db,
        user_id=user.id,
        action="exam.generate",
        resource_type="exam",
        resource_id=exam.id,
        ip_address=ip_address,
        details={
            "subject_id": str(body.subject_id),
            "topic": body.topic,
            "question_count": len(questions),
            "difficulty": body.difficulty,
            "ai_provider": llm_service.llm_provider_label(),
        },
    )
    return exam
