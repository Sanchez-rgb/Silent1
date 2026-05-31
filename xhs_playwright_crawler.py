"""
小红书博主数据爬虫 - Playwright Async版本
使用方法：
1. 安装依赖：pip install playwright && playwright install chromium
2. 直接运行：python xhs_playwright_crawler.py
"""

from playwright.async_api import async_playwright
import json
import time
import random

# 写死的Cookie
HARDCODED_COOKIE = 'abRequestId=ebfed775-9034-5b2b-b04d-fc2c187d6441; ets=1779961601483; xsecappid=xhs-pc-web; a1=19e6dfa9e2bme7x0nwnxhvonc7bkra2tzcj5v9w3p50000277803; webId=2bce05e682230807d2c91f86d544b787; gid=yjdKfi00i8uiyjdKfi0jdSjEJD6dWC8IEICxVqUhlISWD228TF0J9h888JWWY8q8DfS2WSDY; web_session=040069b913a3eb64b3b84b472d384b269fbd0b; id_token=VjEAADytvWiR/xz6YDljNx63WcWgU3JC3I07TJ/gtiKzDhn/63EfuCkgLtmQUi+y5wHn8SNUoYymlXDyB0botRcKsbUKUHwo11Zj/KvlpQF4+TH4NbfJRbw2AIJA08/of0o3Ycjj; x-rednote-datactry=CN; x-rednote-holderctry=CN; webBuild=6.13.3; acw_tc=0a5085ef17800804284253235e8cc9cf1bc806d7ef67f8671bd43a9dfdbc3b; unread={%22ub%22:%226a115578000000003701e122%22%2C%22ue%22:%2269f7246700000000360333f6%22%2C%22uc%22:25}; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=6e650f36-3505-4cb4-8de3-56e9a5d3d6cc; loadts=1780081672553'


async def crawl_blogger_with_playwright(blogger_id: str, max_scrolls: int = 5) -> dict:
    """
    使用Playwright异步爬取小红书博主数据

    :param blogger_id: 博主ID
    :param max_scrolls: 最大滚动次数（加载更多笔记）
    :return: 包含博主信息和笔记列表的字典
    """
    result = {
        "blogger_id": blogger_id,
        "blogger_name": "",
        "notes": [],
        "success": False,
        "error": None
    }

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,  # 无头模式
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        # 创建上下文（相当于新的浏览器配置文件）
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )

        # 反爬虫检测参数
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # 设置Cookie
        cookies = parse_cookie_string(HARDCODED_COOKIE)
        await context.add_cookies(cookies)
        print(f"已设置 {len(cookies)} 个Cookie")

        # 创建页面
        page = await context.new_page()

        try:
            # 访问博主主页
            url = f"https://www.xiaohongshu.com/user/profile/{blogger_id}"
            print(f"正在访问: {url}")

            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print(f"页面状态码: {response.status if response else 'None'}")

            # 等待页面基本加载
            print("等待页面加载...")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(8000)  # 等待8秒确保动态内容渲染

            # 尝试等待主要容器加载
            try:
                await page.wait_for_selector(".feeds-container, .user-profile, [class*='profile']", timeout=10000)
                print("主要容器已加载")
            except:
                print("未能检测到主要容器，继续...")

            # 提取博主名称
            blogger_name = await extract_blogger_name(page)
            result["blogger_name"] = blogger_name
            print(f"博主名称: {blogger_name}")

            # 滚动页面加载更多笔记
            print(f"开始滚动页面（最多 {max_scrolls} 次）...")
            for i in range(max_scrolls):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(random.uniform(1000, 2000))
                print(f"  滚动第 {i+1}/{max_scrolls} 次")

                # 点击"加载更多"按钮（如果存在）
                try:
                    load_more_btn = page.locator(".load-more")
                    if await load_more_btn.is_visible():
                        await load_more_btn.click()
                        await page.wait_for_timeout(1000)
                        print("  点击了加载更多按钮")
                except:
                    pass

            # 提取笔记列表
            notes = await extract_notes(page)
            result["notes"] = notes
            print(f"共提取到 {len(notes)} 篇笔记")

            # 打印页面HTML片段用于调试
            try:
                page_content = await page.content()
                print(f"页面HTML长度: {len(page_content)} 字符")
                # 打印body前500字符
                body_start = page_content.find("<body")
                if body_start != -1:
                    body_snippet = page_content[body_start:body_start+1000]
                    print(f"Body片段: {body_snippet[:500]}...")
            except Exception as e:
                print(f"调试信息获取失败: {e}")

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            print(f"爬取失败: {e}")

        finally:
            await browser.close()

    return result


def parse_cookie_string(cookie_string: str) -> list:
    """将Cookie字符串转换为Playwright需要的格式"""
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


async def extract_blogger_name(page) -> str:
    """提取博主名称"""
    selectors = [
        ".name",
        ".nickname",
        "[class*='name']",
        "[class*='nickname']",
        "h1.user-name",
        ".user-name",
        "[data-v-xxxxx-title]"  # 小红书某些版本的用户名容器
    ]

    for selector in selectors:
        try:
            elements = page.locator(selector)
            count = await elements.count()
            if count > 0:
                name = (await elements.first.inner_text()).strip()
                if name:
                    return name
        except:
            continue

    # 尝试从页面源码中提取
    try:
        title = await page.title()
        if "的小红书" in title:
            return title.split("的小红书")[0].strip()
    except:
        pass

    return "未知博主"


