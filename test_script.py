
# test_script.py
import requests
import time
import sys

BASE = "http://localhost:8000"

print("Step 1: Login")
try:
    login_res = requests.post(f"{BASE}/login", data={
        "username": "testuser",
        "password": "test123456"
    })
    print(f"  Status: {login_res.status_code}")
    token = login_res.json()["access_token"]
    print(f"  Token length: {len(token)}")
    headers = {"Authorization": f"Bearer {token}"}
except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

print("\nStep 2: Dashboard")
try:
    res = requests.get(f"{BASE}/dashboard", headers=headers, timeout=30)
    print(f"  Status: {res.status_code}")
    if res.status_code == 200:
        print(f"  Success! Data keys: {list(res.json().keys())}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone!")
