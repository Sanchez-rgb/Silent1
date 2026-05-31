import sqlite3
import datetime

def update_database_structure():
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("开始更新数据库结构...")
    print("=" * 60 + "\n")
    
    # 1. 创建新的 notes 表
    print("1. 创建 notes 表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            note_title TEXT,
            note_url TEXT,
            blogger_id TEXT NOT NULL,
            publish_time DATETIME,
            analyze_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("   notes 表已创建\n")
    
    # 2. 检查 comments_analysis 表是否有 note_id 字段
    print("2. 更新 comments_analysis 表...")
    cursor.execute("PRAGMA table_info(comments_analysis)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'note_id' not in columns:
        print("   增加 note_id 字段...")
        cursor.execute('ALTER TABLE comments_analysis ADD COLUMN note_id TEXT')
        print("   note_id 字段已添加")
    else:
        print("   note_id 字段已存在，跳过")
    
    print()
    
    # 3. 检查表结构
    print("3. 验证表结构...")
    
    # 检查 notes 表
    cursor.execute("PRAGMA table_info(notes)")
    notes_columns = cursor.fetchall()
    print("\n   notes 表字段：")
    for col in notes_columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 检查 comments_analysis 表
    cursor.execute("PRAGMA table_info(comments_analysis)")
    comments_columns = cursor.fetchall()
    print("\n   comments_analysis 表字段：")
    for col in comments_columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 4. 为现有数据填充 note_id（如果有）
    print("\n4. 检查现有数据...")
    cursor.execute("SELECT COUNT(*) FROM notes")
    notes_count = cursor.fetchone()[0]
    print(f"   notes 表现有记录数: {notes_count}")
    
    cursor.execute("SELECT COUNT(*) FROM comments_analysis")
    comments_count = cursor.fetchone()[0]
    print(f"   comments_analysis 表现有记录数: {comments_count}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("数据库结构更新完成！")
    print("=" * 60)

if __name__ == "__main__":
    update_database_structure()
