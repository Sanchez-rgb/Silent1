
"""简单的Playwright测试 - 自动关闭浏览器"""
from playwright.async_api import async_playwright
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

async def test_crawl():
    async with async_playwright() as p:
        print("="*60)
        print("启动浏览器...")
        browser = await p.chromium.launch(headless=True)
        
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
        """)
        
        page = await context.new_page()
        
        blogger_id = "5cc3fdb0000000001601f5e9"
        url = f"https://www.xiaohongshu.com/user/profile/{blogger_id}"
        print(f"\n访问: {url}")
        
        try:
            # 访问页面
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print(f"状态码: {response.status if response else 'None'}")
            print(f"页面标题: {await page.title()}")
            
            # 等待页面加载
            print(f"\n等待 10 秒让页面完全加载...")
            await asyncio.sleep(10)
            
            # 截图
            await page.screenshot(path="test_screenshot.png", full_page=True)
            print(f"✓ 截图已保存: test_screenshot.png")
            
            # 保存页面源码
            page_content = await page.content()
            with open("test_page_source.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            print(f"✓ 页面源码已保存: test_page_source.html")
            print(f"  源码长度: {len(page_content)}")
            
            # 查找笔记链接
            print(f"\n查找笔记链接...")
            note_links = []
            all_links = await page.locator("a").all()
            for link in all_links:
                href = await link.get_attribute("href")
                if href and ("/discovery/item/" in href or "/explore/" in href):
                    text = (await link.inner_text()).strip()
                    note_links.append({
                        "href": href,
                        "text": text
                    })
            
            print(f"找到 {len(note_links)} 个可能的笔记链接")
            for i, note in enumerate(note_links[:10]):
                print(f"  [{i+1}] {note['href']} - {note['text'][:50]}")
            
            # 查找博主名称
            print(f"\n尝试提取博主名称...")
            name_selectors = [".name", ".nickname", "h1", "[class*='name']", "[class*='nickname']"]
            blogger_name = None
            for selector in name_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for elem in elements:
                        text = (await elem.inner_text()).strip()
                        if text and len(text) > 1 and len(text) < 30:
                            blogger_name = text
                            print(f"找到博主名称: {blogger_name} (使用选择器: {selector})")
                            break
                    if blogger_name:
                        break
                except:
                    pass
            
            if not blogger_name:
                title = await page.title()
                if "的小红书" in title:
                    blogger_name = title.split("的小红书")[0].strip()
                    print(f"从页面标题提取博主名称: {blogger_name}")
            
            # 尝试滚动加载更多
            print(f"\n尝试滚动页面...")
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                print(f"  滚动 {i+1}/3")
            
            # 再次查找笔记
            print(f"\n滚动后再次查找笔记链接...")
            note_links_after = []
            all_links_after = await page.locator("a").all()
            for link in all_links_after:
                href = await link.get_attribute("href")
                if href and ("/discovery/item/" in href or "/explore/" in href):
                    text = (await link.inner_text()).strip()
                    note_links_after.append({
                        "href": href,
                        "text": text
                    })
            
            print(f"滚动后找到 {len(note_links_after)} 个笔记链接")
            
            print("\n" + "="*60)
            print("测试完成!")
            print("="*60)
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_crawl())
