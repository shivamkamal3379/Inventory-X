def test_create_item_succeeds(client, auth_headers):
    """Regression: POST /items/ used to raise TypeError every single time,
    because the schema field was `manufactureYr` and the column `ManufactureYr`."""
    r = client.post(
        "/items/",
        json={"name": "Drill", "description": "cordless", "qty": 10},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["name"] == "Drill"
    assert r.json()["itemId"] > 0


def test_create_item_with_manufacture_year(client, auth_headers):
    r = client.post(
        "/items/",
        json={"name": "Mixer", "qty": 3, "manufactureYr": "2023-05-01T00:00:00"},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["manufactureYr"].startswith("2023-05-01")


def test_creating_item_initialises_stock(client, auth_headers, item):
    r = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {
        "itemId": item["itemId"],
        "qty": 10,
        "RentedOutQty": 0,
        "availableQty": 10,
    }


def test_item_create_sets_rental_price(client, auth_headers, item):
    r = client.get(f"/prices/{item['itemId']}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["rent"] == 500.0


def test_list_items_includes_stock_and_price(client, auth_headers, item):
    r = client.get("/items/", headers=auth_headers)
    assert r.status_code == 200
    row = r.json()[0]
    assert row["availableQty"] == 10
    assert row["rentedOutQty"] == 0
    assert row["rent"] == 500.0


def test_negative_qty_rejected(client, auth_headers):
    r = client.post("/items/", json={"name": "Bad", "qty": -5}, headers=auth_headers)
    assert r.status_code == 422


def test_blank_name_rejected(client, auth_headers):
    r = client.post("/items/", json={"name": "", "qty": 1}, headers=auth_headers)
    assert r.status_code == 422


def test_update_item_syncs_stock(client, auth_headers, item):
    r = client.put(f"/items/{item['itemId']}", json={"qty": 25}, headers=auth_headers)
    assert r.status_code == 200
    stock = client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).json()
    assert stock == {
        "itemId": item["itemId"],
        "qty": 25,
        "RentedOutQty": 0,
        "availableQty": 25,
    }


def test_update_does_not_clobber_created_at(client, auth_headers, item):
    """The old ItemUpdate carried `created_at` with a default_factory, so every
    PUT silently reset the item's creation timestamp."""
    original = item["created_at"]
    client.put(f"/items/{item['itemId']}", json={"name": "Renamed"}, headers=auth_headers)
    after = client.get(f"/items/{item['itemId']}", headers=auth_headers).json()
    assert after["created_at"] == original
    assert after["name"] == "Renamed"


def test_partial_update_preserves_other_fields(client, auth_headers, item):
    client.put(f"/items/{item['itemId']}", json={"name": "Only Name"}, headers=auth_headers)
    after = client.get(f"/items/{item['itemId']}", headers=auth_headers).json()
    assert after["description"] == "Cordless power drill"
    assert after["qty"] == 10


def test_search_items(client, auth_headers, item):
    assert len(client.get("/items/?q=drill", headers=auth_headers).json()) == 1
    assert len(client.get("/items/?q=zzzz", headers=auth_headers).json()) == 0


def test_search_tolerates_null_description(client, auth_headers):
    client.post("/items/", json={"name": "NoDesc", "qty": 1}, headers=auth_headers)
    r = client.get("/items/?q=nodesc", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_delete_item_cascades_stock_and_price(client, auth_headers, item):
    assert client.delete(f"/items/{item['itemId']}", headers=auth_headers).status_code == 204
    assert client.get(f"/items/{item['itemId']}", headers=auth_headers).status_code == 404
    assert client.get(f"/items/{item['itemId']}/stock", headers=auth_headers).status_code == 404
    assert client.get(f"/prices/{item['itemId']}", headers=auth_headers).status_code == 404


def test_page_size_is_capped(client, auth_headers):
    for i in range(5):
        client.post("/items/", json={"name": f"i{i}", "qty": 1}, headers=auth_headers)
    r = client.get("/items/?limit=100000", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) <= 200
