from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging_config import get_logger
from app.core.tenant import (
    assert_center_access,
    get_tenant_context_optional,
    get_user_center_filter,
    resolve_tenant_context,
    teacher_group_ids_subquery,
)
from app.models.academics import Exam, ExamQuestion, ExamResult
from app.models.identity import User
from app.schemas.exams import (
    ExamCreate,
    ExamDetailResponse,
    ExamQuestionResponse,
    ExamResponse,
    ExamResultResponse,
    ExamSubmitRequest,
    ExamUpdate,
)
from app.services.audit_service import write_audit_log

logger = get_logger(__name__)


def exam_to_response(exam: Exam, *, question_count: int | None = None) -> ExamResponse:
    count = question_count if question_count is not None else len(exam.questions)
    return ExamResponse(
        id=exam.id,
        center_id=exam.center_id,
        subject_id=exam.subject_id,
        group_id=exam.group_id,
        title=exam.title,
        description=exam.description,
        pass_score=exam.pass_score,
        duration_minutes=exam.duration_minutes,
        is_published=exam.is_published,
        question_count=count,
    )


def exam_to_detail(exam: Exam, *, include_answers: bool) -> ExamDetailResponse:
    base = exam_to_response(exam)
    questions = sorted(exam.questions, key=lambda q: q.order_index)
    return ExamDetailResponse(
        **base.model_dump(),
        questions=[
            ExamQuestionResponse(
                id=q.id,
                question_text=q.question_text,
                options_json=q.options_json,
                correct_answer=q.correct_answer if include_answers else None,
                points=q.points,
                order_index=q.order_index,
            )
            for q in questions
        ],
    )


