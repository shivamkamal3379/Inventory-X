"""Password hashing, JWT issuing/validation and the current-user dependency."""

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.models.auth import User

# tokenUrl is relative so it keeps working when the app is mounted behind the
# reverse proxy at /api (FastAPI prepends root_path).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# bcrypt truncates silently past 72 bytes; reject rather than accept a password
# whose tail is ignored.
BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise HTTPException(
            status_code=422,  # renamed across Starlette versions; the literal is stable
            detail=f"Password must be at most {BCRYPT_MAX_BYTES} bytes.",
        )
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed hash in the database — treat as a failed login, not a 500.
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire, "iat": now, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise CREDENTIALS_EXCEPTION from None

    if payload.get("type") != "access":
        raise CREDENTIALS_EXCEPTION

    username = payload.get("sub")
    if not username:
        raise CREDENTIALS_EXCEPTION

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise CREDENTIALS_EXCEPTION
    return user
