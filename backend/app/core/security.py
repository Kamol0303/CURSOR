import base64
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

import bcrypt
import pyotp
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.config import settings

MFA_MANDATORY_ROLES = {"super_admin", "hokimiyat_operator", "center_director"}
PASSWORD_MIN_LENGTH = 12
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
PASSWORD_HISTORY_COUNT = 5

_breached_passwords: set[str] | None = None


def _get_fernet(key_setting: str) -> Fernet:
    key = key_setting.encode() if isinstance(key_setting, str) else key_setting
    try:
        return Fernet(key)
    except Exception:
        padded = base64.urlsafe_b64encode(key[:32].ljust(32, b"0"))
        return Fernet(padded)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def load_breached_passwords() -> set[str]:
    global _breached_passwords
    if _breached_passwords is not None:
        return _breached_passwords

    breached_file = Path(__file__).parent.parent.parent / "data" / "breached_passwords.txt"
    if breached_file.exists():
        _breached_passwords = {
            line.strip().lower() for line in breached_file.read_text().splitlines() if line.strip()
        }
    else:
        _breached_passwords = {
            "password123",
            "123456789",
            "qwerty123",
            "admin123",
            "password",
            "12345678",
            "tamor2026",
            "letmein",
            "welcome1",
            "changeme",
        }
    return _breached_passwords


def validate_password_policy(password: str) -> tuple[bool, str | None]:
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, "PASSWORD_TOO_SHORT"
    if not any(c.isupper() for c in password):
        return False, "PASSWORD_MISSING_UPPERCASE"
    if not any(c.islower() for c in password):
        return False, "PASSWORD_MISSING_LOWERCASE"
    if not any(c.isdigit() for c in password):
        return False, "PASSWORD_MISSING_DIGIT"
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "PASSWORD_MISSING_SPECIAL"
    if password.lower() in load_breached_passwords():
        return False, "PASSWORD_BREACHED"
    return True, None


def check_password_history(password: str, history_hashes: list[str]) -> bool:
    return any(verify_password(password, h) for h in history_hashes)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _load_rsa_keys() -> tuple[str, str]:
    private_path = Path(settings.jwt_private_key_path)
    public_path = Path(settings.jwt_public_key_path)

    if private_path.exists() and public_path.exists():
        return private_path.read_text(), public_path.read_text()

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_text(private_pem)
    public_path.write_text(public_pem)
    return private_pem, public_pem


def create_access_token(
    user_id: str,
    role: str,
    center_id: str | None,
    permissions: list[str],
    locale: str,
) -> str:
    private_key, _ = _load_rsa_keys()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "role": role,
        "center_id": center_id,
        "permissions": permissions,
        "locale": locale,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, private_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    _, public_key = _load_rsa_keys()
    try:
        return jwt.decode(token, public_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def encrypt_totp_secret(secret: str) -> str:
    fernet = _get_fernet(settings.totp_encryption_key)
    return fernet.encrypt(secret.encode()).decode()


def decrypt_totp_secret(encrypted: str) -> str:
    fernet = _get_fernet(settings.totp_encryption_key)
    return fernet.decrypt(encrypted.encode()).decode()


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="TaMoR")


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 10) -> list[str]:
    return [secrets.token_hex(4).upper() for _ in range(count)]


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def is_account_locked(user) -> bool:
    if user.is_locked and user.locked_until:
        if datetime.now(UTC) < user.locked_until.replace(tzinfo=UTC):
            return True
    return False


def calculate_lockout_until(failed_attempts: int) -> datetime:
    multiplier = 2 ** max(0, (failed_attempts // MAX_FAILED_ATTEMPTS) - 1)
    minutes = LOCKOUT_MINUTES * multiplier
    return datetime.now(UTC) + timedelta(minutes=minutes)
