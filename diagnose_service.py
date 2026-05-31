"""诊断服务问题"""
import sys
import os

print("="*60)
print("服务诊断工具")
print("="*60)

# 检查 Python 版本
print(f"\n1. Python 版本: {sys.version}")

# 检查依赖
print("\n2. 检查依赖...")
dependencies = [
    'fastapi',
    'uvicorn',
    'docx2pdf',
]

for dep in dependencies:
    try:
        __import__(dep.replace('-', '_'))
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - 未安装")

# 检查关键文件
print("\n3. 检查关键文件...")
key_files = [
    'main.py',
    'converter.py',
    'index.html',
    'requirements.txt',
]

for f in key_files:
    if os.path.exists(f):
        print(f"   ✅ {f} ({os.path.getsize(f)} bytes)")
    else:
        print(f"   ❌ {f} - 不存在")

# 检查测试文件
print("\n4. 检查测试文件...")
test_dir = 'test_data'
if os.path.exists(test_dir):
    files = os.listdir(test_dir)
    print(f"   📁 {test_dir}/: {files}")
else:
    print(f"   ❌ {test_dir}/ - 不存在")

# 尝试导入主应用
print("\n5. 尝试导入应用...")
try:
    from main import app
    print("   ✅ 应用导入成功")
    
    # 检查路由
    print("\n6. 检查路由...")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = ','.join(route.methods) if hasattr(route, 'methods') else 'N/A'
            print(f"   {methods:15} {route.path}")
            
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("诊断完成")
print("="*60)
print("\n建议:")
print("  1. 如果缺少依赖: pip install -r requirements.txt")
print("  2. 启动服务: python main.py")
print("  3. 访问: http://localhost:8000")
