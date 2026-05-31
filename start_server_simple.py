#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("="*60)
print("  启动服务器")
print("="*60)
print()

try:
    import uvicorn
    print("✅ uvicorn 已安装")
    
    print()
    print("正在启动服务器...")
    print(f"📱 前端页面: file://c:/Users/55382/Documents/trae_projects/j/index-v3.html")
    print(f"🌐 API地址: http://127.0.0.1:8082")
    print(f"📄 API文档: http://127.0.0.1:8082/docs")
    print()
    print("="*60)
    print()
    
    uvicorn.run("main_v2:app", host="127.0.0.1", port=8082)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
