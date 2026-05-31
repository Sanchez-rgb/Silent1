#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uvicorn
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("   红评洞察 - 小红书情感分析平台")
print("="*60)
print()
print("正在启动服务...")
print()

try:
    # 启动服务
    uvicorn.run(
        "main_v2:app", 
        host="127.0.0.1", 
        port=8080,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n\n服务已停止")
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
