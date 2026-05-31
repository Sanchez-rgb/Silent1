
import requests
import json
import os

BASE = "http://localhost:8000"

# First, let's clean any old data and register a fresh user with the correct blogger ID
# First delete the test user if exists
import sqlite3
conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM users WHERE username = 'testuser'")
conn.commit()
conn.close()

# Register fresh
r = requests.post(f"{BASE}/register", json={
    "username": "testuser",
    "password": "test123456",
    "blogger_id": "blogger_001"
})

# Login
r = requests.post(f"{BASE}/login", data={
    "username": "testuser",
    "password": "test123456"
})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Run analyze_all_notes first to create reports
# Let's modify main_v2 to add a helper function
# But wait, let's test dashboard first
r = requests.get(f"{BASE}/dashboard", headers=headers)
with open("dashboard_result.json", "w", encoding="utf-8") as f:
    json.dump(r.json(), f, ensure_ascii=False, indent=2)

# Now let's write a script to run analyze_all_notes directly
with open("run_analysis.py", "w", encoding="utf-8") as f:
    f.write('''
import sqlite3
import json
from snownlp import SnowNLP

def analyze_sentiment_snownlp(text):
    try:
        s = SnowNLP(text)
        sentiment = s.sentiments
        if sentiment > 0.6:
            return "positive", sentiment
        elif sentiment < 0.4:
            return "negative", sentiment
        else:
            return "neutral", sentiment
    except:
        return "neutral", 0.5

conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

# Get all notes for blogger_001
cursor.execute("SELECT note_id, note_title FROM notes WHERE blogger_id = ?", ("blogger_001",))
notes = cursor.fetchall()
print(f"Found {len(notes)} notes")

for note in notes:
    note_id = note[0]
    print(f"Processing note {note_id}")
    
    # Get comments
    cursor.execute("SELECT id, comment_text, sentiment, confidence FROM comments WHERE note_id = ?", (note_id,))
    comments = cursor.fetchall()
    
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    sentiment_scores = []
    negative_comments = []
    
    for comment in comments:
        c_id, text, old_sent, old_conf = comment
        sentiment, confidence = analyze_sentiment_snownlp(text)
        
        if sentiment == "positive":
            positive_count += 1
        elif sentiment == "negative":
            negative_count += 1
            negative_comments.append({
                "comment_id": str(c_id),
                "comment_text": text,
                "confidence": confidence
            })
        else:
            neutral_count += 1
        
        score = confidence if sentiment == "positive" else -confidence if sentiment == "negative" else 0
        sentiment_scores.append(score)
    
    avg_sentiment_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    top_negative = sorted(negative_comments, key=lambda x: -x["confidence"])[:5]
    top_negative_json = json.dumps(top_negative, ensure_ascii=False)
    
    if avg_sentiment_score > 0.3:
        rating = "优秀"
    elif avg_sentiment_score > 0:
        rating = "良好"
    elif avg_sentiment_score > -0.3:
        rating = "预警"
    else:
        rating = "危险"
    
    # Delete old report
    cursor.execute("DELETE FROM note_reports WHERE note_id = ?", (note_id,))
    
    # Insert new report
    cursor.execute('''
        INSERT INTO note_reports 
        (note_id, sentiment_score, positive_count, neutral_count, negative_count, top_negative_comments, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (note_id, avg_sentiment_score, positive_count, neutral_count, negative_count, top_negative_json, rating))
    
    print(f"  Added report for note {note_id}")

conn.commit()
conn.close()
print("Analysis complete!")
''')

# Run analysis
import subprocess
result = subprocess.run(["python", "run_analysis.py"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# Now test dashboard again
r = requests.get(f"{BASE}/dashboard", headers=headers)
with open("dashboard_final.json", "w", encoding="utf-8") as f:
    json.dump(r.json(), f, ensure_ascii=False, indent=2)

print("\n=== FINAL DASHBOARD ===")
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
