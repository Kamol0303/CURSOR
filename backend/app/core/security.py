import hashlib
import hmac
import secrets
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.core.config import settings

password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# Computed once at import for constant-time login path when username not found
DUMMY_PASSWORD_HASH: str = password_hasher.hash("__tamor_timing_dummy_password__")

BREACHED_PASSWORDS: set[str] = set()


def load_breached_passwords() -> None:
    path = Path(__file__).parent / "data" / "breached_passwords.txt"
    if path.exists():
        BREACHED_PASSWORDS.update(
            line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
        )


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        password_hasher.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False


def is_breached_password(password: str) -> bool:
    return password.lower() in BREACHED_PASSWORDS


def validate_password_policy(password: str) -> list[str]:
    errors: list[str] = []
    if len(password) < 12:
        errors.append("PASSWORD_TOO_SHORT")
    if not any(c.isupper() for c in password):
        errors.append("PASSWORD_MISSING_UPPERCASE")
    if not any(c.islower() for c in password):
        errors.append("PASSWORD_MISSING_LOWERCASE")
    if not any(c.isdigit() for c in password):
        errors.append("PASSWORD_MISSING_DIGIT")
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        errors.append("PASSWORD_MISSING_SPECIAL")
    if is_breached_password(password):
        errors.append("PASSWORD_BREACHED")
    return errors


def _load_key(path: str) -> str:
    key_path = Path(path)
    if not key_path.exists():
        raise FileNotFoundError(f"JWT key not found at {path}")
    return key_path.read_text(encoding="utf-8")


def create_access_token(
    *,
    user_id: UUID,
    role: str,
    center_id: UUID | None,
    permissions: list[str],
    locale: str,
) -> tuple[str, str, datetime]:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid4())
    payload = {
        "sub": str(user_id),
        "role": role,
        "center_id": str(center_id) if center_id else None,
        "permissions": permissions,
        "locale": locale,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": jti,
    }
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    token = jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expire


def decode_access_token(token: str) -> dict:
    public_key = _load_key(settings.JWT_PUBLIC_KEY_PATH)
    return jwt.decode(
        token,
        public_key,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_aud": False},
    )


def verify_access_token(token: str) -> dict:
    try:
        return decode_access_token(token)
    except JWTError as exc:
        raise ValueError("INVALID_TOKEN") from exc


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _get_fernet() -> Fernet:
    import base64

    raw = hashlib.sha256(settings.TOTP_ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))


def encrypt_totp_secret(secret: str) -> str:
    return _get_fernet().encrypt(secret.encode()).decode()


def decrypt_totp_secret(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()


def hash_backup_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def device_fingerprint_hash(user_agent: str, client_hint: str = "") -> str:
    raw = f"{user_agent}|{client_hint}".encode()
    return hashlib.sha256(raw).hexdigest()


def constant_time_elapsed(start: float) -> None:
    elapsed_ms = (time.perf_counter() - start) * 1000
    remaining = settings.LOGIN_MIN_RESPONSE_MS - elapsed_ms
    if remaining > 0:
        time.sleep(remaining / 1000)


def sign_hmac_request(secret: str, timestamp: str, body_hash: str) -> str:
    message = f"{timestamp}.{body_hash}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


load_breached_passwords()
