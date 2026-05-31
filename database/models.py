
# SQLAlchemy ORM模型定义
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    blogger_id = Column(String(255), nullable=True)
    xhs_cookie = Column(Text, nullable=True)  # 小红书Cookie
    created_at = Column(DateTime, default=datetime.utcnow)
    last_analysis_time = Column(DateTime, nullable=True)

    # 关系
    crawl_tasks = relationship("CrawlTask", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")


class CrawlTask(Base):
    """爬虫任务表"""
    __tablename__ = "crawl_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(String(50), default="pending")  # pending/running/completed/failed
    total_notes = Column(Integer, default=0)
    current_note = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)

    # 关系
    user = relationship("User", back_populates="crawl_tasks")
    notes = relationship("Note", back_populates="crawl_task", cascade="all, delete-orphan")


class Note(Base):
    """笔记表"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    note_id = Column(String(255), unique=True, index=True, nullable=False)
    note_title = Column(String(500), nullable=True)
    note_url = Column(String(500), nullable=True)
    blogger_id = Column(String(255), nullable=False)
    publish_time = Column(DateTime, nullable=True)
    analyze_time = Column(DateTime, nullable=True)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="notes")
    crawl_task = relationship("CrawlTask", back_populates="notes")
    comments = relationship("Comment", back_populates="note", cascade="all, delete-orphan")
    reports = relationship("NoteReport", back_populates="note", cascade="all, delete-orphan")


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    note_id = Column(String(255), nullable=False)
    comment_id = Column(String(255), nullable=True)
    comment_text = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    is_analyzed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    note = relationship("Note", back_populates="comments")


class NoteReport(Base):
    """笔记情感报告表"""
    __tablename__ = "note_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    note_id = Column(String(255), ForeignKey("notes.note_id"), nullable=False)
    sentiment_score = Column(Float, nullable=True)
    positive_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    top_negative_comments = Column(Text, nullable=True)  # JSON格式
    rating = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    note = relationship("Note", back_populates="reports")
