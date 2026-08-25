from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.rate_limit import client_key, enforce_login_rate_limit, login_limiter
from src.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from src.models.auth import User
from src.schemas.auth import PasswordChange, Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a user account.

    Disabled by setting ALLOW_REGISTRATION=false, which is what you want once the
    first admin exists — otherwise anyone who can reach the API can grant
    themselves full access to the inventory.
    """
    if not settings.ALLOW_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled.",
        )

    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already registered"
        )

    user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _: None = Depends(enforce_login_rate_limit),
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        # One message for both cases, so the response cannot be used to
        # enumerate valid usernames.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

    login_limiter.reset(client_key(request))
    return Token(access_token=create_access_token(subject=user.username))


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Used by the frontend to validate a stored token on boot."""
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    current_user.hashed_password = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
