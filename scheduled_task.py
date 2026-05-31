import sqlite3
import datetime
import time
import random
import schedule
from snownlp import SnowNLP
import json

# 模拟小红书API - 生成测试数据
class XiaohongshuMockAPI:
    def __init__(self):
        self.blogger_notes = {}
        self._init_mock_data()

    def _init_mock_data(self):
        # 为每个博主生成模拟笔记数据
        bloggers = ['blogger_001', 'blogger_002', 'blogger_003']
        
        for blogger_id in bloggers:
            self.blogger_notes[blogger_id] = []
            # 生成3-5条模拟笔记
            num_notes = random.randint(3, 5)
            for i in range(num_notes):
                publish_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                note = {
                    'note_id': f'note_{blogger_id}_{i}_{int(time.time())}',
                    'title': self._generate_random_title(),
                    'content': self._generate_random_content(),
                    'publish_time': publish_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'comments': self._generate_random_comments()
                }
                self.blogger_notes[blogger_id].append(note)

    def _generate_random_title(self):
        titles = [
            '今天分享我的穿搭秘诀！', '这款护肤品真的太好用了',
            '周末探店vlog来啦', '美食分享：这家店绝了',
            '旅行攻略：小众打卡地', '好物推荐：必买清单',
            '生活日常记录', '化妆教程：新手也能学会'
        ]
        return random.choice(titles)

    def _generate_random_content(self):
        contents = [
            '今天天气真好，心情特别棒！', '这款产品真的很推荐，大家可以试试',
            '这个地方真的太美了，下次还要来', '这家店的味道太赞了，强烈推荐',
            '今天学习了很多新东西，很开心', '分享一下我的日常，希望大家喜欢'
        ]
        return random.choice(contents)

    def _generate_random_comments(self):
        comments = []
        sentiments = ['positive', 'neutral', 'negative']
        positive_texts = ['太赞了！', '好喜欢！', '太棒了！', '学到了！', '种草了！']
        neutral_texts = ['还行吧', '一般般', '看看', '嗯', '了解了']
        negative_texts = ['不太好', '一般', '不喜欢', '有点失望', '不怎么样']

        num_comments = random.randint(15, 25)
        for i in range(num_comments):
            sentiment = random.choice(sentiments)
            if sentiment == 'positive':
                text = random.choice(positive_texts)
            elif sentiment == 'neutral':
                text = random.choice(neutral_texts)
            else:
                text = random.choice(negative_texts)

            comments.append({
                'comment_id': f'comment_{i}_{int(time.time())}',
                'text': text,
                'user': f'user_{i}'
            })
        return comments

    def get_blogger_notes(self, blogger_id):
        return self.blogger_notes.get(blogger_id, [])

# 情感分析函数
def analyze_sentiment(text):
    try:
        s = SnowNLP(text)
        score = s.sentiments
        if score > 0.6:
            return 'positive', score
        elif score < 0.4:
            return 'negative', score
        else:
            return 'neutral', score
    except Exception as e:
        return 'neutral', 0.5

# 数据库操作类
class DatabaseManager:
    def __init__(self, db_name='xiaohongshu.db'):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def get_followed_blogs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT blogger_id, blogger_name, last_check_time FROM followed_blogs')
        blogs = cursor.fetchall()
        conn.close()
        return blogs

    def update_last_check_time(self, blogger_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE followed_blogs
            SET last_check_time = ?
            WHERE blogger_id = ?
        ''', (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), blogger_id))
        conn.commit()
        conn.close()

    def save_comment_analysis(self, blogger_id, blogger_name, note_id, note_title, note_publish_time, comment_id, comment_text, sentiment, confidence):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO comments_analysis 
                (blogger_id, blogger_name, note_id, note_title, note_publish_time, 
                 comment_id, comment_text, sentiment, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (blogger_id, blogger_name, note_id, note_title, note_publish_time,
                 comment_id, comment_text, sentiment, confidence))
            conn.commit()
        except Exception as e:
            print(f"保存评论分析时出错: {e}")
        finally:
            conn.close()

    def save_note(self, blogger_id, blogger_name, note_id, title, content, publish_time):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO notes 
                (note_id, blogger_id, blogger_name, title, content, publish_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (note_id, blogger_id, blogger_name, title, content, publish_time))
            conn.commit()
        except Exception as e:
            print(f"保存笔记时出错: {e}")
        finally:
            conn.close()

# 主任务执行函数
def run_task():
    print(f"\n{'='*60}")
    print(f"任务开始执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        api = XiaohongshuMockAPI()
        db = DatabaseManager()

        # 获取所有关注的博主
        bloggers = db.get_followed_blogs()
        print(f"找到 {len(bloggers)} 位关注的博主\n")

        total_processed = 0
        total_comments = 0

        for blogger_id, blogger_name, last_check_time_str in bloggers:
            print(f"\n--- 处理博主: {blogger_name} (ID: {blogger_id}) ---")
            print(f"上次检查时间: {last_check_time_str}")

            try:
                last_check_time = datetime.datetime.strptime(last_check_time_str, '%Y-%m-%d %H:%M:%S')
            except:
                last_check_time = datetime.datetime(2000, 1, 1)

            # 获取博主最新笔记
            notes = api.get_blogger_notes(blogger_id)
            new_notes_count = 0

            for note in notes:
                try:
                    note_publish_time = datetime.datetime.strptime(note['publish_time'], '%Y-%m-%d %H:%M:%S')
                except:
                    continue

                # 检查笔记是否是上次检查后发布的
                if note_publish_time > last_check_time:
                    new_notes_count += 1
                    print(f"\n发现新笔记: {note['title']}")
                    print(f"发布时间: {note['publish_time']}")

                    # 保存笔记
                    db.save_note(blogger_id, blogger_name, note['note_id'], 
                               note['title'], note['content'], note['publish_time'])

                    # 获取前20条评论并分析
                    comments = note['comments'][:20]
                    print(f"处理 {len(comments)} 条评论...")

                    for comment in comments:
                        sentiment, confidence = analyze_sentiment(comment['text'])
                        db.save_comment_analysis(
                            blogger_id, blogger_name,
                            note['note_id'], note['title'], note['publish_time'],
                            comment['comment_id'], comment['text'],
                            sentiment, confidence
                        )
                        total_comments += 1

                    print(f"笔记分析完成: {len(comments)} 条评论已处理")

            # 更新最后检查时间
            if new_notes_count > 0:
                db.update_last_check_time(blogger_id)
                print(f"更新检查时间完成")

            total_processed += 1
            print(f"博主处理完成: {new_notes_count} 条新笔记")

        print(f"\n{'='*60}")
        print(f"任务执行完成!")
        print(f"处理博主数: {total_processed}")
        print(f"处理评论数: {total_comments}")
        print(f"完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"任务执行出错: {e}")
        import traceback
        traceback.print_exc()

# 立即执行一次测试
def run_now():
    print("立即执行一次任务...")
    run_task()

# 主函数
def main():
    # 初始化数据库
    print("初始化数据库...")
    import init_db
    init_db.init_database()

    print("\n小红书定时任务系统启动!")
    print("任务配置: 每天凌晨 02:00 执行")
    print("按 Ctrl+C 停止程序\n")

    # 设置定时任务
    schedule.every().day.at("02:00").do(run_task)

    # 立即执行一次（测试用）
    print("执行一次测试任务...")
    run_task()

    # 主循环
    print("\n开始等待定时任务...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main()
