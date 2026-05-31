#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt

def test_bcrypt():
    print("="*50)
    print("测试 bcrypt 密码加密")
    print("="*50)
    
    test_password = "123456"
    
    # 1. 哈希密码
    print(f"\n[1] 密码: {test_password}")
    
    salt = bcrypt.gensalt()
    print(f"    盐值: {salt}")
    
    hashed = bcrypt.hashpw(test_password.encode('utf-8'), salt)
    hashed_str = hashed.decode('utf-8')
    print(f"    哈希: {hashed_str}")
    
    # 2. 验证正确的密码
    print("\n[2] 验证正确密码...")
    result = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
    print(f"    结果: {result}")
    
    # 3. 验证错误的密码
    print("\n[3] 验证错误密码...")
    wrong_password = "wrong_password"
    result = bcrypt.checkpw(wrong_password.encode('utf-8'), hashed)
    print(f"    结果: {result}")
    
    # 4. 再次生成哈希（确保每次不同）
    print("\n[4] 再次生成哈希（bcrypt每次不同）...")
    hashed2 = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
    print(f"    哈希1: {hashed_str}")
    print(f"    哈希2: {hashed2.decode('utf-8')}")
    print(f"    是否相同: {hashed_str == hashed2.decode('utf-8')}")
    
    # 5. 验证两个不同的哈希都能通过
    print("\n[5] 验证两个不同的哈希...")
    result1 = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
    result2 = bcrypt.checkpw(test_password.encode('utf-8'), hashed2)
    print(f"    哈希1验证: {result1}")
    print(f"    哈希2验证: {result2}")
    
    print("\n" + "="*50)
    print("测试完成！")
    print("="*50)

if __name__ == "__main__":
    test_bcrypt()