async def extract_notes(page) -> list:
    """提取笔记列表"""
    notes = []

    # 小红书笔记的选择器 - 扩展更多选择器
    note_selectors = [
        ".note-item",
        ".user-tab a[href*='/discovery/item']",
        "[class*='note-item']",
        ".cards .card",
        ".feeds-container .feeds-item",
        ".feeds .feeds-item",
        "a[href*='/discovery/item/']",
        "[data-v-bh74dcdc] a[href]",
        ".author-works .author-works-item",
        ".works-item",
        "#detail .feeds-container > div",
        ".profile-tab a[href*='note']",
    ]

    found_selector = None
    found_count = 0

    for selector in note_selectors:
        try:
            elements = page.locator(selector)
            count = await elements.count()
            if count > 0:
                print(f"  尝试选择器 '{selector}': 找到 {count} 个元素")
                if found_count == 0:
                    found_selector = selector
                    found_count = count
        except Exception as e:
            print(f"  选择器 '{selector}' 出错: {e}")
            continue

    print(f"  最终使用选择器 '{found_selector}' (共 {found_count} 个元素)")

    # 方法1: 从feeds容器提取
    try:
        feeds = page.locator(".feeds-container .feeds-item, .feeds .feeds-item, [class*='feeds-item']")
        count = await feeds.count()
        print(f"  尝试从feeds-item提取: {count} 个")
        if count > 0:
            for i in range(count):
                note = await extract_single_note_from_element(feeds.nth(i))
                if note:
                    notes.append(note)
            if notes:
                print(f"  从feeds-item成功提取 {len(notes)} 篇笔记")
                return notes
    except Exception as e:
        print(f"  feeds-item提取失败: {e}")

    # 方法2: 从笔记链接提取
    try:
        note_links = page.locator("a[href*='/discovery/item/'], a[href*='/user/profile/']")
        link_count = await note_links.count()
        print(f"  找到 {link_count} 个相关链接")
        seen_urls = set()
        for i in range(link_count):
            if len(notes) >= 30:
                break

            try:
                href = await note_links.nth(i).get_attribute("href")
                if href and href not in seen_urls and '/discovery/item/' in href:
                    seen_urls.add(href)
                    note_info = {
                        "title": "",
                        "url": f"https://www.xiaohongshu.com{href}" if href.startswith("/") else href,
                        "likes": 0,
                        "comments": 0
                    }

                    # 尝试获取标题 - 多种方式
                    try:
                        # 先尝试直接获取链接的文字
                        link_text = (await note_links.nth(i).inner_text()).strip()
                        if link_text and len(link_text) > 3:
                            note_info["title"] = link_text[:100]
                    except:
                        pass

                    if not note_info["title"]:
                        try:
                            parent = note_links.nth(i).locator("..")
                            for title_selector in ["[class*='title']", "[class*='desc']", ".title", "span", "div"]:
                                title_elem = parent.locator(title_selector)
                                title_count = await title_elem.count()
                                if title_count > 0:
                                    text = (await title_elem.first.inner_text()).strip()
                                    if text and len(text) > 3:
                                        note_info["title"] = text[:100]
                                        break
                        except:
                            pass

                    if note_info["title"]:
                        notes.append(note_info)
                        print(f"    提取笔记: {note_info['title'][:50]}...")
            except Exception as e:
                continue
    except Exception as e:
        print(f"  链接提取失败: {e}")

    print(f"  最终提取到 {len(notes)} 篇笔记")
    return notes


async def extract_single_note_from_element(element) -> dict:
    """从单个笔记元素中提取信息"""
    try:
        note_info = {
            "title": "",
            "url": "",
            "likes": 0,
            "comments": 0
        }

        # 获取链接
        try:
            link = element.locator("a").first
            href = await link.get_attribute("href")
            if href:
                note_info["url"] = f"https://www.xiaohongshu.com{href}" if href.startswith("/") else href
        except:
            pass

        # 获取标题
        try:
            title_elem = element.locator("[class*='title'], [class*='desc'], .title, h2, h3")
            title_count = await title_elem.count()
            if title_count > 0:
                note_info["title"] = (await title_elem.first.inner_text()).strip()
        except:
            pass

        # 获取点赞数
        try:
            like_elem = element.locator("[class*='like'] span, [class*='liked']")
            like_count = await like_elem.count()
            if like_count > 0:
                like_text = (await like_elem.first.inner_text()).strip()
                note_info["likes"] = parse_count(like_text)
        except:
            pass

        return note_info if note_info["title"] else None

    except:
        return None


def parse_count(text: str) -> int:
    """解析点赞/评论数（如 1.2万 -> 12000）"""
    if not text:
        return 0

    text = text.strip()

    try:
        # 直接是数字
        if text.isdigit():
            return int(text)

        # 处理万为单位
        if "万" in text:
            num = float(text.replace("万", ""))
            return int(num * 10000)

        # 处理其他格式
        text = text.replace(",", "").replace(" ", "")
        return int(float(text))

    except:
        return 0


async def main():
    """主函数"""
    # 要爬取的博主ID
    blogger_id = "5e12345abcdef1234567890"  # 替换为您要爬取的博主ID

    print("=" * 60)
    print("小红书博主数据爬虫 - Playwright Async版本")
    print("=" * 60)

    # 执行爬取
    result = await crawl_blogger_with_playwright(blogger_id, max_scrolls=3)

    # 输出结果
    print("\n" + "=" * 60)
    print("爬取结果:")
    print("=" * 60)

    if result["success"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"爬取失败: {result.get('error')}")

    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
