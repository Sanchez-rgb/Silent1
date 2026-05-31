#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

os.chdir(r'c:\Users\55382\Documents\trae_projects\j')

print("="*60)
print("  测试二维码生成")
print("="*60)
print()

try:
    print("[1] 测试qrcode模块...")
    import qrcode
    print("    ✅ qrcode模块已安装！")

    print()
    print("[2] 生成测试二维码...")
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data("https://xiaohongshu.com/login/qrcode?qr_id=test123")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 保存到文件
    img.save("test_qrcode.png")
    print("    ✅ 二维码已保存到 test_qrcode.png")

    print()
    print("[3] 测试后端API...")
    import requests
    import time

    # 启动服务
    print("    启动服务...")
    import subprocess
    proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "main_v2:app", "--host", "127.0.0.1", "--port", "8084"
    ], cwd=r'c:\Users\55382\Documents\trae_projects\j')

    # 等待服务启动
    time.sleep(5)

    # 测试健康检查
    print("    测试健康检查...")
    r = requests.get("http://127.0.0.1:8084/health")
    print(f"        状态码: {r.status_code}")
    print(f"        响应: {r.text}")

    # 测试注册
    print("    测试注册...")
    data = {"phone": "13800138000", "password": "test123456"}
    r = requests.post("http://127.0.0.1:8084/register", json=data)
    print(f"        状态码: {r.status_code}")
    result = r.json()
    print(f"        响应: {result}")

    if result.get("success"):
        token = result.get("token")
        print(f"        ✅ 注册成功！")

        # 测试生成二维码
        print()
        print("    测试生成二维码...")
        r = requests.get(
            "http://127.0.0.1:8084/qrcode/generate",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"        状态码: {r.status_code}")
        qr_data = r.json()
        print(f"        qr_id: {qr_data.get('qr_id')}")
        print(f"        qr_image长度: {len(qr_data.get('qr_image', ''))} 字符")

        if qr_data.get('qr_image'):
            # 保存二维码图片
            img_data = qr_data['qr_image'].split(',')[1]
            import base64
            with open("api_qrcode.png", "wb") as f:
                f.write(base64.b64decode(img_data))
            print("        ✅ 二维码已保存到 api_qrcode.png")

    print()
    print("="*60)
    print("  测试完成！")
    print("="*60)

    proc.terminate()

except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
