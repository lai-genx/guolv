#!/usr/bin/env python3
"""
Web采集器URL诊断脚本 - 验证所有URL是否可正常访问
用法: python test_web_urls.py
"""

import asyncio
import httpx
from datetime import datetime
from loguru import logger
from collectors.web_sites_config import DEFAULT_SITES

# 配置日志
logger.remove()
logger.add(
    lambda msg: print(msg, end=''),
    format="{time:MM-DD HH:mm:ss} | {level: <8} | {message}"
)

class WebURLDiagnostic:
    """Web采集器URL诊断工具"""

    def __init__(self):
        self.timeout = 30
        self.results = []

    async def test_url(self, site_name: str, url: str) -> dict:
        """测试单个URL"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": "https://www.google.com/",
                }
            ) as client:
                response = await client.get(url)

                # 分析响应
                if response.status_code == 200:
                    status = "✓ OK"
                    icon = "✓"
                elif response.status_code == 403:
                    status = "! BLOCKED (403 Forbidden)"
                    icon = "✗"
                elif 300 <= response.status_code < 400:
                    status = f"→ REDIRECT ({response.status_code})"
                    icon = "→"
                else:
                    status = f"✗ ERROR ({response.status_code})"
                    icon = "✗"

                return {
                    "site": site_name,
                    "url": url,
                    "status_code": response.status_code,
                    "status": status,
                    "icon": icon,
                    "success": response.status_code == 200
                }

        except asyncio.TimeoutError:
            return {
                "site": site_name,
                "url": url,
                "status_code": None,
                "status": "✗ TIMEOUT",
                "icon": "✗",
                "success": False
            }
        except Exception as e:
            error_msg = str(e)
            if "redirect" in error_msg.lower():
                status = "✗ REDIRECT ERROR"
            else:
                status = f"✗ ERROR: {error_msg[:30]}"

            return {
                "site": site_name,
                "url": url,
                "status_code": None,
                "status": status,
                "icon": "✗",
                "success": False
            }

    async def diagnose_all(self):
        """诊断所有URL"""
        print("\n" + "=" * 80)
        print("Web采集器URL诊断 - %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 80 + "\n")

        # 并发测试所有URL
        tasks = [
            self.test_url(site["name"], site["url"])
            for site in DEFAULT_SITES
        ]

        self.results = await asyncio.gather(*tasks)

        # 按优先级分类显示
        print("测试结果:\n")

        for priority in ["P0", "P1", "P2"]:
            priority_sites = [
                s for s in self.results
                if any(
                    site["name"] == s["site"] and site.get("priority") == priority
                    for site in DEFAULT_SITES
                )
            ]

            if priority_sites:
                priority_names = {
                    "P0": "优先级最高 (主要企业)",
                    "P1": "优先级中等 (重要企业)",
                    "P2": "优先级较低 (其他企业)"
                }
                print(f"\n【{priority_names.get(priority, priority)}】\n")

                for result in priority_sites:
                    print(f"  {result['icon']} {result['site']:<15} {result['status']:<25} {result['url']}")

        # 统计信息
        success_count = sum(1 for r in self.results if r["success"])
        total_count = len(self.results)

        print("\n" + "=" * 80)
        print("统计:\n")
        print(f"  总计: {total_count} 个企业")
        print(f"  成功: {success_count} 个 ({success_count*100//total_count}%)")
        print(f"  失败: {total_count - success_count} 个")

        # 列出失败的企业
        failed = [r for r in self.results if not r["success"]]
        if failed:
            print(f"\n【需要修复的企业】\n")
            for result in failed:
                print(f"  - {result['site']:<15} {result['status']}")
                print(f"    URL: {result['url']}")

        print("\n" + "=" * 80 + "\n")

        return self.results

async def main():
    """主函数"""
    diagnostic = WebURLDiagnostic()
    results = await diagnostic.diagnose_all()

    # 返回成功/失败状态
    success_count = sum(1 for r in results if r["success"])
    return 0 if success_count >= len(results) * 0.8 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
