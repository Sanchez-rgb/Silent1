#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

print("="*50)
print("测试登录API")
print("="*50)
print()

base_url = "http://127.0.0.1:8084"

# 测试1: 健康检查
print("[1] 健康检查...")
try:
    r = requests.get(f"{base_url}/health")
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text}")
    print("    ✅ 服务正常")
except Exception as e:
    print(f"    ❌ 失败: {e}")

print()

# 测试2: 登录测试
print("[2] 登录测试...")
try:
    data = {
        "username": "admin",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/login", data=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text}")
    if r.status_code == 200:
        print("    ✅ 登录成功！")
    else:
        print("    ❌ 登录失败")
except Exception as e:
    print(f"    ❌ 失败: {e}")

print()

# 测试3: 注册测试
print("[3] 注册测试...")
try:
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    r = requests.post(f"{base_url}/register", json=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text}")
    if r.status_code == 200:
        print("    ✅ 注册成功！")
    else:
        print("    ❌ 注册失败")
except Exception as e:
    print(f"    ❌ 失败: {e}")

print()

# 测试4: 测试新用户登录
print("[4] 新用户登录测试...")
try:
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    r = requests.post(f"{base_url}/login", data=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text}")
    if r.status_code == 200:
        print("    ✅ 新用户登录成功！")
    else:
        print("    ❌ 新用户登录失败")
except Exception as e:
    print(f"    ❌ 失败: {e}")

print()
print("="*50)
print("测试完成！")
print("="*50)
