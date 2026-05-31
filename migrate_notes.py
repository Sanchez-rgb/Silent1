import sqlite3
from datetime import datetime

def migrate_notes():
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    
    try:
        # 1. 从 comments_analysis 表提取唯一的笔记信息
        print("正在提取笔记信息...")
        cursor.execute('''
            SELECT DISTINCT 
                note_id,
                note_title,
                blogger_id,
                note_publish_time
            FROM comments_analysis
            WHERE note_id IS NOT NULL AND note_id != ''
        ''')
        
        notes_data = cursor.fetchall()
        print(f"找到 {len(notes_data)} 条唯一笔记记录")
        
        # 2. 插入到 notes 表
        print("\n正在插入到 notes 表...")
        inserted_count = 0
        skipped_count = 0
        
        for note in notes_data:
            note_id, note_title, blogger_id, publish_time = note
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM notes WHERE note_id = ?', (note_id,))
            if cursor.fetchone():
                skipped_count += 1
                continue
            
            # 插入新记录
            cursor.execute('''
                INSERT INTO notes 
                (note_id, note_title, note_url, blogger_id, publish_time, analyze_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_id,
                note_title or '',
                '',  # note_url 暂时为空
                blogger_id or '',
                publish_time,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            inserted_count += 1
        
        print(f"[OK] 成功插入 {inserted_count} 条笔记")
        print(f"[OK] 跳过 {skipped_count} 条已存在的笔记")
        
        # 3. 验证数据并更新（其实 note_id 已经在 comments_analysis 表里了）
        print("\n正在验证数据完整性...")
        cursor.execute('SELECT COUNT(*) FROM notes')
        notes_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT note_id) FROM comments_analysis WHERE note_id IS NOT NULL AND note_id != ""')
        distinct_notes_in_comments = cursor.fetchone()[0]
        
        print(f"notes 表记录数: {notes_count}")
        print(f"comments_analysis 中唯一笔记数: {distinct_notes_in_comments}")
        
        # 4. 提交事务
        conn.commit()
        print("\n[OK] 数据迁移完成！")
        
        # 5. 显示一些示例数据
        print("\n=== 前 5 条笔记示例 ===")
        cursor.execute('SELECT note_id, note_title, blogger_id FROM notes LIMIT 5')
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (博主: {row[2]})")
        
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_notes()
