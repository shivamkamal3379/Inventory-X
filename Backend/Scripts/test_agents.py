import requests
from utils import BASE_URL, get_headers


def test_agents():
    print("Testing Agents CRUD...")
    headers = get_headers()

    # 1. Create
    print("1. Creating agent...")
    agent_data = {
        "AgentName": "Test Agent",
        "mobile": "9876543210",
        "aadhar": "123456789012",
        "email": "agent@test.com",
    }
    resp = requests.post(f"{BASE_URL}/agents/", json=agent_data, headers=headers)
    if resp.status_code == 200:
        agent = resp.json()
        agent_id = agent["agentId"]
        print(f"   ✅ Agent created. ID: {agent_id}")
    else:
        print(f"   ❌ Agent creation failed. {resp.text}")
        return

    # 2. Read All
    print("2. Reading all agents...")
    resp = requests.get(f"{BASE_URL}/agents/", headers=headers)
    if resp.status_code == 200:
        print(f"   ✅ Fetched {len(resp.json())} agents.")
    else:
        print(f"   ❌ Read all failed. {resp.text}")

    # 3. Read Single
    print("3. Reading specific agent...")
    resp = requests.get(f"{BASE_URL}/agents/{agent_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Read individual agent successfully.")
    else:
        print(f"   ❌ Read individual failed. {resp.text}")

    # 4. Update
    print("4. Updating agent...")
    update_data = {
        "AgentName": "Updated Test Agent",
        "mobile": "9876543211",
        "aadhar": "123456789012",
        "email": "updated@test.com",
    }
    resp = requests.put(
        f"{BASE_URL}/agents/{agent_id}", json=update_data, headers=headers
    )
    if resp.status_code == 200:
        print("   ✅ Agent updated successfully.")
    else:
        print(f"   ❌ Update failed. {resp.text}")

    # 5. Delete
    print("5. Deleting agent...")
    resp = requests.delete(f"{BASE_URL}/agents/{agent_id}", headers=headers)
    if resp.status_code == 200:
        print("   ✅ Agent deleted successfully.")
    else:
        print(f"   ❌ Delete failed. {resp.text}")


if __name__ == "__main__":
    test_agents()
