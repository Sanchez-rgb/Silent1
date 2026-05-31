
import requests
import json

BASE = "http://localhost:8000"
output_file = "auth_test_results.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("=== 认证流程测试 ===\n\n")
    
    # 0. Cleanup
    import sqlite3
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = 'demo_user'")
    conn.commit()
    conn.close()
    f.write("1. 清理测试数据完成\n\n")
    
    # 1. Register
    f.write("2. 注册用户...\n")
    reg = requests.post(f"{BASE}/register", json={
        "username": "demo_user",
        "password": "demo_password123",
        "blogger_id": "demo_blogger_001"
    })
    f.write(f"   状态码: {reg.status_code}\n")
    f.write(f"   响应: {reg.text}\n\n")
    
    # 2. Login
    f.write("3. 登录...\n")
    login = requests.post(f"{BASE}/login", data={
        "username": "demo_user",
        "password": "demo_password123"
    })
    f.write(f"   状态码: {login.status_code}\n")
    f.write(f"   响应: {login.text}\n\n")
    
    if login.status_code == 200:
        token = login.json()["access_token"]
        
        # 3. Test Dashboard
        f.write("4. 访问Dashboard...\n")
        dash = requests.get(f"{BASE}/dashboard", headers={"Authorization": f"Bearer {token}"})
        f.write(f"   状态码: {dash.status_code}\n")
        if dash.status_code == 200:
            f.write(f"   响应键: {list(dash.json().keys())}\n\n")
    
    # 4. Test wrong password
    f.write("5. 测试错误密码...\n")
    wrong_login = requests.post(f"{BASE}/login", data={
        "username": "demo_user",
        "password": "wrong_password"
    })
    f.write(f"   状态码: {wrong_login.status_code}\n")
    f.write(f"   响应: {wrong_login.text}\n\n")
    
    f.write("=== 测试完成 ===\n")

print("测试完成，结果已保存到 auth_test_results.txt")
