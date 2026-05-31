import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaohongshu_scheduler import run_task, init_database

print("初始化数据库...")
init_database()

print("\n运行定时任务...")
run_task()
