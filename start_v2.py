#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

os.chdir(r'c:\Users\55382\Documents\trae_projects\j')

print("="*60)
print("  红评洞察 v2.0 - 启动服务")
print("="*60)
print()

try:
    print("[1] 检查语法...")
    import ast
    with open('main_v2.py', 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print("    ✅ 语法正确！")

    print()
    print("[2] 启动服务...")
    print("    📱 前端: file://c:/Users/55382/Documents/trae_projects/j/index-v4.html")
    print("    🌐 API: http://127.0.0.1:8084")
    print("    📄 文档: http://127.0.0.1:8084/docs")
    print()
    print("    测试账号：13800138000 / test123456")
    print("    测试验证码：123456（固定）")
    print()
    print("="*60)
    print()

    import uvicorn
    uvicorn.run("main_v2:app", host="127.0.0.1", port=8084)

except Exception as e:
    print(f"\n❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
