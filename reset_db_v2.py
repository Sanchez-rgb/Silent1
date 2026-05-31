#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

db_file = 'xiaohongshu.db'

if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ 已删除旧数据库: {db_file}")
else:
    print(f"ℹ️ 数据库不存在: {db_file}")

print()
print("现在请重新启动服务:")
print("    python start_v2.py")