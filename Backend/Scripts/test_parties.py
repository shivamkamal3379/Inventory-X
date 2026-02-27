import requests
from utils import BASE_URL, get_headers


def test_parties():
    print("Testing Parties CRUD...")
    headers = get_headers()

    # 1. Create Party
    print("1. Creating party...")
    party_data = {
        "id": "CUST999",
        "name": "Test Party",
        "mobile": "1234567890",
        "aadhaar": "987654321012",
    }
    resp = requests.post(f"{BASE_URL}/parties/", json=party_data, headers=headers)
    if resp.status_code == 200:
        party = resp.json()
        party_id = party["id"]
        print(f"   ✅ Party created. ID: {party_id}")
    else:
        print(f"   ❌ Party creation failed. {resp.text}")
        return

    # 2. Read All
    print("2. Reading all parties...")
    resp = requests.get(f"{BASE_URL}/parties/", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Fetched {len(resp.json())} parties.")
    else:
        print(f"   ❌ Read all failed. {resp.text}")

    # 3. Read Single
    print("3. Reading specific party...")
    resp = requests.get(f"{BASE_URL}/parties/{party_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Read individual party successfully.")
    else:
        print(f"   ❌ Read individual failed. {resp.text}")

    # 4. Update
    print("4. Updating party...")
    update_data = {
        "id": party_id,
        "name": "Updated Test Party",
        "mobile": "1234567891",
        "aadhaar": "987654321012",
    }
    resp = requests.put(
        f"{BASE_URL}/parties/{party_id}", json=update_data, headers=headers
    )
    if resp.status_code == 200:
        print("   ✅ Party updated successfully.")
    else:
        print(f"   ❌ Update failed. {resp.text}")

    # 5. Delete
    print("5. Deleting party...")
    resp = requests.delete(f"{BASE_URL}/parties/{party_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Party deleted successfully.")
    else:
        print(f"   ❌ Delete failed. {resp.text}")


if __name__ == "__main__":
    test_parties()
