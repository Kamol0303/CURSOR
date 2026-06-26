from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.academics import Exam, ExamResult, Grade
from app.models.education import Enrollment, Student
from app.models.identity import User
from app.models.operations import AttendanceRecord


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
