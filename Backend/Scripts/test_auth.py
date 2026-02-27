import requests
from utils import BASE_URL


def test_auth_flow():
    print("Testing Auth Flow...")

    username = "auth_test_user"
    password = "secretpassword"

    # 1. Register
    print("1. Registering new user...")
    register_data = {"username": username, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if resp.status_code == 200:
        print("   ✅ User registered successfully.")
    elif resp.status_code == 400 and "already registered" in resp.text:
        print("   ⚠️ User already exists, proceeding to login.")
    else:
        print(f"   ❌ Registration failed: {resp.text}")

    # 2. Login
    print("2. Logging in...")
    login_data = {"username": username, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        if token:
            print(f"   ✅ Login successful. Token received: {token[:15]}...")
        else:
            print("   ❌ Login response missing token.")
    else:
        print(f"   ❌ Login failed: {resp.text}")


if __name__ == "__main__":
    test_auth_flow()
