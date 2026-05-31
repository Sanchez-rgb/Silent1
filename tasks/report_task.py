
# 报告生成任务
from celery_app import celery_app
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import User, Note, NoteReport
from analyzer.ai_advisor import get_ai_advisor
from jinja2 import Template
from datetime import datetime
import json


@celery_app.task
def generate_user_report(user_id: int):
    """生成用户报告"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        # 获取笔记报告
        reports = db.query(NoteReport).join(Note).filter(Note.user_id == user_id).all()
        
        # 计算统计
        avg_sentiment_score = 0
        excellent_count = 0
        good_count = 0
        warning_count = 0
        danger_count = 0
        all_negative_comments = []
        
        if reports:
            scores = [r.sentiment_score for r in reports if r.sentiment_score is not None]
            avg_sentiment_score = sum(scores) / len(scores) if scores else 0
            
            for report in reports:
                if report.rating == "优秀":
                    excellent_count += 1
                elif report.rating == "良好":
                    good_count += 1
                elif report.rating == "预警":
                    warning_count += 1
                elif report.rating == "危险":
                    danger_count += 1
                
                if report.top_negative_comments:
                    try:
                        negatives = json.loads(report.top_negative_comments)
                        all_negative_comments.extend(negatives)
                    except:
                        pass
        
        # 获取最佳和最差笔记
        notes_reports = (
            db.query(NoteReport, Note)
            .join(Note, NoteReport.note_id == Note.note_id)
            .filter(Note.user_id == user_id)
            .all()
        )
        
        sorted_reports = sorted(notes_reports, key=lambda x: x[0].sentiment_score or 0, reverse=True)
        top_best = sorted_reports[:3]
        top_worst = sorted_reports[-3:][::-1]
        
        # 生成AI建议
        advisor = get_ai_advisor()
        total = len(reports)
        ai_advice = advisor.generate_advice({
            'average_sentiment': avg_sentiment_score,
            'positive_ratio': excellent_count / total if total &gt; 0 else 0,
            'negative_ratio': danger_count / total if total &gt; 0 else 0,
            'neutral_ratio': (warning_count + good_count) / total if total &gt; 0 else 0,
            'negative_comments': all_negative_comments
        })
        
        # 准备报告数据
        report_data = {
            "user_info": {
                "username": user.username,
                "blogger_id": user.blogger_id,
                "last_analysis_time": user.last_analysis_time.isoformat() if user.last_analysis_time else None
            },
            "overview": {
                "average_sentiment_score": avg_sentiment_score,
                "excellent_count": excellent_count,
                "good_count": good_count,
                "warning_count": warning_count,
                "danger_count": danger_count
            },
            "top_best_notes": [
                {
                    "title": nr[1].note_title,
                    "sentiment_score": nr[0].sentiment_score,
                    "note_url": nr[1].note_url
                }
                for nr in top_best
            ],
            "top_worst_notes": [
                {
                    "title": nr[1].note_title,
                    "sentiment_score": nr[0].sentiment_score,
                    "note_url": nr[1].note_url
                }
                for nr in top_worst
            ],
            "ai_advice": ai_advice,
            "generated_at": datetime.now().isoformat()
        }
        
        # 生成HTML报告
        html_report = generate_html_report(report_data)
        
        return {
            "status": "completed",
            "report_data": report_data,
            "html_report": html_report
        }
        
    except Exception as e:
        print(f"生成报告出错: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


def generate_html_report(data: dict) -&gt; str:
    """生成HTML报告"""
    template_str = """
