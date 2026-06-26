from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pinfl import decrypt_pinfl, encrypt_pinfl, mask_pinfl, validate_pinfl
from app.core.tenant import (
    assert_center_access,
    assert_student_in_scope,
    get_tenant_context_optional,
    apply_student_list_scope,
    resolve_tenant_context,
)
from app.models.academics import Exam, ExamResult, Grade
from app.models.education import Enrollment, Guardian, Student
from app.models.identity import User
from app.models.operations import AttendanceRecord
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


async def _tenant_ctx(db: AsyncSession, user: User):
    ctx = get_tenant_context_optional()
    if ctx is None:
        ctx = await resolve_tenant_context(db, user)
    return ctx


async def list_students(
    db: AsyncSession,
    user: User,
    *,
    page: int = 1,
    per_page: int = 20,
    center_id: UUID | None = None,
) -> tuple[list[Student], int]:
    ctx = await _tenant_ctx(db, user)
    query = select(Student).where(Student.deleted_at.is_(None))
    query = apply_student_list_scope(query, ctx)
    if ctx.is_district_wide and center_id:
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
    ctx = await _tenant_ctx(db, user)
    await assert_student_in_scope(db, ctx, student)
    return student


async def create_student(db: AsyncSession, user: User, data: StudentCreate) -> Student:
    assert_center_access(user, data.center_id)
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
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
    if user.role.code not in {"super_admin", "center_director", "center_admin"}:
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
    if user.role.code != "super_admin":
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


# --- Student cabinet (self-scoped) ---


async def get_linked_student(db: AsyncSession, user: User) -> Student:
    if user.role.code != "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.center))
        .where(Student.user_id == user.id, Student.deleted_at.is_(None))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_PROFILE_NOT_FOUND"})
    return student


async def get_student_profile(db: AsyncSession, user: User) -> dict:
    student = await get_linked_student(db, user)
    return {
        "id": str(student.id),
        "full_name": student.full_name,
        "grade": student.grade,
        "school": student.school,
        "center_name": student.center.name if student.center else "",
    }


async def get_student_grades(db: AsyncSession, user: User) -> list[dict]:
    student = await get_linked_student(db, user)
    result = await db.execute(
        select(Grade)
        .options(selectinload(Grade.subject))
        .where(Grade.student_id == student.id, Grade.deleted_at.is_(None))
        .order_by(Grade.graded_at.desc())
    )
    grades = list(result.scalars().all())
    locale = user.locale_preference or "uz"
    return [
        {
            "id": str(g.id),
            "grade_value": g.grade_value,
            "grade_type": g.grade_type,
            "term": g.term,
            "subject_name": getattr(g.subject, f"name_{locale}", g.subject.name_uz) if g.subject else "",
            "graded_at": g.graded_at.isoformat(),
        }
        for g in grades
    ]


async def get_student_exams(db: AsyncSession, user: User) -> list[dict]:
    student = await get_linked_student(db, user)
    enrollments = await db.execute(
        select(Enrollment.group_id).where(
            Enrollment.student_id == student.id,
            Enrollment.status == "active",
            Enrollment.deleted_at.is_(None),
        )
    )
    group_ids = [row[0] for row in enrollments.all()]
    query = select(Exam).where(Exam.deleted_at.is_(None), Exam.is_published.is_(True))
    if group_ids:
        query = query.where((Exam.group_id.in_(group_ids)) | (Exam.group_id.is_(None)))
    else:
        query = query.where(Exam.center_id == student.center_id)
    result = await db.execute(query.order_by(Exam.created_at.desc()))
    exams = list(result.scalars().all())
    return [
        {
            "id": str(e.id),
            "title": e.title,
            "pass_score": e.pass_score,
            "duration_minutes": e.duration_minutes,
        }
        for e in exams
    ]


async def get_student_exam_results(db: AsyncSession, user: User) -> list[dict]:
    student = await get_linked_student(db, user)
    result = await db.execute(
        select(ExamResult)
        .options(selectinload(ExamResult.exam))
        .where(ExamResult.student_id == student.id)
        .order_by(ExamResult.submitted_at.desc())
    )
    rows = list(result.scalars().all())
    return [
        {
            "id": str(r.id),
            "exam_title": r.exam.title if r.exam else "",
            "score": r.score,
            "max_score": r.max_score,
            "passed": r.passed,
            "submitted_at": r.submitted_at.isoformat(),
        }
        for r in rows
    ]


async def get_student_attendance(db: AsyncSession, user: User) -> list[dict]:
    student = await get_linked_student(db, user)
    result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.student_id == student.id)
        .order_by(AttendanceRecord.session_date.desc())
        .limit(50)
    )
    rows = list(result.scalars().all())
    return [
        {
            "id": str(r.id),
            "session_date": r.session_date.isoformat(),
            "status": r.status,
            "group_id": str(r.group_id),
        }
        for r in rows
    ]


async def get_student_enrollments(db: AsyncSession, user: User) -> list[dict]:
    student = await get_linked_student(db, user)
    result = await db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.group))
        .where(Enrollment.student_id == student.id, Enrollment.deleted_at.is_(None))
    )
    rows = list(result.scalars().unique().all())
    return [
        {
            "id": str(e.id),
            "group_name": e.group.name if e.group else "",
            "status": e.status,
            "enrolled_at": e.enrolled_at.isoformat(),
        }
        for e in rows
    ]
