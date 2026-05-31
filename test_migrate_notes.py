"""测试 migrate_notes.py 的逻辑 - 使用 Mock 数据"""
import sqlite3
import os
from datetime import datetime


def create_test_database():
    """创建测试数据库和表结构"""
    # 使用测试数据库文件
    test_db = 'test_xiaohongshu.db'
    
    # 如果已存在，先删除
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"已删除旧的测试数据库: {test_db}")
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # 创建 comments_analysis 表
    cursor.execute('''
        CREATE TABLE comments_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT,
            comment_text TEXT,
            comment_user TEXT,
            comment_time TEXT,
            sentiment TEXT,
            sentiment_score REAL,
            note_id TEXT,
            note_title TEXT,
            blogger_id TEXT,
            note_publish_time TEXT,
            created_at TEXT
        )
    ''')
    print("✅ 创建 comments_analysis 表")
    
    # 创建 notes 表
    cursor.execute('''
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE,
            note_title TEXT,
            note_url TEXT,
            blogger_id TEXT,
            publish_time TEXT,
            analyze_time TEXT,
            created_at TEXT
        )
    ''')
    print("✅ 创建 notes 表")
    
    conn.commit()
    conn.close()
    
    return test_db


def insert_mock_data(db_path):
    """插入 Mock 测试数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Mock 数据 - 模拟评论分析表中的数据
    mock_comments = [
        # 笔记1的评论（3条评论，同一个笔记）
        ('c001', '这个产品太棒了！推荐购买', 'user_张三', '2024-01-15 10:30:00', 'positive', 0.85, 'note_001', '我的护肤心得分享', 'blogger_A', '2024-01-10 09:00:00'),
        ('c002', '价格有点贵，但质量不错', 'user_李四', '2024-01-15 11:20:00', 'neutral', 0.10, 'note_001', '我的护肤心得分享', 'blogger_A', '2024-01-10 09:00:00'),
        ('c003', '物流很快，包装精美', 'user_王五', '2024-01-15 14:30:00', 'positive', 0.75, 'note_001', '我的护肤心得分享', 'blogger_A', '2024-01-10 09:00:00'),
        
        # 笔记2的评论（2条评论）
        ('c004', '踩雷了，不推荐', 'user_赵六', '2024-01-16 09:00:00', 'negative', -0.65, 'note_002', '购物避坑指南', 'blogger_B', '2024-01-12 15:00:00'),
        ('c005', '谢谢分享，很有帮助', 'user_孙七', '2024-01-16 10:30:00', 'positive', 0.70, 'note_002', '购物避坑指南', 'blogger_B', '2024-01-12 15:00:00'),
        
        # 笔记3的评论（4条评论）
        ('c006', '颜值很高，很喜欢', 'user_周八', '2024-01-17 08:00:00', 'positive', 0.90, 'note_003', '新年穿搭推荐', 'blogger_C', '2024-01-14 12:00:00'),
        ('c007', '配色很棒', 'user_吴九', '2024-01-17 09:30:00', 'positive', 0.80, 'note_003', '新年穿搭推荐', 'blogger_C', '2024-01-14 12:00:00'),
        ('c008', '价格实惠', 'user_郑十', '2024-01-17 11:00:00', 'neutral', 0.05, 'note_003', '新年穿搭推荐', 'blogger_C', '2024-01-14 12:00:00'),
        ('c009', '已下单，期待收货', 'user_钱一', '2024-01-17 14:00:00', 'positive', 0.75, 'note_003', '新年穿搭推荐', 'blogger_C', '2024-01-14 12:00:00'),
        
        # 笔记4（只有1条评论）
        ('c010', '学习了，感谢博主', 'user_陈二', '2024-01-18 10:00:00', 'positive', 0.85, 'note_004', 'Python入门教程', 'blogger_D', '2024-01-16 08:00:00'),
        
        # 空笔记ID的评论（应该被过滤）
        ('c011', '测试评论', 'user_测试', '2024-01-18 11:00:00', 'neutral', 0.0, None, None, 'blogger_E', '2024-01-17 10:00:00'),
        ('c012', '空笔记测试', 'user_测试2', '2024-01-18 12:00:00', 'neutral', 0.0, '', '', 'blogger_F', '2024-01-17 11:00:00'),
        
        # 笔记5（测试重复插入）
        ('c013', '第一次评论', 'user_甲', '2024-01-19 09:00:00', 'positive', 0.80, 'note_005', '美食探店记录', 'blogger_G', '2024-01-18 10:00:00'),
        ('c014', '第二次评论', 'user_乙', '2024-01-19 10:00:00', 'positive', 0.75, 'note_005', '美食探店记录', 'blogger_G', '2024-01-18 10:00:00'),
    ]
    
    # 插入 mock 数据
    for comment in mock_comments:
        cursor.execute('''
            INSERT INTO comments_analysis 
            (comment_id, comment_text, comment_user, comment_time, sentiment, sentiment_score, 
             note_id, note_title, blogger_id, note_publish_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*comment, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    
    # 统计插入的数据
    cursor.execute('SELECT COUNT(*) FROM comments_analysis')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT note_id) FROM comments_analysis WHERE note_id IS NOT NULL AND note_id != ""')
    distinct_notes = cursor.fetchone()[0]
    
    print(f"\n✅ 插入 Mock 数据完成:")
    print(f"   - 总评论数: {total}")
    print(f"   - 唯一笔记数: {distinct_notes}")
    
    conn.close()


def run_migration_test(db_path):
    """运行迁移逻辑测试"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("开始执行迁移逻辑测试")
    print("="*60)
    
    try:
        # 1. 从 comments_analysis 表提取唯一的笔记信息
        print("\n步骤1: 提取笔记信息...")
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
        
        # 显示提取的笔记
        print("\n提取的笔记列表:")
        for note in notes_data:
            print(f"  - note_id: {note[0]}, title: {note[1]}, blogger: {note[2]}")
        
        # 2. 插入到 notes 表
        print("\n步骤2: 插入到 notes 表...")
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
                '',
                blogger_id or '',
                publish_time,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            inserted_count += 1
        
        print(f"✅ 成功插入 {inserted_count} 条笔记")
        print(f"✅ 跳过 {skipped_count} 条已存在的笔记")
        
        # 3. 验证数据完整性
        print("\n步骤3: 验证数据完整性...")
        cursor.execute('SELECT COUNT(*) FROM notes')
        notes_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT note_id) FROM comments_analysis WHERE note_id IS NOT NULL AND note_id != ""')
        distinct_notes_in_comments = cursor.fetchone()[0]
        
        print(f"notes 表记录数: {notes_count}")
        print(f"comments_analysis 中唯一笔记数: {distinct_notes_in_comments}")
        
        if notes_count == distinct_notes_in_comments:
            print("✅ 数据完整性验证通过！")
        else:
            print("⚠️ 数据数量不一致，请检查")
        
        # 4. 提交事务
        conn.commit()
        print("\n✅ 数据迁移完成！")
        
        # 5. 显示迁移后的数据
        print("\n步骤4: 查看迁移结果...")
        cursor.execute('SELECT note_id, note_title, blogger_id, publish_time FROM notes')
        print("\nnotes 表中的所有记录:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (博主: {row[2]}, 发布: {row[3]})")
        
        # 6. 测试重复运行迁移（应该跳过所有）
        print("\n步骤5: 测试重复运行迁移...")
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
        repeat_inserted = 0
        repeat_skipped = 0
        
        for note in notes_data:
            note_id, note_title, blogger_id, publish_time = note
            cursor.execute('SELECT id FROM notes WHERE note_id = ?', (note_id,))
            if cursor.fetchone():
                repeat_skipped += 1
                continue
            repeat_inserted += 1
        
        print(f"重复运行结果: 插入 {repeat_inserted} 条, 跳过 {repeat_skipped} 条")
        if repeat_inserted == 0 and repeat_skipped == len(notes_data):
            print("✅ 重复运行测试通过！所有记录都被正确跳过")
        else:
            print("⚠️ 重复运行测试失败！")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


def cleanup_test(db_path):
    """清理测试数据"""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"\n✅ 已清理测试数据库: {db_path}")


if __name__ == '__main__':
    print("="*60)
    print("migrate_notes.py 逻辑测试")
    print("="*60)
    
    # 1. 创建测试数据库
    test_db = create_test_database()
    
    # 2. 插入 mock 数据
    insert_mock_data(test_db)
    
    # 3. 运行迁移测试
    run_migration_test(test_db)
    
    # 4. 询问是否清理
    print("\n" + "="*60)
    user_input = input("是否清理测试数据库？(y/n): ").strip().lower()
    if user_input == 'y':
        cleanup_test(test_db)
    else:
        print(f"测试数据库保留在: {test_db}")
        print("您可以手动查看或删除")
    
    print("\n测试完成！")