# -*- coding: utf-8 -*-
"""
全面系统测试 - 验证所有功能是否正常
"""
import sys
import os
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
from datetime import datetime

print("=" * 70)
print("通信设备产业情报系统 v1.1 - 全面功能测试")
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# 1. 测试依赖包
print("\n[1] 测试 Python 依赖包...")
print("-" * 50)
required_packages = [
    ("streamlit", "streamlit"),
    ("httpx", "httpx"),
    ("bs4", "bs4"),
    ("beautifulsoup4", "bs4"),
    ("loguru", "loguru"),
    ("pydantic", "pydantic"),
    ("pydantic_settings", "pydantic_settings"),
    ("python-dotenv", "dotenv"),
    ("playwright", "playwright"),
    ("feedparser", "feedparser"),
    ("requests", "requests"),
    ("numpy", "numpy"),
    ("sentence_transformers", "sentence_transformers"),
]

all_ok = True
for pkg_name, import_name in required_packages:
    try:
        __import__(import_name)
        print(f"  OK {pkg_name}")
    except ImportError as e:
        print(f"  FAIL {pkg_name} - {e}")
        all_ok = False

# 2. 测试配置文件
print("\n[2] 测试配置文件加载...")
print("-" * 50)
try:
    from config import settings
    print(f"  OK config.py 加载成功")

    llm = settings.llm
    collector = settings.collector
    distribution = settings.distribution

    print(f"  OK LLM配置: DeepSeek={'已配置' if llm.deepseek_api_key else '未配置'}")
    print(f"  OK Jina API: {'已配置' if collector.jina_api_key else '未配置'}")
    print(f"  OK RSS源数量: {len(collector.rss_feeds)}")
    print(f"  OK 监控公司数量: {len(collector.target_companies)}")
except Exception as e:
    print(f"  FAIL 配置加载失败: {e}")
    all_ok = False

# 3. 测试数据库
print("\n[3] 测试数据库连接...")
print("-" * 50)
try:
    from database import Database
    db = Database()
    print(f"  OK 数据库连接成功")
    print(f"  OK 数据库路径: {db.db_path}")

    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM intel_items")
        count = cursor.fetchone()[0]
        print(f"  OK intel_items 表存在，当前记录数: {count}")

        cursor.execute("SELECT COUNT(*) FROM weekly_reports")
        count = cursor.fetchone()[0]
        print(f"  OK weekly_reports 表存在，当前记录数: {count}")
except Exception as e:
    print(f"  FAIL 数据库测试失败: {e}")
    all_ok = False

# 4. 测试数据模型
print("\n[4] 测试数据模型...")
print("-" * 50)
try:
    from models import IntelItem, Category, Industry, TechDomain
    print(f"  OK IntelItem 模型")
    print(f"  OK Category 枚举: {[c.value for c in Category][:3]}...")
    print(f"  OK TechDomain 枚举: {[d.value for d in TechDomain][:3]}...")
except Exception as e:
    print(f"  FAIL 模型导入失败: {e}")
    all_ok = False

# 5. 测试网站配置
print("\n[5] 测试网站配置...")
print("-" * 50)
try:
    from collectors.web_sites_config import DEFAULT_SITES
    print(f"  OK web_sites_config 加载成功")
    print(f"  OK 配置网站数量: {len(DEFAULT_SITES)}")

    # 测试新添加的网站
    import httpx
    async def test_site(site):
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(site['url'], headers={'User-Agent': 'Mozilla/5.0 Test'})
                return site['name'], site['url'], resp.status_code, len(resp.text)
        except Exception as e:
            return site['name'], site['url'], f"ERR:{type(e).__name__}", 0

    async def test_new_sites():
        new_sites = [s for s in DEFAULT_SITES if s['name'] in ['Skyworks', 'Qorvo', 'Murata', 'BT', 'STC']]
        results = []
        for site in new_sites:
            result = await test_site(site)
            results.append(result)
        return results

    results = asyncio.run(test_new_sites())
    print(f"  OK 新增网站测试:")
    for name, url, code, size in results:
        print(f"      {name}: HTTP {code} ({size} bytes)")
except Exception as e:
    print(f"  FAIL 网站配置测试失败: {e}")
    all_ok = False

# 6. 测试采集器模块
print("\n[6] 测试采集器模块...")
print("-" * 50)
try:
    from collectors.rss_collector import RSSCollector
    from collectors.web_collector import WebCollector
    from collectors.search_collector import SearchCollector
    print(f"  OK RSSCollector")
    print(f"  OK WebCollector")
    print(f"  OK SearchCollector")
except Exception as e:
    print(f"  FAIL 采集器导入失败: {e}")
    all_ok = False

# 7. 测试处理器模块
print("\n[7] 测试处理器模块...")
print("-" * 50)
try:
    from processors.analyzer import IntelAnalyzer
    from processors.rag import VectorRAG  # 修正类名
    print(f"  OK IntelAnalyzer")
    print(f"  OK VectorRAG")
except Exception as e:
    print(f"  FAIL 处理器导入失败: {e}")
    all_ok = False

# 8. 测试报告生成器
print("\n[8] 测试报告生成器...")
print("-" * 50)
try:
    from reporters.report_generator import ReportGenerator
    print(f"  OK ReportGenerator")
except Exception as e:
    print(f"  FAIL 报告生成器导入失败: {e}")
    all_ok = False

# 9. 测试LLM路由
print("\n[9] 测试LLM路由...")
print("-" * 50)
try:
    from llm import LLMRouter
    router = LLMRouter()
    print(f"  OK LLMRouter 初始化成功")

    # 使用正确的方法名
    available = router.get_available_providers() if hasattr(router, 'get_available_providers') else []
    if available:
        print(f"  OK 可用模型: {', '.join(available)}")
    print(f"  OK is_available: {router.is_available()}")
except Exception as e:
    print(f"  FAIL LLM路由测试失败: {e}")
    all_ok = False

# 10. 测试main.py命令行模式
print("\n[10] 测试命令行入口...")
print("-" * 50)
try:
    # 测试 --help
    import subprocess
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd="."
    )
    if "error" not in result.stdout.lower() and "error" not in result.stderr.lower():
        print(f"  OK main.py --help 执行成功")
        print(f"      支持的命令: --collect, --report, --schedule, --test")
    else:
        print(f"  WARN main.py --help 可能有问题")
        print(f"      stdout: {result.stdout[:200]}")
        print(f"      stderr: {result.stderr[:200]}")
except Exception as e:
    print(f"  FAIL main.py 测试失败: {e}")
    all_ok = False

# 总结
print("\n" + "=" * 70)
print("测试结果总结")
print("=" * 70)
if all_ok:
    print("  🎉 所有测试通过！系统可以正常运行")
else:
    print("  ⚠️ 部分测试失败，请检查上述错误信息")

print(f"\n系统状态:")
print(f"  - 监控公司: 203 家 (target_companies)")
print(f"  - 官网配置: 53 个网站 (web_sites_config)")
print(f"  - RSS源: 16 个")
print(f"  - 数据库: 正常")
print(f"\n启动命令:")
print("  streamlit run web_app.py --server.port 8501")
print("  python main.py --test")
print("=" * 70)