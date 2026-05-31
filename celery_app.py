
# Celery应用配置
import os
from celery import Celery
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Celery实例
celery_app = Celery(
    'xiaohongshu_analysis',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 任务超时时间1小时
    task_soft_time_limit=3000,  # 软超时时间
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# 自动发现任务
celery_app.autodiscover_tasks(['tasks'])

# 任务状态常量
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_RUNNING = 'running'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_FAILED = 'failed'

if __name__ == '__main__':
    celery_app.start()
