import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

cursor.execute('''
    UPDATE followed_blogs
    SET last_check_time = '2024-01-01 00:00:00'
''')

conn.commit()
print("已重置所有博主的最后检查时间")

cursor.execute('SELECT blogger_id, blogger_name, last_check_time FROM followed_blogs')
print("当前博主状态:")
for row in cursor.fetchall():
    print(row)

conn.close()

print("\n现在运行 final_scheduler.py 进行测试...")
