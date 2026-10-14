import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXORA Pursuit Engine"
    API_V1_STR: str = "/api/v1"

    # Environment & Security
    ENVIRONMENT: str = "development"
    JWT_SECRET: str = "nexora_super_secret_jwt_key_32_bytes_min_length_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    # Use SQLite async fallback for local dev if Postgres isn't up, but production targets Postgres
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./nexora_pursuit.db"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # options: mock, grok, openai, claude
    GROK_API_KEY: str | None = os.getenv("GROK_API_KEY", None)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", None)

    # Event Bus Strategy
    EVENT_BUS: str = os.getenv("EVENT_BUS", "in_memory")  # in_memory, kafka, rabbitmq

    # External Integration Providers
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "mock")
    CALENDAR_PROVIDER: str = os.getenv("CALENDAR_PROVIDER", "mock")
    LINKEDIN_PROVIDER: str = os.getenv("LINKEDIN_PROVIDER", "mock")

    # Default Tenant
    DEFAULT_TENANT_ID: str = "tenant_nexora_default"

    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
