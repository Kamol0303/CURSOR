"""Parent portal — children and certificates for guardian accounts."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.education import Guardian, Student
from app.models.identity import User
from app.models.ratings_certs import Certificate


async def get_children_for_parent(db: AsyncSession, user: User) -> list[Student]:
    if not user.phone:
        return []

    result = await db.execute(
        select(Student)
        .join(Guardian, Guardian.student_id == Student.id)
        .where(
            Guardian.phone == user.phone,
            Guardian.deleted_at.is_(None),
            Student.deleted_at.is_(None),
        )
        .options(selectinload(Student.center), selectinload(Student.certificates))
    )
    return list(result.scalars().unique().all())


async def get_child_certificates(db: AsyncSession, user: User, student_id: UUID) -> list[Certificate]:
    children = await get_children_for_parent(db, user)
    child_ids = {c.id for c in children}
    if student_id not in child_ids:
        return []

    result = await db.execute(
        select(Certificate)
        .where(
            Certificate.student_id == student_id,
            Certificate.deleted_at.is_(None),
        )
        .order_by(Certificate.issue_date.desc())
    )
    return list(result.scalars().all())
