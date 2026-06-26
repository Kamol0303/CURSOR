"""Teacher portal — scoped views for linked teacher account."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.education import Teacher
from app.models.identity import User
from app.services import group_service


async def get_linked_teacher(db: AsyncSession, user: User) -> Teacher:
    if user.role.code != "teacher":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    result = await db.execute(
        select(Teacher)
        .options(selectinload(Teacher.center))
        .where(Teacher.user_id == user.id, Teacher.deleted_at.is_(None))
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail={"code": "TEACHER_PROFILE_NOT_FOUND"})
    return teacher


async def get_teacher_profile(db: AsyncSession, user: User) -> dict:
    teacher = await get_linked_teacher(db, user)
    return {
        "id": str(teacher.id),
        "full_name": teacher.full_name,
        "phone": teacher.phone,
        "specialization": teacher.specialization,
        "center_id": str(teacher.center_id),
        "center_name": teacher.center.name if teacher.center else "",
        "username": user.username,
    }


async def list_teacher_groups(db: AsyncSession, user: User) -> list[dict]:
    groups, _ = await group_service.list_groups(db, user, per_page=100)
    return [g.model_dump() for g in groups]


async def get_group_students(db: AsyncSession, user: User, group_id: UUID) -> list[dict]:
    await group_service.get_group(db, user, group_id)
    return await group_service.list_group_enrollments(db, user, group_id)


async def get_teacher_schedule(db: AsyncSession, user: User) -> list[dict]:
    groups, _ = await group_service.list_groups(db, user, per_page=100)
    schedule: list[dict] = []
    for g in groups:
        if g.schedule_json:
            schedule.append(
                {
                    "group_id": str(g.id),
                    "group_name": g.name,
                    "room": g.room,
                    "subject_name": g.subject_name_uz,
                    "schedule": g.schedule_json,
                }
            )
    return schedule
