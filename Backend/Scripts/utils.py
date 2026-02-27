import requests

BASE_URL = "http://localhost:8000"


def get_auth_token():
    """Helper to get a JWT token. Assumes api_test_user exists or creates it."""
    # Try to login first
    login_data = {"username": "api_test_user", "password": "testpassword123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

    if response.status_code == 200:
        return response.json().get("access_token")

    # If login fails (maybe user doesn't exist), register
    register_data = {"username": "api_test_user", "password": "testpassword123"}
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 200:
        # After registering, login
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get auth token: {response.text}")


def get_headers():
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}
