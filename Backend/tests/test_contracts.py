"""Contract lifecycle: rent out, return, bill, pay."""

from datetime import datetime, timedelta

START = datetime(2026, 1, 1, 9, 0, 0)


def _create(client, headers, *, items, party="CUST001", advance=0.0, start=START, expected=None):
    payload = {
        "partyId": party,
        "items": items,
        "advancePaid": advance,
        "startDate": start.isoformat(),
    }
    if expected:
        payload["expectedReturnDate"] = expected.isoformat()
    return client.post("/contracts/", json=payload, headers=headers)


def test_one_contract_holds_many_items(client, auth_headers, item, item2, party):
    """The whole point of the restructure: three items = one invoice, not three
    unrelated ledger rows."""
    r = _create(
        client,
        auth_headers,
        items=[
            {"itemId": item["itemId"], "qty": 2},
            {"itemId": item2["itemId"], "qty": 1},
        ],
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert len(body["lines"]) == 2
    assert body["contractNo"].startswith("INV-")
    assert body["status"] == "open"


def test_contract_number_is_sequential_and_unique(client, auth_headers, item, party):
    a = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    b = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    assert a["contractNo"] != b["contractNo"]
    assert a["contractNo"] == "INV-000001"
    assert b["contractNo"] == "INV-000002"


def test_rate_is_captured_from_price_list_not_the_request(client, auth_headers, item, party):
    r = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}])
    assert r.json()["lines"][0]["ratePerUnit"] == 500.0


def test_no_rent_charged_at_pickup(client, auth_headers, item, party):
    """Rent accrues on return, when the duration is finally known."""
    r = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}])
    assert r.json()["accruedRent"] == 0.0
    assert client.get("/parties/CUST001", headers=auth_headers).json()["balance"] == 0.0


def test_advance_is_a_credit_on_the_party(client, auth_headers, item, party):
    _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}], advance=1000.0)
    p = client.get("/parties/CUST001", headers=auth_headers).json()
    assert p["balance"] == -1000.0  # we hold their money


def test_stock_is_reserved_across_all_lines(client, auth_headers, item, item2, party):
    _create(
        client,
        auth_headers,
        items=[
            {"itemId": item["itemId"], "qty": 3},
            {"itemId": item2["itemId"], "qty": 2},
        ],
    )
    s1 = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
    s2 = client.get(f"/items/{item2['itemId']}/stock", headers=auth_headers).json()
    assert s1["availableQty"] == 7 and s1["RentedOutQty"] == 3
    assert s2["availableQty"] == 3 and s2["RentedOutQty"] == 2


def test_insufficient_stock_on_any_line_rejects_whole_contract(
    client, auth_headers, item, item2, party
):
    """Partial success would leave the first item reserved against a contract
    that was never created."""
    r = _create(
        client,
        auth_headers,
        items=[
            {"itemId": item["itemId"], "qty": 2},
            {"itemId": item2["itemId"], "qty": 999},
        ],
    )
    assert r.status_code == 409
    s1 = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
    assert s1["availableQty"] == 10  # untouched
    assert client.get("/contracts/", headers=auth_headers).json() == []


def test_duplicate_item_lines_rejected(client, auth_headers, item, party):
    r = _create(
        client,
        auth_headers,
        items=[
            {"itemId": item["itemId"], "qty": 1},
            {"itemId": item["itemId"], "qty": 2},
        ],
    )
    assert r.status_code == 422


def test_empty_item_list_rejected(client, auth_headers, party):
    r = _create(client, auth_headers, items=[])
    assert r.status_code == 422


def test_expected_return_before_start_rejected(client, auth_headers, item, party):
    r = _create(
        client,
        auth_headers,
        items=[{"itemId": item["itemId"], "qty": 1}],
        expected=START - timedelta(days=2),
    )
    assert r.status_code == 422


# --------------------------------------------------------------------------- #
# Returns and billing
# --------------------------------------------------------------------------- #


def test_return_charges_for_days_held(client, auth_headers, item, party):
    """5 days x 2 units x Rs500/day = Rs5000."""
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}]).json()
    line = c["lines"][0]

    r = client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": line["id"], "qty": 2}],
            "returnDate": (START + timedelta(days=5)).isoformat(),
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["totalCharged"] == 5000.0
    assert r.json()["returns"][0]["daysHeld"] == 5
    assert r.json()["contract"]["status"] == "closed"

    assert client.get("/parties/CUST001", headers=auth_headers).json()["balance"] == 5000.0


