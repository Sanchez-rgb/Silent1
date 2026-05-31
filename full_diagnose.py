
# 完整的诊断脚本 - 无emoji版本
import sys
import traceback

print("=" * 60)
print("诊断 - 步骤1: 检查Python环境")
print("=" * 60)
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")

try:
    print("\n诊断 - 步骤2: 检查依赖")
    import fastapi
    print(f"FastAPI: {fastapi.__version__}")
    
    import uvicorn
    print(f"Uvicorn: {uvicorn.__version__}")
    
    import pydantic
    print(f"Pydantic: {pydantic.__version__}")
    
    import sqlite3
    print(f"SQLite3: OK")
    
    print("\n[OK] 依赖检查通过")
except Exception as e:
    print(f"[FAIL] 依赖错误: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n" + "=" * 60)
    print("诊断 - 步骤3: 导入main_v2")
    print("=" * 60)
    sys.path.insert(0, 'c:\\Users\\55382\\Documents\\trae_projects\\j')
    from main_v2 import app
    print("[OK] 导入成功")
    print(f"应用对象: {app}")
    print(f"路由数量: {len(app.routes)}")
    
    print("\n路由列表:")
    for route in app.routes:
        print(f"  - {route.path} [{', '.join(route.methods)}]")
        
except Exception as e:
    print(f"[FAIL] 导入错误: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n" + "=" * 60)
    print("诊断 - 步骤4: 测试应用基本功能")
    print("=" * 60)
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    print("\n测试根路径 /")
    response = client.get("/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    print("\n测试健康检查 /health")
    response = client.get("/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    print("\n[OK] 应用测试通过")
    
except Exception as e:
    print(f"[FAIL] 测试错误: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成！")
print("=" * 60)
