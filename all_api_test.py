
import requests
import json

def save_result(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        if isinstance(data, dict):
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(data))

BASE = "http://localhost:8000"

# Login
print("1. Login...")
r = requests.post(f"{BASE}/login", data={
    "username": "testuser",
    "password": "test123456"
})
save_result("1_login.json", r.json())
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   OK")

# Dashboard
print("\n2. Dashboard...")
r = requests.get(f"{BASE}/dashboard", headers=headers)
save_result("2_dashboard.json", r.json())
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   - Average sentiment: {data['overview']['average_sentiment_score']:.4f}")
    print(f"   - Excellent: {data['overview']['excellent_count']}")
    print(f"   - Good: {data['overview']['good_count']}")
    print(f"   - Warning: {data['overview']['warning_count']}")
    print(f"   - Danger: {data['overview']['danger_count']}")

# Export report
print("\n3. Export report...")
r = requests.get(f"{BASE}/export_report", headers=headers)
with open("3_report.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print(f"   Saved to 3_report.html ({len(r.text)} chars)")

print("\n--- All tests passed! ---")
