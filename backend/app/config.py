from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://tamor:tamor_dev_password@localhost:5432/tamor"
    database_url_sync: str = "postgresql://tamor:tamor_dev_password@localhost:5432/tamor"
    # Set USE_SQLITE=true for local dev without PostgreSQL:
    # DATABASE_URL=sqlite+aiosqlite:///./tamor.db
    # DATABASE_URL_SYNC=sqlite:///./tamor.db
    use_sqlite: bool = False
    redis_url: str = "redis://localhost:6379/0"

    jwt_private_key_path: str = "./keys/jwt_private.pem"
    jwt_public_key_path: str = "./keys/jwt_public.pem"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    jwt_algorithm: str = "RS256"

    totp_encryption_key: str = "dGVzdC1rZXktMzItYnl0ZXMtZm9yLWRldg=="
    pinfl_encryption_key: str = "dGVzdC1rZXktMzItYnl0ZXMtZm9yLWRldg=="

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "tamor_minio"
    s3_secret_key: str = "tamor_minio_secret"
    s3_bucket: str = "tamor-files"

    sms_provider: str = "console"

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
