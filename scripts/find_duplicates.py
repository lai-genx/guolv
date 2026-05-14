# -*- coding: utf-8 -*-
import re
with open('config.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('target_companies')
list_start = content.find('=[', idx)
bracket_start = list_start + 1
depth = 0
for i in range(bracket_start, len(content)):
    if content[i] == '[':
        depth += 1
    elif content[i] == ']':
        depth -= 1
        if depth == 0:
            bracket_end = i
            break

companies_str = content[bracket_start+1:bracket_end]
all_companies = re.findall(r'"([^"]+)"', companies_str)
print(f'Total: {len(all_companies)}')

# Find duplicates
seen = {}
for c in all_companies:
    if c in seen:
        seen[c] += 1
    else:
        seen[c] = 1
dups = {k:v for k,v in seen.items() if v > 1}
print(f'Duplicates: {dups}')

# Print all companies around the duplicate
for i, c in enumerate(all_companies):
    if '�' in c or len(c) > 15:
        print(f'Line {i}: {repr(c)}')