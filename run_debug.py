#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import traceback

try:
    from main_v2 import app
    print("✅ 导入成功！")
    
    import uvicorn
    print("✅ uvicorn 导入成功！")
    
    uvicorn.run(app, host="127.0.0.1", port=8083)
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
