import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import extract_user_id, get_standard_profile_url

test_cases = [
    # 1. 标准主页链接
    ("https://www.xiaohongshu.com/user/profile/5e12345abcdef1234567890", "5e12345abcdef1234567890"),
    
    # 2. xhs.cn 短链接
    ("https://xhs.cn/u/1234567890", "1234567890"),
    
    # 3. hongshu.com 链接
    ("https://hongshu.com/u/abc123xyz", "abc123xyz"),
    
    # 4. xiaohongshu.com/user/ 格式
    ("https://www.xiaohongshu.com/user/5f12345abcdef1234567890", "5f12345abcdef1234567890"),
    
    # 5. 纯数字用户ID
    ("1234567890", "1234567890"),
    ("9876543210", "9876543210"),
    
    # 6. 字母数字组合的用户ID
    ("abc123XYZ", "abc123XYZ"),
    ("user123test", "user123test"),
    
    # 7. 其他格式（测试边界情况）
    ("  12345  ", "12345"),  # 带空格
    ("", None),  # 空字符串
    ("invalid!@#", None),  # 特殊字符
]

print("="*70)
print("Test extract_user_id function")
print("="*70)

all_passed = True
for input_str, expected in test_cases:
    result = extract_user_id(input_str)
    passed = (result == expected)
    all_passed = all_passed and passed
    
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status}")
    print(f"  Input: {repr(input_str)}")
    print(f"  Expected: {repr(expected)}")
    print(f"  Got: {repr(result)}")
    
    if result:
        print(f"  Standard URL: {get_standard_profile_url(result)}")

print("\n" + "="*70)
if all_passed:
    print("All tests passed!")
else:
    print("Some tests failed, please check the code")
print("="*70)
