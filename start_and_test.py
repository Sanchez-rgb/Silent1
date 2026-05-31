#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import sys
import requests

print("="*60)
print("  红评洞察 - 启动并测试")
print("="*60)
print()

# 启动服务
print("[1] 启动服务...")
proc = subprocess.Popen([
    sys.executable, "-m", "uvicorn", 
    "main_v2:app", "--host", "127.0.0.1", "--port", "8084"
], cwd=r'c:\Users\55382\Documents\trae_projects\j')

# 等待服务启动
print("    等待服务启动...")
time.sleep(4)

# 检查服务是否启动成功
if proc.poll() is not None:
    print("    ❌ 服务启动失败！")
    sys.exit(1)

print("    ✅ 服务启动成功！")
print()

# 测试登录API
print("[2] 测试登录API...")

base_url = "http://127.0.0.1:8084"

# 测试健康检查
print("    健康检查...")
try:
    r = requests.get(f"{base_url}/health")
    print(f"        状态码: {r.status_code}")
    if r.status_code == 200:
        print("        ✅ 健康检查通过")
    else:
        print("        ❌ 健康检查失败")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试登录 (使用JSON格式)
print("    登录测试...")
try:
    data = {"username": "admin", "password": "123456"}
    r = requests.post(f"{base_url}/login", json=data)
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {r.text}")
    response_data = r.json()
    if response_data.get("success"):
        print("        ✅ 登录成功！")
    else:
        print(f"        ❌ 登录失败: {response_data.get('message')}")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试注册
print("    注册测试...")
try:
    data = {"username": "testuser2", "password": "testpass123"}
    r = requests.post(f"{base_url}/register", json=data)
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {r.text}")
    response_data = r.json()
    if response_data.get("success"):
        print("        ✅ 注册成功！")
    else:
        print(f"        ❌ 注册失败: {response_data.get('message')}")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试新用户登录
print("    新用户登录测试...")
try:
    data = {"username": "testuser2", "password": "testpass123"}
    r = requests.post(f"{base_url}/login", json=data)
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {r.text}")
    response_data = r.json()
    if response_data.get("success"):
        print("        ✅ 新用户登录成功！")
    else:
        print(f"        ❌ 新用户登录失败: {response_data.get('message')}")
except Exception as e:
    print(f"        ❌ 失败: {e}")

print()

# 保持服务运行
print("[3] 服务运行中...")
print(f"    📱 前端: file://c:/Users/55382/Documents/trae_projects/j/index-v3.html")
print(f"    🌐 API: http://127.0.0.1:8084")
print(f"    👤 测试账号: admin / 123456")
print()
print("按 Ctrl+C 停止服务")

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    print("\n服务已停止！")