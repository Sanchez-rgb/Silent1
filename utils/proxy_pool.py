# 代理池管理
import random
import time
import requests
import threading
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyPool:
    """代理池管理类"""
    
    def __init__(self):
        self.proxies = []  # 可用代理列表
        self.last_refresh = None
        self.lock = threading.Lock()
        self.is_running = False
        
    def get_random_proxy(self):
        """获取随机代理"""
        with self.lock:
            if not self.proxies:
                return None
            return random.choice(self.proxies)
    
    def get_random_delay(self):
        """获取随机延迟（8-12秒）"""
        return random.uniform(8, 12)
    
    def refresh_proxies(self):
        """从免费源刷新代理"""
        logger.info("开始刷新代理池...")
        
        new_proxies = []
        
        # 1. 从 free-proxy-list.net 采集
        try:
            fps_proxies = self._scrape_free_proxy_list()
            logger.info(f"从 free-proxy-list.net 获取到 {len(fps_proxies)} 个代理")
            new_proxies.extend(fps_proxies)
        except Exception as e:
            logger.error(f"采集 free-proxy-list.net 失败: {e}")
        
        # 2. 从 proxyscrape.com 采集
        try:
            ps_proxies = self._scrape_proxyscrape()
            logger.info(f"从 proxyscrape.com 获取到 {len(ps_proxies)} 个代理")
            new_proxies.extend(ps_proxies)
        except Exception as e:
            logger.error(f"采集 proxyscrape.com 失败: {e}")
        
        # 去重
        new_proxies = list(set(new_proxies))
        
        # 验证代理可用性
        valid_proxies = self._validate_proxies(new_proxies)
        
        with self.lock:
            self.proxies = valid_proxies
            self.last_refresh = datetime.now()
        
        logger.info(f"代理池刷新完成，可用代理: {len(valid_proxies)}")
    
    def _scrape_free_proxy_list(self):
        """从 free-proxy-list.net 采集代理"""
        url = "https://free-proxy-list.net/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        proxies = []
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    https = cols[6].text.strip().lower() == 'yes'
                    
                    if ip and port:
                        protocol = 'https' if https else 'http'
                        proxies.append(f"{protocol}://{ip}:{port}")
        
        return proxies
    
    def _scrape_proxyscrape(self):
        """从 proxyscrape.com 采集代理"""
        url = "https://api.proxyscrape.com/?request=displayproxies&proxytype=http"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        proxies = []
        lines = response.text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                proxies.append(f"http://{line}")
        
        return proxies
    
    def _validate_proxies(self, proxies, test_url="http://httpbin.org/get", timeout=5):
        """验证代理可用性"""
        valid = []
        
        for proxy in proxies:
            try:
                start_time = time.time()
                response = requests.get(
                    test_url,
                    proxies={"http": proxy, "https": proxy},
                    timeout=timeout
                )
                if response.status_code == 200:
                    latency = round((time.time() - start_time) * 1000, 2)
                    valid.append({
                        "url": proxy,
                        "latency": latency,
                        "last_verified": datetime.now()
                    })
                    logger.debug(f"代理 {proxy} 可用，延迟: {latency}ms")
            except Exception as e:
                continue
        
        return valid
    
    def start_background_refresh(self):
        """启动后台刷新任务（每30分钟）"""
        def refresh_loop():
            while self.is_running:
                try:
                    self.refresh_proxies()
                except Exception as e:
                    logger.error(f"后台刷新失败: {e}")
                
                time.sleep(30 * 60)  # 30分钟
        
        if not self.is_running:
            self.is_running = True
            # 立即刷新一次
            try:
                self.refresh_proxies()
            except Exception as e:
                logger.error(f"初始刷新失败: {e}")
            
            # 启动后台线程
            thread = threading.Thread(target=refresh_loop, daemon=True)
            thread.start()
            logger.info("代理池后台刷新任务已启动")
    
    def stop_background_refresh(self):
        """停止后台刷新"""
        self.is_running = False


# 全局代理池实例
proxy_pool = ProxyPool()


def get_proxy():
    """获取代理（优先从代理池）"""
    proxy = proxy_pool.get_random_proxy()
    if proxy:
        return proxy["url"]
    return None


def get_delay():
    """获取延迟（无代理时使用）"""
    return proxy_pool.get_random_delay()


def init_proxy_pool():
    """初始化代理池"""
    proxy_pool.start_background_refresh()
