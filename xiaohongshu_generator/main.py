from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import re
import random
from datetime import datetime, timedelta
import httpx
from contextlib import contextmanager
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(title="小红书AI文案生成器")

DATABASE_DIR = "data"
DATABASE_FILE = os.path.join(DATABASE_DIR, "xiaohongshu.db")
os.makedirs(DATABASE_DIR, exist_ok=True)

PROHIBITED_WORDS = {"最", "第一", "百分百", "绝对", "全网"}

EMOJIS = ["✨", "💕", "🌟", "💖", "🎀", "🌸", "💎", "🎉", "🔥", "💯", "🌈", "🍃", "🍬", "💫", "🎁"]

class GenerateRequest(BaseModel):
    keywords: str
    selling_points: str
    target_audience: str
    tone: str
    api_key: Optional[str] = None

class CheckProhibitedRequest(BaseModel):
    text: str

class OptimizeFormatRequest(BaseModel):
    text: str

class LoginRequest(BaseModel):
    phone: str
    code: str

class SaveHistoryRequest(BaseModel):
    title: str
    content: str
    tags: str

class UserHistory(BaseModel):
    id: int
    title: str
    content: str
    tags: str
    created_at: str

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                is_vip BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

init_db()

def check_prohibited_words(text: str) -> dict:
    found = []
    for word in PROHIBITED_WORDS:
        if word in text:
            found.append(word)
    return {"has_prohibited": len(found) > 0, "words": found}

def optimize_format(text: str) -> str:
    text = re.sub(r'[。！？；]', '。', text)
    sentences = text.split('。')
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            if len(sentence) > 30:
                parts = re.split(r'[,，]', sentence)
                for part in parts:
                    part = part.strip()
                    if part:
                        if random.random() > 0.3:
                            emoji = random.choice(EMOJIS)
                            result.append(f"{part}{emoji}")
                        else:
                            result.append(part)
            else:
                if random.random() > 0.5:
                    emoji = random.choice(EMOJIS)
                    result.append(f"{sentence}{emoji}")
                else:
                    result.append(sentence)
    return '\n\n'.join(result)

async def generate_with_deepseek(prompt: str, api_key: str) -> str:
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的小红书文案写手，擅长创作吸引人的标题和正文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API 调用失败: {str(e)}")

def build_prompt(keywords: str, selling_points: str, target_audience: str, tone: str, version: int) -> str:
    tones = {
        "sweet": "甜美可爱",
        "professional": "专业干货",
        "humorous": "幽默搞笑",
        "emotional": "情感共鸣"
    }
    tone_desc = tones.get(tone, "甜美可爱")
    return f"""请帮我生成一篇小红书风格的文案，包含标题、正文和标签。

产品关键词：{keywords}
卖点：{selling_points}
目标人群：{target_audience}
语气风格：{tone_desc}

要求：
1. 标题要吸引眼球，15-25字
2. 正文300-500字，分段落
3. 标签5-8个，包含热门标签
4. 用{tone_desc}的语气

请按以下格式返回：
标题：[标题内容]
正文：[正文内容]
标签：#[标签1] #[标签2] ...

这是第{version}版，请提供不同的创意角度。"""

def parse_response(response: str) -> dict:
    title = ""
    content = ""
    tags = ""
    
    lines = response.split('\n')
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("标题："):
            title = line.replace("标题：", "").strip()
            current_section = None
        elif line.startswith("正文："):
            current_section = "content"
            content_line = line.replace("正文：", "").strip()
            if content_line:
                content = content_line
        elif line.startswith("标签："):
            tags = line.replace("标签：", "").strip()
            current_section = None
        else:
            # 如果在正文部分，继续追加
            if current_section == "content":
                if content:
                    content += "\n" + line
                else:
                    content = line
    
    return {"title": title, "content": content, "tags": tags}

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    # 从环境变量读取 API Key，不再提供默认值
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="请设置环境变量 DEEPSEEK_API_KEY")
    
    versions = []
    for i in range(1, 4):
        prompt = build_prompt(request.keywords, request.selling_points, request.target_audience, request.tone, i)
        response = await generate_with_deepseek(prompt, api_key)
        parsed = parse_response(response)
        versions.append(parsed)
    return {"versions": versions}

@app.post("/api/check-prohibited")
async def check_prohibited(request: CheckProhibitedRequest):
    return check_prohibited_words(request.text)

@app.post("/api/optimize-format")
async def optimize_format_api(request: OptimizeFormatRequest):
    return {"optimized": optimize_format(request.text)}

@app.post("/api/login")
async def login(request: LoginRequest):
    if request.code != "123456":
        raise HTTPException(status_code=400, detail="验证码错误")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone = ?", (request.phone,))
        user = cursor.fetchone()
        if not user:
            cursor.execute("INSERT INTO users (phone) VALUES (?)", (request.phone,))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE phone = ?", (request.phone,))
            user = cursor.fetchone()
        return {
            "user_id": user["id"],
            "phone": user["phone"],
            "is_vip": bool(user["is_vip"])
        }

@app.post("/api/users/{user_id}/subscribe")
async def subscribe(user_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_vip = 1 WHERE id = ?", (user_id,))
        conn.commit()
        return {"success": True, "is_vip": True}

@app.post("/api/users/{user_id}/history")
async def save_history(user_id: int, request: SaveHistoryRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO histories (user_id, title, content, tags) VALUES (?, ?, ?, ?)",
            (user_id, request.title, request.content, request.tags)
        )
        conn.commit()
        return {"success": True, "id": cursor.lastrowid}

@app.get("/api/users/{user_id}/history")
async def get_history(user_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM histories WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        histories = cursor.fetchall()
        return [
            {
                "id": h["id"],
                "title": h["title"],
                "content": h["content"],
                "tags": h["tags"],
                "created_at": h["created_at"]
            }
            for h in histories
        ]

@app.delete("/api/users/{user_id}/history/{history_id}")
async def delete_history(user_id: int, history_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM histories WHERE user_id = ? AND id = ?",
            (user_id, history_id)
        )
        conn.commit()
        return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
