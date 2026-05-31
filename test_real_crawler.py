"""真实爬虫测试脚本"""
import requests
import json
import random
import time

# 写死的Cookie
HARDCODED_COOKIE = 'abRequestId=ebfed775-9034-5b2b-b04d-fc2c187d6441; ets=1779961601483; xsecappid=xhs-pc-web; a1=19e6dfa9e2bme7x0nwnxhvonc7bkra2tzcj5v9w3p50000277803; webId=2bce05e682230807d2c91f86d544b787; gid=yjdKfi00i8uiyjdKfi0jdSjEJD6dWC8IEICxVqUhlISWD228TF0J9h888JWWY8q8DfS2WSDY; web_session=040069b913a3eb64b3b84b472d384b269fbd0b; id_token=VjEAADytvWiR/xz6YDljNx63WcWgU3JC3I07TJ/gtiKzDhn/63EfuCkgLtmQUi+y5wHn8SNUoYymlXDyB0botRcKsbUKUHwo11Zj/KvlpQF4+TH4NbfJRbw2AIJA08/of0o3Ycjj; x-rednote-datactry=CN; x-rednote-holderctry=CN; webBuild=6.13.3; acw_tc=0a5085ef17800804284253235e8cc9cf1bc806d7ef67f8671bd43a9dfdbc3b; unread={%22ub%22:%226a115578000000003701e122%22%2C%22ue%22:%2269f7246700000000360333f6%22%2C%22uc%22:25}; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=6e650f36-3505-4cb4-8de3-56e9a5d3d6cc; loadts=1780081672553'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': HARDCODED_COOKIE,
    'Referer': 'https://www.xiaohongshu.com/',
    'Origin': 'https://www.xiaohongshu.com',
}

def test_api(blogger_id):
    """测试API调用"""
    print(f"="*60)
    print(f"开始测试爬虫，博主ID: {blogger_id}")
    print(f"="*60)
    
    # 测试1: 获取博主主页
    print(f"\n【测试1】访问博主主页")
    profile_url = f"https://www.xiaohongshu.com/user/profile/{blogger_id}"
    try:
        r = requests.get(profile_url, headers=HEADERS, timeout=30)
        print(f"状态码: {r.status_code}")
        print(f"响应长度: {len(r.text)}")
        if r.status_code == 200:
            # 查找页面中的关键信息
            if '笔记' in r.text:
                print("✓ 页面包含'笔记'关键词")
            if '小红书' in r.text:
                print("✓ 页面包含'小红书'关键词")
            # 保存响应到文件
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(r.text)
            print(f"✓ 页面已保存到 debug_page.html")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 测试2: 尝试API端点
    print(f"\n【测试2】尝试API端点")
    api_endpoints = [
        f"https://edith.xiaohongshu.com/api/sns/web/v1/user/otherinfo?target_user_id={blogger_id}",
        f"https://edith.xiaohongshu.com/api/sns/web/v1/user/notes?user_id={blogger_id}&cursor=&num=10",
        f"https://edith.xiaohongshu.com/api/sns/web/v2/user/note/feed?user_id={blogger_id}&cursor=&count=10",
    ]
    
    for api in api_endpoints:
        try:
            r = requests.get(api, headers=HEADERS, timeout=20)
            print(f"\n{api}")
            print(f"  状态码: {r.status_code}")
            try:
                data = r.json()
                print(f"  响应: {json.dumps(data, ensure_ascii=False)[:500]}...")
                # 保存API响应
                with open(f'debug_api_{blogger_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  ✓ API响应已保存")
            except Exception as e:
                print(f"  响应内容: {r.text[:500]}...")
        except Exception as e:
            print(f"\n{api}")
            print(f"  ✗ 错误: {e}")
    
    print(f"\n【测试完成】请查看 debug_page.html 和 debug_api_*.json 文件")

if __name__ == "__main__":
    test_blogger_id = "26487961577"
    test_api(test_blogger_id)
