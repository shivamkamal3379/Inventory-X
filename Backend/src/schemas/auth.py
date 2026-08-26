from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.config import settings


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=1, max_length=200)

    @field_validator("username")
    @classmethod
    def _strip_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be blank")
        return v

    @field_validator("password")
    @classmethod
    def _password_policy(cls, v: str) -> str:
        if len(v) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool
    is_superuser: bool = False
    created_at: datetime | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default_factory=lambda: settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        description="Token lifetime in seconds.",
    )


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=1, max_length=200)

    @field_validator("new_password")
    @classmethod
    def _password_policy(cls, v: str) -> str:
        if len(v) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters")
        return v
