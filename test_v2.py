#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import sys
import requests

print("="*60)
print("  红评洞察 v2.0 - 启动并测试")
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
time.sleep(5)

# 检查服务是否启动成功
if proc.poll() is not None:
    print("    ❌ 服务启动失败！")
    sys.exit(1)

print("    ✅ 服务启动成功！")
print()

# 测试API
print("[2] 测试API...")
base_url = "http://127.0.0.1:8084"

# 测试健康检查
print("    健康检查...")
try:
    r = requests.get(f"{base_url}/health")
    if r.status_code == 200:
        print("        ✅ 健康检查通过")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试注册
print("    测试注册...")
try:
    data = {"phone": "13800138000", "password": "test123456"}
    r = requests.post(f"{base_url}/register", json=data)
    result = r.json()
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {result}")
    if result.get("success"):
        print("        ✅ 注册成功！")
        test_token = result.get("token")
    else:
        print(f"        ❌ 注册失败: {result.get('detail')}")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试登录
print("    测试密码登录...")
try:
    data = {"phone": "13800138000", "password": "test123456"}
    r = requests.post(f"{base_url}/login", json=data)
    result = r.json()
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {result}")
    if result.get("success"):
        print("        ✅ 登录成功！")
        test_token = result.get("token")
    else:
        print(f"        ❌ 登录失败: {result.get('detail')}")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试发送验证码
print("    测试发送验证码...")
try:
    data = {"phone": "13800138001"}
    r = requests.post(f"{base_url}/send_code", json=data)
    result = r.json()
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {result}")
    if result.get("success"):
        print("        ✅ 验证码发送成功！")
except Exception as e:
    print(f"        ❌ 失败: {e}")

# 测试验证码登录
print("    测试验证码登录...")
try:
    data = {"phone": "13800138001", "code": "123456"}
    r = requests.post(f"{base_url}/login_by_code", json=data)
    result = r.json()
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {result}")
    if result.get("success"):
        print("        ✅ 验证码登录成功！")
    else:
        print(f"        ❌ 验证码登录失败: {result.get('detail')}")
except Exception as e:
    print(f"        ❌ 失败: {e}")

print()
print("[3] 服务运行中...")
print(f"    📱 前端: file://c:/Users/55382/Documents/trae_projects/j/index-v4.html")
print(f"    🌐 API: http://127.0.0.1:8084")
print(f"    📄 文档: http://127.0.0.1:8084/docs")
print()
print("测试账号：13800138000 / test123456")
print("测试验证码：123456（固定）")
print()
print("按 Ctrl+C 停止服务")

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    print("\n服务已停止！")
