
import requests
import sys

BASE = "http://localhost:8000"

# Clean up
import sqlite3
conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM users WHERE username = 'demo_user'")
conn.commit()
conn.close()

# Test register
print("1. Register...")
reg = requests.post(f"{BASE}/register", json={
    "username": "demo_user",
    "password": "demo_password123",
    "blogger_id": "demo_blogger_001"
})
print(f"   Status: {reg.status_code}")
print(f"   Response: {reg.text}")

# Test login
print("\n2. Login...")
login = requests.post(f"{BASE}/login", data={
    "username": "demo_user",
    "password": "demo_password123"
})
print(f"   Status: {login.status_code}")
if login.status_code == 200:
    print(f"   Token received!")
    
    # Test dashboard
    print("\n3. Dashboard...")
    token = login.json()["access_token"]
    dash = requests.get(f"{BASE}/dashboard", headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {dash.status_code}")
    print(f"   Response keys: {list(dash.json().keys())}")

# Test wrong password
print("\n4. Wrong password...")
wrong_login = requests.post(f"{BASE}/login", data={
    "username": "demo_user",
    "password": "wrong"
})
print(f"   Status: {wrong_login.status_code}")
print(f"   Response: {wrong_login.text}")
