#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import threading
import webbrowser
import time

os.chdir(r'c:\Users\55382\Documents\trae_projects\j')

print("="*60)
print("  红评洞察 - 小红书情感分析")
print("="*60)
print()

try:
    print("[1] 检查语法...")
    with open('main_v2.py', 'r', encoding='utf-8') as f:
        content = f.read()
    import ast
    ast.parse(content)
    print("✅ 语法正确！")
    
    print()
    print("[2] 导入测试...")
    sys.path.insert(0, r'c:\Users\55382\Documents\trae_projects\j')
    from main_v2 import app
    print("✅ main_v2 导入成功！")
    
    print()
    print("[3] 启动服务...")
    print(f"📱 前端页面: file://c:/Users/55382/Documents/trae_projects/j/index-v3.html")
    print(f"🌐 API地址: http://127.0.0.1:8084")
    print(f"📄 API文档: http://127.0.0.1:8084/docs")
    print(f"👤 测试账号: admin / 123456")
    print()
    print("="*60)
    print()
    
    # 启动服务线程
    def run_server():
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8084)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务启动
    time.sleep(3)
    
    # 打开前端页面
    print("打开前端页面...")
    html_path = os.path.abspath('index-v3.html')
    file_url = f'file:///{html_path.replace(os.sep, "/")}'
    webbrowser.open(file_url)
    
    print()
    print("服务已启动！按 Ctrl+C 停止...")
    print()
    
    # 保持运行
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print()
    print("服务已停止！")
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
