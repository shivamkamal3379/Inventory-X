import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"


def log(msg, status="INFO"):
    print(f"[{status}] {msg}")


def check_health():
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            log("Health check passed: " + str(r.json()), "PASS")
            return True
        else:
            log(f"Health check failed with {r.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"Health check exception: {e}", "FAIL")
        return False


def test_agents():
    log("Testing Agents API...")
    # Create Agent
    data = {"AgentName": "Test Agent", "mobile": "1234567890"}
    r = requests.post(f"{BASE_URL}/agents/", json=data)
    if r.status_code == 200:
        agent_id = r.json().get("agentId")
        log(f"Created Agent ID: {agent_id}", "PASS")
    else:
        log(f"Failed to create agent: {r.text}", "FAIL")
        return None

    # List Agents
    r = requests.get(f"{BASE_URL}/agents/")
    if r.status_code == 200 and len(r.json()) > 0:
        log(f"Listed {len(r.json())} agents", "PASS")
    else:
        log("Failed to list agents", "FAIL")

    return agent_id


def test_items():
    log("Testing Items API...")
    # Create Item
    data = {
        "name": "Drill Machine",
        "description": "Powerful drill",
        "qty": 10,  # Initial master qty
        "rent": 50.0,
        "rentFrequency": "daily",
    }
    r = requests.post(f"{BASE_URL}/items/", json=data)
    if r.status_code == 200:
        item = r.json()
        item_id = item.get("itemId")
        log(f"Created Item ID: {item_id}", "PASS")
    else:
        log(f"Failed to create item: {r.text}", "FAIL")
        return None

    # Check Stock
    r = requests.get(f"{BASE_URL}/items/{item_id}/stock")
    if r.status_code == 200:
        stock = r.json()
        log(f"Initial Stock: {stock}", "PASS")
    else:
        log(f"Failed to get stock: {r.status_code}", "FAIL")

    return item_id


def test_rentals(item_id, agent_id):
    log("Testing Rentals API (No Stock Logic Yet)...")
    # Create Party
    party_data = {"name": "Test Customer", "mobile": "9876543210"}
    r = requests.post(f"{BASE_URL}/parties/", json=party_data)
    party_id = r.json().get("id") if r.status_code == 200 else None

    if not party_id:
        log("Could not create party, skipping rental test", "FAIL")
        return

    # Create Rental
    rental_data = {
        "itemId": item_id,
        "partyId": party_id,
        "agentId": agent_id,
        "qty": 2,
        "bookedBy": "Staff",
    }
    r = requests.post(f"{BASE_URL}/rent/", json=rental_data)
    if r.status_code == 200:
        log("Rental Created Successfully", "PASS")
    else:
        log(f"Rental Creation Failed: {r.text}", "FAIL")

    # Check Stock Again (Expect NO Change yet)
    r = requests.get(f"{BASE_URL}/items/{item_id}/stock")
    if r.status_code == 200:
        stock = r.json()
        log(f"Post-Rent Stock: {stock}", "INFO")
        if (
            stock.get("availableQty") == 10
        ):  # Assuming initial 10 and no deduction logic
            log("Stock logic NOT implemented (Expected behavior for now)", "INFO")
        else:
            log("Stock CHANGED! (Logic might be implemented?)", "WARN")


def main():
    if not check_health():
        return

    agent_id = test_agents()
    item_id = test_items()

    if agent_id and item_id:
        test_rentals(item_id, agent_id)


if __name__ == "__main__":
    main()
