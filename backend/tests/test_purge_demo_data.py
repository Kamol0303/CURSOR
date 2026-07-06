"""Tests for demo data purge script."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.academics import Course, Exam, ExamQuestion, ExamResult, Grade, Lesson
from app.models.education import Enrollment, Group, Guardian, Student, Subject, Teacher, TeacherSubject
from app.models.files_messages import Message, StoredFile
from app.models.finance import PaymentTransaction
from app.models.identity import Role, TrainingCenter, User
from app.models.operations import AttendanceRecord, AttendanceSession, StudentPayment
from app.models.ratings_certs import Certificate
from scripts.purge_demo_data import collect_counts, purge_demo_rows


async def _ensure_center_admin_role(db_session) -> Role:
    role = (await db_session.execute(select(Role).where(Role.code == "center_admin"))).scalar_one_or_none()
    if not role:
        role = Role(code="center_admin", name_uz="Admin", name_ru="Admin", name_en="Admin")
        db_session.add(role)
        await db_session.flush()
    return role


async def _seed_demo_ocms_bundle(db_session, *, suffix: str | None = None) -> dict:
    """Create a demo center with representative OCMS rows for purge testing."""
    tag = suffix or uuid.uuid4().hex[:8]
    role = await _ensure_center_admin_role(db_session)

    center = TrainingCenter(
        name=f"Demo OCMS Center {tag}",
        stir=f"9{tag[:8]}",
        director_name="Purge Test",
        phone="+998900000001",
        center_type="private",
        is_active=True,
        is_demo_data=True,
    )
    db_session.add(center)
    await db_session.flush()

    user = User(
        username=f"purge.ocms.{tag}",
        password_hash=hash_password("Test#12345!"),
        role_id=role.id,
        center_id=center.id,
        is_demo_account=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    teacher = Teacher(
        center_id=center.id,
        full_name=f"Demo Teacher {tag}",
        is_active=True,
        is_demo_data=True,
    )
    db_session.add(teacher)
    await db_session.flush()

    subject = Subject(
        name_uz=f"Fan {tag}",
        name_ru=f"Fan {tag}",
        name_en=f"Subject {tag}",
        is_active=True,
    )
    db_session.add(subject)
    await db_session.flush()

    group = Group(
        center_id=center.id,
        subject_id=subject.id,
        name=f"Demo Group {tag}",
        teacher_id=teacher.id,
        is_active=True,
    )
    db_session.add(group)
    await db_session.flush()

    student = Student(
        center_id=center.id,
        full_name=f"Demo Student {tag}",
        grade="10",
        is_demo_data=True,
    )
    db_session.add(student)
    await db_session.flush()

    db_session.add(
        Enrollment(student_id=student.id, group_id=group.id, center_id=center.id, status="active")
    )
    db_session.add(Guardian(student_id=student.id, full_name="Demo Parent", phone="+998900000002"))
    db_session.add(TeacherSubject(teacher_id=teacher.id, subject_id=subject.id))

    course = Course(
        center_id=center.id,
        subject_id=subject.id,
        name=f"Demo Course {tag}",
        is_active=True,
    )
    db_session.add(course)
    await db_session.flush()

    lesson = Lesson(
        course_id=course.id,
        center_id=center.id,
        group_id=group.id,
        title=f"Demo Lesson {tag}",
    )
    db_session.add(lesson)

    exam = Exam(
        center_id=center.id,
        subject_id=subject.id,
        group_id=group.id,
        title=f"Demo Exam {tag}",
        created_by=user.id,
    )
    db_session.add(exam)
    await db_session.flush()

    db_session.add(
        ExamQuestion(
            exam_id=exam.id,
            question_text="2+2=?",
            correct_answer="4",
            order_index=0,
        )
    )
    db_session.add(
        ExamResult(
            exam_id=exam.id,
            student_id=student.id,
            center_id=center.id,
            score=4.0,
            max_score=5.0,
            passed=True,
        )
    )
    db_session.add(
        Grade(
            student_id=student.id,
            group_id=group.id,
            subject_id=subject.id,
            center_id=center.id,
            grade_value=4.5,
            graded_by=user.id,
        )
    )

    payment = StudentPayment(
        student_id=student.id,
        center_id=center.id,
        amount=100000.0,
        status="paid",
        created_by=user.id,
    )
    db_session.add(payment)
    await db_session.flush()

    db_session.add(
        PaymentTransaction(
            payment_id=payment.id,
            center_id=center.id,
            amount=100000.0,
            provider="click",
            status="completed",
        )
    )

    session_date = date.today()
    db_session.add(
        AttendanceSession(
            group_id=group.id,
            center_id=center.id,
            session_date=session_date,
            qr_token_hash=f"hash-{tag}",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            created_by=user.id,
        )
    )
    db_session.add(
        AttendanceRecord(
            student_id=student.id,
            group_id=group.id,
            center_id=center.id,
            session_date=session_date,
            status="present",
        )
    )

    stored_file = StoredFile(
        center_id=center.id,
        owner_type="student",
        owner_id=student.id,
        file_name=f"photo-{tag}.jpg",
        mime_type="image/jpeg",
        storage_path=f"demo/{tag}.jpg",
        uploaded_by=user.id,
    )
    db_session.add(stored_file)
    await db_session.flush()
    student.photo_file_id = stored_file.id

    db_session.add(
        Message(
            center_id=center.id,
            sender_id=user.id,
            title=f"Demo message {tag}",
            body="Test body",
        )
    )
    db_session.add(
        Certificate(
            certificate_number=f"DEMO-{tag.upper()}",
            student_id=student.id,
            center_id=center.id,
            subject_id=subject.id,
            course_name_uz="Kurs",
            course_name_ru="Kurs",
            course_name_en="Course",
            issue_date=date.today(),
            integrity_hash=f"hash-{tag}",
            is_demo_data=True,
            file_id=stored_file.id,
        )
    )

    await db_session.commit()
    return {
        "center": center,
        "user": user,
        "student": student,
        "teacher": teacher,
        "group": group,
        "subject": subject,
        "course": course,
        "exam": exam,
        "payment": payment,
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_purge_removes_demo_entities(db_session, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    role = await _ensure_center_admin_role(db_session)

    center = TrainingCenter(
        name="Demo Purge Center",
        stir="999999999",
        director_name="Test",
        phone="+998900000000",
        center_type="private",
        is_active=True,
        is_demo_data=True,
    )
    db_session.add(center)
    await db_session.flush()

    user = User(
        username="purge.test.demo",
        password_hash=hash_password("Test#12345!"),
        role_id=role.id,
        center_id=center.id,
        is_demo_account=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    before = await collect_counts(db_session)
    assert before["demo_users"] >= 1
    assert before["demo_centers"] >= 1

    await purge_demo_rows(db_session)
    await db_session.commit()

    after = await collect_counts(db_session)
    assert after["demo_users"] == 0
    assert after["demo_centers"] == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_collect_counts_includes_ocms_tables(db_session, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    await _seed_demo_ocms_bundle(db_session)

    counts = await collect_counts(db_session)
    assert counts["demo_exams"] >= 1
    assert counts["demo_exam_results"] >= 1
    assert counts["demo_grades"] >= 1
    assert counts["demo_payments"] >= 1
    assert counts["demo_payment_transactions"] >= 1
    assert counts["demo_attendance_records"] >= 1
    assert counts["demo_attendance_sessions"] >= 1
    assert counts["demo_courses"] >= 1
    assert counts["demo_lessons"] >= 1
    assert counts["demo_messages"] >= 1
    assert counts["demo_files"] >= 1
    assert counts["demo_certificates"] >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_purge_removes_ocms_demo_data(db_session, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    bundle = await _seed_demo_ocms_bundle(db_session)
    center_id = bundle["center"].id
    student_id = bundle["student"].id
    exam_id = bundle["exam"].id

    before = await collect_counts(db_session)
    assert before["demo_exams"] >= 1

    await purge_demo_rows(db_session)
    await db_session.commit()

    after = await collect_counts(db_session)
    assert after["demo_users"] == 0
    assert after["demo_centers"] == 0
    assert after["demo_students"] == 0
    assert after["demo_exams"] == 0
    assert after["demo_exam_results"] == 0
    assert after["demo_grades"] == 0
    assert after["demo_payments"] == 0
    assert after["demo_payment_transactions"] == 0
    assert after["demo_attendance_records"] == 0
    assert after["demo_attendance_sessions"] == 0
    assert after["demo_courses"] == 0
    assert after["demo_lessons"] == 0
    assert after["demo_messages"] == 0
    assert after["demo_files"] == 0
    assert after["demo_certificates"] == 0

    remaining_exam = (
        await db_session.execute(select(func.count()).select_from(Exam).where(Exam.id == exam_id))
    ).scalar()
    remaining_student = (
        await db_session.execute(select(func.count()).select_from(Student).where(Student.id == student_id))
    ).scalar()
    remaining_center = (
        await db_session.execute(
            select(func.count()).select_from(TrainingCenter).where(TrainingCenter.id == center_id)
        )
    ).scalar()

    assert remaining_exam == 0
    assert remaining_student == 0
    assert remaining_center == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_purge_leaves_non_demo_data(db_session, security_fixtures, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    keep_center = security_fixtures["center_b"]
    keep_student = security_fixtures["student_b"]
    keep_center_id = keep_center.id
    keep_student_id = keep_student.id

    await _seed_demo_ocms_bundle(db_session)

    await purge_demo_rows(db_session)
    await db_session.commit()

    remaining_centers = (
        await db_session.execute(
            select(func.count()).select_from(TrainingCenter).where(TrainingCenter.id == keep_center_id)
        )
    ).scalar()
    remaining_students = (
        await db_session.execute(select(func.count()).select_from(Student).where(Student.id == keep_student_id))
    ).scalar()
    demo_left = (
        await db_session.execute(
            select(func.count()).select_from(TrainingCenter).where(TrainingCenter.is_demo_data.is_(True))
        )
    ).scalar()

    assert remaining_centers == 1
    assert remaining_students == 1
    assert demo_left == 0


@pytest.mark.asyncio
async def test_purge_refuses_non_production(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "staging")

    import scripts.purge_demo_data as purge_module

    monkeypatch.setattr(
        purge_module,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "i_understand_this_deletes_demo_data": True,
                "dry_run": False,
                "allow_non_production": False,
            },
        )(),
    )

    with pytest.raises(SystemExit) as exc:
        await purge_module.purge()

    assert exc.value.code == 1
