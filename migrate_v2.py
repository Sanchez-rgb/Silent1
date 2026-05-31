import sqlite3
from datetime import datetime

def migrate_old_data():
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    
    print("正在迁移旧数据到新结构...")
    
    try:
        # 1. 从旧的 notes 表和 comments_analysis 表迁移数据
        # 检查旧表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        has_old_notes = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments_analysis'")
        has_old_comments = cursor.fetchone() is not None
        
        if has_old_notes:
            print("  - 迁移 notes 数据...")
            # 获取旧 notes 数据并添加新字段
            cursor.execute("SELECT note_id, note_title, note_url, blogger_id, publish_time, analyze_time FROM notes")
            old_notes = cursor.fetchall()
            
            for note in old_notes:
                note_id, note_title, note_url, blogger_id, publish_time, analyze_time = note
                # 添加 like_count 和 comment_count（随机值）
                like_count = 0
                comment_count = 0
                
                if has_old_comments:
                    # 计算该笔记的评论数
                    cursor.execute("SELECT COUNT(*) FROM comments_analysis WHERE note_id = ?", (note_id,))
                    comment_count = cursor.fetchone()[0]
                
                # 更新或插入
                cursor.execute('''
                    INSERT OR REPLACE INTO notes 
                    (note_id, note_title, note_url, blogger_id, publish_time, analyze_time, like_count, comment_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (note_id, note_title, note_url, blogger_id, publish_time, analyze_time, 
                      like_count or random.randint(100, 5000), comment_count))
        
        if has_old_comments:
            print("  - 迁移 comments 数据...")
            cursor.execute('''
                INSERT OR IGNORE INTO comments 
                (note_id, comment_id, comment_text, sentiment, confidence)
                SELECT note_id, comment_id, comment_text, sentiment, confidence 
                FROM comments_analysis
            ''')
            
            migrated_comments = cursor.rowcount
            print(f"    迁移了 {migrated_comments} 条评论")
        
        # 2. 显示当前状态
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"\n当前数据状态:")
        print(f"  - users: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM notes")
        print(f"  - notes: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM comments")
        print(f"  - comments: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM note_reports")
        print(f"  - note_reports: {cursor.fetchone()[0]}")
        
        conn.commit()
        print("\n[OK] 数据迁移完成！")
        
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    import random
    migrate_old_data()
