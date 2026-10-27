#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

data = json.load(open('DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', encoding='utf-8-sig'))
rule = data['rules'].get('v50.SQL.OUTERJOIN.п.1.1', {})
patterns = rule.get('regex_patterns', {}).get('for_search', [])

print(f'Паттернов для OUTERJOIN: {len(patterns)}')
for i, p in enumerate(patterns):
    print(f'  {i+1}. {p.get("pattern")}')
