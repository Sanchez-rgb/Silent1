#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

print("="*60)
print("  红评洞察 v2.0 - 登录功能测试")
print("="*60)
print()

base_url = "http://127.0.0.1:8084"

# 测试数据
test_phone = "13800138000"
test_password = "test123456"
test_code = "123456"

print("📋 测试数据：")
print(f"    手机号: {test_phone}")
print(f"    密码: {test_password}")
print(f"    验证码: {test_code}（固定）")
print()

# 1. 测试健康检查
print("[1] 健康检查...")
try:
    r = requests.get(f"{base_url}/health")
    print(f"    ✅ 服务正常运行")
except Exception as e:
    print(f"    ❌ 服务未启动: {e}")
    print("    请先运行: python start_v2.py")
    exit(1)

print()

# 2. 测试密码登录
print("[2] 测试密码登录...")
try:
    data = {"phone": test_phone, "password": test_password}
    r = requests.post(f"{base_url}/login", json=data)
    result = r.json()
    
    if result.get("success"):
        print(f"    ✅ 登录成功！")
        print(f"    Token: {result.get('token')[:30]}...")
        print(f"    用户ID: {result.get('user', {}).get('id')}")
        token = result.get('token')
    else:
        # 如果登录失败，尝试注册
        print(f"    ❌ 登录失败: {result.get('detail')}")
        print()
        print("[3] 尝试注册新用户...")
        
        data = {"phone": test_phone, "password": test_password}
        r = requests.post(f"{base_url}/register", json=data)
        result = r.json()
        
        if result.get("success"):
            print(f"    ✅ 注册成功！")
            print(f"    Token: {result.get('token')[:30]}...")
            token = result.get('token')
        else:
            print(f"    ❌ 注册失败: {result.get('detail')}")
            token = None
except Exception as e:
    print(f"    ❌ 网络错误: {e}")
    token = None

print()

# 3. 测试验证码登录
print("[4] 测试验证码登录...")
new_phone = "13900139000"

print(f"    步骤1: 发送验证码到 {new_phone}")
try:
    data = {"phone": new_phone}
    r = requests.post(f"{base_url}/send_code", json=data)
    result = r.json()
    
    if result.get("success"):
        print(f"    ✅ 验证码已发送！")
        print(f"    验证码: {test_code}（测试环境固定）")
        
        print()
        print(f"    步骤2: 使用验证码登录")
        data = {"phone": new_phone, "code": test_code}
        r = requests.post(f"{base_url}/login_by_code", json=data)
        result = r.json()
        
        if result.get("success"):
            print(f"    ✅ 验证码登录成功！")
            print(f"    Token: {result.get('token')[:30]}...")
            print(f"    用户ID: {result.get('user', {}).get('id')}")
        else:
            print(f"    ❌ 验证码登录失败: {result.get('detail')}")
    else:
        print(f"    ❌ 发送验证码失败: {result.get('detail')}")
except Exception as e:
    print(f"    ❌ 网络错误: {e}")

print()

# 4. 测试获取用户信息
if token:
    print("[5] 测试获取用户信息...")
    try:
        r = requests.get(f"{base_url}/me", headers={"Authorization": f"Bearer {token}"})
        result = r.json()
        print(f"    ✅ 用户信息获取成功")
        print(f"    手机号: {result.get('phone')}")
        print(f"    Cookie状态: {'已绑定' if result.get('has_cookie') else '未绑定'}")
    except Exception as e:
        print(f"    ❌ 获取失败: {e}")

print()
print("="*60)
print("  测试完成！")
print("="*60)
print()
print("💡 使用提示：")
print("    1. 打开前端页面: index-v4.html")
print("    2. 输入手机号: 13800138000")
print("    3. 输入密码: test123456")
print("    4. 点击「登录」按钮")
print()
print("    或者使用验证码登录：")
print("    1. 输入任意手机号（如: 13900139000）")
print("    2. 点击「获取验证码」")
print("    3. 输入验证码: 123456")
print("    4. 点击「登录」按钮")
print()