#!/usr/bin/env python3
"""Seed demo users for non-production environments only.

Usage:
  python -m scripts.seed_demo_users --i-understand-this-creates-demo-credentials
"""

from __future__ import annotations

import argparse
import asyncio
import secrets
import sys
from datetime import UTC, date, datetime, timedelta

import pyotp
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS
from app.core.security import encrypt_totp_secret, hash_password
from app.core.pinfl import encrypt_pinfl
from app.models.education import Guardian, Mahalla, Region, Student, Subject, Teacher, TeacherSubject
from app.models.identity import Permission, Role, RolePermission, TrainingCenter, User


DEMO_USERS = [
    ("super_admin", "admin.tmb", "Tmb#2026Admin!", True),
    ("hokimiyat_operator", "operator.hokimiyat", "Hokim#Op2026!", True),
    ("center_director", "director.aspect", "Direktor#2026!", True),
    ("center_admin", "admin.aspect", "CenterAdmin#26!", False),
    ("teacher", "teacher.dilnoza", "Teach#Dil2026!", False),
    ("auditor", "auditor.tuman", "Audit#Check26!", False),
]

PARENT_PHONE = "+998901234567"

DEFAULT_SUBJECTS = [
    ("Ingliz tili", "Английский язык", "English"),
    ("Matematika", "Математика", "Mathematics"),
    ("Informatika", "Информатика", "IT"),
    ("Dasturlash", "Программирование", "Programming"),
]


async def seed_education_data(session: AsyncSession, center: TrainingCenter, roles: dict[str, Role]) -> None:
    region_result = await session.execute(select(Region).where(Region.name_uz == "Samarqand viloyati"))
    region = region_result.scalar_one_or_none()
    if not region:
        region = Region(name_uz="Samarqand viloyati", name_ru="Самаркандская область", name_en="Samarkand Region")
        session.add(region)
        await session.flush()

    mahalla_result = await session.execute(select(Mahalla).where(Mahalla.name_uz == "Toyloq MFY"))
    mahalla = mahalla_result.scalar_one_or_none()
    if not mahalla:
        mahalla = Mahalla(
            region_id=region.id,
            name_uz="Toyloq MFY",
            name_ru="Тойлок МФЙ",
            name_en="Toyloq Mahalla",
        )
        session.add(mahalla)
        await session.flush()

    center.mahalla_id = mahalla.id
    center.is_demo_data = True

    subjects: list[Subject] = []
    for uz, ru, en in DEFAULT_SUBJECTS:
        result = await session.execute(select(Subject).where(Subject.name_uz == uz))
        subject = result.scalar_one_or_none()
        if not subject:
            subject = Subject(name_uz=uz, name_ru=ru, name_en=en, is_active=True)
            session.add(subject)
            await session.flush()
        subjects.append(subject)

    teacher_user = (
        await session.execute(select(User).where(User.username == "teacher.dilnoza"))
    ).scalar_one_or_none()
    teacher_result = await session.execute(
        select(Teacher).where(Teacher.full_name == "Dilnoza Karimova")
    )
    teacher = teacher_result.scalar_one_or_none()
    if not teacher:
        teacher = Teacher(
            center_id=center.id,
            user_id=teacher_user.id if teacher_user else None,
            full_name="Dilnoza Karimova",
            phone="+998901112233",
            specialization="Ingliz tili",
            years_of_experience=5,
            is_demo_data=True,
        )
        session.add(teacher)
        await session.flush()
        if subjects:
            session.add(TeacherSubject(teacher_id=teacher.id, subject_id=subjects[0].id))

    student_result = await session.execute(select(Student).where(Student.full_name == "Aliyev Sardor"))
    if not student_result.scalar_one_or_none():
        student = Student(
            center_id=center.id,
            full_name="Aliyev Sardor",
            jshshir_encrypted=encrypt_pinfl("12345678901234"),
            grade="9",
            school="Toyloq maktabi",
            is_demo_data=True,
            consent_given_at=datetime.now(UTC),
        )
        session.add(student)
        await session.flush()
        session.add(
            Guardian(
                student_id=student.id,
                full_name="Aliyev Botir",
                phone=PARENT_PHONE,
            )
        )

    # Second center for cross-tenant IDOR tests
    other_center_result = await session.execute(
        select(TrainingCenter).where(TrainingCenter.name == "Demo Boshqa Markaz")
    )
    if not other_center_result.scalar_one_or_none():
        other = TrainingCenter(
            name="Demo Boshqa Markaz",
            stir="987654321",
            center_type="public",
            is_active=True,
            is_demo_data=True,
            mahalla_id=mahalla.id,
        )
        session.add(other)
        await session.flush()
        session.add(
            Student(
                center_id=other.id,
                full_name="Demo Boshqa O'quvchi",
                is_demo_data=True,
            )
        )

    from app.models.ratings_certs import Certificate
    from app.services.certificate_service import compute_integrity_hash, generate_certificate_number

    student_for_cert = (
        await session.execute(select(Student).where(Student.full_name == "Aliyev Sardor"))
    ).scalar_one_or_none()
    if student_for_cert and subjects:
        existing_cert = (
            await session.execute(
                select(Certificate).where(Certificate.student_id == student_for_cert.id)
            )
        ).scalar_one_or_none()
        if not existing_cert:
            cert_num = generate_certificate_number()
            issue_d = datetime.now(UTC).date()
            cert = Certificate(
                certificate_number=cert_num,
                student_id=student_for_cert.id,
                center_id=center.id,
                subject_id=subjects[0].id,
                course_name_uz=subjects[0].name_uz,
                course_name_ru=subjects[0].name_ru,
                course_name_en=subjects[0].name_en,
                issue_date=issue_d,
                integrity_hash=compute_integrity_hash(
                    certificate_number=cert_num,
                    student_name=student_for_cert.full_name,
                    center_name=center.name,
                    course_name=subjects[0].name_uz,
                    issue_date=issue_d,
                ),
                is_demo_data=True,
            )
            session.add(cert)
            student_for_cert.graduation_date = issue_d
            print(f"Demo certificate: {cert_num}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed TMB demo users (non-production only)")
    parser.add_argument(
        "--i-understand-this-creates-demo-credentials",
        action="store_true",
        help="Required flag confirming you understand this creates demo credentials",
    )
    return parser.parse_args()


