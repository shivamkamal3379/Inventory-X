"""Uniform JSON error envelope for every failure mode.

Clients get {"detail": ..., "request_id": ...} whatever goes wrong, and
unexpected exceptions never leak a stack trace or a database string.
"""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger("inventoryx.errors")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": _request_id(request)},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,  # renamed across Starlette versions; the literal is stable
            content={
                "detail": "Validation failed",
                "errors": [
                    {
                        "field": ".".join(str(p) for p in err["loc"][1:]) or "body",
                        "message": err["msg"],
                    }
                    for err in exc.errors()
                ],
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        # A unique/FK violation is a client mistake (409), not a server fault —
        # but the driver message can contain table and column names, so it is
        # logged rather than returned.
        logger.warning("Integrity error: %s", exc, exc_info=False)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "The request conflicts with existing data.",
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database temporarily unavailable.",
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error.",
                "request_id": _request_id(request),
            },
        )
