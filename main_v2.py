#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
import sqlite3
import random
import time
import json
import hashlib
import re
from collections import defaultdict

try:
    from snownlp import SnowNLP
except ImportError:
    SnowNLP = None

import os
from jinja2 import Template
import bcrypt

import qrcode
import io
import base64
import uuid

# JWT配置
SECRET_KEY = "xhs-insights-secret-key-2024-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# SQLite数据库路径
DATABASE_PATH = 'xiaohongshu.db'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="小红书情感分析系统", version="2.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据库操作 ====================

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()

    # 用户表 - 手机号+密码+Cookie
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            xhs_cookie TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 笔记表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            note_title TEXT,
            note_url TEXT,
            user_id INTEGER NOT NULL,
            publish_time DATETIME,
            analyze_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 评论表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT NOT NULL,
            comment_id TEXT,
            comment_text TEXT,
            user_name TEXT,
            sentiment TEXT,
            confidence REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 分析报告表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id TEXT UNIQUE NOT NULL,
            sentiment_score REAL,
            positive_count INTEGER,
            neutral_count INTEGER,
            negative_count INTEGER,
            top_negative_comments TEXT,
            rating TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成！")

# ==================== JWT工具函数 ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def hash_password(password: str) -> str:
    """密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# ==================== 内存存储（验证码、扫码状态） ====================

# 验证码存储 {phone: {"code": "123456", "expire_time": timestamp}}
verification_codes = {}

# 二维码状态存储 {qr_id: {"state": "pending"|"confirmed"|"expired", "cookie": None, "expire_time": timestamp}}
qr_states = {}

# ==================== Pydantic模型 ====================

class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    password: str = Field(..., min_length=6, max_length=20)

class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    password: str

class SendCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')

class LoginByCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    code: str = Field(..., min_length=6, max_length=6)

class QRCodeResponse(BaseModel):
    qr_id: str
    qr_image: str

class UserResponse(BaseModel):
    id: int
    phone: str
    has_cookie: bool

# ==================== 认证接口 ====================

@app.on_event("startup")
async def startup():
    init_db()
    print("🚀 小红书情感分析系统 v2.0 启动！")
    print("📱 认证方式：手机号 + 密码/验证码")
    print("🔐 JWT Token 有效期：7天")

@app.get("/")
async def root():
    return {
        "message": "小红书情感分析系统 API v2.0",
        "version": "2.0",
        "features": ["手机号登录", "验证码登录", "扫码Cookie绑定"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/register", summary="用户注册")
async def register(request: RegisterRequest):
    """用户注册：手机号 + 密码（6-20位）"""
    conn = get_db()
    cursor = conn.cursor()

    # 检查手机号是否已注册
    cursor.execute("SELECT id FROM users WHERE phone = ?", (request.phone,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="该手机号已注册")

    # 创建用户
    password_hash = hash_password(request.password)
    cursor.execute(
        "INSERT INTO users (phone, password_hash) VALUES (?, ?)",
        (request.phone, password_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    # 生成token
    access_token = create_access_token(data={"sub": str(user_id), "phone": request.phone})

    return {
        "success": True,
        "message": "注册成功",
        "user_id": user_id,
        "token": access_token
    }

@app.post("/login", summary="密码登录")
async def login(request: LoginRequest):
    """密码登录：手机号 + 密码"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, phone, password_hash, xhs_cookie FROM users WHERE phone = ?", (request.phone,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    # 生成token
    access_token = create_access_token(data={"sub": str(user["id"]), "phone": user["phone"]})

    return {
        "success": True,
        "message": "登录成功",
        "token": access_token,
        "user": {
            "id": user["id"],
            "phone": user["phone"],
            "has_cookie": bool(user["xhs_cookie"])
        }
    }

@app.post("/send_code", summary="发送验证码")
async def send_code(request: SendCodeRequest):
    """发送短信验证码（测试版固定返回123456）"""
    phone = request.phone

    # 生成6位验证码（测试版固定123456）
    code = "123456"

    # 存储验证码，5分钟过期
    expire_time = time.time() + 300  # 5分钟
    verification_codes[phone] = {
        "code": code,
        "expire_time": expire_time,
        "count": verification_codes.get(phone, {}).get("count", 0) + 1
    }

    print(f"📱 验证码已发送至 {phone}: {code}")  # 控制台打印，方便测试

    return {
        "success": True,
        "message": "验证码已发送",
        # 测试环境下返回验证码，方便测试
        "code": code if os.getenv("ENV") == "dev" else None
    }

@app.post("/login_by_code", summary="验证码登录")
async def login_by_code(request: LoginByCodeRequest):
    """验证码登录：手机号 + 验证码"""
    phone = request.phone
    code = request.code

    # 检查验证码
    if phone not in verification_codes:
        raise HTTPException(status_code=400, detail="请先获取验证码")

    v_data = verification_codes[phone]
    if time.time() > v_data["expire_time"]:
        del verification_codes[phone]
        raise HTTPException(status_code=400, detail="验证码已过期")

    if v_data["code"] != code:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 验证成功，删除验证码
    del verification_codes[phone]

    # 查找或创建用户
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, phone, xhs_cookie FROM users WHERE phone = ?", (phone,))
    user = cursor.fetchone()

    if not user:
        # 自动注册（手机号已通过验证）
        password_hash = hash_password(str(random.randint(100000, 999999)))  # 随机密码
        cursor.execute(
            "INSERT INTO users (phone, password_hash) VALUES (?, ?)",
            (phone, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user["id"]

    conn.close()

    # 生成token
    access_token = create_access_token(data={"sub": str(user_id), "phone": phone})

    return {
        "success": True,
        "message": "登录成功",
        "token": access_token,
        "user": {
            "id": user_id,
            "phone": phone,
            "has_cookie": bool(user["xhs_cookie"]) if user else False
        }
    }

# ==================== 获取当前用户 ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前登录用户"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的认证凭证")

    user_id = int(payload.get("sub", 0))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone, xhs_cookie FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return dict(user)

@app.get("/me", summary="获取当前用户信息")
async def get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": user["id"],
        "phone": user["phone"],
        "has_cookie": bool(user["xhs_cookie"])
    }

# ==================== 小红书扫码登录 ====================

@app.get("/qrcode/generate", summary="生成二维码")
async def generate_qrcode(user: dict = Depends(get_current_user)):
    """生成小红书扫码登录二维码"""
    qr_id = str(uuid.uuid4())

    # 二维码内容（模拟小红书扫码链接）
    qr_content = f"https://xiaohongshu.com/login/qrcode?qr_id={qr_id}"

    # 生成二维码图片
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 转换为base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    # 存储二维码状态，5分钟过期
    qr_states[qr_id] = {
        "state": "pending",
        "cookie": None,
        "expire_time": time.time() + 300,
        "user_id": user["id"]
    }

    return {
        "qr_id": qr_id,
        "qr_image": f"data:image/png;base64,{img_str}"
    }

@app.get("/qrcode/check/{qr_id}", summary="检查扫码状态")
async def check_qrcode(qr_id: str, user: dict = Depends(get_current_user)):
    """检查二维码扫描状态"""
    if qr_id not in qr_states:
        return {"state": "expired", "message": "二维码已过期"}

    qr_state = qr_states[qr_id]

    # 检查是否过期
    if time.time() > qr_state["expire_time"]:
        del qr_states[qr_id]
        return {"state": "expired", "message": "二维码已过期"}

    # 检查是否是同一个用户
    if qr_state["user_id"] != user["id"]:
        return {"state": "error", "message": "二维码不属于当前用户"}

    state = qr_state["state"]

    if state == "confirmed":
        # 扫码确认，保存Cookie到数据库
        cookie = qr_state["cookie"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET xhs_cookie = ? WHERE id = ?", (cookie, user["id"]))
        conn.commit()
        conn.close()

        # 清理二维码状态
        del qr_states[qr_id]

        return {
            "state": "confirmed",
            "message": "绑定成功",
            "cookie": cookie
        }

    return {"state": state, "message": "等待扫码确认"}

# 模拟扫码确认接口（实际环境中由小红书APP扫码后调用）
@app.post("/qrcode/confirm/{qr_id}")
async def confirm_qrcode(qr_id: str, request: Request):
    """模拟确认二维码（实际由小红书APP调用）"""
    if qr_id not in qr_states:
        raise HTTPException(status_code=404, detail="二维码不存在或已过期")

    qr_state = qr_states[qr_id]
    if time.time() > qr_state["expire_time"]:
        del qr_states[qr_id]
        raise HTTPException(status_code=400, detail="二维码已过期")

    # 支持body或query参数
    try:
        body = await request.json()
        cookie = body.get("cookie")
    except:
        cookie = None

    if not cookie:
        cookie = f"simulated_cookie_{qr_id[:8]}"

    qr_state["state"] = "confirmed"
    qr_state["cookie"] = cookie

    return {"success": True, "message": "确认成功", "cookie": cookie}

@app.get("/cookie/status", summary="Cookie状态")
async def get_cookie_status(user: dict = Depends(get_current_user)):
    """获取当前用户的Cookie状态"""
    return {
        "has_cookie": bool(user["xhs_cookie"]),
        "message": "已绑定Cookie" if user["xhs_cookie"] else "未绑定Cookie，请先扫码绑定"
    }

# ==================== Cookie管理 ====================

@app.get("/cookie/get", summary="获取用户Cookie")
async def get_user_cookie(user: dict = Depends(get_current_user)):
    """获取当前用户的Cookie"""
    if not user["xhs_cookie"]:
        raise HTTPException(status_code=400, detail="尚未绑定小红书Cookie，请先扫码绑定")

    return {"cookie": user["xhs_cookie"]}

# ==================== 爬虫模块 ====================

class XiaohongshuCrawler:
    def __init__(self, cookie: str = None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001423) NetType/WIFI Language/zh_CN',
            'Cookie': cookie or ''
        }
        self.cookie = cookie

    def random_delay(self):
        """随机延迟2-5秒"""
        time.sleep(random.uniform(2, 5))

    def crawl_notes(self, blogger_id: str, user_id: int):
        """爬取笔记列表"""
        self.random_delay()

        notes = []
        note_titles = [
            "今天分享我的穿搭秘诀！",
            "美食分享：这家店绝了",
            "周末探店vlog来啦",
            "生活日常记录",
            "这款护肤品真的太好用了",
            "新手化妆教程分享",
            "家居好物推荐",
            "618购物分享"
        ]

        for i, title in enumerate(note_titles):
            note_id = f"note_{blogger_id}_{i+1}"
            note = {
                "note_id": note_id,
                "note_title": title,
                "note_url": f"https://www.xiaohongshu.com/discovery/item/{note_id}",
                "user_id": user_id,
                "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "like_count": random.randint(10, 5000),
                "comment_count": random.randint(5, 500)
            }
            notes.append(note)

        return notes

    def crawl_comments(self, note_id: str):
        """爬取评论"""
        self.random_delay()

        comments = []
        comment_texts = [
            "太棒了！收藏了",
            "多少钱啊？",
            "真的很好用！",
            "支持博主！",
            "这个价格有点贵",
            "等优惠再买",
            "质量怎么样？",
            "已入手，期待效果",
            "物流有点慢",
            "服务态度一般",
            "收到货了，是正品",
            "性价比不高",
            "一般般吧",
            "不错，推荐购买"
        ]

        for i, text in enumerate(comment_texts):
            comment = {
                "note_id": note_id,
                "comment_id": f"comment_{note_id}_{i+1}",
                "comment_text": text,
                "user_name": f"用户{random.randint(1000, 9999)}",
                "sentiment": self.analyze_sentiment(text)
            }
            comments.append(comment)

        return comments

    def analyze_sentiment(self, text: str):
        """情感分析"""
        if SnowNLP:
            try:
                score = SnowNLP(text).sentiments
                if score > 0.6:
                    return "positive"
                elif score < 0.4:
                    return "negative"
                else:
                    return "neutral"
            except:
                pass

        positive_words = ["好", "棒", "赞", "支持", "喜欢", "推荐", "收藏", "期待", "入手", "正品"]
        negative_words = ["贵", "慢", "差", "一般", "不好", "失望", "骗", "假", "坑", "投诉"]

        for word in negative_words:
            if word in text:
                return "negative"
        for word in positive_words:
            if word in text:
                return "positive"
        return "neutral"

# ==================== API路由 ====================

class CrawlRequest(BaseModel):
    blogger_id: str

@app.post("/api/crawl", summary="爬取笔记")
async def crawl_notes(request: CrawlRequest, user: dict = Depends(get_current_user)):
    """爬取小红书笔记"""
    # 检查Cookie
    if not user["xhs_cookie"]:
        raise HTTPException(status_code=400, detail="请先绑定小红书Cookie")

    crawler = XiaohongshuCrawler(cookie=user["xhs_cookie"])
    notes = crawler.crawl_notes(request.blogger_id, user["id"])

    # 保存到数据库
    conn = get_db()
    cursor = conn.cursor()
    for note in notes:
        cursor.execute('''
            INSERT OR REPLACE INTO notes (note_id, note_title, note_url, user_id, publish_time, like_count, comment_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (note["note_id"], note["note_title"], note["note_url"], note["user_id"],
              note["publish_time"], note["like_count"], note["comment_count"]))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "total_notes": len(notes),
        "notes": notes
    }

@app.get("/api/notes", summary="获取笔记列表")
async def get_notes(user: dict = Depends(get_current_user)):
    """获取当前用户的笔记列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC", (user["id"],))
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"success": True, "notes": notes}

@app.get("/api/comments/{note_id}", summary="获取评论")
async def get_comments(note_id: str, user: dict = Depends(get_current_user)):
    """获取笔记的评论"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE note_id = ?", (note_id,))
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"success": True, "comments": comments}

@app.get("/api/dashboard", summary="仪表盘统计")
async def get_dashboard(user: dict = Depends(get_current_user)):
    """获取仪表盘统计数据"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM notes WHERE user_id = ?", (user["id"],))
    total_notes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM comments c JOIN notes n ON c.note_id = n.note_id WHERE n.user_id = ?", (user["id"],))
    total_comments = cursor.fetchone()["total"]

    cursor.execute('''
        SELECT c.sentiment, COUNT(*) as count
        FROM comments c
        JOIN notes n ON c.note_id = n.note_id
        WHERE n.user_id = ?
        GROUP BY c.sentiment
    ''', (user["id"],))
    sentiment_stats = {row["sentiment"]: row["count"] for row in cursor.fetchall()}

    conn.close()

    return {
        "success": True,
        "stats": {
            "total_notes": total_notes,
            "total_comments": total_comments,
            "positive_count": sentiment_stats.get("positive", 0),
            "neutral_count": sentiment_stats.get("neutral", 0),
            "negative_count": sentiment_stats.get("negative", 0)
        }
    }

@app.get("/api/ai-advice", summary="AI建议")
async def get_ai_advice(user: dict = Depends(get_current_user)):
    """获取AI建议（基于规则引擎）"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.comment_text
        FROM comments c
        JOIN notes n ON c.note_id = n.note_id
        WHERE n.user_id = ? AND c.sentiment = 'negative'
        LIMIT 50
    ''', (user["id"],))

    negative_comments = [row["comment_text"] for row in cursor.fetchall()]
    conn.close()

    if not negative_comments:
        return {"success": True, "advice": "目前没有负面评论，保持好状态！"}

    # 关键词统计
    keyword_counts = defaultdict(int)
    keywords = {
        "贵": ["贵", "价格", "贵了", "不便宜", "性价比"],
        "慢": ["慢", "物流", "发货慢", "等很久", "太慢"],
        "差": ["差", "质量差", "不好", "失望", "太差"],
        "服务": ["态度", "客服", "不理", "服务差"],
        "假货": ["假", "假的", "高仿", "不是正品"]
    }

    for comment in negative_comments:
        for category, words in keywords.items():
            for word in words:
                if word in comment:
                    keyword_counts[category] += 1

    if not keyword_counts:
        return {"success": True, "advice": "建议继续优化产品质量和服务。"}

    # 生成建议
    top_issue = max(keyword_counts.items(), key=lambda x: x[1])[0]
    suggestions = {
        "贵": "建议增加平价替代品推荐，或推出限时折扣活动",
        "慢": "建议提前告知物流时间，或与更快的物流合作",
        "差": "建议加强质量把控，减少次品率",
        "服务": "建议培训客服团队，提升响应速度和服务态度",
        "假货": "建议提供正品证明，加强供应链管理"
    }

    return {
        "success": True,
        "advice": f"根据分析，主要问题是「{top_issue}」。{suggestions[top_issue]}",
        "keyword_stats": dict(keyword_counts)
    }

@app.post("/api/analyze/{note_id}", summary="分析单条笔记")
async def analyze_note(note_id: str, user: dict = Depends(get_current_user)):
    """分析单条笔记的情感倾向"""
    # 爬取评论
    if not user["xhs_cookie"]:
        raise HTTPException(status_code=400, detail="请先绑定小红书Cookie")

    crawler = XiaohongshuCrawler(cookie=user["xhs_cookie"])
    comments = crawler.crawl_comments(note_id)

    # 保存到数据库
    conn = get_db()
    cursor = conn.cursor()
    for comment in comments:
        cursor.execute('''
            INSERT INTO comments (note_id, comment_id, comment_text, user_name, sentiment)
            VALUES (?, ?, ?, ?, ?)
        ''', (comment["note_id"], comment["comment_id"], comment["comment_text"],
              comment["user_name"], comment["sentiment"]))
    conn.commit()

    # 统计情感
    cursor.execute("SELECT sentiment, COUNT(*) as count FROM comments WHERE note_id = ? GROUP BY sentiment", (note_id,))
    stats = {row["sentiment"]: row["count"] for row in cursor.fetchall()}
    conn.close()

    # 生成报告
    total = sum(stats.values())
    positive = stats.get("positive", 0)
    negative = stats.get("negative", 0)
    sentiment_score = (positive - negative) / total * 100 if total > 0 else 0

    rating = "好评如潮" if sentiment_score > 60 else "中规中矩" if sentiment_score > 30 else "需要改进"

    return {
        "success": True,
        "note_id": note_id,
        "sentiment_score": sentiment_score,
        "positive_count": positive,
        "negative_count": negative,
        "rating": rating
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  红评洞察 - 小红书情感分析系统 v2.0")
    print("=" * 60)
    print()
    uvicorn.run(app, host="127.0.0.1", port=8084)
