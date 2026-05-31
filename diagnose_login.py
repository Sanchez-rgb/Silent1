#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_database():
    print("="*60)
    print("数据库诊断工具")
    print("="*60)
    print()
    
    conn = sqlite3.connect('xiaohongshu.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 检查用户表
    print("【1】检查用户表...")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("   ⚠️  没有找到任何用户！")
    else:
        print(f"   ✅ 找到 {len(users)} 个用户：")
        for user in users:
            print(f"      - ID: {user['id']}")
            print(f"        用户名: {user['username']}")
            print(f"        密码哈希: {user['password']}")
            print()
    
    # 测试密码验证
    print("【2】测试密码验证...")
    test_password = input("请输入要测试的密码（输入 q 跳过）：")
    if test_password.lower() != 'q':
        for user in users:
            hashed = hash_password(test_password)
            print(f"\n      测试用户 '{user['username']}':")
            print(f"      输入密码哈希: {hashed}")
            print(f"      数据库哈希:   {user['password']}")
            if hashed == user['password']:
                print(f"      ✅ 密码匹配！")
            else:
                print(f"      ❌ 密码不匹配！")
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)
    print()
    print("提示：您可以选择：")
    print("  1. 重新注册一个新用户")
    print("  2. 清空数据库重新开始")
    
    choice = input("\n是否要清空数据库重新初始化？(y/n): ")
    if choice.lower() == 'y':
        print("正在删除数据库...")
        import os
        try:
            os.remove('xiaohongshu.db')
            print("✅ 数据库已删除！请重新启动服务")
        except Exception as e:
            print(f"❌ 删除失败: {e}")

if __name__ == "__main__":
    check_database()
