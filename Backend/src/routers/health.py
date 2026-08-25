"""Liveness and readiness probes.

Kept separate because they mean different things to an orchestrator: /health
says the process is up, /ready says it can actually serve traffic. Docker's
healthcheck and any future k8s readiness probe use /ready; restarting a
container because the database blipped would be the wrong response, which is
why /health never touches the database.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready")
def ready(response: Response, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "down", "error": str(exc)[:200]}
    return {"status": "ready", "database": "up"}
