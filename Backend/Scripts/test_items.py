import requests
from utils import BASE_URL, get_headers


def test_items():
    print("Testing Items CRUD & Stock...")
    headers = get_headers()

    # 1. Create Item
    print("1. Creating item...")
    item_data = {
        "name": "Test Item",
        "qty": 50,
        "description": "A test item for scripts",
    }
    resp = requests.post(f"{BASE_URL}/items/", json=item_data, headers=headers)
    if resp.status_code == 200:
        item = resp.json()
        item_id = item["itemId"]
        print(f"   ✅ Item created. ID: {item_id}")
    else:
        print(f"   ❌ Item creation failed. {resp.text}")
        return

    # 2. Read All Items
    print("2. Reading all items...")
    resp = requests.get(f"{BASE_URL}/items/", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Fetched {len(resp.json())} items.")
    else:
        print(f"   ❌ Read all items failed. {resp.text}")

    # 3. Read Single Item
    print("3. Reading specific item...")
    resp = requests.get(f"{BASE_URL}/items/{item_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Read individual item successfully.")
    else:
        print(f"   ❌ Read individual item failed. {resp.text}")

    # 4. Check Stock
    print("4. Checking item stock...")
    resp = requests.get(f"{BASE_URL}/items/{item_id}/stock", headers=headers)
    if resp.status_code == 200:
        stock = resp.json()
        print(
            f"   ✅ Stock details: Total {stock.get('qty')}, Available {stock.get('availableQty')}."
        )
    else:
        print(f"   ❌ Get stock failed. {resp.text}")

    # 5. Update Item
    print("5. Updating item...")
    update_data = {
        "name": "Updated Test Item",
        "qty": 60,
        "description": "Updated test item for scripts",
    }
    resp = requests.put(
        f"{BASE_URL}/items/{item_id}", json=update_data, headers=headers
    )
    if resp.status_code == 200:
        print("   ✅ Item updated successfully.")
    else:
        print(f"   ❌ Update item failed. {resp.text}")

    # 6. Delete Item
    print("6. Deleting item...")
    resp = requests.delete(f"{BASE_URL}/items/{item_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Item deleted successfully.")
    else:
        print(f"   ❌ Delete item failed. {resp.text}")


if __name__ == "__main__":
    test_items()
