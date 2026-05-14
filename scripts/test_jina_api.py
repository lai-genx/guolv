# -*- coding: utf-8 -*-
"""
测试Jina Reader API - 使用正确的端点格式
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
    """使用Jina Reader API抓取网页 - r.jina.ai端点"""
    api_key = os.getenv('COLLECTOR__JINA_API_KEY', '')

    if not api_key:
        print(f"  Jina API Key not configured")
        return None

    # Using r.jina.ai endpoint as per the web_collector.py
    jina_url = f"https://r.jina.ai/{url}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "text/plain"
            }
            resp = await client.get(jina_url, headers=headers)

            if resp.status_code == 200:
                content = resp.text
                print(f"  Jina success! Content length: {len(content)} chars")

                # Parse the content - it returns markdown
                lines = content.split('\n')
                # Find news items (lines starting with #)
                news_lines = [l for l in lines if l.strip().startswith('# ')]
                print(f"  News lines found: {len(news_lines)}")

                if news_lines:
                    print(f"  Sample titles:")
                    for line in news_lines[:5]:
                        print(f"    - {line[:80]}")

                return True
            else:
                print(f"  Error: {resp.status_code} - {resp.text[:100]}")
                return False
    except Exception as e:
        print(f"  Exception: {e}")
        return None

async def main():
    test_cases = [
        ("高通", "https://www.qualcomm.com/news"),
        ("Skyworks", "https://www.skyworksinc.com/news"),
        ("博通", "https://www.broadcom.com/blog"),
        ("诺基亚", "https://www.nokia.com/news"),
        ("Lumentum", "https://www.lumentum.com/en/news"),
    ]

    print("=" * 70)
    print("Jina Reader API Test (r.jina.ai endpoint)")
    print("=" * 70)

    for name, url in test_cases:
        print(f"\n[{name}] {url}")
        await test_jina_reader(url, name)

if __name__ == "__main__":
    asyncio.run(main())