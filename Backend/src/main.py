"""Inventory X API application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import SessionLocal, engine
from src.core.errors import register_exception_handlers
from src.core.logging_config import configure_logging
from src.core.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from src.routers import (
    agents,
    auth,
    contracts,
    dashboard,
    health,
    items,
    parties,
    payments,
    prices,
    returns,
)
from src.routers.deps import CurrentUser

logger = logging.getLogger("inventoryx")


def _bootstrap_admin() -> None:
    """Create the initial admin from env vars, if configured and absent.

    Lets a fresh deployment come up with a usable login without leaving
    /auth/register open to the internet.
    """
    if not (settings.FIRST_ADMIN_USERNAME and settings.FIRST_ADMIN_PASSWORD):
        return

    from src.core.security import hash_password
    from src.models.auth import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.FIRST_ADMIN_USERNAME).first()
        if existing:
            return
        db.add(
            User(
                username=settings.FIRST_ADMIN_USERNAME,
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                is_superuser=True,
            )
        )
        db.commit()
        logger.info("Bootstrapped admin user %r", settings.FIRST_ADMIN_USERNAME)
    except Exception:
        db.rollback()
        logger.exception("Failed to bootstrap admin user")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info(
        "Starting %s v%s (env=%s)",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )

    # Schema is owned by Alembic (`alembic upgrade head`), which the container
    # entrypoint runs before the server starts. create_all() is used only for
    # local SQLite runs and tests, where there is no migration step.
    if settings.DATABASE_URL.startswith("sqlite"):
        from src import models  # noqa: F401  - registers every table on Base
        from src.core.database import Base

        Base.metadata.create_all(bind=engine)
        logger.info("SQLite detected — tables ensured via create_all()")

    _bootstrap_admin()
    yield
    engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend API for Inventory X / RentalPro — rental inventory, parties and transactions.",
        lifespan=lifespan,
        root_path=settings.ROOT_PATH,
        # Interactive docs are useful in development but describe every endpoint
        # and payload shape; keep them off the public production surface.
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )

    register_exception_handlers(app)

    # Public: probes and authentication.
    app.include_router(health.router)
    app.include_router(auth.router)

    # Everything else requires a valid bearer token. Applying the dependency at
    # include time means any route added to these routers later is protected by
    # default rather than by remembering to annotate it.
    protected = [
        agents.router,
        items.router,
        parties.router,
        contracts.router,
        returns.router,
        payments.router,
        prices.router,
        dashboard.router,
    ]
    for router in protected:
        app.include_router(router, dependencies=[CurrentUser])

    @app.get("/", tags=["health"], include_in_schema=False)
    def root():
        return {
            "status": "running",
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": None if settings.is_production else "/docs",
        }

    return app


app = create_app()
