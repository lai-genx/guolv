#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 Web 采集器的 CSS 选择器配置
问题: 许多企业网站的实际HTML结构与现有选择器不匹配
解决: 使用更通用、更智能的选择器策略
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

# 生成改进的CSS选择器配置
IMPROVED_SELECTORS = {
    # 列表容器选择器（优先级顺序）
    "list_selector": [
        # 标准新闻/文章容器
        "article",
        ".news-item",
        ".news-article",
        "[role='article']",
        ".press-release",
        ".blog-post",
        ".post-item",
        ".content-item",
        # 容器包装
        ".news-list",
        ".news-container",
        ".article-list",
        ".articles",
        ".posts",
        ".stories",
        # 通用容器
        ".item",
        ".entry",
        ".card",
        "li[class*='news']",
        "div[class*='article']",
        "section[class*='news']",
    ],

    # 标题选择器
    "title_selector": [
        "h1",
        "h2",
        "h3",
        ".title",
        ".headline",
        ".news-title",
        "[class*='title']",
        ".heading",
        ".post-title",
        "a[href]",  # 备用：直接用链接文本
    ],

    # 链接选择器
    "link_selector": [
        "a[href*='news']",
        "a[href*='press']",
        "a[href*='article']",
        "a[href*='blog']",
        "a[href]",  # 通用链接
    ],

    # 日期选择器
    "date_selector": [
        "time",
        ".date",
        ".publish-date",
        ".posted-on",
        "[class*='date']",
        ".meta-date",
        ".timestamp",
        "[data-date]",
    ]
}

# 生成改进的配置函数
def generate_improved_config(name: str, url: str, priority: str = "P1") -> dict:
    """生成改进的网站配置"""

    # 转换列表为CSS选择器字符串（用逗号分隔）
    def selector_list_to_string(selectors: list) -> str:
        return ", ".join(selectors)

    return {
        "name": name,
        "url": url,
        "list_selector": selector_list_to_string(IMPROVED_SELECTORS["list_selector"]),
        "title_selector": selector_list_to_string(IMPROVED_SELECTORS["title_selector"]),
        "link_selector": selector_list_to_string(IMPROVED_SELECTORS["link_selector"]),
        "date_selector": selector_list_to_string(IMPROVED_SELECTORS["date_selector"]),
        "base_url": url.split('/news')[0] if '/news' in url else url.rstrip('/'),
        "priority": priority,
        "use_jina_only": True,  # 所有新企业都用Jina+智能选择器
    }

# 失败的企业列表（需要修复）
FAILED_COMPANIES = {
    "思科": ("https://www.cisco.com/c/en/us/news/", "P0"),
    "爱立信": ("https://www.ericsson.com/en/news/", "P0"),
    "烽火通信": ("https://www.fiberhome.com.cn/newslist/", "P1"),
    "新华三": ("https://www.h3c.com.cn/Home/News/", "P1"),
    "锐捷网络": ("https://www.ruijie.com.cn/Home/News/", "P1"),
    "高通": ("https://www.qualcomm.com/news", "P0"),
    "英特尔": ("https://www.intel.com/", "P0"),
    "Coherent": ("https://www.coherent.com/", "P0"),
    "Lumentum": ("https://www.lumentum.com/", "P0"),
    "Broadcom": ("https://www.broadcom.com/", "P0"),
    "中际旭创": ("https://www.innolight.com.cn/News/", "P1"),
    "中国移动": ("https://www.10086.cn/about/news/", "P0"),
    "中国电信": ("https://www.chinatelecom.com.cn/news", "P0"),
    "中国联通": ("https://www.chinaunicom.com.cn/news/", "P0"),
    "中国铁塔": ("https://www.china-tower.com/news", "P2"),
    "光迅科技": ("https://www.accelink.com/", "P1"),
    "康普通讯": ("https://www.commscope.com/", "P0"),
    "凯士林": ("https://www.kathrein.com/", "P0"),
    "RFS": ("https://www.rfsworld.com/", "P0"),
    "华工正源": ("https://www.hgzy.com.cn/", "P1"),
    "仕佳光子": ("https://www.shijiaphotonics.com/", "P1"),
    "唯捷创芯": ("http://www.wayjem.com/", "P1"),
    "中科汉天下": ("http://www.hexintek.com/", "P1"),
    "卓胜微": ("https://www.zhuoshengwei.com/", "P1"),
    "慧智微": ("https://www.microintelli.com/", "P1"),
    "格科微电子": ("https://www.gcoreinc.com/", "P1"),
    "源杰科技": ("https://www.synlighttech.com/", "P1"),
    "海信宽带": ("https://www.hisense-broadband.com/", "P1"),
    "新易盛": ("https://www.eoptolink.com/", "P1"),
    "摩比发展": ("https://www.mobie.com.cn/", "P1"),
    "大富科技": ("https://www.tuftiem.com/", "P1"),
    "天孚通信": ("https://www.turfib.com/", "P1"),
    "京信通信": ("https://www.comba.net.cn/", "P1"),
    "通宇通讯": ("https://www.tytx.com.cn/", "P1"),
    "东山精密": ("https://www.dongsheng.com/", "P1"),
    "武汉凡谷": ("https://www.fangu.com/", "P1"),
    "翱捷科技": ("https://www.asrmicro.com/", "P0"),
    "紫光展锐": ("https://www.unisoc.com/", "P0"),
    "移芯通信": ("https://www.xtechcomm.com/", "P0"),
    "瑞芯微电子": ("https://www.rock-chips.com/", "P0"),
    "思比科": ("https://www.siliconimage.com.cn/", "P0"),
    "联发科": ("https://www.mediatek.com/", "P0"),
    "三星LSI": ("https://semiconductor.samsung.com/", "P0"),
    "德州仪器": ("https://www.ti.com/", "P0"),
}

