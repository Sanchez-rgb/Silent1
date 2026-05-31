#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check():
    conn = sqlite3.connect('xiaohongshu.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Checking users...")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("No users found!")
        print("\nDo you want to create a test user? (y/n)")
        choice = input()
        if choice.lower() == 'y':
            username = input("Username: ")
            password = input("Password: ")
            blogger_id = input("Blogger ID (optional): ")
            
            hashed = hash_password(password)
            try:
                cursor.execute(
                    "INSERT INTO users (username, password, blogger_id) VALUES (?, ?, ?)",
                    (username, hashed, blogger_id)
                )
                conn.commit()
                print("User created successfully!")
            except Exception as e:
                print(f"Error: {e}")
    else:
        print(f"\nFound {len(users)} users:")
        for user in users:
            print(f"  ID: {user['id']}, Username: {user['username']}")
            print(f"  Hashed password: {user['password']}")
            
            test_pwd = input(f"\nTest password for {user['username']} (or press Enter to skip): ")
            if test_pwd:
                hashed_test = hash_password(test_pwd)
                print(f"  Your input hashed: {hashed_test}")
                if hashed_test == user['password']:
                    print("  Password matches!")
                else:
                    print("  Password does not match!")
    
    conn.close()

if __name__ == "__main__":
    check()
