# -*- coding: utf-8 -*-
"""
从通信设备产业链企业清单导入公司到监控系统
"""
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read the markdown file
with open('C:/Users/G1142/Documents/WXWork/1688854689765845/Cache/File/2026-04/通信设备产业链全球主要企业清单.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract company names and websites from tables
companies = []
lines = content.split('\n')
for line in lines:
    if 'http' in line and '|' in line:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 5 and parts[4].startswith('http'):
            name = parts[1].strip()
            url = parts[4].strip().rstrip(')')
            name = re.sub(r'\*\*(.*?)\*\*', r'\1', name)
            if ' / ' in url:
                url = url.split(' / ')[0].strip()
            companies.append((name, url))

print(f'Found {len(companies)} companies with URLs\n')

# Read existing config
with open('config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

# Extract current target_companies
idx = config_content.find('target_companies')
list_start = config_content.find('=[', idx)
bracket_start = list_start + 1
depth = 0
for i in range(bracket_start, len(config_content)):
    if config_content[i] == '[':
        depth += 1
    elif config_content[i] == ']':
        depth -= 1
        if depth == 0:
            bracket_end = i
            break

companies_str = config_content[bracket_start+1:bracket_end]
existing = set(re.findall(r'"([^"]+)"', companies_str))
print(f'Existing target_companies: {len(existing)}')

# Find new companies
new_for_config = []
seen_names = set()

for name, url in companies:
    if '(' in name and ')' in name:
        cn_name = name.split('(')[0].strip()
        en_name = name.split('(')[1].rstrip(')').strip()
        # Check if we have either
        if cn_name not in existing and en_name not in existing and cn_name not in seen_names:
            new_for_config.append((cn_name, en_name, url))
            seen_names.add(cn_name)
            if en_name:
                seen_names.add(en_name)
    else:
        if name not in existing and name not in seen_names:
            new_for_config.append((name, None, url))
            seen_names.add(name)

print(f'\nNew companies to add: {len(new_for_config)}')
for cn, en, url in new_for_config[:20]:
    if en:
        print(f'  {cn} ({en}): {url}')
    else:
        print(f'  {cn}: {url}')
if len(new_for_config) > 20:
    print(f'  ... ({len(new_for_config) - 20} more)')

# ============================================================
# Generate output
# ============================================================
print('\n' + '='*70)
print('STEP 1: Add these companies to target_companies in config.py')
print('='*70)
print('Copy the following lines into config.py after line ~224 (before the closing ]):\n')
for cn, en, url in new_for_config:
    if en:
        print(f'        "{cn}",  # {en}')
    else:
        print(f'        "{cn}",')

# ============================================================
print('\n' + '='*70)
print('STEP 2: Add website configurations to web_sites_config.py')
print('='*70)
print('(Optional - only if you want to scrape their official websites)\n')

# For companies without existing web config, show what to add
web_config_path = 'collectors/web_sites_config.py'
with open(web_config_path, 'r', encoding='utf-8') as f:
    web_config_content = f.read()

# Extract existing site names
existing_sites = set(re.findall(r'"name":\s*"([^"]+)"', web_config_content))
print(f'Existing websites configured: {len(existing_sites)}')

# Companies that need web config
need_web_config = []
for cn, en, url in new_for_config:
    name = en if en else cn
    if name not in existing_sites:
        need_web_config.append((cn, en, url))

print(f'\nCompanies needing web config: {len(need_web_config)}')

# Common CSS selectors
list_sel = "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']"
title_sel = "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]"
link_sel = "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]"
date_sel = "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]"

for cn, en, url in need_web_config[:30]:
    display_name = en if en else cn
    base_url = url.rstrip('/')
    print(f'''    {{
        "name": "{display_name}",
        "url": "{url}",
        "list_selector": "{list_sel}",
        "title_selector": "{title_sel}",
        "link_selector": "{link_sel}",
        "date_selector": "{date_sel}",
        "base_url": "{base_url}",
        "priority": "P2",
        "use_jina_only": True
    }},''')
    print()

if len(need_web_config) > 30:
    print(f'... ({len(need_web_config) - 30} more - showing first 30)')

print('\n' + '='*70)
print('SUMMARY')
print('='*70)
print(f'Total companies in markdown: {len(companies)}')
print(f'Already in target_companies: {len(existing)}')
print(f'New to add to target_companies: {len(new_for_config)}')
print(f'New needing web config: {len(need_web_config)}')