import sqlite3
import datetime

def init_database():
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()

    # 创建 followed_blogs 表 - 关注的博主
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS followed_blogs (
            blogger_id TEXT PRIMARY KEY,
            blogger_name TEXT NOT NULL,
            last_check_time DATETIME DEFAULT '2000-01-01 00:00:00',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建 comments_analysis 表 - 评论分析结果
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blogger_id TEXT NOT NULL,
            blogger_name TEXT NOT NULL,
            note_id TEXT NOT NULL,
            note_title TEXT,
            note_publish_time DATETIME,
            comment_id TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blogger_id) REFERENCES followed_blogs (blogger_id)
        )
    ''')

    # 创建 notes 表 - 笔记信息
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            blogger_id TEXT NOT NULL,
            blogger_name TEXT NOT NULL,
            title TEXT,
            content TEXT,
            publish_time DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blogger_id) REFERENCES followed_blogs (blogger_id)
        )
    ''')

    # 插入一些示例博主数据（如果不存在）
    sample_bloggers = [
        ('blogger_001', '时尚达人小美', '2024-01-01 00:00:00'),
        ('blogger_002', '美食探店家', '2024-01-01 00:00:00'),
        ('blogger_003', '旅行日记', '2024-01-01 00:00:00')
    ]

    for blogger_id, name, check_time in sample_bloggers:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO followed_blogs (blogger_id, blogger_name, last_check_time)
                VALUES (?, ?, ?)
            ''', (blogger_id, name, check_time))
        except Exception as e:
            pass

    conn.commit()
    conn.close()
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_database()
