"""Playwright真实爬虫调试版 - 带截图功能"""
from playwright.async_api import async_playwright
import json
import asyncio

# 写死的Cookie
HARDCODED_COOKIE = 'abRequestId=ebfed775-9034-5b2b-b04d-fc2c187d6441; ets=1779961601483; xsecappid=xhs-pc-web; a1=19e6dfa9e2bme7x0nwnxhvonc7bkra2tzcj5v9w3p50000277803; webId=2bce05e682230807d2c91f86d544b787; gid=yjdKfi00i8uiyjdKfi0jdSjEJD6dWC8IEICxVqUhlISWD228TF0J9h888JWWY8q8DfS2WSDY; web_session=040069b913a3eb64b3b84b472d384b269fbd0b; id_token=VjEAADytvWiR/xz6YDljNx63WcWgU3JC3I07TJ/gtiKzDhn/63EfuCkgLtmQUi+y5wHn8SNUoYymlXDyB0botRcKsbUKUHwo11Zj/KvlpQF4+TH4NbfJRbw2AIJA08/of0o3Ycjj; x-rednote-datactry=CN; x-rednote-holderctry=CN; webBuild=6.13.3; acw_tc=0a5085ef17800804284253235e8cc9cf1bc806d7ef67f8671bd43a9dfdbc3b; unread={%22ub%22:%226a115578000000003701e122%22%2C%22ue%22:%2269f7246700000000360333f6%22%2C%22uc%22:25}; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=6e650f36-3505-4cb4-8de3-56e9a5d3d6cc; loadts=1780081672553'

def parse_cookie_string(cookie_string):
    cookies = []
    for item in cookie_string.split(";"):
        item = item.strip()
        if "=" in item:
            name, value = item.split("=", 1)
            cookies.append({
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".xiaohongshu.com",
                "path": "/"
            })
    return cookies

async def debug_crawl(blogger_id):
    async with async_playwright() as p:
        print(f"="*60)
        print(f"启动浏览器...")
        browser = await p.chromium.launch(headless=False)  # 显示浏览器窗口！
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )
        
        # 设置Cookie
        cookies = parse_cookie_string(HARDCODED_COOKIE)
        await context.add_cookies(cookies)
        print(f"已设置 {len(cookies)} 个Cookie")
        
        # 反检测
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        """)
        
        page = await context.new_page()
        
        url = f"https://www.xiaohongshu.com/user/profile/{blogger_id}"
        print(f"\n访问: {url}")
        
        try:
            # 访问页面，不等待networkidle，只等待domcontentloaded
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print(f"状态码: {response.status if response else 'None'}")
            print(f"页面标题: {await page.title()}")
            
            # 截图1 - 刚加载
            await page.screenshot(path="debug_screenshot_1.png", full_page=True)
            print(f"✓ 截图1已保存: debug_screenshot_1.png")
            
            # 等待较长时间，确保完全加载
            print(f"\n等待 15 秒让页面完全加载...")
            await asyncio.sleep(15)
            
            # 截图2 - 加载后
            await page.screenshot(path="debug_screenshot_2.png", full_page=True)
            print(f"✓ 截图2已保存: debug_screenshot_2.png")
            
            # 保存页面源码
            page_content = await page.content()
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            print(f"✓ 页面源码已保存: debug_page_source.html")
            print(f"  源码长度: {len(page_content)}")
            
            # 查找所有a标签
            links = await page.locator("a").all()
            print(f"\n找到 {len(links)} 个链接")
            for i, link in enumerate(links[:30]):  # 只看前30个
                try:
                    href = await link.get_attribute("href")
                    text = (await link.inner_text()).strip()[:50]
                    if href:
                        print(f"  [{i}] {href} | {text}")
                except:
                    pass
            
            # 查找所有div
            all_divs = await page.locator("div").all()
            print(f"\n找到 {len(all_divs)} 个div")
            
            # 查找包含特定关键词的元素
            keywords = ["笔记", "作品", "Note", "note"]
            print(f"\n查找包含关键词的元素: {keywords}")
            for keyword in keywords:
                try:
                    elements = await page.locator(f":text('{keyword}')").all()
                    print(f"  '{keyword}': 找到 {len(elements)} 个元素")
                except:
                    pass
            
            # 查看页面中是否有特定的class
            print(f"\n查找常见class:")
            common_classes = [
                "feeds-item", "note-item", "author-works", "works-item",
                "card", "post", "article", "content"
            ]
            for cls in common_classes:
                try:
                    elements = await page.locator(f".{cls}").all()
                    if elements:
                        print(f"  .{cls}: 找到 {len(elements)} 个元素")
                except:
                    pass
            
            print(f"\n浏览器窗口保持打开，请手动检查页面！")
            print(f"按 Ctrl+C 关闭浏览器...")
            
            # 保持浏览器打开，直到用户按Ctrl+C
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_crawl("5cc3fdb0000000001601f5e9"))