def main():
    print("\n" + "="*80)
    print("  Web采集器 CSS 选择器修复工具")
    print("="*80 + "\n")

    print(f"需要修复的企业数: {len(FAILED_COMPANIES)}\n")

    # 生成改进的配置
    improved_configs = []
    for name, (url, priority) in FAILED_COMPANIES.items():
        config = generate_improved_config(name, url, priority)
        improved_configs.append(config)

    # 输出Python代码
    print("以下是改进的配置（可直接复制到web_sites_config.py）:\n")
    print("-" * 80)
    print("\nFAILED_COMPANIES_IMPROVED = [")

    for config in improved_configs:
        print(f"\n    {{\n        \"name\": \"{config['name']}\",")
        print(f"        \"url\": \"{config['url']}\",")
        print(f"        \"list_selector\": \"{config['list_selector'][:100]}...\",")
        print(f"        \"title_selector\": \"{config['title_selector'][:100]}...\",")
        print(f"        \"link_selector\": \"{config['link_selector'][:80]}...\",")
        print(f"        \"date_selector\": \"{config['date_selector'][:80]}...\",")
        print(f"        \"base_url\": \"{config['base_url']}\",")
        print(f"        \"priority\": \"{config['priority']}\",")
        print(f"        \"use_jina_only\": True")
        print(f"    }},")

    print("]\n")
    print("-" * 80)

    # 保存完整配置到JSON
    import json
    with open('improved_web_selectors.json', 'w', encoding='utf-8') as f:
        json.dump(improved_configs, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 改进的配置已保存到: improved_web_selectors.json")
    print(f"\n📊 统计信息:")
    print(f"   • 需要修复的企业: {len(FAILED_COMPANIES)}")
    print(f"   • 列表选择器选项: {len(IMPROVED_SELECTORS['list_selector'])}")
    print(f"   • 标题选择器选项: {len(IMPROVED_SELECTORS['title_selector'])}")
    print(f"   • 链接选择器选项: {len(IMPROVED_SELECTORS['link_selector'])}")
    print(f"   • 日期选择器选项: {len(IMPROVED_SELECTORS['date_selector'])}")

    print(f"\n💡 改进策略:")
    print(f"   ✓ 使用多个备选选择器（提高匹配率）")
    print(f"   ✓ 所有企业启用 Jina Reader（确保内容获取）")
    print(f"   ✓ 选择器按通用性排序（优先匹配通用选择器）")

    return improved_configs

if __name__ == "__main__":
    configs = main()
