
import sqlite3

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

# Update the test user to use blogger_001
cursor.execute("UPDATE users SET blogger_id = ? WHERE username = ?", ("blogger_001", "testuser"))
conn.commit()

# Verify
cursor.execute("SELECT * FROM users WHERE username = ?", ("testuser",))
user = cursor.fetchone()
print("Updated user:")
print(user)

conn.close()
