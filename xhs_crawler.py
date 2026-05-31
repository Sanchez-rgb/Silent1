import requests
import re
import json
import time
import random
from typing import Optional, List, Dict, Tuple

# 写死的Cookie
HARDCODED_COOKIE = 'abRequestId=ebfed775-9034-5b2b-b04d-fc2c187d6441; ets=1779961601483; xsecappid=xhs-pc-web; a1=19e6dfa9e2bme7x0nwnxhvonc7bkra2tzcj5v9w3p50000277803; webId=2bce05e682230807d2c91f86d544b787; gid=yjdKfi00i8uiyjdKfi0jdSjEJD6dWC8IEICxVqUhlISWD228TF0J9h888JWWY8q8DfS2WSDY; web_session=040069b913a3eb64b3b84b472d384b269fbd0b; id_token=VjEAADytvWiR/xz6YDljNx63WcWgU3JC3I07TJ/gtiKzDhn/63EfuCkgLtmQUi+y5wHn8SNUoYymlXDyB0botRcKsbUKUHwo11Zj/KvlpQF4+TH4NbfJRbw2AIJA08/of0o3Ycjj; x-rednote-datactry=CN; x-rednote-holderctry=CN; webBuild=6.13.3; acw_tc=0a5085ef17800804284253235e8cc9cf1bc806d7ef67f8671bd43a9dfdbc3b; unread={%22ub%22:%226a115578000000003701e122%22%2C%22ue%22:%2269f7246700000000360333f6%22%2C%22uc%22:25}; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=6e650f36-3505-4cb4-8de3-56e9a5d3d6cc; loadts=1780081672553'

class XiaohongshuCrawler:
    """小红书爬虫类"""

    def __init__(self, cookie: str = None):
        # 使用写死的Cookie，忽略传入的参数
        self.cookie = HARDCODED_COOKIE
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Cookie': self.cookie,
            'Referer': 'https://www.xiaohongshu.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        }

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        url = f"https://edith.xiaohongshu.com/api/sns/web/v1/user_otherinfo"
        params = {
            'target_user_id': user_id
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', {})
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None

    def get_user_notes(self, user_id: str, limit: int = 30) -> List[Dict]:
        """获取用户笔记列表"""
        url = "https://edith.xiaohongshu.com/api/sns/web/v1/user_posted"
        params = {
            'user_id': user_id,
            'cursor': '',
            'num': limit,
            'sort': 'time'
        }

        notes = []
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    items = data.get('data', {}).get('notes', [])
                    for item in items:
                        notes.append({
                            'note_id': item.get('note_id', ''),
                            'title': item.get('title', ''),
                            'url': f"https://www.xiaohongshu.com/note/{item.get('note_id', '')}",
                            'like_count': item.get('interact_info', {}).get('liked_count', 0),
                            'comment_count': item.get('interact_info', {}).get('comment_count', 0),
                            'type': item.get('type', 'normal')
                        })
            return notes
        except Exception as e:
            print(f"获取笔记列表失败: {e}")
            return notes

    def get_note_comments(self, note_id: str, limit: int = 50) -> List[Dict]:
        """获取笔记评论"""
        url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"
        params = {
            'note_id': note_id,
            'cursor': '',
            'num': limit,
            'top_comment_id': ''
        }

        comments = []
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    comments_data = data.get('data', {}).get('comments', [])
                    for comment in comments_data:
                        comments.append({
                            'comment_text': comment.get('content', ''),
                            'user_nickname': comment.get('user_info', {}).get('nickname', ''),
                            'like_count': comment.get('like_count', 0)
                        })
            return comments
        except Exception as e:
            print(f"获取评论失败: {e}")
            return comments

    def crawl_blogger_data(self, blogger_id: str, max_notes: int = 30, max_comments_per_note: int = 50) -> Tuple[List[Dict], List[Dict]]:
        """
        爬取博主数据
        :param blogger_id: 博主ID
        :param max_notes: 最大笔记数
        :param max_comments_per_note: 每篇笔记最大评论数
        :return: (笔记列表, 评论列表)
        """
        print(f"开始爬取博主 {blogger_id} 的数据...")

        # 随机延迟 3-6 秒
        delay = random.uniform(3, 6)
        print(f"随机延迟 {delay:.2f} 秒...")
        time.sleep(delay)

        # 获取笔记列表
        print(f"正在获取笔记列表 (最多 {max_notes} 篇)...")
        notes = self.get_user_notes(blogger_id, limit=max_notes)

        if not notes:
            print("未获取到笔记数据，返回空列表")
            return [], []

        print(f"成功获取 {len(notes)} 篇笔记")

        # 限制笔记数量
        notes = notes[:max_notes]

        all_comments = []

        # 获取每篇笔记的评论
        for i, note in enumerate(notes):
            print(f"正在获取第 {i+1}/{len(notes)} 篇笔记的评论: {note.get('title', '')[:30]}...")
            comments = self.get_note_comments(note['note_id'], limit=max_comments_per_note)
            all_comments.extend(comments)
            print(f"  获取到 {len(comments)} 条评论")

            # 每篇笔记之间随机延迟 1-3 秒
            if i < len(notes) - 1:
                note_delay = random.uniform(1, 3)
                time.sleep(note_delay)

        print(f"总共获取 {len(all_comments)} 条评论")
        return notes, all_comments


def crawl_blogger_notes(blogger_id: str, cookie: str = None) -> Tuple[List[Dict], List[Dict]]:
    """
    爬取博主笔记和评论的入口函数
    :param blogger_id: 博主ID
    :param cookie: 小红书Cookie（忽略，使用写死的Cookie）
    :return: (笔记列表, 评论列表)
    """
    # 使用写死的Cookie
    print(f"使用写死的Cookie")
    crawler = XiaohongshuCrawler()

    try:
        # 爬取博主数据：最多30篇笔记，每篇最多50条评论
        notes, comments = crawler.crawl_blogger_data(
            blogger_id,
            max_notes=30,
            max_comments_per_note=50
        )

        # 如果真实爬虫失败，返回空数据而不是模拟数据
        if not notes and not comments:
            print("真实爬虫未能获取到数据，返回空列表")
            return [], []

        return notes, comments

    except Exception as e:
        print(f"爬虫执行出错: {e}")
        # 爬虫失败时返回空数据，不使用模拟数据
        return [], []