async def ensure_roles_and_permissions(session: AsyncSession) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for code, uz, ru, en in ROLE_DEFINITIONS:
        result = await session.execute(select(Role).where(Role.code == code))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(code=code, name_uz=uz, name_ru=ru, name_en=en)
            session.add(role)
            await session.flush()
        roles[code] = role

    for role_code, perms in ROLE_PERMISSIONS.items():
        role = roles[role_code]
        for perm_code in perms:
            result = await session.execute(select(Permission).where(Permission.code == perm_code))
            perm = result.scalar_one_or_none()
            if not perm:
                module, action = perm_code.split(".", 1)
                perm = Permission(code=perm_code, module=module, action=action)
                session.add(perm)
                await session.flush()
            link = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            )
            if not link.scalar_one_or_none():
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))

    return roles


async def seed() -> None:
    args = parse_args()
    if not args.i_understand_this_creates_demo_credentials:
        print("ERROR: Must pass --i-understand-this-creates-demo-credentials", file=sys.stderr)
        sys.exit(1)

    if settings.ENVIRONMENT == "production":
        print("ERROR: Refusing to run in production environment", file=sys.stderr)
        sys.exit(1)

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        from app.core.rls import apply_rls_context, set_rls_role

        set_rls_role("system")
        await apply_rls_context(session)

        count_result = await session.execute(
            select(func.count()).select_from(User).where(User.is_demo_account.is_(False))
        )
        non_demo_count = count_result.scalar() or 0
        if non_demo_count > settings.SEED_NON_DEMO_USER_THRESHOLD:
            print(
                f"ERROR: Found {non_demo_count} non-demo users (threshold: {settings.SEED_NON_DEMO_USER_THRESHOLD})",
                file=sys.stderr,
            )
            sys.exit(1)

        roles = await ensure_roles_and_permissions(session)

        center_result = await session.execute(
            select(TrainingCenter).where(TrainingCenter.name == "Aspect Ta'lim Markazi")
        )
        center = center_result.scalar_one_or_none()
        if not center:
            center = TrainingCenter(
                name="Aspect Ta'lim Markazi",
                stir="123456789",
                director_name="Direktor Aspekt",
                phone="+998662123456",
                center_type="private",
                is_active=True,
            )
            session.add(center)
            await session.flush()

        print("\n" + "=" * 60)
        print("WARNING: DEMO CREDENTIALS — NON-PRODUCTION ONLY")
        print("=" * 60 + "\n")

        for role_code, username, password, mfa in DEMO_USERS:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role_id=roles[role_code].id,
                    center_id=center.id if role_code in {"center_director", "center_admin", "teacher"} else None,
                    is_demo_account=True,
                    is_active=True,
                    password_changed_at=datetime.now(UTC),
                )
                session.add(user)
                await session.flush()

            if mfa:
                secret = pyotp.random_base32()
                user.mfa_enabled = True
                user.mfa_method = "totp"
                user.mfa_secret_encrypted = encrypt_totp_secret(secret)
                totp = pyotp.TOTP(secret)
                print(f"Role: {role_code}")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print(f"  TOTP Secret: {secret}")
                print(f"  TOTP URI: {totp.provisioning_uri(name=username, issuer_name='TMB')}")
                print()
            else:
                print(f"Role: {role_code}")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print()

        parent_role = roles["parent"]
        parent_result = await session.execute(select(User).where(User.phone == PARENT_PHONE))
        parent = parent_result.scalar_one_or_none()
        if not parent:
            parent = User(
                phone=PARENT_PHONE,
                role_id=parent_role.id,
                is_demo_account=True,
                is_active=True,
                locale_preference="uz",
            )
            session.add(parent)

        api_key = f"tamor_demo_sk_live_{secrets.token_hex(16)}"
        hmac_secret = secrets.token_hex(32)
        print("External API Consumer:")
        print(f"  API Key: {api_key}")
        print(f"  HMAC Secret: {hmac_secret}")
        print()
        print("Parent/Guardian:")
        print(f"  Phone: {PARENT_PHONE}")
        print("  OTP: logged to console in dev (no real SMS)")

        await seed_education_data(session, center, roles)

        from app.services import rating_service

        await rating_service.compute_ratings(session)
        print("Demo ratings computed.")

        from app.models.analytics_notifications import AiAnalysisLog, AiPrediction
        from app.services import notification_service

        admin_user = (
            await session.execute(select(User).where(User.username == "admin.tmb"))
        ).scalar_one_or_none()
        operator_user = (
            await session.execute(select(User).where(User.username == "operator.hokimiyat"))
        ).scalar_one_or_none()

        existing_preds = (await session.execute(select(AiPrediction).limit(1))).scalar_one_or_none()
        if not existing_preds:
            today = date.today()
            period_start = date.today() - timedelta(days=30)
            session.add(
                AiPrediction(
                    prediction_type="fastest_growing_center",
                    payload={
                        "center_id": str(center.id),
                        "center_name": center.name,
                        "new_students": 1,
                        "total_students": 1,
                        "growth_rate_pct": 100.0,
                    },
                    confidence_score=0.85,
                    period_start=period_start,
                    period_end=today,
                )
            )
            session.add(
                AiPrediction(
                    prediction_type="education_gap_index",
                    payload={
                        "gap_index": 0.42,
                        "interpretation": "lower_is_better",
                        "total_centers": 2,
                        "total_students": 2,
                        "certification_rate_pct": 50.0,
                        "student_teacher_ratio": 1.0,
                    },
                    confidence_score=0.88,
                    period_start=period_start,
                    period_end=today,
                )
            )
            session.add(
                AiAnalysisLog(
                    run_id=__import__("uuid").uuid4(),
                    status="completed",
                    metrics_count=2,
                    duration_ms=120,
                    triggered_by="seed",
                )
            )
            print("Demo AI predictions seeded.")

        if admin_user:
            await notification_service.create_notification(
                session,
                user_id=admin_user.id,
                event_type="rating_change",
                context={
                    "center_name": center.name,
                    "rank": 1,
                    "direction": "o'rnini saqladi",
                    "change": "0",
                },
                channels=["in_app"],
            )
        if operator_user:
            await notification_service.create_notification(
                session,
                user_id=operator_user.id,
                event_type="license_expiry",
                context={"center_name": center.name, "days": 30},
                channels=["in_app"],
            )
            print("Demo notifications created.")

        print("\n" + "=" * 60 + "\n")

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
