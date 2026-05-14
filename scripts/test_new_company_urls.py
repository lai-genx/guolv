# -*- coding: utf-8 -*-
"""
测试新公司官网URL可访问性，并生成web_sites_config.py条目
"""
import asyncio
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import httpx
import re

# Companies to test and add
companies_to_test = [
    # (name, url, priority, news_url_suffix)
    ("Skyworks", "https://www.skyworksinc.com", "P1", "/news"),
    ("Qorvo", "https://www.qorvo.com", "P1", "/news"),
    ("Murata", "https://www.murata.com", "P1", "/news"),
    ("Taiyo Yuden", "https://www.yuden.co.jp", "P2", "/news"),
    ("TDK", "https://www.tdk.com", "P2", "/en/news"),
    ("Avary Holding", "https://www.avaryholding.com", "P2", ""),
    ("SCC", "https://www.scc.com.cn", "P2", ""),
    ("WUS Printed Circuit", "https://www.wuspca.com", "P2", ""),
    ("Unimicron", "https://www.unimicron.com", "P2", ""),
    ("Compeq", "https://www.compeq.com.tw", "P2", ""),
    ("TE Connectivity", "https://www.te.com", "P1", "/news"),
    ("Amphenol", "https://www.amphenol.com", "P1", "/news"),
    ("Molex", "https://www.molex.com", "P2", ""),
    ("Samtec", "https://www.samtec.com", "P2", ""),
    ("Hirose", "https://www.hirose.com", "P2", ""),
    ("Luxshare", "https://www.luxshare-ict.com", "P2", ""),
    ("BT", "https://www.bt.com", "P1", "/news"),
    ("KDDI", "https://www.kddi.com", "P1", "/news"),
    ("LG U+", "https://www.lguplus.com", "P1", "/news"),
    ("Singtel", "https://www.singtel.com", "P1", "/news"),
    ("Telstra", "https://www.telstra.com", "P1", "/news"),
    ("STC", "https://www.stc.com.sa", "P2", "/news"),
    ("Etisalat", "https://www.eand.com", "P2", "/news"),
]

async def test_url(name, base_url, news_suffix):
    """测试URL可访问性"""
    url = base_url + news_suffix if news_suffix else base_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            return name, base_url, url, resp.status_code, len(resp.text), resp.status_code == 200
    except Exception as e:
        return name, base_url, url, str(e)[:50], 0, False

async def main():
    print("Testing company URLs...\n")

    results = []
    for name, base_url, priority, news_suffix in companies_to_test:
        result = await test_url(name, base_url, news_suffix)
        results.append(result)

    print("=" * 80)
    print(f"{'Name':<20} {'URL':<50} {'Status':<10}")
    print("=" * 80)

    accessible = []
    for name, base_url, url, status, content_len, ok in results:
        status_str = str(status) if isinstance(status, int) else "ERR"
        print(f"{name:<20} {url:<50} {status_str:<10} ({content_len} chars)" if ok else f"{name:<20} {url:<50} {status_str:<10}")
        if ok:
            accessible.append((name, base_url, news_suffix if 'news_suffix' in locals() else ''))

    print(f"\nAccessible URLs: {len(accessible)}/{len(results)}")

    # Generate config entries for accessible URLs
    print("\n" + "=" * 80)
    print("Config entries to add to web_sites_config.py:")
    print("=" * 80)

    list_sel = "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']"
    title_sel = "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]"
    link_sel = "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]"
    date_sel = "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]"

    # Re-test accessible ones to find proper news URLs
    print("\nDetailed analysis of accessible sites:")
    for name, base_url, news_suffix in companies_to_test:
        if any(r[0] == name and r[5] for r in results):
            print(f'\n    {{')
            print(f'        "name": "{name}",')
            print(f'        "url": "{base_url}{news_suffix}",')
            print(f'        "list_selector": "{list_sel}",')
            print(f'        "title_selector": "{title_sel}",')
            print(f'        "link_selector": "{link_sel}",')
            print(f'        "date_selector": "{date_sel}",')
            print(f'        "base_url": "{base_url}",')
            print(f'        "priority": "P2",')
            print(f'        "use_jina_only": True')
            print(f'    }},')
            print()

if __name__ == "__main__":
    asyncio.run(main())