&lt;!DOCTYPE html&gt;
&lt;html lang="zh-CN"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;
    &lt;title&gt;小红书情感分析报告&lt;/title&gt;
    &lt;style&gt;
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff2442 0%, #ff6b6b 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 { font-size: 36px; margin-bottom: 10px; }
        .content { padding: 40px; }
        .section { margin-bottom: 40px; }
        .section h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
            border-bottom: 3px solid #ff2442;
            padding-bottom: 10px;
            display: inline-block;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-card {
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stat-card.excellent { background: linear-gradient(135deg, #84fab0, #8fd3f4); color: #155724; }
        .stat-card.good { background: linear-gradient(135deg, #fff3cd, #ffeaa7); color: #856404; }
        .stat-card.warning { background: linear-gradient(135deg, #ffe5d0, #fab1a0); color: #856404; }
        .stat-card.danger { background: linear-gradient(135deg, #ffcccb, #ff7675); color: #721c24; }
        .stat-card.avg { background: linear-gradient(135deg, #a18cd1, #fbc2eb); color: #333; }
        .stat-card .score { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
        .note-list { display: flex; flex-direction: column; gap: 15px; }
        .note-item {
            padding: 20px;
            border-left: 5px solid;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .note-item.positive { border-color: #28a745; }
        .note-item.negative { border-color: #dc3545; }
        .note-item h3 { color: #333; margin-bottom: 10px; }
        .note-item .score { color: #666; font-size: 14px; }
        .advice-box {
            background: linear-gradient(135deg, #e0c3fc, #8ec5fc);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #8ec5fc;
        }
        .advice-box h3 { color: #333; margin-bottom: 15px; }
        .advice-box p { color: #555; line-height: 1.8; white-space: pre-line; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #eee;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="container"&gt;
        &lt;div class="header"&gt;
            &lt;h1&gt;🎨 小红书情感分析报告&lt;/h1&gt;
            &lt;p&gt;博主: {{ user_info.username }} | 生成时间: {{ generated_at }}&lt;/p&gt;
        &lt;/div&gt;
        
        &lt;div class="content"&gt;
            &lt;div class="section"&gt;
                &lt;h2&gt;📊 总览统计&lt;/h2&gt;
                &lt;div class="stats-grid"&gt;
                    &lt;div class="stat-card avg"&gt;
                        &lt;div class="score"&gt;{{ "%.2f"|format(overview.average_sentiment_score) }}&lt;/div&gt;
                        &lt;div&gt;平均情感分数&lt;/div&gt;
                    &lt;/div&gt;
                    &lt;div class="stat-card excellent"&gt;
                        &lt;div class="score"&gt;{{ overview.excellent_count }}&lt;/div&gt;
                        &lt;div&gt;优秀笔记&lt;/div&gt;
                    &lt;/div&gt;
                    &lt;div class="stat-card good"&gt;
                        &lt;div class="score"&gt;{{ overview.good_count }}&lt;/div&gt;
                        &lt;div&gt;良好笔记&lt;/div&gt;
                    &lt;/div&gt;
                    &lt;div class="stat-card warning"&gt;
                        &lt;div class="score"&gt;{{ overview.warning_count }}&lt;/div&gt;
                        &lt;div&gt;预警笔记&lt;/div&gt;
                    &lt;/div&gt;
                    &lt;div class="stat-card danger"&gt;
                        &lt;div class="score"&gt;{{ overview.danger_count }}&lt;/div&gt;
                        &lt;div&gt;危险笔记&lt;/div&gt;
                    &lt;/div&gt;
                &lt;/div&gt;
            &lt;/div&gt;
            
            {% if top_best_notes %}
            &lt;div class="section"&gt;
                &lt;h2&gt;🏆 最佳笔记 TOP3&lt;/h2&gt;
                &lt;div class="note-list"&gt;
                    {% for note in top_best_notes %}
                    &lt;div class="note-item positive"&gt;
                        &lt;h3&gt;{{ note.title }}&lt;/h3&gt;
                        &lt;p class="score"&gt;情感分数: {{ "%.4f"|format(note.sentiment_score) }}&lt;/p&gt;
                        {% if note.note_url %}
                        &lt;a href="{{ note.note_url }}" target="_blank" style="color: #28a745; text-decoration: none;"&gt;查看笔记 →&lt;/a&gt;
                        {% endif %}
                    &lt;/div&gt;
                    {% endfor %}
                &lt;/div&gt;
            &lt;/div&gt;
            {% endif %}
            
            {% if top_worst_notes %}
            &lt;div class="section"&gt;
                &lt;h2&gt;⚠️ 需要关注的笔记 TOP3&lt;/h2&gt;
                &lt;div class="note-list"&gt;
                    {% for note in top_worst_notes %}
                    &lt;div class="note-item negative"&gt;
                        &lt;h3&gt;{{ note.title }}&lt;/h3&gt;
                        &lt;p class="score"&gt;情感分数: {{ "%.4f"|format(note.sentiment_score) }}&lt;/p&gt;
                        {% if note.note_url %}
                        &lt;a href="{{ note.note_url }}" target="_blank" style="color: #dc3545; text-decoration: none;"&gt;查看笔记 →&lt;/a&gt;
                        {% endif %}
                    &lt;/div&gt;
                    {% endfor %}
                &lt;/div&gt;
            &lt;/div&gt;
            {% endif %}
            
            &lt;div class="section"&gt;
                &lt;h2&gt;💡 AI优化建议&lt;/h2&gt;
                &lt;div class="advice-box"&gt;
                    &lt;h3&gt;🤖 建议摘要&lt;/h3&gt;
                    &lt;p&gt;{{ ai_advice }}&lt;/p&gt;
                &lt;/div&gt;
            &lt;/div&gt;
        &lt;/div&gt;
        
        &lt;div class="footer"&gt;
            &lt;p&gt;由小红书情感分析系统生成 · {{ generated_at }}&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
    """
    
    template = Template(template_str)
    return template.render(**data)
