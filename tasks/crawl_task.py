
# 爬虫异步任务
from celery_app import celery_app, TASK_STATUS_RUNNING, TASK_STATUS_COMPLETED, TASK_STATUS_FAILED
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import CrawlTask, Note, Comment
from crawler.xiaohongshu import XiaohongshuCrawler
from datetime import datetime
import traceback


def update_task_progress(task_id: str, current: int, total: int):
    """更新任务进度"""
    db = SessionLocal()
    try:
        task = db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
        if task:
            task.current_note = current
            task.total_notes = total
            db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_blogger_all_notes(self, user_id: int, blogger_id: str, xhs_cookie: str = None):
    """
    爬取博主所有笔记的Celery任务
    支持断点续爬，被反爬时自动重试
    """
    task_id = self.request.id
    db = SessionLocal()
    
    try:
        # 检查或创建任务记录
        crawl_task = db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
        if not crawl_task:
            crawl_task = CrawlTask(
                user_id=user_id,
                task_id=task_id,
                status=TASK_STATUS_RUNNING,
                total_notes=0,
                current_note=0
            )
            db.add(crawl_task)
            db.commit()
        else:
            # 断点续爬 - 从上次位置继续
            crawl_task.status = TASK_STATUS_RUNNING
            db.commit()
        
        start_index = crawl_task.current_note
        
        # 创建爬虫
        crawler = XiaohongshuCrawler(xhs_cookie)
        
        # 爬取笔记
        print(f"开始爬取博主 {blogger_id} 的笔记，从索引 {start_index} 开始")
        notes = crawler.crawl_notes(blogger_id, start_index)
        
        if not notes:
            crawl_task.status = TASK_STATUS_COMPLETED
            db.commit()
            return {"status": "completed", "total_notes": 0}
        
        total_notes = start_index + len(notes)
        current = start_index
        
        # 保存笔记和评论
        for i, note_data in enumerate(notes):
            try:
                current = start_index + i + 1
                
                # 检查笔记是否已存在
                existing_note = db.query(Note).filter(Note.note_id == note_data["note_id"]).first()
                if existing_note:
                    continue
                
                # 保存笔记
                note = Note(
                    note_id=note_data["note_id"],
                    note_title=note_data["note_title"],
                    note_url=note_data["note_url"],
                    blogger_id=note_data["blogger_id"],
                    publish_time=datetime.fromisoformat(note_data["publish_time"].replace('Z', '+00:00')),
                    like_count=note_data["like_count"],
                    comment_count=note_data["comment_count"],
                    task_id=crawl_task.id,
                    user_id=user_id
                )
                db.add(note)
                
                # 爬取评论
                comments = crawler.crawl_comments(note_data["note_id"])
                for comment_data in comments:
                    comment = Comment(
                        note_id=comment_data["note_id"],
                        comment_id=comment_data["comment_id"],
                        comment_text=comment_data["comment_text"],
                        is_analyzed=False
                    )
                    db.add(comment)
                
                # 每10篇更新进度
                if (i + 1) % 10 == 0:
                    update_task_progress(task_id, current, total_notes)
                    db.commit()
                
            except Exception as e:
                print(f"处理笔记 {note_data['note_id']} 时出错: {e}")
                continue
        
        # 提交剩余数据
        db.commit()
        
        # 更新任务状态
        crawl_task.status = TASK_STATUS_COMPLETED
        crawl_task.current_note = current
        crawl_task.total_notes = total_notes
        db.commit()
        
        return {
            "status": "completed",
            "total_notes": total_notes,
            "start_index": start_index,
            "processed_notes": current - start_index
        }
        
    except Exception as e:
        print(f"爬虫任务出错: {e}")
        print(traceback.format_exc())
        
        # 检查是否应该重试
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            # 重试次数用尽，标记为失败
            crawl_task = db.query(CrawlTask).filter(CrawlTask.task_id == task_id).first()
            if crawl_task:
                crawl_task.status = TASK_STATUS_FAILED
                crawl_task.error_message = str(e)
                db.commit()
            return {"status": "failed", "error": str(e)}
    finally:
        db.close()
