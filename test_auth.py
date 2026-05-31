
import requests
import json

BASE = "http://localhost:8000"

print("=" * 60)
print("测试注册和登录流程")
print("=" * 60)

# 1. 先删除测试用户（如果存在）
import sqlite3
conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM users WHERE username = 'demo_user'")
conn.commit()
conn.close()
print("\n[1] 清理旧数据完成")

# 2. 注册新用户
print("\n[2] 注册新用户...")
register_data = {
    "username": "demo_user",
    "password": "demo_password123",
    "blogger_id": "demo_blogger_001"
}

r = requests.post(f"{BASE}/register", json=register_data)
print(f"  状态码: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"  注册成功！")
    print(f"  用户ID: {result['id']}")
    print(f"  用户名: {result['username']}")
    print(f"  博主ID: {result['blogger_id']}")
else:
    print(f"  注册失败: {r.text}")

# 3. 登录
print("\n[3] 登录测试...")
login_data = {
    "username": "demo_user",
    "password": "demo_password123"
}
r = requests.post(f"{BASE}/login", data=login_data)
print(f"  状态码: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"  登录成功！")
    print(f"  Token类型: {result['token_type']}")
    print(f"  Access Token (前50字符): {result['access_token'][:50]}...")
    token = result['access_token']
    
    # 4. 测试需要认证的接口
    print("\n[4] 测试需要认证的接口（访问Dashboard）...")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/dashboard", headers=headers)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        print("  Dashboard访问成功！")
else:
    print(f"  登录失败: {r.text}")

# 5. 测试错误密码
print("\n[5] 测试错误密码...")
wrong_login_data = {
    "username": "demo_user",
    "password": "wrong_password"
}
r = requests.post(f"{BASE}/login", data=wrong_login_data)
print(f"  状态码: {r.status_code}")
print(f"  响应: {r.text}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
