import requests
import sys

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0


def check(label, r, expected=200):
    global PASS, FAIL
    ok = r.status_code == expected
    status = "PASS" if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    try:
        body = r.json()
    except:
        body = r.text[:200]
    print(f"[{status}] {label}: {r.status_code} -> {body}")
    return body if ok else None


# 1. Health
check("Health", requests.get(f"{BASE}/"))

# 2. Dashboard (empty)
check("Dashboard (empty)", requests.get(f"{BASE}/dashboard/stats"))

# 3. Register
check(
    "Register",
    requests.post(
        f"{BASE}/auth/register", json={"username": "admin", "password": "admin123"}
    ),
)

# 4. Login
login = check(
    "Login",
    requests.post(
        f"{BASE}/auth/login", data={"username": "admin", "password": "admin123"}
    ),
)
token = login["access_token"] if login else None
headers = {"Authorization": f"Bearer {token}"} if token else {}

# 5. Create Agent
check(
    "Create Agent",
    requests.post(
        f"{BASE}/agents/", json={"AgentName": "Agent Smith", "mobile": "9999999999"}
    ),
)

# 6. Create Item
check(
    "Create Item",
    requests.post(
        f"{BASE}/items/", json={"name": "Drill", "description": "Power tool", "qty": 10}
    ),
)

# 7. Check Stock
stock = check("Initial Stock", requests.get(f"{BASE}/items/1/stock"))

# 8. Create Party
check(
    "Create Party",
    requests.post(
        f"{BASE}/parties/",
        json={"id": "P001", "name": "John Doe", "mobile": "1234567890"},
    ),
)

# 9. Create Rental Price
check(
    "Create Price",
    requests.post(
        f"{BASE}/prices/",
        json={"itemId": 1, "itemName": "Drill", "rent": 50.0, "rentFrequency": "daily"},
    ),
)

# 10. Rent Out
check(
    "Rent Out",
    requests.post(
        f"{BASE}/rent/",
        json={
            "partyId": "P001",
            "itemId": 1,
            "itemQty": 3,
            "rentAmount": 150.0,
            "paidAmount": 50.0,
            "Item": "Drill",
            "agentId": 1,
            "AgentName": "Agent Smith",
            "PartyName": "John Doe",
        },
    ),
)

# 11. Stock after rent
stock2 = check("Stock After Rent", requests.get(f"{BASE}/items/1/stock"))
if stock2:
    assert stock2["availableQty"] == 7, (
        f"Expected 7 available, got {stock2['availableQty']}"
    )
    assert stock2["RentedOutQty"] == 3, (
        f"Expected 3 rented, got {stock2['RentedOutQty']}"
    )
    print("  -> Stock deduction VERIFIED")

# 12. Party after rent
party = check("Party After Rent", requests.get(f"{BASE}/parties/P001"))
if party:
    print(
        f"  -> balance={party['balance']}, activeItems={party['activeItems']}, status={party['status']}"
    )

# 13. Return
check(
    "Return",
    requests.post(
        f"{BASE}/returns/",
        json={
            "partyId": "P001",
            "itemId": 1,
            "itemQty": 2,
            "refundAmount": 50.0,
            "Item": "Drill",
        },
    ),
)

# 14. Stock after return
stock3 = check("Stock After Return", requests.get(f"{BASE}/items/1/stock"))
if stock3:
    assert stock3["availableQty"] == 9, f"Expected 9, got {stock3['availableQty']}"
    assert stock3["RentedOutQty"] == 1, f"Expected 1, got {stock3['RentedOutQty']}"
    print("  -> Stock restock VERIFIED")

# 15. Party after return
party2 = check("Party After Return", requests.get(f"{BASE}/parties/P001"))
if party2:
    print(
        f"  -> balance={party2['balance']}, activeItems={party2['activeItems']}, status={party2['status']}"
    )

# 16. Get rentals by party
check("Rentals by Party", requests.get(f"{BASE}/rent/party/P001"))

# 17. Get returns by party
check("Returns by Party", requests.get(f"{BASE}/returns/party/P001"))

# 18. Dashboard (with data)
check("Dashboard (final)", requests.get(f"{BASE}/dashboard/stats"))

# 19. List prices
check("List Prices", requests.get(f"{BASE}/prices/"))

print(f"\n{'=' * 40}")
print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
if FAIL > 0:
    sys.exit(1)
