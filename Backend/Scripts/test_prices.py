import requests
from utils import BASE_URL, get_headers


def test_prices():
    print("Testing Prices CRUD...")
    headers = get_headers()

    # Prerequisite: Create an item for the price
    print("--- Prerequisite: Creating item for pricing...")
    item_data = {"name": "Pricing Item", "qty": 10}
    item_resp = requests.post(f"{BASE_URL}/items/", json=item_data, headers=headers)
    if item_resp.status_code != 200:
        print("   ❌ Failed to create prerequisite item.")
        return
    item_id = item_resp.json()["itemId"]

    # 1. Create Price
    print("1. Creating price...")
    price_data = {"itemId": item_id, "rent": 150.0, "rentFrequency": "Monthly"}
    resp = requests.post(f"{BASE_URL}/prices/", json=price_data, headers=headers)
    if resp.status_code == 200:
        print("   ✅ Price created successfully.")
    else:
        print(f"   ❌ Price creation failed. {resp.text}")
        return

    # 2. Read All Prices
    print("2. Reading all prices for item...")
    resp = requests.get(f"{BASE_URL}/prices/item/{item_id}", headers=headers)
    if resp.status_code == 200:
        prices = resp.json()
        print(f"   ✅ Fetched {len(prices)} prices for item {item_id}.")
        # Need to read price via main endpoint? The API uses /prices/item/{item_id}
    else:
        print(f"   ❌ Read prices by item failed. {resp.text}")

    # 3. Reading all prices
    print("3. Reading all prices...")
    resp = requests.get(f"{BASE_URL}/prices/", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Fetched {len(resp.json())} total prices.")
    else:
        print(f"   ❌ Read all prices failed. {resp.text}")

    # Prerequisite Cleanup: Delete the item
    print("--- Cleanup: Deleting prerequisite item...")
    del_resp = requests.delete(f"{BASE_URL}/items/{item_id}", headers=headers)
    if del_resp.status_code == 200:
        print("   ✅ Cleanup successful.")
    else:
        print("   ⚠️ Cleanup failed.")


if __name__ == "__main__":
    test_prices()
