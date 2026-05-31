#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time

print("="*60)
print("  扫码绑定Cookie测试")
print("="*60)
print()

base_url = "http://127.0.0.1:8084"

# 1. 登录获取token
print("[1] 登录获取token...")
try:
    data = {"phone": "13800138000", "password": "test123456"}
    r = requests.post(f"{base_url}/login", json=data)
    result = r.json()
    if result.get("success"):
        token = result.get("token")
        print(f"    ✅ 登录成功！Token: {token[:30]}...")
    else:
        print(f"    ❌ 登录失败: {result.get('detail')}")
        exit(1)
except Exception as e:
    print(f"    ❌ 错误: {e}")
    exit(1)

print()

# 2. 生成二维码
print("[2] 生成二维码...")
try:
    r = requests.get(f"{base_url}/qrcode/generate", headers={"Authorization": f"Bearer {token}"})
    result = r.json()
    if result.get("qr_id"):
        qr_id = result.get("qr_id")
        qr_image = result.get("qr_image")
        print(f"    ✅ 二维码已生成！")
        print(f"    QR ID: {qr_id}")
        print(f"    图片长度: {len(qr_image)} 字符")
    else:
        print(f"    ❌ 生成失败: {result}")
        exit(1)
except Exception as e:
    print(f"    ❌ 错误: {e}")
    exit(1)

print()

# 3. 检查二维码状态（多次轮询）
print("[3] 检查二维码状态（模拟扫码）...")
for i in range(3):
    try:
        r = requests.get(f"{base_url}/qrcode/check/{qr_id}", headers={"Authorization": f"Bearer {token}"})
        result = r.json()
        print(f"    第{i+1}次检查: {result}")
        time.sleep(1)
    except Exception as e:
        print(f"    ❌ 错误: {e}")

print()

# 4. 模拟确认（如果状态是pending）
print("[4] 模拟确认扫码...")
try:
    data = {"cookie": "test_cookie_12345"}
    r = requests.post(f"{base_url}/qrcode/confirm/{qr_id}", json=data, headers={"Authorization": f"Bearer {token}"})
    result = r.json()
    print(f"    确认结果: {result}")

    if result.get("success"):
        print(f"    ✅ Cookie绑定成功！")

        # 5. 验证Cookie是否保存
        print()
        print("[5] 验证Cookie是否保存...")
        r = requests.get(f"{base_url}/me", headers={"Authorization": f"Bearer {token}"})
        user = r.json()
        print(f"    用户信息: {user}")
        print(f"    Cookie状态: {'已绑定' if user.get('has_cookie') else '未绑定'}")
    else:
        print(f"    ❌ 绑定失败: {result.get('detail')}")

except Exception as e:
    print(f"    ❌ 错误: {e}")

print()
print("="*60)