
import requests

print("测试服务访问...")
print("=" * 50)

urls = [
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000/health",
    "http://127.0.0.1:8000/docs"
]

for url in urls:
    try:
        print(f"\n访问: {url}")
        response = requests.get(url, timeout=5)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200 and 'json' in response.headers.get('content-type', ''):
            print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 50)
print("\n测试注册接口...")
try:
    import random
    username = f"test_user_{random.randint(1000, 9999)}"
    response = requests.post(
        "http://127.0.0.1:8000/register",
        json={
            "username": username,
            "password": "test123",
            "blogger_id": "test_blogger"
        },
        timeout=5
    )
    print(f"注册 - 状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"注册成功: {response.json()}")
    else:
        print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")
