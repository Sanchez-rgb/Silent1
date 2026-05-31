#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os

def hash_password(password: str) -> str:
    import bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def reset_database():
    print("Resetting database...")
    
    if os.path.exists('xiaohongshu.db'):
        os.remove('xiaohongshu.db')
        print("Database deleted.")
    
    print("\nCreating new database...")
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
    test_username = "admin"
    test_password = "123456"
    hashed = hash_password(test_password)
    
    cursor.execute(
        "INSERT INTO users (username, password, blogger_id) VALUES (?, ?, ?)",
        (test_username, hashed, "test_blogger_123")
    )
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("Database reset successfully!")
    print("="*50)
    print(f"\nTest account created:")
    print(f"  Username: {test_username}")
    print(f"  Password: {test_password}")
    print(f"  Blogger ID: test_blogger_123")
    print("\nYou can use this account to login, or register a new one!")

if __name__ == "__main__":
    print("="*50)
    print("小红书情感分析平台 - 数据库重置工具")
    print("="*50)
    print()
    
    choice = input("Are you sure you want to reset the database? (y/n): ")
    if choice.lower() == 'y':
        reset_database()
    else:
        print("Cancelled.")
