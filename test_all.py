import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing API...")
print("=" * 60)

# Test 1: Register
print("\n1. Testing register...")
register_data = {
    "username": "testuser",
    "password": "test123456",
    "blogger_id": "blogger_123456"
}
try:
    r = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("OK - Register success!")
    elif r.status_code == 400 and "已存在" in r.text:
        print("OK - User already exists")
    else:
        print(r.text)
except Exception as e:
    print(f"Error: {e}")

# Test 2: Login
print("\n2. Testing login...")
login_data = {
    "username": "testuser",
    "password": "test123456"
}
try:
    r = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("OK - Login success!")
        print(f"Token: {token[:50]}...")
    else:
        print(r.text)
except Exception as e:
    print(f"Error: {e}")
    token = None

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Crawl
    print("\n3. Testing crawl...")
    try:
        r = requests.get(f"{BASE_URL}/crawl/my_all_notes", headers=headers, timeout=300)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"OK - Crawl success!")
            print(r.json())
        else:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Dashboard
    print("\n4. Testing dashboard...")
    try:
        r = requests.get(f"{BASE_URL}/dashboard", headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("OK - Dashboard success!")
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
        else:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Export
    print("\n5. Testing export...")
    try:
        r = requests.get(f"{BASE_URL}/export_report", headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("OK - Export success!")
            print(f"HTML length: {len(r.text)}")
        else:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
