#!/usr/bin/env python3
"""Purge all demo accounts and demo-tagged data before production go-live.

Usage:
  python scripts/purge_demo_data.py --i-understand-this-deletes-demo-data
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.rls import apply_rls_context, set_rls_role
from app.models.education import Guardian, Student, Teacher
from app.models.identity import RefreshToken, TrainingCenter, User
from app.models.ratings_certs import Certificate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purge TaMoR demo data")
    parser.add_argument(
        "--i-understand-this-deletes-demo-data",
        action="store_true",
        required=True,
        help="Required confirmation flag",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report counts without deleting")
    return parser.parse_args()


async def purge() -> None:
    args = parse_args()

    if settings.ENVIRONMENT == "production" and not args.i_understand_this_deletes_demo_data:
        print("ERROR: Confirmation flag required", file=sys.stderr)
        sys.exit(1)

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        set_rls_role("system")
        await apply_rls_context(session)

        demo_user_ids = (
            await session.execute(select(User.id).where(User.is_demo_account.is_(True)))
        ).scalars().all()

        counts = {
            "demo_users": len(demo_user_ids),
            "demo_centers": (
                await session.execute(
                    select(TrainingCenter).where(TrainingCenter.is_demo_data.is_(True))
                )
            ).scalars().all(),
        }

        print("Demo data to purge:")
        print(f"  Users (is_demo_account): {counts['demo_users']}")
        print(f"  Centers (is_demo_data): {len(counts['demo_centers'])}")

        if args.dry_run:
            print("Dry run — no changes made.")
            await engine.dispose()
            return

        if demo_user_ids:
            await session.execute(delete(RefreshToken).where(RefreshToken.user_id.in_(demo_user_ids)))
            await session.execute(delete(User).where(User.is_demo_account.is_(True)))

        await session.execute(delete(Certificate).where(Certificate.is_demo_data.is_(True)))
        await session.execute(delete(Guardian).where(Guardian.student_id.in_(
            select(Student.id).where(Student.is_demo_data.is_(True))
        )))
        await session.execute(delete(Student).where(Student.is_demo_data.is_(True)))
        await session.execute(delete(Teacher).where(Teacher.is_demo_data.is_(True)))
        await session.execute(delete(TrainingCenter).where(TrainingCenter.is_demo_data.is_(True)))

        await session.commit()
        print("Demo data purged successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(purge())
