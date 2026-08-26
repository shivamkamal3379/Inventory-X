"""Regression tests for the vulnerability that every business endpoint was
reachable without a token."""

import pytest

PROTECTED_GETS = [
    "/items/",
    "/parties/",
    "/agents/",
    "/prices/",
    "/contracts/",
    "/returns/",
    "/payments/",
    "/dashboard/stats",
    "/dashboard/activity",
    "/dashboard/trend",
]


@pytest.mark.parametrize("path", PROTECTED_GETS)
def test_requires_authentication(client, path):
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("path", PROTECTED_GETS)
def test_rejects_garbage_token(client, path):
    r = client.get(path, headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("post", "/items/", {"name": "X", "qty": 1}),
        ("post", "/parties/", {"id": "P1", "name": "X", "mobile": "1234567"}),
        ("post", "/agents/", {"AgentName": "X", "mobile": "1234567"}),
        ("post", "/contracts/", {"partyId": "P1", "items": [{"itemId": 1, "qty": 1}]}),
    ],
)
def test_writes_require_authentication(client, method, path, payload):
    assert getattr(client, method)(path, json=payload).status_code == 401


def test_token_signed_with_another_key_is_rejected(client):
    from datetime import UTC, datetime, timedelta

    from jose import jwt

    forged = jwt.encode(
        {"sub": "tester", "exp": datetime.now(UTC) + timedelta(hours=1), "type": "access"},
        "an-attacker-chosen-key",
        algorithm="HS256",
    )
    r = client.get("/items/", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


def test_expired_token_is_rejected(client, auth_headers):
    from datetime import timedelta

    from src.core.security import create_access_token

    expired = create_access_token(subject="tester", expires_delta=timedelta(seconds=-10))
    r = client.get("/items/", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_health_endpoints_stay_public(client):
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200


def test_security_headers_present(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["X-Request-ID"]
