#!/usr/bin/env python3
"""Purge all demo accounts and demo-tagged data before production go-live.

Usage:
  python scripts/purge_demo_data.py --i-understand-this-deletes-demo-data
  python scripts/purge_demo_data.py --i-understand-this-deletes-demo-data --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.rls import apply_rls_context, set_rls_role
from app.models.analytics_notifications import (
    Notification,
    NotificationLog,
    NotificationPreference,
)
from app.models.education import Enrollment, Group, Guardian, Student, Teacher, TeacherSubject
from app.models.identity import (
    AuditLog,
    DeviceFingerprint,
    LoginAuditLog,
    MfaBackupCode,
    PasswordResetToken,
    RefreshToken,
    SecurityEvent,
    Session,
    TrainingCenter,
    User,
)
from app.models.integrations import TelegramSubscription
from app.models.ratings_certs import (
    Certificate,
    CertificateVerification,
    RatingHistory,
    Report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purge TMB demo data before go-live")
    parser.add_argument(
        "--i-understand-this-deletes-demo-data",
        action="store_true",
        required=True,
        help="Required confirmation flag",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report counts without deleting")
    parser.add_argument(
        "--allow-non-production",
        action="store_true",
        help="Allow running when ENVIRONMENT is not production (staging test only)",
    )
    return parser.parse_args()


async def _count(session, stmt) -> int:
    return (await session.execute(stmt)).scalar() or 0


async def collect_counts(session) -> dict[str, int]:
    demo_users = select(User.id).where(User.is_demo_account.is_(True))
    demo_centers = select(TrainingCenter.id).where(TrainingCenter.is_demo_data.is_(True))
    demo_students = select(Student.id).where(Student.is_demo_data.is_(True))
    demo_teachers = select(Teacher.id).where(Teacher.is_demo_data.is_(True))
    demo_certs = select(Certificate.id).where(Certificate.is_demo_data.is_(True))

    return {
        "demo_users": await _count(session, select(func.count()).select_from(User).where(User.is_demo_account.is_(True))),
        "demo_centers": await _count(
            session, select(func.count()).select_from(TrainingCenter).where(TrainingCenter.is_demo_data.is_(True))
        ),
        "demo_students": await _count(
            session, select(func.count()).select_from(Student).where(Student.is_demo_data.is_(True))
        ),
        "demo_teachers": await _count(
            session, select(func.count()).select_from(Teacher).where(Teacher.is_demo_data.is_(True))
        ),
        "demo_certificates": await _count(
            session, select(func.count()).select_from(Certificate).where(Certificate.is_demo_data.is_(True))
        ),
        "demo_ratings": await _count(
            session, select(func.count()).select_from(RatingHistory).where(RatingHistory.center_id.in_(demo_centers))
        ),
        "demo_enrollments": await _count(
            session,
            select(func.count())
            .select_from(Enrollment)
            .where(or_(Enrollment.center_id.in_(demo_centers), Enrollment.student_id.in_(demo_students))),
        ),
        "demo_refresh_tokens": await _count(
            session, select(func.count()).select_from(RefreshToken).where(RefreshToken.user_id.in_(demo_users))
        ),
        "demo_cert_verifications": await _count(
            session,
            select(func.count())
            .select_from(CertificateVerification)
            .where(CertificateVerification.certificate_id.in_(demo_certs)),
        ),
    }


async def purge_demo_rows(session) -> None:
    """Delete demo-tagged rows in FK-safe order."""
    demo_users = select(User.id).where(User.is_demo_account.is_(True))
    demo_centers = select(TrainingCenter.id).where(TrainingCenter.is_demo_data.is_(True))
    demo_students = select(Student.id).where(Student.is_demo_data.is_(True))
    demo_teachers = select(Teacher.id).where(Teacher.is_demo_data.is_(True))
    demo_certs = select(Certificate.id).where(Certificate.is_demo_data.is_(True))

    await session.execute(
        delete(CertificateVerification).where(CertificateVerification.certificate_id.in_(demo_certs))
    )
    await session.execute(delete(Certificate).where(Certificate.is_demo_data.is_(True)))
    await session.execute(delete(RatingHistory).where(RatingHistory.center_id.in_(demo_centers)))
    await session.execute(delete(Report).where(Report.requested_by.in_(demo_users)))
    await session.execute(
        delete(Enrollment).where(
            or_(Enrollment.center_id.in_(demo_centers), Enrollment.student_id.in_(demo_students))
        )
    )
    await session.execute(delete(Guardian).where(Guardian.student_id.in_(demo_students)))
    await session.execute(delete(TeacherSubject).where(TeacherSubject.teacher_id.in_(demo_teachers)))
    await session.execute(delete(Teacher).where(Teacher.is_demo_data.is_(True)))
    await session.execute(delete(Group).where(Group.center_id.in_(demo_centers)))
    await session.execute(delete(Student).where(Student.is_demo_data.is_(True)))

    demo_notifications = select(Notification.id).where(Notification.user_id.in_(demo_users))
    await session.execute(delete(NotificationLog).where(NotificationLog.notification_id.in_(demo_notifications)))
    await session.execute(delete(Notification).where(Notification.user_id.in_(demo_users)))
    await session.execute(delete(NotificationPreference).where(NotificationPreference.user_id.in_(demo_users)))
    await session.execute(delete(TelegramSubscription).where(TelegramSubscription.user_id.in_(demo_users)))

    for model, column in [
        (RefreshToken, RefreshToken.user_id),
        (Session, Session.user_id),
        (DeviceFingerprint, DeviceFingerprint.user_id),
        (LoginAuditLog, LoginAuditLog.user_id),
        (MfaBackupCode, MfaBackupCode.user_id),
        (PasswordResetToken, PasswordResetToken.user_id),
        (SecurityEvent, SecurityEvent.user_id),
        (AuditLog, AuditLog.user_id),
    ]:
        await session.execute(delete(model).where(column.in_(demo_users)))

    await session.execute(delete(User).where(User.is_demo_account.is_(True)))
    await session.execute(delete(TrainingCenter).where(TrainingCenter.is_demo_data.is_(True)))


async def purge() -> None:
    args = parse_args()

    if settings.ENVIRONMENT != "production" and not args.allow_non_production:
        print(
            "ERROR: Refusing purge outside production. "
            "Use --allow-non-production only to test on staging.",
            file=sys.stderr,
        )
        sys.exit(1)

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        set_rls_role("system")
        await apply_rls_context(session)

        counts = await collect_counts(session)
        print("Demo data to purge:")
        for label, value in counts.items():
            print(f"  {label}: {value}")

        total = sum(counts.values())
        if total == 0:
            print("Nothing to purge.")
            await engine.dispose()
            return

        if args.dry_run:
            print("Dry run — no changes made.")
            await engine.dispose()
            return

        await purge_demo_rows(session)
        await session.commit()
        print("Demo data purged successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(purge())
