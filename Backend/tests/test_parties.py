def test_create_party(client, auth_headers):
    r = client.post(
        "/parties/",
        json={"id": "CUST900", "name": "Acme Co", "mobile": "9998887776"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["id"] == "CUST900"
    assert r.json()["balance"] == 0.0


def test_duplicate_party_id_is_409_not_500(client, auth_headers, party):
    """Previously surfaced as an unhandled IntegrityError (500)."""
    r = client.post(
        "/parties/",
        json={"id": "CUST001", "name": "Someone Else", "mobile": "1112223334"},
        headers=auth_headers,
    )
    assert r.status_code == 409


def test_party_id_is_normalised(client, auth_headers):
    r = client.post(
        "/parties/",
        json={"id": "  cust777 ", "name": "X", "mobile": "1234567"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["id"] == "CUST777"


def test_party_id_rejects_unsafe_characters(client, auth_headers):
    r = client.post(
        "/parties/",
        json={"id": "cust/../etc", "name": "X", "mobile": "1234567"},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_invalid_email_rejected(client, auth_headers):
    r = client.post(
        "/parties/",
        json={"id": "C1", "name": "X", "mobile": "1234567", "email": "not-an-email"},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_update_cannot_rewrite_balance(client, auth_headers, party):
    """balance is derived from the ledger; a PUT must not be able to set it."""
    client.put("/parties/CUST001", json={"balance": 99999.0}, headers=auth_headers)
    assert client.get("/parties/CUST001", headers=auth_headers).json()["balance"] == 0.0


def test_update_cannot_rewrite_id(client, auth_headers, party):
    client.put("/parties/CUST001", json={"id": "HACKED"}, headers=auth_headers)
    assert client.get("/parties/CUST001", headers=auth_headers).status_code == 200
    assert client.get("/parties/HACKED", headers=auth_headers).status_code == 404


def test_search_and_filter(client, auth_headers, party):
    assert len(client.get("/parties/?q=jane", headers=auth_headers).json()) == 1
    assert len(client.get("/parties/?q=nobody", headers=auth_headers).json()) == 0
    assert len(client.get("/parties/?status=active", headers=auth_headers).json()) == 1
    assert len(client.get("/parties/?status=closed", headers=auth_headers).json()) == 0


def test_delete_blocked_while_holding_items(client, auth_headers, item, party):
    client.post(
        "/contracts/",
        json={"partyId": "CUST001", "items": [{"itemId": item["itemId"], "qty": 1}]},
        headers=auth_headers,
    )
    assert client.delete("/parties/CUST001", headers=auth_headers).status_code == 409


def test_default_status_is_a_manual_override(client, auth_headers, item, party):
    """A party flagged DEFAULT keeps that flag through a rental, instead of being
    silently recalculated back to active/payment_due."""
    client.put("/parties/CUST001", json={"status": "default"}, headers=auth_headers)
    client.post(
        "/contracts/",
        json={"partyId": "CUST001", "items": [{"itemId": item["itemId"], "qty": 1}]},
        headers=auth_headers,
    )
    assert client.get("/parties/CUST001", headers=auth_headers).json()["status"] == "default"
