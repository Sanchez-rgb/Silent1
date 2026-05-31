import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduled_task import run_task

print("测试定时任务...")
run_task()
