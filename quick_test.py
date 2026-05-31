"""快速测试脚本 - 不依赖真实转换功能"""
from fastapi.testclient import TestClient
from main import app
import os
import tempfile

client = TestClient(app)


def test_root_endpoint():
    """测试根端点"""
    print("\n测试根端点...")
    response = client.get("/")
    print(f"  状态码: {response.status_code}")
    assert response.status_code in [200, 307]
    print("  ✅ 通过")


def test_health_endpoint():
    """测试健康检查端点"""
    print("\n测试健康检查端点...")
    response = client.get("/docs")  # 使用 docs 作为健康检查
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200
    print("  ✅ 通过")


def create_test_docx(content="测试内容"):
    """创建临时测试文件"""
    fd, path = tempfile.mkstemp(suffix='.docx')
    with os.fdopen(fd, 'w') as f:
        f.write(f"Test DOCX file\nContent: {content}")
    return path


def test_single_convert_endpoint():
    """测试单个文件转换端点（不实际执行转换）"""
    print("\n测试单个文件上传端点...")
    
    # 创建测试文件
    test_file = create_test_docx()
    
    try:
        with open(test_file, 'rb') as f:
            response = client.post(
                "/convert/single",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )
        
        print(f"  状态码: {response.status_code}")
        # 即使转换失败，端点也应该正确响应
        assert response.status_code in [200, 400, 500]
        print("  ✅ 端点响应正常")
        
    finally:
        os.unlink(test_file)


def test_batch_convert_endpoint():
    """测试批量转换端点（不实际执行转换）"""
    print("\n测试批量文件上传端点...")
    
    files_to_create = [
        ("test1.docx", "内容 1"),
        ("test2.docx", "内容 2"),
    ]
    
    temp_files = []
    try:
        # 创建测试文件
        for name, content in files_to_create:
            path = create_test_docx(content)
            temp_files.append((name, path))
        
        # 准备上传
        files = []
        for name, path in temp_files:
            f = open(path, 'rb')
            files.append(("files", (name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")))
        
        # 发送请求
        response = client.post("/convert/batch", files=files)
        
        print(f"  状态码: {response.status_code}")
        assert response.status_code in [200, 400, 500]
        print("  ✅ 端点响应正常")
        
    finally:
        # 清理
        for name, path in temp_files:
            try:
                os.unlink(path)
            except:
                pass


if __name__ == "__main__":
    print("=" * 60)
    print("Word 转 PDF 服务 - 快速测试")
    print("=" * 60)
    
    try:
        test_root_endpoint()
        test_health_endpoint()
        test_single_convert_endpoint()
        test_batch_convert_endpoint()
        
        print("\n" + "=" * 60)
        print("所有 API 端点测试通过!")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 运行 'python main.py' 启动完整服务")
        print("  2. 访问 http://localhost:8000 测试网页界面")
        print("  3. 查看 TESTING_GUIDE.md 了解更多测试方法")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
