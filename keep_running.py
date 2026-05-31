#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import sys

print("="*60)
print("  红评洞察 - 启动服务")
print("="*60)
print()

while True:
    print(f"[{time.strftime('%H:%M:%S')}] 启动服务...")
    print(f"📱 前端: file://c:/Users/55382/Documents/trae_projects/j/index-v3.html")
    print(f"🌐 API: http://127.0.0.1:8084")
    print(f"👤 账号: admin / 123456")
    print()
    
    # 启动服务
    proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "main_v2:app", "--host", "127.0.0.1", "--port", "8084"
    ], cwd=r'c:\Users\55382\Documents\trae_projects\j')
    
    # 等待服务运行
    time.sleep(5)
    
    # 检查进程是否还在运行
    if proc.poll() is None:
        print("✅ 服务启动成功！")
        print("按 Ctrl+C 停止服务")
        proc.wait()
    else:
        print(f"❌ 服务意外退出，退出码: {proc.returncode}")
        print("等待5秒后重新启动...")
        time.sleep(5)
    
    print()
