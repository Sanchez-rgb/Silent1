#!/usr/bin/env python
# -*- coding: utf-8 -*-

print("开始测试...")

try:
    import sys
    print(f"Python版本: {sys.version}")
    
    print("\n[1] 尝试导入 FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI 导入成功！")
    
    print("\n[2] 尝试导入 uvicorn...")
    import uvicorn
    print("✅ uvicorn 导入成功！")
    
    print("\n[3] 尝试导入 main_v2...")
    sys.path.insert(0, r'c:\Users\55382\Documents\trae_projects\j')
    from main_v2 import app
    print("✅ main_v2 导入成功！")
    
    print("\n所有导入成功！")
    
except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
