from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pinfl import decrypt_pinfl, encrypt_pinfl, mask_pinfl, validate_pinfl
from app.core.tenant import assert_center_access, get_user_center_filter
from app.models.education import Guardian, Student
from app.models.identity import User
from app.schemas.students import StudentCreate, StudentResponse, StudentUpdate
from app.services.audit_service import write_audit_log


def student_to_response(student: Student, *, include_masked_pinfl: bool = True) -> StudentResponse:
    masked = None
    if include_masked_pinfl and student.jshshir_encrypted:
        try:
            plain = decrypt_pinfl(student.jshshir_encrypted)
            masked = mask_pinfl(plain)
        except Exception:
            masked = "••••••••••••••"
    return StudentResponse(
        id=student.id,
        center_id=student.center_id,
        full_name=student.full_name,
        jshshir_masked=masked,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        phone=student.phone,
        address=student.address,
        school=student.school,
        grade=student.grade,
        enrollment_date=student.enrollment_date,
        graduation_date=student.graduation_date,
        consent_given_at=student.consent_given_at,
    )


async def list_students(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
    center_id: UUID | None = None,
) -> tuple[list[Student], int]:
    center_filter = get_user_center_filter(user)
    query = select(Student).where(Student.deleted_at.is_(None))
    if center_filter:
        query = query.where(Student.center_id == center_filter)
    elif center_id:
        query = query.where(Student.center_id == center_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.order_by(Student.full_name).offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


async def get_student(db: AsyncSession, user: User, student_id: UUID) -> Student:
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.guardians))
        .where(Student.id == student_id, Student.deleted_at.is_(None))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    assert_center_access(user, student.center_id)
    return student


async def create_student(db: AsyncSession, user: User, data: StudentCreate) -> Student:
    assert_center_access(user, data.center_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin", "teacher"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    encrypted = None
    if data.jshshir:
        if not validate_pinfl(data.jshshir):
            raise HTTPException(status_code=422, detail={"code": "PINFL_INVALID", "field": "jshshir"})
        encrypted = encrypt_pinfl(data.jshshir)

    student = Student(
        center_id=data.center_id,
        full_name=data.full_name,
        jshshir_encrypted=encrypted,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        phone=data.phone,
        address=data.address,
        school=data.school,
        grade=data.grade,
        enrollment_date=data.enrollment_date,
        consent_given_at=datetime.now(UTC) if data.guardian_phone else None,
    )
    db.add(student)
    await db.flush()

    if data.guardian_name and data.guardian_phone:
        db.add(
            Guardian(
                student_id=student.id,
                full_name=data.guardian_name,
                phone=data.guardian_phone,
            )
        )
    return student


async def update_student(
    db: AsyncSession, user: User, student_id: UUID, data: StudentUpdate
) -> Student:
    student = await get_student(db, user, student_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin", "teacher"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    await db.flush()
    return student


async def delete_student(db: AsyncSession, user: User, student_id: UUID) -> None:
    if user.role.code not in {"super_admin", "center_director"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    student = await get_student(db, user, student_id)
    student.deleted_at = datetime.now(UTC)


async def reveal_pinfl(
    db: AsyncSession,
    user: User,
    student_id: UUID,
    *,
    ip_address: str | None,
) -> str:
    if user.role.code != "auditor":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    student = await get_student(db, user, student_id)
    if not student.jshshir_encrypted:
        raise HTTPException(status_code=404, detail={"code": "PINFL_NOT_SET"})
    plain = decrypt_pinfl(student.jshshir_encrypted)
    await write_audit_log(
        db,
        user_id=user.id,
        action="pinfl.reveal",
        resource_type="student",
        resource_id=student.id,
        ip_address=ip_address,
        details={"student_id": str(student.id)},
    )
    return plain
