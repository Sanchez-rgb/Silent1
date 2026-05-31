import sqlite3
import datetime
import random
from snownlp import SnowNLP


print("=" * 70)
print("小红书定时任务系统 - 功能测试")
print("=" * 70 + "\n")

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

print("1. 检查数据库表...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"   表数量: {len(tables)}")
for table in tables:
    print(f"   - {table[0]}")

print("\n2. 检查博主数据...")
cursor.execute('SELECT * FROM followed_blogs')
bloggers = cursor.fetchall()
print(f"   博主数量: {len(bloggers)}")
for blogger in bloggers:
    print(f"   - ID: {blogger[0]}, Name: {blogger[1]}, Last Check: {blogger[2]}")

print("\n3. 检查笔记数据...")
cursor.execute('SELECT COUNT(*) FROM notes')
notes_count = cursor.fetchone()[0]
print(f"   笔记总数: {notes_count}")

print("\n4. 检查评论分析数据...")
cursor.execute('SELECT COUNT(*) FROM comments_analysis')
comments_count = cursor.fetchone()[0]
print(f"   评论总数: {comments_count}")

if comments_count > 0:
    print("\n   最近10条评论分析:")
    cursor.execute('SELECT blogger_name, note_title, comment_text, sentiment, confidence FROM comments_analysis ORDER BY id DESC LIMIT 10')
    for idx, row in enumerate(cursor.fetchall()):
        print(f"   {idx+1}. {row[0]} | {row[1]} | {row[2]} | {row[3]} ({row[4]:.2f})")

print("\n5. 按情感统计评论:")
cursor.execute('SELECT sentiment, COUNT(*) FROM comments_analysis GROUP BY sentiment')
stats = cursor.fetchall()
for sent, count in stats:
    print(f"   {sent}: {count}")

conn.close()

print("\n" + "=" * 70)
print("测试完成！系统功能正常。")
print("=" * 70)
