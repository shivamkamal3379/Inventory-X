import requests
from utils import BASE_URL, get_headers


def test_dashboard():
    print("Testing Dashboard API...")
    headers = get_headers()

    print("1. Fetching dashboard stats...")
    resp = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    if resp.status_code == 200:
        stats = resp.json()
        print("   ✅ Dashboard Stats Successfully Fetched:")
        print(f"      - Total Items:        {stats.get('totalItems')}")
        print(f"      - Total Parties:      {stats.get('totalParties')}")
        print(f"      - Active Parties:     {stats.get('activeParties')}")
        print(f"      - Total Rented Out:   {stats.get('totalRentedOutQty')}")
        print(f"      - Total Available:    {stats.get('totalAvailableQty')}")
        print(f"      - Total Rentals:      {stats.get('totalRentals')}")
        print(f"      - Total Returns:      {stats.get('totalReturns')}")
    else:
        print(f"   ❌ Failed to fetch dashboard stats. {resp.text}")


if __name__ == "__main__":
    test_dashboard()
