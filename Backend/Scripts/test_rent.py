import requests
from utils import BASE_URL, get_headers


def test_rent():
    print("Testing Rent API...")
    headers = get_headers()

    # Prerequisite: Create Party and Item
    print("--- Prerequisite: Creating Party and Item for rental...")
    party_data = {"id": "RENT_CUST", "name": "Rental Customer", "mobile": "9998887776"}
    item_data = {"name": "Rental Item", "qty": 20}

    party_resp = requests.post(f"{BASE_URL}/parties/", json=party_data, headers=headers)
    item_resp = requests.post(f"{BASE_URL}/items/", json=item_data, headers=headers)

    if party_resp.status_code != 200 or item_resp.status_code != 200:
        print("   ❌ Failed to create prerequisites.")
        return

    party_id = party_resp.json()["id"]
    item_id = item_resp.json()["itemId"]

    # 1. Rent Out
    print("1. Renting out an item...")
    rent_data = {
        "partyId": party_id,
        "itemId": item_id,
        "itemQty": 5,
        "rentAmount": 500.0,
        "paidAmount": 100.0,
    }
    resp = requests.post(f"{BASE_URL}/rent/", json=rent_data, headers=headers)
    if resp.status_code == 200:
        rent_txn = resp.json()
        txn_id = rent_txn["id"]
        print(f"   ✅ Rent Out created. Txn ID: {txn_id}")
    else:
        print(f"   ❌ Rent Out failed. {resp.text}")
        return

    # 2. Read All Rent Outs
    print("2. Reading all rental transactions...")
    resp = requests.get(f"{BASE_URL}/rent/", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Fetched {len(resp.json())} rental transactions.")
    else:
        print(f"   ❌ Read all rentals failed. {resp.text}")

    # 3. Read specific rental
    print("3. Reading specific rental...")
    resp = requests.get(f"{BASE_URL}/rent/{txn_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Read individual rental successfully.")
    else:
        print(f"   ❌ Read individual rental failed. {resp.text}")

    # 4. Read by Party
    print("4. Reading rentals by party...")
    resp = requests.get(f"{BASE_URL}/rent/party/{party_id}", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Read {len(resp.json())} rentals for party.")
    else:
        print(f"   ❌ Read by party failed. {resp.text}")


if __name__ == "__main__":
    test_rent()
