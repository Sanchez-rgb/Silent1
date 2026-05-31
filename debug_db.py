import sqlite3
import json

# Test database operations
conn = sqlite3.connect('xiaohongshu.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Testing database...")

# Check users table
try:
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(f"Users in DB: {len(users)}")
    for u in users:
        print(f"  {dict(u)}")
except Exception as e:
    print(f"Users table error: {e}")
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            blogger_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_analysis_time DATETIME
        )
    ''')
    print("Created users table")

# Try inserting a test user
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("test123456")
    print(f"Generated hash: {hashed}")
    
    cursor.execute('''
        INSERT OR REPLACE INTO users (username, password, blogger_id)
        VALUES (?, ?, ?)
    ''', ("testuser", hashed, "blogger_test_123"))
    conn.commit()
    print("Inserted test user")
except Exception as e:
    print(f"Insert error: {e}")
    import traceback
    traceback.print_exc()

# Verify
cursor.execute("SELECT * FROM users WHERE username = ?", ("testuser",))
user = cursor.fetchone()
if user:
    print(f"User found: {dict(user)}")

conn.close()
print("Done!")
