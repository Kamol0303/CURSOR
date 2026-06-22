#!/usr/bin/env python3
"""Pre-deployment gate — blocks production deploy if unsafe configuration detected."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.production import validate_no_demo_accounts, validate_production_settings
from app.models.education import Student, Teacher
from app.models.identity import TrainingCenter, User
from app.models.ratings_certs import Certificate


async def check_demo_data(session) -> list[str]:
    errors: list[str] = []
    demo_users = (
        await session.execute(select(func.count()).select_from(User).where(User.is_demo_account.is_(True)))
    ).scalar() or 0
    if demo_users:
        errors.append(f"Found {demo_users} demo accounts (is_demo_account=true)")

    for model, label in [
        (TrainingCenter, "demo centers"),
        (Student, "demo students"),
        (Teacher, "demo teachers"),
        (Certificate, "demo certificates"),
    ]:
        count = (
            await session.execute(select(func.count()).select_from(model).where(model.is_demo_data.is_(True)))
        ).scalar() or 0
        if count:
            errors.append(f"Found {count} {label} (is_demo_data=true)")
    return errors


async def run_checks(skip_demo: bool = False) -> int:
    errors = validate_production_settings()
    if settings.SECRETS_BACKEND != "vault":
        errors.append("SECRETS_BACKEND must be 'vault' for production deploy")
    elif not settings.VAULT_ADDR:
        errors.append("VAULT_ADDR must be set when SECRETS_BACKEND=vault")
    elif not settings.VAULT_TOKEN:
        errors.append("VAULT_TOKEN must be set when SECRETS_BACKEND=vault")

    if not Path(settings.JWT_PUBLIC_KEY_PATH).exists():
        errors.append(f"JWT public key missing at {settings.JWT_PUBLIC_KEY_PATH}")

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        demo_err = await validate_no_demo_accounts(session)
        if demo_err:
            errors.append(demo_err)
        if not skip_demo:
            errors.extend(await check_demo_data(session))

    await engine.dispose()

    if errors:
        print("PRE-DEPLOY CHECK FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    print("PRE-DEPLOY CHECK PASSED")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="TMB pre-deployment safety gate")
    parser.add_argument(
        "--skip-demo-data-check",
        action="store_true",
        help="Skip is_demo_data entity checks (still checks is_demo_account users)",
    )
    args = parser.parse_args()
    if settings.ENVIRONMENT != "production":
        print("WARNING: ENVIRONMENT is not 'production' — running checks anyway", file=sys.stderr)
    sys.exit(asyncio.run(run_checks(skip_demo=args.skip_demo_data_check)))


if __name__ == "__main__":
    main()
