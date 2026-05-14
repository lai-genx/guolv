#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新config.py中的target_companies为完整的152企业列表
"""

import json
import re
from pathlib import Path

# 读取所有企业名称
with open('merged_companies.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

names = sorted(list(set([c['name'] for c in companies])))

# 生成新的target_companies
target_companies_code = '    target_companies: List[str] = Field(default=[\n'
for i, name in enumerate(names):
    name_escaped = name.replace('"', '\\"')
    target_companies_code += f'        "{name_escaped}",\n'
target_companies_code += '    ], description="监控的目标公司列表")\n'

# 读取config.py
with open('config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

# 找到并替换target_companies部分
# 使用正则表达式匹配从 target_companies: List[str] = Field(default=[ 到 ], description= 的部分
pattern = r'target_companies: List\[str\] = Field\(default=\[.*?\], description="监控的目标公司列表"\)'
replacement = target_companies_code.rstrip('\n')

new_config = re.sub(pattern, replacement, config_content, flags=re.DOTALL)

# 验证替换成功
if new_config != config_content:
    # 备份原文件
    with open('config.py.bak', 'w', encoding='utf-8') as f:
        f.write(config_content)

    # 写入新文件
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(new_config)

    print("[OK] config.py updated")
    print(f"   - Backup saved to config.py.bak")
    print(f"   - Added {len(names)} companies to target_companies")
    print(f"   - SearchCollector will use complete company list if enabled later")
else:
    print("[ERROR] target_companies pattern not found, please check config.py manually")

print(f"\n[INFO] Company coverage:")
print(f"   - Total companies (deduplicated): {len(names)}")