def test_longer_rental_costs_more(client, auth_headers, item, item2, party):
    short = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    long = _create(client, auth_headers, items=[{"itemId": item2["itemId"], "qty": 1}]).json()

    s = client.post(
        f"/contracts/{short['contractId']}/return",
        json={
            "items": [{"lineId": short["lines"][0]["id"], "qty": 1}],
            "returnDate": (START + timedelta(days=2)).isoformat(),
        },
        headers=auth_headers,
    ).json()
    long_result = client.post(
        f"/contracts/{long['contractId']}/return",
        json={
            "items": [{"lineId": long["lines"][0]["id"], "qty": 1}],
            "returnDate": (START + timedelta(days=20)).isoformat(),
        },
        headers=auth_headers,
    ).json()

    assert long_result["totalCharged"] > s["totalCharged"]
    assert s["totalCharged"] == 1000.0  # 2 days x Rs500
    assert long_result["totalCharged"] == 4000.0  # 20 days x Rs200


def test_partial_return_leaves_contract_partial(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 5}]).json()
    line = c["lines"][0]

    r = client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": line["id"], "qty": 2}],
            "returnDate": (START + timedelta(days=1)).isoformat(),
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    contract = r.json()["contract"]
    assert contract["status"] == "partial"
    assert contract["lines"][0]["returnedQty"] == 2
    assert contract["lines"][0]["outstandingQty"] == 3

    stock = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
    assert stock["availableQty"] == 7 and stock["RentedOutQty"] == 3


def test_cannot_return_more_than_outstanding(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}]).json()
    r = client.post(
        f"/contracts/{c['contractId']}/return",
        json={"items": [{"lineId": c["lines"][0]["id"], "qty": 500}]},
        headers=auth_headers,
    )
    assert r.status_code == 409
    stock = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
    assert stock["availableQty"] + stock["RentedOutQty"] == stock["qty"] == 10


def test_cannot_return_a_line_from_another_contract(client, auth_headers, item, item2, party):
    a = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    b = _create(client, auth_headers, items=[{"itemId": item2["itemId"], "qty": 1}]).json()
    r = client.post(
        f"/contracts/{a['contractId']}/return",
        json={"items": [{"lineId": b["lines"][0]["id"], "qty": 1}]},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_return_before_start_date_rejected(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    r = client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 1}],
            "returnDate": (START - timedelta(days=3)).isoformat(),
        },
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_payment_at_return_reduces_balance(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 1}],
            "returnDate": (START + timedelta(days=4)).isoformat(),
            "amountPaid": 1500.0,
        },
        headers=auth_headers,
    )
    # 4 days x Rs500 = Rs2000 charged, Rs1500 paid
    assert client.get("/parties/CUST001", headers=auth_headers).json()["balance"] == 500.0


def test_advance_offsets_the_final_bill(client, auth_headers, item, party):
    c = _create(
        client,
        auth_headers,
        items=[{"itemId": item["itemId"], "qty": 1}],
        advance=2000.0,
    ).json()
    client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 1}],
            "returnDate": (START + timedelta(days=3)).isoformat(),
        },
        headers=auth_headers,
    )
    # Rs1500 rent against a Rs2000 advance leaves Rs500 credit.
    p = client.get("/parties/CUST001", headers=auth_headers).json()
    assert p["balance"] == -500.0
    assert p["status"] == "closed"


# --------------------------------------------------------------------------- #
# Quote
# --------------------------------------------------------------------------- #


def test_quote_prices_without_committing(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}]).json()
    as_of = (START + timedelta(days=3)).isoformat()

    q = client.get(f"/contracts/{c['contractId']}/quote?asOf={as_of}", headers=auth_headers)
    assert q.status_code == 200
    assert q.json()["subtotal"] == 3000.0  # 3 days x 2 x Rs500

    # Nothing changed.
    after = client.get(f"/contracts/{c['contractId']}", headers=auth_headers).json()
    assert after["accruedRent"] == 0.0
    assert after["status"] == "open"
    stock = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
    assert stock["RentedOutQty"] == 2


