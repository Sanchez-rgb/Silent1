
import sys
sys.path.insert(0, 'c:\\Users\\55382\\Documents\\trae_projects\\j')

# 导入应用
from main_v2 import app
import uvicorn
import threading
import time
import requests

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

# 启动服务
print("启动服务...")
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# 等待服务启动
time.sleep(5)

# 测试访问
print("\n测试服务...")
try:
    # 测试根路径
    r = requests.get("http://127.0.0.1:8000/", timeout=5)
    print(f"根路径 - 状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"响应: {r.json()}")
    
    # 测试健康检查
    r = requests.get("http://127.0.0.1:8000/health", timeout=5)
    print(f"\n健康检查 - 状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"响应: {r.json()}")
    
    print("\n✅ 服务运行正常！")
    print(f"\n📱 API文档: http://127.0.0.1:8000/docs")
    print(f"🔗 首页: http://127.0.0.1:8000/")
    print(f"\n按 Ctrl+C 停止服务")
    
    # 保持运行
    while True:
        time.sleep(1)
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
