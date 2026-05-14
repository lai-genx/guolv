#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多种Google News RSS源格式和替代源
"""

import asyncio
import httpx
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 尝试多种Google News RSS源格式
test_feeds = {
    "Google News Formats": [
        ("Google News - Generic", "https://news.google.com/rss"),
        ("Google News - US", "https://news.google.com/rss?hl=en&gl=US&ceid=US:en"),
        ("Google News - Tech", "https://news.google.com/rss/topics/TCPqyQIqGBD?hl=en&gl=US&ceid=US:en"),
    ],
    "Alternative Tech News Sources": [
        ("Reddit r/technology", "https://www.reddit.com/r/technology/.rss"),
        ("Hacker News (YCombinator)", "https://news.ycombinator.com/rss"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
    ]
}

async def test_feed(name: str, url: str, timeout: int = 10, follow_redirects: bool = True) -> dict:
    """测试单个RSS源"""
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=follow_redirects) as client:
            response = await client.get(url)

            if response.status_code == 200:
                content = response.text
                if '<rss' in content or '<feed' in content or 'entry' in content:
                    item_count = content.count('<item>') + content.count('<entry>')
                    return {
                        'name': name,
                        'url': url,
                        'status': 'OK',
                        'status_code': 200,
                        'items': item_count,
                        'error': None
                    }
                else:
                    return {
                        'name': name,
                        'url': url,
                        'status': 'WARN',
                        'status_code': 200,
                        'items': 0,
                        'error': 'Possibly not RSS format'
                    }
            elif response.status_code == 302:
                return {
                    'name': name,
                    'url': url,
                    'status': 'REDIRECT',
                    'status_code': 302,
                    'items': 0,
                    'error': 'HTTP 302 (requires redirect)'
                }
            else:
                return {
                    'name': name,
                    'url': url,
                    'status': 'ERROR',
                    'status_code': response.status_code,
                    'items': 0,
                    'error': f'HTTP {response.status_code}'
                }
    except Exception as e:
        return {
            'name': name,
            'url': url,
            'status': 'ERROR',
            'status_code': 0,
            'items': 0,
            'error': str(e)[:50]
        }

async def main():
    print("=" * 80)
    print("RSS源兼容性测试（Google News + 替代源）")
    print("=" * 80)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    all_results = []
    success_count = 0
    total_count = 0

    for category, feeds in test_feeds.items():
        print(f"\n📋 {category}")
        print("-" * 80)

        tasks = []
        for name, url in feeds:
            tasks.append(test_feed(name, url))

        results = await asyncio.gather(*tasks)
        all_results.extend(results)

        print(f"{'名称':<30} {'状态':<12} {'项目数':<10} {'说明':<25}")
        print("-" * 80)

        for result in results:
            total_count += 1
            status_emoji = {
                'OK': '✅',
                'WARN': '⚠️',
                'REDIRECT': '🔄',
                'ERROR': '❌'
            }.get(result['status'], '?')

            items_text = str(result['items']) if result['status'] == 'OK' else "N/A"
            error_text = result['error'] or "Unknown"
            print(f"{result['name']:<30} {status_emoji} {result['status']:<10} {items_text:<10} {error_text:<25}")

            if result['status'] == 'OK':
                success_count += 1

    print("\n" + "=" * 80)
    print(f"总体统计: {success_count}/{total_count} 源可用")
    print("=" * 80)

    if success_count > 0:
        print(f"\n✅ 找到 {success_count} 个可用的替代RSS源\n")
        print("推荐配置以下替代源到config.py:")
        print("-" * 80)
        for result in all_results:
            if result['status'] == 'OK':
                print(f'        "{result["url"]}",  # {result["name"]} ({result["items"]} items)')
    else:
        print("\n❌ 所有Google News源都不可用，但替代源(TechCrunch, MIT Tech Review等)应该可用")

    print("\n💡 建议:")
    print("  - Google News RSS功能受限，建议使用替代技术新闻源")
    print("  - TechCrunch, MIT Technology Review, The Verge 都是优质替代选择")
    print("  - Reddit r/technology 可以获取社区讨论的热点新闻")

if __name__ == "__main__":
    asyncio.run(main())
