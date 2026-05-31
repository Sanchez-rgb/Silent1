
# 情感分析任务
from celery_app import celery_app
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import Comment, Note, NoteReport
from analyzer.sentiment import get_sentiment_analyzer
from datetime import datetime
import json
from typing import List, Dict


@celery_app.task
def analyze_all_comments(note_id: str):
    """分析单篇笔记的所有评论"""
    db = SessionLocal()
    
    try:
        # 获取未分析的评论
        comments = db.query(Comment).filter(
            Comment.note_id == note_id,
            Comment.is_analyzed == False
        ).all()
        
        if not comments:
            return {"status": "completed", "analyzed": 0}
        
        # 分析情感
        analyzer = get_sentiment_analyzer()
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        sentiment_scores = []
        negative_comments = []
        
        for comment in comments:
            sentiment, confidence = analyzer.analyze(comment.comment_text or "")
            
            comment.sentiment = sentiment
            comment.confidence = confidence
            comment.is_analyzed = True
            
            if sentiment == "positive":
                positive_count += 1
                sentiment_scores.append(confidence)
            elif sentiment == "negative":
                negative_count += 1
                sentiment_scores.append(-confidence)
                negative_comments.append({
                    "comment_id": comment.comment_id,
                    "comment_text": comment.comment_text,
                    "confidence": confidence
                })
            else:
                neutral_count += 1
                sentiment_scores.append(0)
        
        # 计算平均情感分数
        avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # 确定评级
        if avg_score &gt; 0.3:
            rating = "优秀"
        elif avg_score &gt; 0:
            rating = "良好"
        elif avg_score &gt; -0.3:
            rating = "预警"
        else:
            rating = "危险"
        
        # 获取TOP5负面评论
        top_negative = sorted(negative_comments, key=lambda x: -x["confidence"])[:5]
        top_negative_json = json.dumps(top_negative, ensure_ascii=False)
        
        # 保存或更新报告
        report = db.query(NoteReport).filter(NoteReport.note_id == note_id).first()
        if not report:
            report = NoteReport(
                note_id=note_id,
                sentiment_score=avg_score,
                positive_count=positive_count,
                neutral_count=neutral_count,
                negative_count=negative_count,
                top_negative_comments=top_negative_json,
                rating=rating
            )
            db.add(report)
        else:
            report.sentiment_score = avg_score
            report.positive_count = positive_count
            report.neutral_count = neutral_count
            report.negative_count = negative_count
            report.top_negative_comments = top_negative_json
            report.rating = rating
        
        # 更新笔记的分析时间
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            note.analyze_time = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "completed",
            "note_id": note_id,
            "analyzed": len(comments),
            "positive": positive_count,
            "neutral": neutral_count,
            "negative": negative_count,
            "rating": rating,
            "score": avg_score
        }
        
    except Exception as e:
        print(f"情感分析出错: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task
def analyze_user_notes(user_id: int):
    """分析用户的所有笔记"""
    db = SessionLocal()
    
    try:
        # 获取用户的所有笔记
        notes = db.query(Note).filter(Note.user_id == user_id).all()
        
        results = []
        for note in notes:
            result = analyze_all_comments.delay(note.note_id).get()
            results.append(result)
        
        return {
            "status": "completed",
            "total_notes": len(notes),
            "results": results
        }
    except Exception as e:
        print(f"批量分析出错: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
