#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

print("="*60)
print("  详细测试登录接口")
print("="*60)
print()

base_url = "http://127.0.0.1:8084"

# 1. 测试根路径
print("[1] 测试根路径...")
try:
    r = requests.get(f"{base_url}/")
    print(f"    状态码: {r.status_code}")
    print(f"    响应: {r.text}")
except Exception as e:
    print(f"    ❌ 错误: {e}")

print()

# 2. 测试注册
print("[2] 测试注册接口...")
try:
    data = {"phone": "13800138000", "password": "test123456"}
    print(f"    发送数据: {data}")
    r = requests.post(f"{base_url}/register", json=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应内容: {r.text}")
    print(f"    响应头: {r.headers}")
except Exception as e:
    print(f"    ❌ 错误: {e}")

print()

# 3. 测试登录
print("[3] 测试登录接口...")
try:
    data = {"phone": "13800138000", "password": "test123456"}
    print(f"    发送数据: {data}")
    r = requests.post(f"{base_url}/login", json=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应内容: {r.text}")
    print(f"    响应头: {r.headers}")
except Exception as e:
    print(f"    ❌ 错误: {e}")

print()

# 4. 测试发送验证码
print("[4] 测试发送验证码...")
try:
    data = {"phone": "13900139000"}
    print(f"    发送数据: {data}")
    r = requests.post(f"{base_url}/send_code", json=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应内容: {r.text}")
except Exception as e:
    print(f"    ❌ 错误: {e}")

print()

# 5. 测试验证码登录
print("[5] 测试验证码登录...")
try:
    data = {"phone": "13900139000", "code": "123456"}
    print(f"    发送数据: {data}")
    r = requests.post(f"{base_url}/login_by_code", json=data)
    print(f"    状态码: {r.status_code}")
    print(f"    响应内容: {r.text}")
except Exception as e:
    print(f"    ❌ 错误: {e}")

print()
print("="*60)