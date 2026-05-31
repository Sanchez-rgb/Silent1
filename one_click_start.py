#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import webbrowser

def main():
    print("="*65)
    print("   红评洞察 - 小红书情感分析平台 - 一键启动")
    print("="*65)
    print()

    # 1. 重置数据库
    print("[1/4] 重置数据库...")
    import sqlite3
    import hashlib
    import os
    
    if os.path.exists('xiaohongshu.db'):
        os.remove('xiaohongshu.db')
    
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            blogger_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_analysis_time DATETIME
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            note_title TEXT,
            note_url TEXT,
            blogger_id TEXT,
            publish_time TEXT,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            analyze_time TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT NOT NULL,
            comment_id TEXT,
            comment_text TEXT,
            user_name TEXT,
            sentiment TEXT,
            confidence REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            sentiment_score REAL,
            positive_count INTEGER DEFAULT 0,
            neutral_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            top_negative_comments TEXT,
            rating TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建测试用户
    def hash_password(password):
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    test_username = "admin"
    test_password = "123456"
    hashed = hash_password(test_password)
    
    cursor.execute(
        "INSERT INTO users (username, password, blogger_id) VALUES (?, ?, ?)",
        (test_username, hashed, "test_blogger_123")
    )
    
    conn.commit()
    conn.close()
    print("   数据库初始化完成！")

    # 2. 启动服务
    print()
    print("[2/4] 启动API服务...")
    
    import threading
    import uvicorn
    
    def run_server():
        uvicorn.run("main_v2:app", host="127.0.0.1", port=8081, log_level="info")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("   等待服务启动...")
    time.sleep(4)
    print("   API服务已启动！")

    # 3. 打开浏览器
    print()
    print("[3/4] 打开前端页面...")
    
    html_path = os.path.abspath('index-v3.html')
    file_url = f'file:///{html_path.replace(os.sep, "/")}'
    
    webbrowser.open(file_url)
    print("   前端页面已打开！")

    # 4. 显示信息
    print()
    print("[4/4] 启动完成！")
    print()
    print("="*65)
    print("   项目已成功运行！")
    print("="*65)
    print()
    print("📱 访问地址：")
    print(f"   前端页面: {file_url}")
    print("   API文档:  http://127.0.0.1:8081/docs")
    print("   健康检查: http://127.0.0.1:8081/health")
    print()
    print("👤 测试账号：")
    print(f"   用户名: {test_username}")
    print(f"   密码:   {test_password}")
    print(f"   博主ID: test_blogger_123")
    print()
    print("💡 使用提示：")
    print("   1. 使用测试账号登录，或注册新账号")
    print("   2. 配置博主ID和Cookie（可选）")
    print("   3. 点击「开始爬取」进行分析")
    print()
    print("按 Ctrl+C 停止服务")
    print()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("服务已停止！")

if __name__ == "__main__":
    main()
