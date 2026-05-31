
import requests
import json
import time

BASE_URL = "http://localhost:8000"
output_file = "test_output.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write("Testing API...\n")
    f.write("=" * 60 + "\n\n")

    # 1. Register
    f.write("1. Testing register...\n")
    register_data = {
        "username": "testuser",
        "password": "test123456",
        "blogger_id": "blogger_123456"
    }
    try:
        r = requests.post(f"{BASE_URL}/register", json=register_data)
        f.write(f"   Status: {r.status_code}\n")
        if r.status_code == 200:
            f.write("   OK - Register success!\n")
        elif r.status_code == 400 and "已存在" in r.text:
            f.write("   OK - User already exists\n")
        else:
            f.write(f"   {r.text}\n")
    except Exception as e:
        f.write(f"   Error: {e}\n")
    f.write("\n")

    # 2. Login
    f.write("2. Testing login...\n")
    login_data = {
        "username": "testuser",
        "password": "test123456"
    }
    token = None
    try:
        r = requests.post(f"{BASE_URL}/login", data=login_data)
        f.write(f"   Status: {r.status_code}\n")
        if r.status_code == 200:
            token = r.json()["access_token"]
            f.write("   OK - Login success!\n")
            f.write(f"   Token: {token[:50]}...\n")
        else:
            f.write(f"   {r.text}\n")
    except Exception as e:
        f.write(f"   Error: {e}\n")
    f.write("\n")

    if token:
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Dashboard
        f.write("3. Testing dashboard...\n")
        try:
            r = requests.get(f"{BASE_URL}/dashboard", headers=headers)
            f.write(f"   Status: {r.status_code}\n")
            if r.status_code == 200:
                f.write("   OK - Dashboard success!\n")
                data = r.json()
                f.write(f"   User info: {data['user_info']}\n")
                f.write(f"   Overview: {data['overview']}\n")
            else:
                f.write(f"   {r.text}\n")
        except Exception as e:
            f.write(f"   Error: {e}\n")
        f.write("\n")

    f.write("=" * 60 + "\n")
    f.write("TEST COMPLETE!\n")
    f.write("=" * 60 + "\n")

print("Test completed! Output saved to test_output.txt")
with open(output_file, "r", encoding="utf-8") as f:
    print(f.read())
