import requests
from utils import BASE_URL, get_headers


def test_returns():
    print("Testing Returns API...")
    headers = get_headers()

    # Prerequisite: Create Party, Item, and Rent Out
    print("--- Prerequisite: Setting up rental transaction to return...")
    party_data = {"id": "RET_CUST", "name": "Return Customer", "mobile": "5554443332"}
    item_data = {"name": "Returnable Item", "qty": 10}

    party_resp = requests.post(f"{BASE_URL}/parties/", json=party_data, headers=headers)
    item_resp = requests.post(f"{BASE_URL}/items/", json=item_data, headers=headers)

    if party_resp.status_code == 200 and item_resp.status_code == 200:
        party_id = party_resp.json()["id"]
        item_id = item_resp.json()["itemId"]

        rent_data = {
            "partyId": party_id,
            "itemId": item_id,
            "itemQty": 2,
            "rentAmount": 200.0,
            "paidAmount": 200.0,
        }
        rent_resp = requests.post(f"{BASE_URL}/rent/", json=rent_data, headers=headers)
        if rent_resp.status_code != 200:
            print(f"   ❌ Failed to create rental transaction. {rent_resp.text}")
            return
    else:
        print("   ❌ Failed to create basic prerequisites for return test.")
        return

    # 1. Return Item
    print("1. Returning an item...")
    return_data = {
        "partyId": party_id,
        "itemId": item_id,
        "itemQty": 2,
        "refundAmount": 0.0,
    }
    resp = requests.post(f"{BASE_URL}/returns/", json=return_data, headers=headers)
    if resp.status_code == 200:
        ret_txn = resp.json()
        txn_id = ret_txn["id"]
        print(f"   ✅ Return created. Txn ID: {txn_id}")
    else:
        print(f"   ❌ Return failed. {resp.text}")
        return

    # 2. Read All Returns
    print("2. Reading all return transactions...")
    resp = requests.get(f"{BASE_URL}/returns/", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Fetched {len(resp.json())} return transactions.")
    else:
        print(f"   ❌ Read all returns failed. {resp.text}")

    # 3. Read specific return
    print("3. Reading specific return...")
    resp = requests.get(f"{BASE_URL}/returns/{txn_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Read individual return successfully.")
    else:
        print(f"   ❌ Read individual return failed. {resp.text}")

    # 4. Read by Party
    print("4. Reading returns by party...")
    resp = requests.get(f"{BASE_URL}/returns/party/{party_id}", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Read {len(resp.json())} returns for party.")
    else:
        print(f"   ❌ Read by party failed. {resp.text}")


if __name__ == "__main__":
    test_returns()