async def list_exams(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[ExamResponse], int]:
    center_filter = get_user_center_filter(user)
    ctx = get_tenant_context_optional() or await resolve_tenant_context(db, user)
    query = select(Exam).where(Exam.deleted_at.is_(None))
    if center_filter:
        query = query.where(Exam.center_id == center_filter)
    if ctx.role == "teacher":
        if not ctx.teacher_id:
            query = query.where(Exam.id.in_([]))
        else:
            query = query.where(Exam.group_id.in_(teacher_group_ids_subquery(ctx.teacher_id)))

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    result = await db.execute(
        query.options(selectinload(Exam.questions))
        .order_by(Exam.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    exams = list(result.scalars().all())
    return [exam_to_response(e) for e in exams], total


async def create_exam(db: AsyncSession, user: User, body: ExamCreate) -> ExamResponse:
    center_id = body.center_id or user.center_id
    if not center_id:
        raise HTTPException(status_code=422, detail={"code": "CENTER_REQUIRED"})
    assert_center_access(user, center_id)

    exam = Exam(
        center_id=center_id,
        subject_id=body.subject_id,
        group_id=body.group_id,
        title=body.title,
        description=body.description,
        pass_score=body.pass_score,
        duration_minutes=body.duration_minutes,
        created_by=user.id,
    )
    db.add(exam)
    await db.flush()

    for q in body.questions:
        db.add(
            ExamQuestion(
                exam_id=exam.id,
                question_text=q.question_text,
                options_json=q.options_json,
                correct_answer=q.correct_answer,
                points=q.points,
                order_index=q.order_index,
            )
        )
    await db.flush()
    await db.refresh(exam, ["questions"])
    logger.info("exam_created exam_id=%s center_id=%s", exam.id, center_id)
    return exam_to_response(exam)


async def get_exam_detail(db: AsyncSession, user: User, exam_id: UUID) -> ExamDetailResponse:
    published_only = user.role.code == "student"
    exam = await _get_exam(db, user, exam_id, published_only=published_only)
    include_answers = user.role.code != "student"
    return exam_to_detail(exam, include_answers=include_answers)


async def delete_exam(db: AsyncSession, user: User, exam_id: UUID) -> None:
    from datetime import UTC, datetime

    if user.role.code not in {"super_admin", "center_director", "teacher"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    exam = await _get_exam(db, user, exam_id)
    exam.deleted_at = datetime.now(UTC)
    await db.flush()


async def update_exam(db: AsyncSession, user: User, exam_id: UUID, body: ExamUpdate) -> ExamResponse:
    exam = await _get_exam(db, user, exam_id)
    if body.title is not None:
        exam.title = body.title
    if body.description is not None:
        exam.description = body.description
    if body.pass_score is not None:
        exam.pass_score = body.pass_score
    if body.duration_minutes is not None:
        exam.duration_minutes = body.duration_minutes
    if body.is_published is not None:
        exam.is_published = body.is_published
    await db.flush()
    if body.is_published is not None:
        await write_audit_log(
            db,
            user_id=user.id,
            action="exam.publish" if body.is_published else "exam.unpublish",
            resource_type="exam",
            resource_id=exam.id,
            details={"title": exam.title, "is_published": exam.is_published},
        )
    elif any(v is not None for v in [body.title, body.description, body.pass_score, body.duration_minutes]):
        await write_audit_log(
            db,
            user_id=user.id,
            action="exam.update",
            resource_type="exam",
            resource_id=exam.id,
            details={"title": exam.title},
        )
    return exam_to_response(exam)


async def submit_exam(db: AsyncSession, user: User, exam_id: UUID, body: ExamSubmitRequest) -> ExamResultResponse:
    exam = await _get_exam(db, user, exam_id, published_only=True)
    if not exam.questions:
        raise HTTPException(status_code=422, detail={"code": "EXAM_EMPTY"})

    student_id = body.student_id
    if user.role.code == "student":
        from app.services import student_service

        student = await student_service.get_linked_student(db, user)
        student_id = student.id
    if not student_id:
        raise HTTPException(status_code=422, detail={"code": "STUDENT_REQUIRED"})

    answers_map = {str(a.question_id): a.answer for a in body.answers}
    score = 0.0
    max_score = sum(q.points for q in exam.questions)
    for q in exam.questions:
        if answers_map.get(str(q.id), "").strip().lower() == q.correct_answer.strip().lower():
            score += q.points

    passed = max_score > 0 and (score / max_score * 100) >= exam.pass_score
    result = ExamResult(
        exam_id=exam.id,
        student_id=student_id,
        center_id=exam.center_id,
        score=score,
        max_score=max_score,
        passed=passed,
        answers_json=answers_map,
    )
    db.add(result)
    await db.flush()
    logger.info("exam_submitted exam_id=%s student_id=%s score=%s", exam.id, student_id, score)
    return ExamResultResponse(
        id=result.id,
        exam_id=result.exam_id,
        student_id=result.student_id,
        score=result.score,
        max_score=result.max_score,
        passed=result.passed,
        submitted_at=result.submitted_at.date() if result.submitted_at else None,
    )


async def list_results(db: AsyncSession, user: User, exam_id: UUID) -> list[ExamResultResponse]:
    exam = await _get_exam(db, user, exam_id)
    result = await db.execute(select(ExamResult).where(ExamResult.exam_id == exam.id).order_by(ExamResult.submitted_at.desc()))
    rows = list(result.scalars().all())
    return [
        ExamResultResponse(
            id=r.id,
            exam_id=r.exam_id,
            student_id=r.student_id,
            score=r.score,
            max_score=r.max_score,
            passed=r.passed,
            submitted_at=r.submitted_at.date() if r.submitted_at else None,
        )
        for r in rows
    ]


async def _get_exam(db: AsyncSession, user: User, exam_id: UUID, *, published_only: bool = False) -> Exam:
    result = await db.execute(
        select(Exam).options(selectinload(Exam.questions)).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, exam.center_id)
    if published_only and not exam.is_published:
        raise HTTPException(status_code=403, detail={"code": "EXAM_NOT_PUBLISHED"})
    return exam
