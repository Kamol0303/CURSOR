from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_NAME: str = "TMB API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://tamor:tamor_dev@localhost:5432/tamor"
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_MEMORY_REDIS: bool = False

    JWT_PRIVATE_KEY_PATH: str = "/secrets/jwt_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "/secrets/jwt_public.pem"
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    TOTP_ENCRYPTION_KEY: str = "dev-only-change-in-production-32bytes!!"
    PINFL_ENCRYPTION_KEY: str = "dev-pinfl-key-change-in-prod!!"

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    LOGIN_MIN_RESPONSE_MS: int = 200
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15
    MFA_VERIFY_MAX_ATTEMPTS: int = 5
    MFA_VERIFY_WINDOW_SECONDS: int = 300

    SEED_NON_DEMO_USER_THRESHOLD: int = 5

    AI_ANALYTICS_URL: str = "http://ai-analytics:8001"
    # LLM gateway (BazaarLink OpenAI-compatible or direct OpenAI)
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://bazaarlink.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-4o-mini"
    AI_ENABLED: bool = True
    # Gemini fallback when BazaarLink limit/quota exceeded
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    # Legacy aliases — LLM_API_KEY takes precedence when set
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_EXAM_ENABLED: bool = True
    AI_EXAM_MAX_QUESTIONS: int = 30
    AI_LESSON_MAX_SLIDES: int = 12
    AI_LESSON_MAX_ROUNDS: int = 10
    SMS_WEBHOOK_SECRET: str = "dev-sms-webhook-secret-change-me"
    ESKIZ_API_TOKEN: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = "dev-telegram-webhook-secret"
    PARENT_OTP_EXPIRE_SECONDS: int = 300
    PARENT_OTP_MAX_ATTEMPTS: int = 5

    SECRETS_BACKEND: str = "file"
    VAULT_ADDR: str = ""
    VAULT_TOKEN: str = ""
    VAULT_MOUNT: str = "secret"
    VAULT_SECRET_PREFIX: str = "tmb"

    ESKIZ_EMAIL: str = ""
    ESKIZ_PASSWORD: str = ""

    # Payment gateways (Click / Payme)
    CLICK_SERVICE_ID: str = ""
    CLICK_SECRET_KEY: str = ""
    PAYME_SECRET_KEY: str = ""
    PAYME_MERCHANT_LOGIN: str = "Paycom"
    PAYME_WEBHOOK_HMAC_SECRET: str = ""
    PAYMENT_WEBHOOK_ALLOW_UNSIGNED_DEV: bool = False

    FILE_UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024
    METRICS_ENABLED: bool = True

    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_SUBJECT: str = "mailto:admin@tmb.local"


settings = Settings()
