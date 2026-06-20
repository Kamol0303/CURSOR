from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TAMOR_", case_sensitive=False)

    app_name: str = "TaMoR API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./tamor.db"
    sync_database_url: str = "sqlite:///./tamor.db"
    redis_url: str = "redis://localhost:6379/0"
    allowed_origins: str = "http://localhost:3000"

    jwt_private_key: str = Field(
        default="""-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDMXYCFd8g9+dvz
t45K9PuM4NW4PuYqZFeoc/MsBBdzcIm5KFtJBb8IaKQAa1ouSlPRWr6eLLoaXg0n
ydglmFPKZzIzlsOJ73f6H7lu550EpkCQTdNTTCTuxvx4G1gw7cEynx/9UPuCzeW2
D7kdx1Cmy8xlxdsqe5aUkUVoHkR17wNj+23MteFBWBLeuUF1EbEBqeD+V/OFkOsq
hkWAMSRAupNldGvQPTy+moV38RFgR4nqFgM3f4JwbjssTShch/+zetBneIqRP3iL
5oqmYaBANYYeJKpZLSfZIOeGuoKBBtu9jTGxIJO1cfsaQil8o0dE9PDcn5JUfZ5j
x7GXwfKnAgMBAAECggEADT68HypZvIaOlledrcb97K3/u/67nSC+u6i0KHSlbnJr
QqhWbj+kl29svag3gouHrihi9U5xy1awJJWE4D7ko1gX3VcWmkB+dqQKuSDiwNPj
mFaq7RmgxSb5YvFmwFkQbe75PEo82sfsbOXM+hyaYg0QVMJDh5fV9RALPwnDJx92
WuOZLgI/USNClpOSP1V9q+srdHqRwgCN5BUo7/sAA2d7cAM1SQvSYEQ6N685+vMW
WvA5dtVy+4Mc9ClS3Hq/0EW+GETOXTyQDlhx9h1y7DXe+q2uFQj9eT6D5v/tKXqv
23eIleqFmh2YPNWouSyIXFj5ATNVpB2MbCmrmEjf6QKBgQDvsIm/U7K9mlRcHECU
La76HMltkLke4aq0FrT5h3rDKKvcqmAvDxhnINEn3MhYPFLZziRCf3NSjWT+FX22
IsMJlOpq/IqBsPhpZRsnNRrhA3f7ajjJtxmvanyNyYNv/BVYOJShSFQ9XD/ondhF
SERAft5HZGS9hzqPILEYgFcrqQKBgQDaRZp7DigYgl2A8p48dS1QcHF4TRpXXPjQ
q04WDQcFm9b5Dx4p/rQ5Je6Vc8aIQBFrMCFXqdvr1/DFUIhyJamUsL9TL2NnaH5u
LIUnj1OkhxjHwQ0Cu7891bxcDwNKPswgJ2CHKS0KZiRW3g74McOdwlyddx/eoQMF
CI9OBuedzwKBgQCC29sYfdWj9lIAR9xqCdbx7i16h/zJg2LzF0KOyQyY5+eMfegt
SQyFoUEPhlZK9gQ1rXnWZEbN1yxAG/OaMLhSzt58sovb6oZ05CJC8ZdPKdmjhYaj
ejensXd24YHE7depZpqewyJarbamhSbCDIZWv+0TBRiK8P1jjvGg8tCkoQKBgHsH
eIeb9yW5dZLVLjPNqHkKqCqy6wILOYQEysLLHQYgTQ+dYdcx5cvAgbZjx6fM1QSh
4GlVKMzKrr/JIN+WMvvIlE8DCviigYEAPx2JQBAgxerx+a9su+LSspUBMU2MD+qf
x1zn7KdL43fDOpTTF/u4LhPjrWcDQnx30q6cXbkpAoGBAJM3itdI/bN3f/MGA0rZ
DQ0q0O13BYJXPlmzuhoMo9DcVZj5mRs63fiDK0tnp5D4MIoOKQakPD5sq1ODC41q
UZNL5elPWlawsUZY2vYbAWDXQhCMihrkx4l7QSpJI7J0Cs0+BJHEX8AKZl5+8KdQ
94L1CgJAJ+J45ZqPkYct3Zcc
-----END PRIVATE KEY-----""",
    )
    jwt_public_key: str = Field(
        default="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzF2AhXfIPfnb87eOSvT7
jODVuD7mKmRXqHPzLAQXc3CJuShbSQW/CGikAGtaLkpT0Vq+niy6Gl4NJ8nYJZhT
ymcyM5bDie93+h+5buedBKZAkE3TU0wk7sb8eBtYMO3BMp8f/VD7gs3ltg+5HcdQ
psvMZcXbKnuWlJFFaB5Ede8DY/ttzLXhQVgS3rlBdRGxAang/lfzhZDrKoZFgDEk
QLqTZXRr0D08vpqFd/ERYEeJ6hYDN3+CcG47LE0oXIf/s3rQZ3iKkT94i+aKpmGg
QDWGHiSqWS0n2SDnhrqCgQbbvY0xsSCTtXH7GkIpfKNHRPTw3J+SVH2eY8exl8Hy
pwIDAQAB
-----END PUBLIC KEY-----""",
    )
    mfa_encryption_key: str = "qnTo_D3_1wN285-sJAFAmvLGHNwL1JbfLUH195otpU4="
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    parent_otp_ttl_seconds: int = 300
    refresh_cookie_name: str = "tamor_refresh"
    api_key_grace_hours: int = 24
    breached_passwords_path: str = str(BASE_DIR / "app" / "data" / "breached_passwords.txt")
    demo_seed_guard: str = "production"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
