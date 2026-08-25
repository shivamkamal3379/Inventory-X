from datetime import datetime, timedelta

START = datetime(2026, 1, 1, 9, 0, 0)


def _rent(client, headers, item_id, qty=1, advance=0.0):
    return client.post(
        "/contracts/",
        json={
            "partyId": "CUST001",
            "items": [{"itemId": item_id, "qty": qty}],
            "advancePaid": advance,
            "startDate": START.isoformat(),
        },
        headers=headers,
    ).json()


def test_stats_on_empty_database(client, auth_headers):
    r = client.get("/dashboard/stats", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["totalItems"] == 0
    assert r.json()["outstandingBalance"] == 0.0
    assert r.json()["utilisationPct"] == 0.0


def test_stats_reflect_activity(client, auth_headers, item, party):
    _rent(client, auth_headers, item["itemId"], qty=3)
    s = client.get("/dashboard/stats", headers=auth_headers).json()
    assert s["totalItems"] == 1
    assert s["totalParties"] == 1
    assert s["totalRentedOutQty"] == 3
    assert s["totalAvailableQty"] == 7
    assert s["openContracts"] == 1
    assert s["utilisationPct"] == 30.0


def test_overdue_contracts_counted(client, auth_headers, item, party):
    client.post(
        "/contracts/",
        json={
            "partyId": "CUST001",
            "items": [{"itemId": item["itemId"], "qty": 1}],
            "startDate": START.isoformat(),
            "expectedReturnDate": (START + timedelta(days=1)).isoformat(),
        },
        headers=auth_headers,
    )
    # START is in the past relative to now, so this contract is overdue.
    assert client.get("/dashboard/stats", headers=auth_headers).json()["overdueContracts"] == 1


def test_activity_endpoint_exists(client, auth_headers):
    """The dashboard has always called /dashboard/activity; it did not exist,
    so 'Recent Activity' silently rendered empty."""
    r = client.get("/dashboard/activity", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_activity_merges_rentals_returns_and_payments(client, auth_headers, item, party):
    c = _rent(client, auth_headers, item["itemId"], qty=2)
    client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 1}],
            "returnDate": (START + timedelta(days=1)).isoformat(),
        },
        headers=auth_headers,
    )
    client.post(
        f"/contracts/{c['contractId']}/payment", json={"amount": 100.0}, headers=auth_headers
    )

    feed = client.get("/dashboard/activity", headers=auth_headers).json()
    assert {row["type"] for row in feed} == {"RENTAL", "RETURN", "PAYMENT"}


def test_activity_respects_limit(client, auth_headers, item, party):
    for _ in range(5):
        _rent(client, auth_headers, item["itemId"], qty=1)
    assert len(client.get("/dashboard/activity?limit=3", headers=auth_headers).json()) == 3


def test_trend_is_zero_filled(client, auth_headers):
    r = client.get("/dashboard/trend?days=14", headers=auth_headers)
    assert r.status_code == 200
    points = r.json()
    assert len(points) == 14
    assert all(p["revenue"] == 0.0 for p in points)
    # Dates must be contiguous so a chart has no gaps.
    dates = [p["date"] for p in points]
    assert dates == sorted(dates)


def test_top_items_ranks_by_units(client, auth_headers, item, item2, party):
    client.post(
        "/contracts/",
        json={
            "partyId": "CUST001",
            "items": [
                {"itemId": item["itemId"], "qty": 1},
                {"itemId": item2["itemId"], "qty": 4},
            ],
            "startDate": START.isoformat(),
        },
        headers=auth_headers,
    )
    top = client.get("/dashboard/top-items", headers=auth_headers).json()
    assert top[0]["itemId"] == item2["itemId"]
    assert top[0]["unitsRented"] == 4


def test_revenue_this_month_counts_returns(client, auth_headers, item, party):
    """Revenue is recognised when rent is charged, i.e. on return."""
    c = client.post(
        "/contracts/",
        json={"partyId": "CUST001", "items": [{"itemId": item["itemId"], "qty": 1}]},
        headers=auth_headers,
    ).json()
    assert client.get("/dashboard/stats", headers=auth_headers).json()["revenueThisMonth"] == 0.0

    client.post(
        f"/contracts/{c['contractId']}/return",
        json={"items": [{"lineId": c["lines"][0]["id"], "qty": 1}]},
        headers=auth_headers,
    )
    assert client.get("/dashboard/stats", headers=auth_headers).json()["revenueThisMonth"] == 500.0
