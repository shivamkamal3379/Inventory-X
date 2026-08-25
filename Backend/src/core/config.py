"""Application settings.

Every value is environment-driven. The only hard rule is that SECRET_KEY must be
supplied explicitly whenever ENVIRONMENT is not "development" — the app refuses to
boot in staging/production with a default key rather than silently signing tokens
anyone can forge.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET_KEY = "dev-only-insecure-key-do-not-use-outside-development"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --- Core ---
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False
    PROJECT_NAME: str = "Inventory X API"
    VERSION: str = "1.0.0"
    # Set to "/api" when served behind the nginx reverse proxy so that the
    # OpenAPI docs generate correct absolute URLs.
    ROOT_PATH: str = ""

    # --- Database ---
    # Example: postgresql+psycopg://inventoryx:pass@db:5432/inventoryx
    DATABASE_URL: str = "sqlite:///./inventory.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # --- Auth ---
    SECRET_KEY: str = DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Registration is open on a fresh install so the first admin can be created,
    # then should be closed via env. See docs/DEPLOYMENT.md.
    ALLOW_REGISTRATION: bool = True
    MIN_PASSWORD_LENGTH: int = 8

    # --- Bootstrap admin (optional; created on startup when both are set) ---
    FIRST_ADMIN_USERNAME: str | None = None
    FIRST_ADMIN_PASSWORD: str | None = None

    # --- CORS ---
    # Comma-separated list. "*" is rejected outside development.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Rate limiting (login brute-force protection) ---
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 10
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 300

    # --- Logging ---
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_JSON: bool = True

    # --- API behaviour ---
    MAX_PAGE_SIZE: int = Field(default=200, ge=1, le=1000)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT in ("staging", "production")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalise_db_url(cls, v: str) -> str:
        # Managed providers hand out "postgres://" URLs, which SQLAlchemy 2.x
        # does not recognise. Rewrite to the psycopg v3 driver.
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    @model_validator(mode="after")
    def _guard_production(self) -> "Settings":
        if not self.is_production:
            return self

        if self.SECRET_KEY == DEV_SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be set to a unique value of at least 32 characters "
                f"when ENVIRONMENT={self.ENVIRONMENT}. "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if "*" in self.cors_origin_list:
            raise ValueError(
                "CORS_ORIGINS cannot be '*' in production — list your real frontend origins."
            )
        if self.DATABASE_URL.startswith("sqlite"):
            raise ValueError(
                "SQLite is not supported in production. Point DATABASE_URL at PostgreSQL."
            )
        if self.DEBUG:
            raise ValueError("DEBUG must be False in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
