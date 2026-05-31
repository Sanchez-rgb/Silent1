
import asyncio
from xhs_playwright_crawler import crawl_blogger_with_playwright

async def main():
    blogger_id = "5cc3fdb0000000001601f5e9"
    
    print("=" * 60)
    print(f"开始测试爬虫，博主ID: {blogger_id}")
    print("=" * 60)
    
    result = await crawl_blogger_with_playwright(blogger_id, max_scrolls=3)
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print("=" * 60)
    
    if result.get("success"):
        print(f"✓ 爬虫成功!")
        print(f"博主名称: {result.get('blogger_name')}")
        print(f"笔记数量: {len(result.get('notes', []))}")
        
        if result.get('notes'):
            print("\n前3篇笔记:")
            for i, note in enumerate(result.get('notes')[:3]):
                print(f"  {i+1}. {note.get('title', '无标题')[:50]}")
                print(f"     链接: {note.get('url', '无链接')}")
    else:
        print(f"✗ 爬虫失败!")
        print(f"错误信息: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
