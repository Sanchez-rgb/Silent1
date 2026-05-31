import requests
import time

BASE = "http://localhost:8000"

# Login
print("Logging in...")
r = requests.post(f"{BASE}/login", data={"username": "testuser", "password": "test123456"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login OK\n")

# 1. Crawl
print("1. Crawling notes... (this may take a while)")
start = time.time()
r = requests.get(f"{BASE}/crawl/my_all_notes", headers=headers, timeout=300)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Success! Notes: {data['total_notes']}, Comments: {data['total_comments']}, Time: {data['duration_seconds']}s")
else:
    print(f"   Response: {r.text}")
print()

# 2. Dashboard
print("2. Getting dashboard...")
r = requests.get(f"{BASE}/dashboard", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print("   Dashboard data:")
    print(f"   - User: {data['user_info']}")
    print(f"   - Overview: {data['overview']}")
    print(f"   - Top best notes: {len(data['top_best_notes'])}")
    print(f"   - Top worst notes: {len(data['top_worst_notes'])}")
else:
    print(f"   Response: {r.text}")
print()

# 3. Export
print("3. Exporting report...")
r = requests.get(f"{BASE}/export_report", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"   Saved to report.html ({len(r.text)} chars)")
else:
    print(f"   Response: {r.text}")

print("\n=== All tests completed! ===")
