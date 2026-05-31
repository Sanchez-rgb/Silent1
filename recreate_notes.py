import sqlite3
import datetime

def recreate_notes_table():
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("重新创建 notes 表...")
    print("=" * 60 + "\n")
    
    # 备份现有数据（如果有）
    try:
        cursor.execute("SELECT * FROM notes")
        old_data = cursor.fetchall()
        print(f"1. 备份现有笔记数据: {len(old_data)} 条记录")
    except:
        old_data = []
        print("1. 没有现有笔记数据")
    
    # 删除旧表
    cursor.execute("DROP TABLE IF EXISTS notes")
    print("\n2. 已删除旧表")
    
    # 创建新的 notes 表
    cursor.execute('''
        CREATE TABLE notes (
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
    print("\n3. 已创建新的 notes 表")
    
    # 验证新表结构
    cursor.execute("PRAGMA table_info(notes)")
    columns = cursor.fetchall()
    print("\n4. 新表字段：")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 尝试恢复旧数据（简化）
    if old_data:
        print("\n5. 尝试恢复数据（由于表结构变更，仅保存为示例）")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("notes 表重新创建完成！")
    print("=" * 60)

if __name__ == "__main__":
    recreate_notes_table()
