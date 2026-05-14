#!/usr/bin/env python3
"""
RSS源可用性验证脚本
用于快速检查所有RSS源是否可访问和工作正常
"""

import asyncio
import httpx
from typing import List, Dict
from datetime import datetime
from loguru import logger

# 配置日志
logger.add("rss_verify.log", level="INFO")

# RSS源列表（与config.py保持一致）
RSS_FEEDS = [
    ("ITmedia 综合头条", "https://www.itmedia.co.jp/rss/2.0/news_bursts.xml"),
    ("ITmedia NEWS", "https://www.itmedia.co.jp/rss/2.0/news.xml"),
    ("ITmedia AI+", "https://www.itmedia.co.jp/rss/2.0/aiplus.xml"),
    ("ITmedia Mobile", "https://www.itmedia.co.jp/rss/2.0/mobile.xml"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("TechRadar", "https://www.techradar.com/rss.xml"),
    ("Light Reading", "https://www.lightreading.com/feeds/all.xml"),
    ("Semiconductor Digest", "https://www.semiconductordigest.com/feed"),
    ("EE News Analog", "https://www.eenewsanalog.com/rss.xml"),
]

class RSSVerifier:
    """RSS源验证器"""

    def __init__(self):
        self.results: List[Dict] = []
        self.client = httpx.AsyncClient(timeout=20)

    async def verify_url(self, name: str, url: str) -> Dict:
        """验证单个RSS源"""
        try:
            response = await self.client.get(url)

            # 检查状态码
            if response.status_code == 200:
                # 验证是否为有效的RSS/XML
                content = response.text
                if '<?xml' in content or '<rss' in content or '<feed' in content:
                    # 尝试计算条目数
                    item_count = content.count('<item>') + content.count('<entry>')
                    return {
                        'name': name,
                        'url': url,
                        'status': '✅ 可用',
                        'status_code': 200,
                        'items': item_count,
                        'error': None
                    }
                else:
                    return {
                        'name': name,
                        'url': url,
                        'status': '⚠️ 非RSS',
                        'status_code': 200,
                        'items': 0,
                        'error': '返回的不是有效RSS格式'
                    }
            else:
                return {
                    'name': name,
                    'url': url,
                    'status': f'❌ HTTP{response.status_code}',
                    'status_code': response.status_code,
                    'items': 0,
                    'error': f'HTTP状态码: {response.status_code}'
                }

        except asyncio.TimeoutError:
            return {
                'name': name,
                'url': url,
                'status': '⏱️ 超时',
                'status_code': 0,
                'items': 0,
                'error': '请求超时（可能是网络问题）'
            }

        except Exception as e:
            return {
                'name': name,
                'url': url,
                'status': '❌ 错误',
                'status_code': 0,
                'items': 0,
                'error': str(e)
            }

    async def verify_all(self) -> None:
        """验证所有RSS源"""
        print("\n" + "="*100)
        print("🔍 RSS源可用性验证 - 开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*100 + "\n")

        # 并发验证所有源
        tasks = [self.verify_url(name, url) for name, url in RSS_FEEDS]
        self.results = await asyncio.gather(*tasks)

        # 生成报告
        self._print_report()
        self._save_report()

        await self.client.aclose()

    def _print_report(self) -> None:
        """打印验证报告"""
        # 统计
        available = sum(1 for r in self.results if '✅' in r['status'])
        total = len(self.results)

        print(f"📊 验证统计: {available}/{total} 源可用 ({available*100//total}%)\n")

        # 表格显示
        print(f"{'序号':<4} {'状态':<12} {'来源':<20} {'条目数':<8} {'说明':<50}")
        print("-" * 100)

        for i, result in enumerate(self.results, 1):
            name = result['name'][:19]
            status = result['status']
            items = result['items']
            error = result['error'] or (f"{items}条新闻" if items > 0 else "")

            print(f"{i:<4} {status:<12} {name:<20} {items:<8} {error[:48]:<50}")

        # 详细结果
        print("\n" + "="*100)
        print("📋 详细结果:\n")

        for result in self.results:
            symbol = "✅" if "✅" in result['status'] else "❌" if "❌" in result['status'] else "⚠️"
            print(f"{symbol} {result['name']}")
            print(f"   URL: {result['url']}")
            print(f"   状态: {result['status']}")
            if result['error']:
                print(f"   错误: {result['error']}")
            if result['items'] > 0:
                print(f"   新闻条数: {result['items']}")
            print()

    def _save_report(self) -> None:
        """保存报告到文件"""
        with open('rss_verify_report.txt', 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write(f"RSS源可用性验证报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*100 + "\n\n")

            available = sum(1 for r in self.results if '✅' in r['status'])
            total = len(self.results)
            f.write(f"验证统计: {available}/{total} 源可用 ({available*100//total}%)\n\n")

            for i, result in enumerate(self.results, 1):
                f.write(f"{i}. {result['name']}\n")
                f.write(f"   URL: {result['url']}\n")
                f.write(f"   状态: {result['status']}\n")
                if result['error']:
                    f.write(f"   错误: {result['error']}\n")
                if result['items'] > 0:
                    f.write(f"   新闻条数: {result['items']}\n")
                f.write("\n")

        print("📄 报告已保存到: rss_verify_report.txt")


async def main():
    """主函数"""
    verifier = RSSVerifier()
    await verifier.verify_all()


if __name__ == "__main__":
    asyncio.run(main())
