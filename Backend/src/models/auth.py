from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from src.core.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
