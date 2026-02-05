from pydantic import BaseModel
from datetime import datetime


class AuthTokenBase(BaseModel):
    user_id: str
    token: str
    expires_at: datetime


class AuthTokenCreate(AuthTokenBase):
    pass


class AuthTokenOut(AuthTokenBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
