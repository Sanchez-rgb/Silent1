
# 爬虫中间件 - 代理+重试
import time
import random
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from utils.proxy_pool import proxy_pool


class CrawlerMiddleware:
    """爬虫中间件，处理代理、重试、延迟等"""
    
    def __init__(self, cookie: Optional[str] = None):
        self.cookie = cookie
        self.session = self._create_session()
    
    def _create_session(self) -&gt; requests.Session:
        """创建带重试的会话"""
        session = requests.Session()
        
        # 重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        # 设置Cookie
        if self.cookie:
            session.headers.update({
                'Cookie': self.cookie
            })
        
        return session
    
    def random_delay(self):
        """随机延迟"""
        delay = proxy_pool.get_delay()
        time.sleep(delay)
    
    def rotate_proxy_if_needed(self):
        """需要时轮换代理"""
        if proxy_pool.should_rotate():
            proxy_pool.rotate_proxy()
    
    def get(self, url: str, **kwargs) -&gt; requests.Response:
        """带代理和延迟的GET请求"""
        self.rotate_proxy_if_needed()
        self.random_delay()
        
        proxy_params = proxy_pool.get_request_params()
        kwargs.update(proxy_params)
        
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -&gt; requests.Response:
        """带代理和延迟的POST请求"""
        self.rotate_proxy_if_needed()
        self.random_delay()
        
        proxy_params = proxy_pool.get_request_params()
        kwargs.update(proxy_params)
        
        return self.session.post(url, **kwargs)
