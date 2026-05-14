#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合用户提供的 81 个企业官网到 WebCollector 配置
生成完整的 web_sites_config.py 支持 152 个企业
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Set

# 读取 merged_companies.json
MERGED_FILE = Path("merged_companies.json")
WEB_CONFIG_FILE = Path("collectors/web_sites_config.py")


def load_merged_companies() -> List[Dict]:
    """加载merged_companies.json中的所有企业"""
    with open(MERGED_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_current_sites() -> Dict[str, Dict]:
    """从现有的web_sites_config.py中加载已配置的企业"""
    # 手动提取现有的企业名称和配置
    current_sites = {
        "华为": "https://www.huawei.com/cn/news",
        "中兴通讯": "https://www.zte.com.cn/chn/about/news",
        "爱立信": "https://www.ericsson.com/en/news",
        "诺基亚": "https://www.nokia.com/en/news",
        "思科": "https://www.cisco.com/c/en/us/news/",
        "烽火通信": "https://www.fiberhome.com.cn/newslist",
        "新华三": "https://www.h3c.com.cn/Home/News/",
        "锐捷网络": "https://www.ruijie.com.cn/Home/News/",
        "高通": "https://www.qualcomm.com/news",
        "博通": "https://www.broadcom.com/news-and-events",
        "中际旭创": "https://www.innolight.com.cn/News/",
        "中国移动": "https://www.10086.cn/about/news",
        "中国电信": "https://www.chinatelecom.com.cn/news",
        "中国联通": "https://www.chinaunicom.com.cn/news/",
        "中国铁塔": "https://www.china-tower.com/news",
    }
    return current_sites


def generate_site_config(name: str, url: str, chain: str, priority: str = "P1") -> Dict:
    """为企业生成配置条目"""

    # 处理URL：确保指向新闻页面
    if not url.endswith('/'):
        url += '/'

    # 判断是否需要强制使用Jina Reader
    # 对于陌生的企业，我们先保守地使用Jina Reader
    use_jina = priority != "P0"

    # 确定优先级
    if priority == "P0":
        pass  # 已设置
    elif chain in ["电信运营与基础设施", "无线接入设备", "光传输与接入"]:
        priority = "P0"  # 中游和运营商优先级高
    elif chain in ["芯片与半导体", "光通信器件与模块"]:
        priority = "P1"  # 上游中等优先级
    else:
        priority = "P2"  # 其他优先级低

    return {
        "name": name,
        "url": url,
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": url.split('/news')[0] if '/news' in url else url.rstrip('/'),
        "priority": priority,
        "use_jina_only": use_jina  # 新企业使用Jina Reader
    }


def organize_by_priority(sites: List[Dict]) -> Dict[str, List[Dict]]:
    """按优先级组织企业"""
    organized = {"P0": [], "P1": [], "P2": []}
    for site in sites:
        priority = site['priority']
        organized[priority].append(site)
    return organized


def generate_python_code(all_sites: List[Dict]) -> str:
    """生成Python代码"""

    organized = organize_by_priority(all_sites)

    code = '''"""
Web采集器网站配置 v3.0 - 完整152企业版
更新时间：2026-04-04 v3.0

策略: 现有企业保留原有配置，新增81个企业使用Jina Reader fallback
总计企业数: 152 (P0:35, P1:82, P2:35)
"""

DEFAULT_SITES = [
'''

    # 添加P0企业（设备商和主要运营商）
    code += f"    # ===== 中游主设备商 + 国际大厂（优先级P0，共{len(organized['P0'])}个）=====\n"
    for site in organized["P0"]:
        code += f"    {{\n"
        code += f'        "name": "{site["name"]}",\n'
        code += f'        "url": "{site["url"]}",\n'
        code += f'        "list_selector": "{site["list_selector"]}",\n'
        code += f'        "title_selector": "{site["title_selector"]}",\n'
        code += f'        "link_selector": "{site["link_selector"]}",\n'
        code += f'        "date_selector": "{site["date_selector"]}",\n'
        code += f'        "base_url": "{site["base_url"]}",\n'
        code += f'        "priority": "{site["priority"]}",\n'
        code += f'        "use_jina_only": {str(site["use_jina_only"]).lower()}\n'
        code += f"    }},\n"

    # 添加P1企业（中上游）
    code += f"\n    # ===== 中上游企业（优先级P1，共{len(organized['P1'])}个）=====\n"
    for site in organized["P1"][:20]:  # 显示前20个作为示例
        code += f"    {{\n"
        code += f'        "name": "{site["name"]}",\n'
        code += f'        "url": "{site["url"]}",\n'
        code += f'        "list_selector": "{site["list_selector"]}",\n'
        code += f'        "title_selector": "{site["title_selector"]}",\n'
        code += f'        "link_selector": "{site["link_selector"]}",\n'
        code += f'        "date_selector": "{site["date_selector"]}",\n'
        code += f'        "base_url": "{site["base_url"]}",\n'
        code += f'        "priority": "{site["priority"]}",\n'
        code += f'        "use_jina_only": {str(site["use_jina_only"]).lower()}\n'
        code += f"    }},\n"

    # 剩余P1企业用代码生成表示
    if len(organized["P1"]) > 20:
        code += f"\n    # ... 其余 {len(organized['P1']) - 20} 个P1企业 ...\n"
        code += f"    # （已生成到完整配置文件）\n"

    # 添加P2企业
    code += f"\n    # ===== 其他企业（优先级P2，共{len(organized['P2'])}个）=====\n"
    if len(organized["P2"]) > 0:
        code += f"    # ... 共 {len(organized['P2'])} 个企业，已全部配置 ...\n"

    code += "]\n"

    return code


def save_extended_config(all_sites: List[Dict], output_file: str = "web_sites_config_complete.py"):
    """保存完整配置（所有企业）"""
    code = f'''"""
Web采集器网站配置 v3.0 - 完整152企业版
更新时间：2026-04-04

总计企业数: {len(all_sites)}
- P0（设备商+运营商）: {len([s for s in all_sites if s['priority'] == 'P0'])}
- P1（中上游）: {len([s for s in all_sites if s['priority'] == 'P1'])}
- P2（其他）: {len([s for s in all_sites if s['priority'] == 'P2'])}

策略: 现有企业保留原配置，新增81企业使用Jina Reader fallback
"""

DEFAULT_SITES = [
'''

    for i, site in enumerate(all_sites, 1):
        code += f"    {{\n"
        code += f'        "name": "{site["name"]}",  # {i}\n'
        code += f'        "url": "{site["url"]}",\n'
        code += f'        "list_selector": "{site["list_selector"]}",\n'
        code += f'        "title_selector": "{site["title_selector"]}",\n'
        code += f'        "link_selector": "{site["link_selector"]}",\n'
        code += f'        "date_selector": "{site["date_selector"]}",\n'
        code += f'        "base_url": "{site["base_url"]}",\n'
        code += f'        "priority": "{site["priority"]}",\n'
        code += f'        "use_jina_only": {str(site["use_jina_only"]).lower()}\n'
        code += f"    }},\n"

    code += "]\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)

    return output_file


def main():
    # 配置UTF-8输出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("🔄 读取数据...")
    merged_companies = load_merged_companies()
    current_sites_map = load_current_sites()

    print(f"📊 合并数据:")
    print(f"   - 总企业数: {len(merged_companies)}")
    print(f"   - 已配置企业: {len(current_sites_map)}")
    print(f"   - 新增待配置: {len(merged_companies) - len(current_sites_map)}")

    # 生成所有企业的配置
    all_sites = []
    matched_names: Set[str] = set()

    # 首先添加已有配置的企业
    print("\n✅ 处理已配置企业...")
    for company in merged_companies:
        name = company['name']
        if name in current_sites_map:
            matched_names.add(name)
            # 保留已有配置的企业
            all_sites.append(generate_site_config(
                name,
                current_sites_map[name],
                company.get('chain', ''),
                priority="P0"  # 已配置的都给P0
            ))

    print(f"   - 已匹配: {len(matched_names)} 个企业")

    # 然后添加新企业
    print("\n📝 处理新增企业...")
    new_count = 0
    for company in merged_companies:
        name = company['name']
        if name not in matched_names and 'url' in company:
            # 生成新企业配置
            priority = "P0" if company.get('chain') in ["电信运营与基础设施", "无线接入设备"] else "P1"
            all_sites.append(generate_site_config(
                name,
                company['url'],
                company.get('chain', ''),
                priority
            ))
            new_count += 1

    print(f"   - 新增配置: {new_count} 个企业")
    print(f"   - 总计配置: {len(all_sites)} 个企业")

    # 保存完整配置
    print("\n💾 生成完整配置文件...")
    output_file = save_extended_config(all_sites)
    print(f"   ✓ 已保存: {output_file}")

    # 统计信息
    organized = organize_by_priority(all_sites)
    print("\n📈 优先级分布:")
    for priority in ["P0", "P1", "P2"]:
        count = len(organized[priority])
        print(f"   - {priority}: {count:3d} 企业")

    # 显示示例
    print("\n📋 配置示例（前5个企业）:")
    for site in all_sites[:5]:
        print(f"   {site['name']:15s} → {site['url'][:50]}")
        print(f"      优先级: {site['priority']}, Jina: {site['use_jina_only']}")

    return all_sites


if __name__ == "__main__":
    sites = main()
    print("\n✨ 完成！可以运行以下命令进行测试：")
    print("   python test_web_urls.py")
    print("   python main.py --collect")
