# -*- coding: utf-8 -*-
"""
生成web_sites_config.py的新公司条目
Based on test results, only add companies with accessible URLs
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# CSS selectors from web_sites_config.py
list_sel = "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']"
title_sel = "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]"
link_sel = "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]"
date_sel = "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]"

# Companies with verified accessible URLs (from test)
accessible_companies = [
    # (name, url, priority)
    ("Skyworks", "https://www.skyworksinc.com/news", "P1"),
    ("Qorvo", "https://www.qorvo.com/news", "P1"),
    ("Murata", "https://www.murata.com/news", "P1"),
    ("Avary Holding", "https://www.avaryholding.com", "P2"),
    ("Samtec", "https://www.samtec.com", "P2"),
    ("Hirose", "https://www.hirose.com", "P2"),
    ("Luxshare", "https://www.luxshare-ict.com", "P2"),
    ("BT", "https://www.bt.com/news", "P1"),
    ("STC", "https://www.stc.com.sa/news", "P2"),
]

print("=" * 70)
print("Web config entries to add (verified accessible):")
print("=" * 70)

for name, url, priority in accessible_companies:
    base_url = url.rsplit('/', 1)[0] if '/' in url else url
    print(f'''
    {{
        "name": "{name}",
        "url": "{url}",
        "list_selector": "{list_sel}",
        "title_selector": "{title_sel}",
        "link_selector": "{link_sel}",
        "date_selector": "{date_sel}",
        "base_url": "{base_url}",
        "priority": "{priority}",
        "use_jina_only": True
    }},''')

print(f"\nTotal verified entries: {len(accessible_companies)}")