def test_quote_matches_what_the_return_actually_charges(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}]).json()
    as_of = START + timedelta(days=6)

    quoted = client.get(
        f"/contracts/{c['contractId']}/quote?asOf={as_of.isoformat()}", headers=auth_headers
    ).json()["subtotal"]
    charged = client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 2}],
            "returnDate": as_of.isoformat(),
        },
        headers=auth_headers,
    ).json()["totalCharged"]

    assert quoted == charged


# --------------------------------------------------------------------------- #
# Payments
# --------------------------------------------------------------------------- #


def test_standalone_payment_reduces_balance(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 1}],
            "returnDate": (START + timedelta(days=2)).isoformat(),
        },
        headers=auth_headers,
    )
    assert client.get("/parties/CUST001", headers=auth_headers).json()["balance"] == 1000.0

    r = client.post(
        f"/contracts/{c['contractId']}/payment",
        json={"amount": 600.0, "method": "cash"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert client.get("/parties/CUST001", headers=auth_headers).json()["balance"] == 400.0
    assert len(client.get("/payments/", headers=auth_headers).json()) == 1


def test_negative_payment_rejected(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}]).json()
    r = client.post(
        f"/contracts/{c['contractId']}/payment", json={"amount": -50}, headers=auth_headers
    )
    assert r.status_code == 422


# --------------------------------------------------------------------------- #
# Invariants and listings
# --------------------------------------------------------------------------- #


def test_stock_conserved_through_full_lifecycle(client, auth_headers, item, party):
    c = _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 6}]).json()
    line_id = c["lines"][0]["id"]

    for qty in (1, 2, 3):
        client.post(
            f"/contracts/{c['contractId']}/return",
            json={
                "items": [{"lineId": line_id, "qty": qty}],
                "returnDate": (START + timedelta(days=1)).isoformat(),
            },
            headers=auth_headers,
        )
        s = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
        assert s["availableQty"] + s["RentedOutQty"] == s["qty"] == 10

    final = client.get(f"/contracts/{c['contractId']}", headers=auth_headers).json()
    assert final["status"] == "closed"
    assert client.get("/parties/CUST001", headers=auth_headers).json()["activeItems"] == 0


def test_list_and_filter_contracts(client, auth_headers, item, party):
    _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}])
    assert len(client.get("/contracts/", headers=auth_headers).json()) == 1
    assert len(client.get("/contracts/?status=open", headers=auth_headers).json()) == 1
    assert len(client.get("/contracts/?status=closed", headers=auth_headers).json()) == 0
    assert len(client.get("/contracts/?q=INV-", headers=auth_headers).json()) == 1
    assert len(client.get("/contracts/?partyId=NOBODY", headers=auth_headers).json()) == 0


def test_contract_summary_carries_counts(client, auth_headers, item, item2, party):
    _create(
        client,
        auth_headers,
        items=[
            {"itemId": item["itemId"], "qty": 2},
            {"itemId": item2["itemId"], "qty": 3},
        ],
    )
    row = client.get("/contracts/", headers=auth_headers).json()[0]
    assert row["itemCount"] == 2
    assert row["outstandingQty"] == 5


def test_party_with_open_contract_cannot_be_deleted(client, auth_headers, item, party):
    _create(client, auth_headers, items=[{"itemId": item["itemId"], "qty": 1}])
    assert client.delete("/parties/CUST001", headers=auth_headers).status_code == 409


def test_party_ledger_reflects_contracts(client, auth_headers, item, party):
    c = _create(
        client, auth_headers, items=[{"itemId": item["itemId"], "qty": 2}], advance=500.0
    ).json()
    client.post(
        f"/contracts/{c['contractId']}/return",
        json={
            "items": [{"lineId": c["lines"][0]["id"], "qty": 2}],
            "returnDate": (START + timedelta(days=2)).isoformat(),
        },
        headers=auth_headers,
    )
    led = client.get("/parties/CUST001/ledger", headers=auth_headers).json()
    assert len(led["contracts"]) == 1
    assert led["totals"]["rentCharged"] == 2000.0
    assert led["totals"]["advances"] == 500.0
    assert led["totals"]["balance"] == 1500.0
