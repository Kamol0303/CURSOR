from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://tamor_analytics:tamor_dev@postgres:5432/tamor"
    JWT_PUBLIC_KEY_PATH: str = "/secrets/jwt_public.pem"
    JWT_ALGORITHM: str = "RS256"
    SCHEDULE_CRON_HOUR: int = 2


settings = Settings()
