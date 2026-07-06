"""AI lesson material generation for teacher portal."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academics import LessonMaterial
from app.models.education import Group, Subject
from app.models.identity import User
from app.schemas.lesson_materials import LessonGenerateRequest, LessonMaterialResponse
from app.services import llm_service
from app.services.audit_service import write_audit_log
from app.services.teacher_portal_service import get_linked_teacher


def material_to_response(material: LessonMaterial, *, subject_name: str | None = None) -> LessonMaterialResponse:
    name = subject_name
    if not name and material.subject_id:
        name = None
    return LessonMaterialResponse(
        id=material.id,
        center_id=material.center_id,
        teacher_id=material.teacher_id,
        group_id=material.group_id,
        subject_id=material.subject_id,
        subject_name_uz=subject_name,
        topic=material.topic,
        content_type=material.content_type,
        locale=material.locale,
        title=material.title,
        content_json=material.content_json,
        status=material.status,
        ai_provider=material.ai_provider,
        started_at=material.started_at,
        created_at=material.created_at,
    )


async def list_teacher_subjects(db: AsyncSession, user: User) -> list[dict]:
    teacher = await get_linked_teacher(db, user)
    result = await db.execute(
        select(Group.subject_id, Subject.name_uz, Subject.name_ru, Subject.name_en)
        .join(Subject, Subject.id == Group.subject_id)
        .where(Group.center_id == teacher.center_id, Group.teacher_id == teacher.id, Group.deleted_at.is_(None))
        .distinct()
    )
    subjects: list[dict] = []
    seen: set[str] = set()
    for row in result.all():
        sid = str(row.subject_id)
        if sid in seen:
            continue
        seen.add(sid)
        subjects.append(
            {
                "id": sid,
                "name_uz": row.name_uz,
                "name_ru": row.name_ru,
                "name_en": row.name_en,
            }
        )
    return subjects


async def list_teacher_materials(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[LessonMaterialResponse], int]:
    teacher = await get_linked_teacher(db, user)
    base = select(LessonMaterial).where(
        LessonMaterial.teacher_id == user.id,
        LessonMaterial.center_id == teacher.center_id,
        LessonMaterial.deleted_at.is_(None),
    )
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    result = await db.execute(
        base.order_by(LessonMaterial.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    materials = list(result.scalars().all())
    responses: list[LessonMaterialResponse] = []
    for m in materials:
        subj = (
            await db.execute(select(Subject).where(Subject.id == m.subject_id))
        ).scalar_one_or_none()
        responses.append(material_to_response(m, subject_name=subj.name_uz if subj else None))
    return responses, total


async def generate_lesson_material(
    db: AsyncSession,
    user: User,
    body: LessonGenerateRequest,
    *,
    ip_address: str | None = None,
) -> LessonMaterialResponse:
    teacher = await get_linked_teacher(db, user)

    subject = (
        await db.execute(select(Subject).where(Subject.id == body.subject_id, Subject.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "SUBJECT_NOT_FOUND"})

    if body.group_id:
        group = (
            await db.execute(
                select(Group).where(
                    Group.id == body.group_id,
                    Group.center_id == teacher.center_id,
                    Group.teacher_id == teacher.id,
                    Group.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail={"code": "GROUP_NOT_FOUND"})
        if group.subject_id != body.subject_id:
            raise HTTPException(status_code=422, detail={"code": "GROUP_SUBJECT_MISMATCH"})

    locale = body.locale if body.locale in {"uz", "ru", "en"} else (user.locale_preference or "uz")
    subject_name = getattr(subject, f"name_{locale}", subject.name_uz)
    content = await llm_service.generate_lesson_content(
        subject_name=subject_name,
        topic=body.topic.strip(),
        content_type=body.content_type,
        locale=locale,
    )
    title = str(content.get("title", f"{subject_name}: {body.topic}"))[:255]

    material = LessonMaterial(
        center_id=teacher.center_id,
        teacher_id=user.id,
        group_id=body.group_id,
        subject_id=body.subject_id,
        topic=body.topic.strip(),
        content_type=body.content_type,
        locale=locale,
        title=title,
        content_json=content,
        status="draft",
        ai_provider=llm_service.llm_provider_label(),
    )
    db.add(material)
    await db.flush()

    await write_audit_log(
        db,
        user_id=user.id,
        action="lesson.generate",
        resource_type="lesson_material",
        resource_id=material.id,
        ip_address=ip_address,
        details={
            "subject_id": str(body.subject_id),
            "topic": body.topic.strip(),
            "content_type": body.content_type,
            "ai_provider": material.ai_provider,
        },
    )
    await db.refresh(material)
    return material_to_response(material, subject_name=subject_name)


async def start_lesson_material(
    db: AsyncSession,
    user: User,
    material_id: UUID,
    *,
    ip_address: str | None = None,
) -> LessonMaterialResponse:
    teacher = await get_linked_teacher(db, user)
    material = (
        await db.execute(
            select(LessonMaterial).where(
                LessonMaterial.id == material_id,
                LessonMaterial.teacher_id == user.id,
                LessonMaterial.center_id == teacher.center_id,
                LessonMaterial.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    material.status = "started"
    material.started_at = datetime.now(timezone.utc)

    await write_audit_log(
        db,
        user_id=user.id,
        action="lesson.start",
        resource_type="lesson_material",
        resource_id=material.id,
        ip_address=ip_address,
        details={
            "title": material.title,
            "content_type": material.content_type,
            "topic": material.topic,
        },
    )

    subj = (await db.execute(select(Subject).where(Subject.id == material.subject_id))).scalar_one_or_none()
    return material_to_response(material, subject_name=subj.name_uz if subj else None)
