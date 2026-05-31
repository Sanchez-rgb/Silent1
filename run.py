import os
import sys
import subprocess
import webbrowser
import time
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 50)
    print("小红书情感分析系统 - 单用户演示版")
    print("=" * 50)

    cookie = os.getenv("XHS_COOKIE", "")
    if not cookie or cookie == "your_xiaohongshu_cookie_here":
        print("\n⚠️  警告: 未配置 XHS_COOKIE 环境变量")
        print("请在 .env 文件中设置您的小红书 Cookie")
        print("格式: XHS_COOKIE=your_cookie_here\n")

    print(f"XHS_COOKIE 配置状态: {'已配置 ✓' if cookie and cookie != 'your_xiaohongshu_cookie_here' else '未配置 ✗'}")
    print("\n正在启动服务器...")

    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    time.sleep(3)

    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    frontend_url = f"file:///{frontend_path.replace(os.sep, '/')}"

    print(f"\n前端页面: {frontend_url}")
    print("后端API: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务器\n")

    webbrowser.open(frontend_url)

    try:
        for line in backend_process.stdout:
            print(line, end="")
    except KeyboardInterrupt:
        print("\n\n正在停止服务器...")
        backend_process.terminate()
        backend_process.wait()
        print("服务器已停止")

if __name__ == "__main__":
    main()
