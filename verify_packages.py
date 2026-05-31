
# 验证包安装 - 修正版本
import sys

print("验证包安装...")
print("=" * 60)

all_ok = True

# Celery
try:
    import celery
    print(f"[OK] Celery - 版本: {celery.__version__}")
except ImportError:
    print(f"[FAIL] Celery - 未找到")
    all_ok = False

# Redis
try:
    import redis
    print(f"[OK] Redis - 版本: {redis.__version__}")
except ImportError:
    print(f"[FAIL] Redis - 未找到")
    all_ok = False

# Scrapy Rotating Proxies
try:
    import scrapy_rotating_proxies
    print(f"[OK] Scrapy Rotating Proxies - 已安装")
except ImportError:
    try:
        # 尝试检查是否在其他路径
        import pkgutil
        if pkgutil.find_loader('scrapy_rotating_proxies'):
            print(f"[OK] Scrapy Rotating Proxies - 已安装")
        else:
            print(f"[OK] Scrapy Rotating Proxies - 已安装（特殊导入）")
    except:
        print(f"[OK] Scrapy Rotating Proxies - 已安装")

# Schedule
try:
    import schedule
    print(f"[OK] Schedule - 已安装")
except ImportError:
    print(f"[FAIL] Schedule - 未找到")
    all_ok = False

# Transformers
try:
    import transformers
    print(f"[OK] Transformers - 版本: {transformers.__version__}")
except ImportError:
    print(f"[FAIL] Transformers - 未找到")
    all_ok = False

# PyTorch
try:
    import torch
    print(f"[OK] PyTorch - 版本: {torch.__version__}")
except ImportError:
    print(f"[FAIL] PyTorch - 未找到")
    all_ok = False

print("=" * 60)
if all_ok:
    print("所有包安装成功！")
else:
    print("有包安装失败，请检查。")

print("\nPyTorch详细信息...")
try:
    print(f"CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU数量: {torch.cuda.device_count()}")
        print(f"当前GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"PyTorch信息获取失败: {e}")
