#!/usr/bin/env python3
"""Show MFA QR code in the terminal for a seeded user.

Usage (inside backend container):
  python scripts/show_mfa_qr.py admin.tmb
  python scripts/show_mfa_qr.py --list
"""

from __future__ import annotations

import argparse
import asyncio
import sys

import pyotp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings
from app.core.security import decrypt_totp_secret
from app.models.identity import User
from scripts.totp_qr_terminal import print_totp_qr


async def run(username: str | None, list_users: bool) -> int:
    if settings.ENVIRONMENT == "production":
        print("ERROR: Refusing to run in production", file=sys.stderr)
        return 1

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        if list_users:
            result = await session.execute(
                select(User)
                .where(User.mfa_enabled.is_(True), User.username.is_not(None))
                .order_by(User.username)
            )
            users = result.scalars().all()
            if not users:
                print("No MFA-enabled users found. Run seed_demo_users.py first.")
                return 1
            print("MFA-enabled users:")
            for user in users:
                print(f"  - {user.username}")
            print("\nShow QR: python scripts/show_mfa_qr.py <username>")
            return 0

        if not username:
            print("ERROR: username required (or use --list)", file=sys.stderr)
            return 1

        result = await session.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            print(f"ERROR: User not found: {username}", file=sys.stderr)
            return 1
        if not user.mfa_enabled or not user.mfa_secret_encrypted:
            print(f"ERROR: {username} does not have MFA configured", file=sys.stderr)
            return 1

        secret = decrypt_totp_secret(user.mfa_secret_encrypted)
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=username, issuer_name="TMB")

        print()
        print(f"Username: {username}")
        print(f"TOTP Secret: {secret}")
        print(f"TOTP URI: {uri}")
        print()
        print_totp_qr(uri, username=username)
        print()

    await engine.dispose()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Print MFA QR code in terminal")
    parser.add_argument("username", nargs="?", help="Login username, e.g. admin.tmb")
    parser.add_argument("--list", action="store_true", help="List MFA-enabled usernames")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.username, args.list)))


if __name__ == "__main__":
    main()
