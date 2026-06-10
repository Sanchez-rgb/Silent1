#!/usr/bin/env python3
"""
初始化脚本 - 生成初始激活码
使用方法: python init_codes.py
"""
import requests
import json
import sys

def generate_initial_codes(count=20):
    """生成初始激活码"""
    base_url = "http://localhost:8000"
    
    print("🚀 正在生成初始激活码...")
    
    try:
        # 生成激活码
        response = requests.post(
            f"{base_url}/api/admin/generate-codes",
            json={"count": count}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 成功生成 {count} 个激活码！\n")
            print("=" * 60)
            
            for i, code in enumerate(data["codes"], 1):
                print(f"{i:2d}. {code}")
            
            print("=" * 60)
            print("\n📋 激活码已复制到剪贴板")
            
            # 复制所有激活码
            codes_text = "\n".join(data["codes"])
            import pyperclip
            pyperclip.copy(codes_text)
            
            print("\n✨ 初始化完成！")
            print(f"\n💡 提示：")
            print(f"   - 管理页面: {base_url}/admin")
            print(f"   - 用户页面: {base_url}")
            print(f"   - 激活码有效期: 30天")
            
            return True
        else:
            print(f"❌ 生成失败: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("💡 请确保服务器正在运行: uvicorn main:app --reload")
        return False
    except ImportError:
        # 如果没有 pyperclip，只显示激活码
        print("\n⚠️ 注意: pyperclip 未安装，无法自动复制到剪贴板")
        print("请手动复制上方的激活码")
        return True
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    generate_initial_codes(count)
