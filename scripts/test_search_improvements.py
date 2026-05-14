#!/usr/bin/env python3
"""
Search采集器改进验证脚本
用于测试和验证HTML提取、Jina fallback等新功能
"""

import asyncio
import sys
from loguru import logger
from collectors.search_collector import SearchCollector

# 配置日志
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>")
logger.add("data/search_collector_test.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")


async def test_single_search(collector: SearchCollector, query: str, max_results: int = 3):
    """测试单个搜索查询"""
    logger.info(f"🔍 测试搜索: {query}")

    try:
        items = await collector._search(query, max_results)

        logger.info(f"✓ 搜索成功，获得 {len(items)} 条结果")

        for i, item in enumerate(items[:3], 1):
            logger.info(f"\n  【结果 {i}】")
            logger.info(f"  标题: {item.title[:60]}...")
            logger.info(f"  URL: {item.url[:80]}...")
            logger.info(f"  源: {item.source}")
            logger.info(f"  摘要: {item.summary[:100]}...")

        return len(items) > 0

    except Exception as e:
        logger.error(f"✗ 搜索失败: {e}", exc_info=True)
        return False


async def test_html_extraction(collector: SearchCollector):
    """测试HTML选择器覆盖"""
    logger.info("\n" + "="*60)
    logger.info("测试1: HTML选择器覆盖")
    logger.info("="*60)

    import urllib.parse
    from bs4 import BeautifulSoup

    # 构建搜索URL
    query = "5G 通信 华为"
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.bing.com/search?q={encoded_query}"

    logger.info(f"🌐 正在获取: {search_url}")

    try:
        response = await collector.client.get(search_url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        # 测试所有选择器
        selectors = [
            '.b_algo',
            'div.b_algo',
            '.b_results > li',
            'li.b_algo',
            '[data-module-id*="organic"]',
            '.result-item',
            'article',
            'div[data-bm]',
            '.ckSGb',
            'main > div',
        ]

        logger.info(f"\n测试 {len(selectors)} 个选择器:")

        for selector in selectors:
            try:
                elements = soup.select(selector)[:3]
                status = f"✓ {len(elements)} 元素" if elements else "✗ 0 元素"
                logger.info(f"  {selector:<35} {status}")
            except Exception as e:
                logger.warning(f"  {selector:<35} ⚠ 错误: {e}")

        return True

    except Exception as e:
        logger.error(f"✗ HTML获取失败: {e}")
        return False


async def test_item_extraction(collector: SearchCollector):
    """测试元素提取逻辑"""
    logger.info("\n" + "="*60)
    logger.info("测试2: 元素详情提取")
    logger.info("="*60)

    test_cases = [
        ("华为 5G 最新动态", "测试中文搜索"),
        ("Huawei 5G news", "测试英文搜索"),
        ("optical fiber communication", "测试技术词搜索"),
    ]

    for query, description in test_cases:
        logger.info(f"\n{description}: {query}")
        success = await test_single_search(collector, query, max_results=2)

        if not success:
            logger.warning(f"  ⚠ 此查询未能获得结果")

    return True


async def test_jina_fallback(collector: SearchCollector):
    """测试Jina Reader API fallback"""
    logger.info("\n" + "="*60)
    logger.info("测试3: Jina Reader API Fallback")
    logger.info("="*60)

    from config import settings

    if not settings.collector.jina_api_key:
        logger.warning("⚠ Jina API密钥未配置，跳过此测试")
        return None

    logger.info(f"✓ Jina API已配置")
    logger.info(f"  API密钥前缀: {settings.collector.jina_api_key[:20]}...")

    # 尝试调用Jina
    logger.info("\n测试Jina Reader调用:")

    try:
        items = await collector._jina_search("华为 通信", max_results=2)

        if items:
            logger.info(f"✓ Jina调用成功，获得 {len(items)} 条结果")
            for item in items[:2]:
                logger.info(f"  - {item.title[:50]}...")
            return True
        else:
            logger.warning("⚠ Jina调用完成但未获得结果")
            return False

    except Exception as e:
        logger.error(f"✗ Jina调用失败: {e}")
        return False


async def test_validation(collector: SearchCollector):
    """测试结果验证框架"""
    logger.info("\n" + "="*60)
    logger.info("测试4: 结果验证框架")
    logger.info("="*60)

    test_cases = [
        # (title, url, should_be_valid, reason)
        ("正常标题", "https://example.com/news", True, "正常中文标题"),
        ("", "https://example.com", False, "空标题"),
        ("标题", "https://bing.com/search", False, "Bing内部链接"),
        ("a", "https://example.com", False, "标题太短（1个中文字）"),
        ("这是一个非常长的标题" * 20, "https://example.com", False, "标题太长"),
        ("123456", "https://example.com", False, "纯数字"),
        ("通信设备 5G", "https://news.example.com", True, "中英混合标题"),
    ]

    logger.info(f"\n验证 {len(test_cases)} 个测试用例:\n")

    passed = 0
    for title, url, expected, reason in test_cases:
        result = collector._is_valid_result(title, url)
        status = "✓" if result == expected else "✗"

        if result == expected:
            passed += 1

        logger.info(f"{status} {reason}")
        logger.info(f"   标题: '{title[:30]}...' | URL: {url[:50]}...")
        logger.info(f"   预期: {expected} | 实际: {result}\n")

    logger.info(f"验证通过: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


async def main():
    """运行所有测试"""
    logger.info("\n" + "="*60)
    logger.info("CT产业情报 - Search采集器改进验证")
    logger.info("="*60)
    logger.info(f"启动时间: {asyncio.get_event_loop().time()}")

    # 创建采集器实例
    collector = SearchCollector()

    results = {}

    # 测试1: HTML选择器
    logger.info("\n⏳ 运行测试1...")
    results['HTML选择器'] = await test_html_extraction(collector)

    # 测试2: 元素提取
    logger.info("\n⏳ 运行测试2...")
    results['元素提取'] = await test_item_extraction(collector)

    # 测试3: Jina Fallback
    logger.info("\n⏳ 运行测试3...")
    results['Jina Fallback'] = await test_jina_fallback(collector)

    # 测试4: 验证框架
    logger.info("\n⏳ 运行测试4...")
    results['验证框架'] = await test_validation(collector)

    # 总结
    logger.info("\n" + "="*60)
    logger.info("测试总结")
    logger.info("="*60)

    for test_name, result in results.items():
        if result is None:
            status = "⊗ 跳过"
        elif result:
            status = "✓ 通过"
        else:
            status = "✗ 失败"
        logger.info(f"{status:8} {test_name}")

    # 关闭连接
    await collector.client.aclose()

    logger.info("\n✓ 测试完成！日志已保存到 data/search_collector_test.log")


if __name__ == "__main__":
    asyncio.run(main())
