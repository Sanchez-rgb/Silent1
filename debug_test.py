#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt
import sqlite3

print("="*60)
print("  详细调试")
print("="*60)
print()

# 1. 测试bcrypt
print("[1] 测试bcrypt...")
try:
    password = "test123456"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"    密码: {password}")
    print(f"    哈希: {hashed.decode()}")
    
    # 验证
    result = bcrypt.checkpw(password.encode('utf-8'), hashed)
    print(f"    验证: {result}")
    print("    ✅ bcrypt正常")
except Exception as e:
    print(f"    ❌ bcrypt错误: {e}")
    import traceback
    traceback.print_exc()

print()

# 2. 测试数据库
print("[2] 测试数据库...")
try:
    conn = sqlite3.connect('xiaohongshu.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            xhs_cookie TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("    ✅ 表创建成功")
    
    # 插入测试数据
    phone = "13800138000"
    password_hash = bcrypt.hashpw("test123456".encode('utf-8'), bcrypt.gensalt()).decode()
    
    cursor.execute("INSERT INTO users (phone, password_hash) VALUES (?, ?)", (phone, password_hash))
    conn.commit()
    print(f"    ✅ 插入成功: {phone}")
    
    # 查询
    cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = cursor.fetchone()
    print(f"    查询结果: id={user['id']}, phone={user['phone']}")
    
    # 验证密码
    result = bcrypt.checkpw("test123456".encode('utf-8'), user['password_hash'].encode('utf-8'))
    print(f"    密码验证: {result}")
    print("    ✅ 数据库正常")
    
    conn.close()
except Exception as e:
    print(f"    ❌ 数据库错误: {e}")
    import traceback
    traceback.print_exc()

print()

# 3. 测试API调用
print("[3] 测试API调用...")
try:
    import requests
    
    # 注册
    data = {"phone": "13900139001", "password": "test123456"}
    r = requests.post("http://127.0.0.1:8084/register", json=data)
    print(f"    注册状态码: {r.status_code}")
    print(f"    注册响应: {r.text}")
    
    # 登录
    data = {"phone": "13900139001", "password": "test123456"}
    r = requests.post("http://127.0.0.1:8084/login", json=data)
    print(f"    登录状态码: {r.status_code}")
    print(f"    登录响应: {r.text}")
except Exception as e:
    print(f"    ❌ API错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)