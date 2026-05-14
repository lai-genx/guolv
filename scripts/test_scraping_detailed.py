# -*- coding: utf-8 -*-
"""
测试Jina Reader API抓取
"""
import asyncio
import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import httpx
import os
from dotenv import load_dotenv

load_dotenv('.env')

async def test_jina_reader(url, name):
    """使用Jina Reader API抓取网页"""
    api_key = os.getenv('COLLECTOR__JINA_API_KEY', '')

    if not api_key:
        print(f"  Jina API Key not configured")
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://r.jina.ai/api/content",
                json={"url": url},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("data", {}).get("content", "")
                title = data.get("data", {}).get("title", "")

                # Parse markdown content
                lines = content.split('\n') if content else []
                # Find news-like items (titles starting with # or ##)
                news_items = [l for l in lines if l.strip().startswith('# ') or l.strip().startswith('## ')]

                print(f"  Title: {title}")
                print(f"  Content length: {len(content)} chars")
                print(f"  News items found: {len(news_items)}")
                if news_items[:3]:
                    print(f"  Sample: {news_items[:2]}")
                return True
            else:
                print(f"  Error: {resp.status_code} - {resp.text[:100]}")
                return False
    except Exception as e:
        print(f"  Exception: {e}")
        return None

async def test_direct_fetch(url, name):
    """直接使用httpx抓取"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            print(f"  Status: {resp.status_code}")
            print(f"  Content length: {len(resp.text)} chars")

            # Check for common news patterns
            text = resp.text
            if 'news' in text.lower()[:10000]:
                print(f"  -> 'news' found in first 10K chars")
            if 'article' in text.lower()[:10000]:
                print(f"  -> 'article' found in first 10K chars")

            # Look for date patterns
            import re
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', text[:50000])
            if dates:
                print(f"  -> Date patterns found: {dates[:3]}")

            return resp.status_code == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False

async def main():
    # Test URLs - mix of new companies
    test_cases = [
        ("高通", "https://www.qualcomm.com/news"),
        ("Skyworks", "https://www.skyworksinc.com/news"),
        ("博通", "https://www.broadcom.com/blog"),
        ("TDK", "https://www.tdk.com/en/news"),
        ("诺基亚", "https://www.nokia.com/news"),
        ("Lumentum", "https://www.lumentum.com/en/news"),
    ]

    print("=" * 70)
    print("Direct HTTP Fetch Test")
    print("=" * 70)

    for name, url in test_cases:
        print(f"\n[{name}] {url}")
        await test_direct_fetch(url, name)

    print("\n" + "=" * 70)
    print("Jina Reader API Test")
    print("=" * 70)

    for name, url in test_cases:
        print(f"\n[{name}] {url}")
        await test_jina_reader(url, name)

if __name__ == "__main__":
    asyncio.run(main())