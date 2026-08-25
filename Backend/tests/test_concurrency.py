"""Proves the oversell guard holds under genuine parallelism.

Skipped on SQLite: it serialises writers with a file lock, so the test would
pass there without demonstrating anything about the FOR UPDATE row lock. Run it
with TEST_DATABASE_URL pointed at PostgreSQL, as CI does.
"""

import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from src.main import app

pytestmark = pytest.mark.skipif(
    "postgres" not in os.environ.get("TEST_DATABASE_URL", ""),
    reason="Concurrency semantics are only meaningful on PostgreSQL",
)


def test_concurrent_rentals_cannot_oversell(client, auth_headers):
    """20 threads each try to rent 1 unit of an item that has 5.

    Without the row lock, several threads read availableQty=5 simultaneously,
    all pass the check, and stock goes negative. Exactly 5 must succeed.
    """
    item_id = client.post(
        "/items/", json={"name": "Scarce", "qty": 5, "rent": 100.0}, headers=auth_headers
    ).json()["itemId"]
    client.post(
        "/parties/",
        json={"id": "RACE01", "name": "Racer", "mobile": "9000000000"},
        headers=auth_headers,
    )

    def attempt(_):
        with TestClient(app) as c:
            return c.post(
                "/contracts/",
                json={"partyId": "RACE01", "items": [{"itemId": item_id, "qty": 1}]},
                headers=auth_headers,
            ).status_code

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(attempt, range(20)))

    created = results.count(201)
    conflicts = results.count(409)

    assert created == 5, f"expected exactly 5 rentals, got {created} (results={results})"
    assert created + conflicts == 20, f"unexpected statuses: {results}"

    stock = client.get(f"/items/{item_id}/stock", headers=auth_headers).json()
    assert stock["availableQty"] == 0
    assert stock["RentedOutQty"] == 5
    assert stock["availableQty"] + stock["RentedOutQty"] == stock["qty"]
