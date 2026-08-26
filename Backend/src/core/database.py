"""Database engine, session factory and the FastAPI session dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    # SQLite has no real pool and needs check_same_thread disabled for TestClient.
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DB_ECHO,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        # Pin the session timezone to UTC. Date-truncating aggregates such as
        # func.date() are evaluated in the session timezone, so without this the
        # dashboard's daily buckets would shift with the server's locale.
        connect_args={"options": "-c timezone=utc"}
        if settings.DATABASE_URL.startswith("postgresql")
        else {},
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE,
        # Verifies a connection is still alive before handing it out, so a
        # restarted database or an idle-timeout proxy doesn't surface as a 500.
        pool_pre_ping=True,
        echo=settings.DB_ECHO,
    )


if _is_sqlite:

    @event.listens_for(Engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        """SQLite ignores FK constraints unless they are switched on per-connection.

        Without this the test suite would silently accept rows that PostgreSQL
        rejects, which is exactly the class of bug that survives to production.
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session]:
    """Yield a session and guarantee it is rolled back on error and always closed."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
