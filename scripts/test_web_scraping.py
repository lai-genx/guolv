# -*- coding: utf-8 -*-
"""
测试网站爬取功能
检查新添加的公司官网是否能被成功爬取
"""
import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')

import httpx
from bs4 import BeautifulSoup

# 测试一些新添加的公司的官网
test_urls = [
    ("高通", "https://www.qualcomm.com/news"),
    ("思佳讯 (Skyworks)", "https://www.skyworksinc.com/news"),
    ("村田 (Murata)", "https://www.murata.com/news"),
    ("TDK", "https://www.tdk.com/news"),
    ("博通 (Broadcom)", "https://www.broadcom.com/news"),
    ("鹏鼎控股", "https://www.avaryholding.com"),
    ("欣兴电子", "https://www.unimicron.com"),
    ("泰科电子", "https://www.te.com/news"),
    ("安费诺", "https://www.amphenol.com/news"),
    ("Lumentum", "https://www.lumentum.com/news"),
    ("Coherent", "https://www.coherent.com/news"),
    ("KDDI", "https://www.kddi.com/news"),
    ("诺基亚", "https://www.nokia.com/news"),
]

# CSS selectors from web_sites_config.py
list_selector = "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']"
title_selector = "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]"
link_selector = "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]"
date_selector = "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]"


async def test_url(name, url):
    """测试单个URL的爬取"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if resp.status_code != 200:
                return name, url, False, f"HTTP {resp.status_code}"

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Try to find news items
            elements = soup.select(list_selector)
            titles = soup.select(title_selector)

            if elements:
                return name, url, True, f"Found {len(elements)} items, {len(titles)} titles"
            else:
                # Check if page has any links that look like news
                links = soup.select(link_selector)
                news_links = [l for l in links if any(x in l.get('href', '') for x in ['news', 'press', 'article'])]
                return name, url, True, f"No list items, but found {len(news_links)} potential news links"

    except Exception as e:
        return name, url, False, str(e)[:50]


async def main():
    print("Testing website scraping for newly added companies\n")
    print("=" * 70)

    results = []
    for name, url in test_urls:
        result = await test_url(name, url)
        results.append(result)
        status = "✓" if result[2] else "✗"
        print(f"{status} {result[0]}: {result[1]}")
        print(f"  -> {result[3]}")
        print()

    success = sum(1 for r in results if r[2])
    print("=" * 70)
    print(f"Summary: {success}/{len(results)} websites accessible")

    # Now test with Jina Reader fallback
    print("\n" + "=" * 70)
    print("Testing Jina Reader API (if configured)")
    print("=" * 70)

    jina_api_key = ""  # Will be loaded from config

    # Check if jina is available
    try:
        from config import settings
        jina_api_key = settings.collector.jina_api_key
        if jina_api_key:
            print(f"Jina API Key: {jina_api_key[:10]}...")

            # Test Jina for one URL
            test_url_jina = "https://www.qualcomm.com/news"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://r.jina.ai/api/content",
                    json={"url": test_url_jina},
                    headers={"Authorization": f"Bearer {jina_api_key}"},
                    timeout=60.0
                )
                if resp.status_code == 200:
                    content = resp.json().get("data", {}).get("content", "")[:500]
                    print(f"\nJina Reader test for 高通:")
                    print(f"  Content preview: {content[:200]}...")
                    print("  -> Jina Reader is working!")
                else:
                    print(f"Jina API error: {resp.status_code}")
        else:
            print("Jina API Key not configured - using generic CSS parsing only")
    except Exception as e:
        print(f"Error checking Jina: {e}")

if __name__ == "__main__":
    asyncio.run(main())