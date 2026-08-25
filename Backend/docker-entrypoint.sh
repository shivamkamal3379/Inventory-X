#!/usr/bin/env bash
# Container entrypoint: wait for the database, migrate, then serve.
set -euo pipefail

log() { echo "[entrypoint] $*"; }

wait_for_db() {
    # The API starts faster than PostgreSQL does. Without this the first boot
    # crash-loops until Docker's restart policy happens to catch a ready DB.
    local attempts="${DB_WAIT_ATTEMPTS:-60}"
    log "Waiting for the database (up to ${attempts}s)..."
    for i in $(seq 1 "$attempts"); do
        if python -c "
import sys
from sqlalchemy import create_engine, text
from src.core.config import settings
try:
    create_engine(settings.DATABASE_URL, pool_pre_ping=True).connect().execute(text('SELECT 1'))
except Exception:
    sys.exit(1)
" 2>/dev/null; then
            log "Database is ready (after ${i}s)."
            return 0
        fi
        sleep 1
    done
    log "ERROR: database did not become ready in time."
    return 1
}

run_migrations() {
    log "Applying migrations..."
    alembic upgrade head
    log "Migrations applied."
}

case "${1:-serve}" in
    serve)
        wait_for_db
        run_migrations
        WORKERS="${WEB_CONCURRENCY:-2}"
        log "Starting gunicorn with ${WORKERS} uvicorn worker(s)..."
        # gunicorn supervises and recycles workers; uvicorn provides the ASGI
        # loop. max-requests recycles workers periodically to bound any leak.
        exec gunicorn src.main:app \
            --worker-class uvicorn.workers.UvicornWorker \
            --workers "${WORKERS}" \
            --bind 0.0.0.0:8000 \
            --timeout "${WEB_TIMEOUT:-60}" \
            --graceful-timeout 30 \
            --keep-alive 5 \
            --max-requests 2000 \
            --max-requests-jitter 200 \
            --access-logfile - \
            --error-logfile -
        ;;
    migrate)
        wait_for_db
        run_migrations
        ;;
    shell)
        exec /bin/bash
        ;;
    *)
        exec "$@"
        ;;
esac
