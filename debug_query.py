import sqlite3

def test_note_stats():
    conn = sqlite3.connect('xiaohongshu.db')
    cursor = conn.cursor()
    
    print("测试查询...")
    try:
        cursor.execute('''
            SELECT 
                ca.note_id,
                COALESCE(n.note_title, ca.note_title) as note_title,
                COALESCE(n.note_url, '') as note_url,
                COALESCE(n.blogger_id, ca.blogger_id) as blogger_id,
                SUM(CASE WHEN ca.sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN ca.sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_count,
                SUM(CASE WHEN ca.sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
                COUNT(*) as total_count
            FROM comments_analysis ca
            LEFT JOIN notes n ON ca.note_id = n.note_id
            WHERE ca.note_id IS NOT NULL AND ca.note_id != ''
            GROUP BY ca.note_id, note_title, note_url, blogger_id
            ORDER BY total_count DESC
        ''')
        
        rows = cursor.fetchall()
        print(f"查询成功，得到 {len(rows)} 条记录")
        
        for row in rows[:3]:  # 只显示前3条
            print(f"  note_id: {row[0]}, title: {row[1]}")
            print(f"    positive: {row[4]}, neutral: {row[5]}, negative: {row[6]}, total: {row[7]}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    test_note_stats()
