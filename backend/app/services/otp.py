from __future__ import annotations

import secrets


def generate_sms_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def dev_delivery_message(phone: str, code: str) -> str:
    return f"[DEV SMS OTP] phone={phone} code={code}"
