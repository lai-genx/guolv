#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Google News RSS源是否可用
"""

import asyncio
import httpx
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

google_news_feeds = [
    ("5G", "https://news.google.com/rss/search?q=5G&hl=en&gl=US&ceid=US:en"),
    ("Semiconductor", "https://news.google.com/rss/search?q=semiconductor&hl=en&gl=US&ceid=US:en"),
    ("Optical Communication", "https://news.google.com/rss/search?q=optical+communication&hl=en&gl=US&ceid=US:en"),
    ("Telecom Network", "https://news.google.com/rss/search?q=telecom+network&hl=en&gl=US&ceid=US:en"),
    ("Wireless Access", "https://news.google.com/rss/search?q=wireless+access&hl=en&gl=US&ceid=US:en"),
]

async def test_feed(name: str, url: str, timeout: int = 15) -> dict:
    """测试单个RSS源"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)

            if response.status_code == 200:
                # 检查是否包含rss或feed标签
                content = response.text
                if '<rss' in content or '<feed' in content:
                    # 计算项目数量
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
                        'status': 'ERROR',
                        'status_code': 200,
                        'items': 0,
                        'error': 'Not valid RSS format'
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
            'error': str(e)
        }

async def main():
    print("=" * 70)
    print("Google News RSS 源验证")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("测试以下Google News RSS源:")
    print("-" * 70)

    results = []
    tasks = []

    for name, url in google_news_feeds:
        tasks.append(test_feed(name, url))

    results = await asyncio.gather(*tasks)

    print(f"\n{'类别':<20} {'状态':<8} {'项目数':<8} {'详情':<30}")
    print("-" * 70)

    success_count = 0
    for result in results:
        status_emoji = "✅" if result['status'] == 'OK' else "❌"
        status_text = result['status']
        items_text = str(result['items']) if result['status'] == 'OK' else "N/A"
        error_text = result['error'] or f"HTTP {result['status_code']}"

        print(f"{result['name']:<20} {status_emoji} {status_text:<6} {items_text:<8} {error_text:<30}")

        if result['status'] == 'OK':
            success_count += 1

    print("-" * 70)
    print(f"\n总体结果: {success_count}/{len(results)} 源可用")

    if success_count == len(results):
        print("✅ 所有Google News RSS源验证通过！\n")
        print("下一步操作:")
        print("  1. 运行 python main.py --test 验证系统配置")
        print("  2. 运行 python main.py --collect 开始采集")
        print("  3. 查看日志: tail -f data/telecom_intel.log")
    else:
        print(f"⚠️ 有 {len(results) - success_count} 个源失败，但Google News通常不稳定")
        print("   系统会自动跳过失败的源继续采集\n")

    print("\nRSS源URL列表(可用于其他工具):")
    print("-" * 70)
    for result in results:
        if result['status'] == 'OK':
            print(f"✅ {result['name']}: {result['url']}")
        else:
            print(f"❌ {result['name']}: {result['url']} ({result['error']})")

if __name__ == "__main__":
    asyncio.run(main())
