"""Test fixtures.

DATABASE_URL is set before any `src` import because the engine and the settings
singleton are both built at module import time — setting it later would build the
engine against the developer's real database.
"""

import os
import tempfile
from pathlib import Path

import pytest

_TMP_DB = Path(tempfile.gettempdir()) / "inventoryx_test.db"

# Defaults to SQLite so `pytest` works with no setup. Point TEST_DATABASE_URL at
# a PostgreSQL instance to run the same suite against the production engine —
# CI does exactly that, because SQLite silently tolerates things Postgres rejects.
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{_TMP_DB}")
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-not-used-outside-the-test-suite"
os.environ["ALLOW_REGISTRATION"] = "true"
os.environ["LOG_JSON"] = "false"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["LOGIN_RATE_LIMIT_ATTEMPTS"] = "1000"

from fastapi.testclient import TestClient  # noqa: E402

from src.core.database import Base, engine  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_schema():
    """Drop and recreate every table between tests.

    Each test therefore starts from an empty database and cannot depend on
    ordering or on rows another test happened to leave behind.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Register + log in, returning a usable Authorization header."""
    client.post("/auth/register", json={"username": "tester", "password": "testpassword123"})
    resp = client.post("/auth/login", data={"username": "tester", "password": "testpassword123"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def item(client, auth_headers):
    resp = client.post(
        "/items/",
        json={
            "name": "Heavy Duty Drill",
            "description": "Cordless power drill",
            "qty": 10,
            "rent": 500.0,
            "rentFrequency": "daily",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def item2(client, auth_headers):
    """A second item on a different rate, so tests can tell the two apart in a bill."""
    resp = client.post(
        "/items/",
        json={
            "name": "Scaffold Tower",
            "description": "5m aluminium",
            "qty": 5,
            "rent": 200.0,
            "rentFrequency": "daily",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def agent(client, auth_headers):
    resp = client.post(
        "/agents/",
        json={"AgentName": "John Doe", "mobile": "9876543210"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def party(client, auth_headers):
    resp = client.post(
        "/parties/",
        json={"id": "CUST001", "name": "Jane Smith", "mobile": "9123456780"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
