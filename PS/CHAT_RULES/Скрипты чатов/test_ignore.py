#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

import json
import re

data = json.load(open('DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', encoding='utf-8-sig'))
rule = data['rules'].get('v50.SQL.OUTERJOIN.п.1.1', {})
ignore_patterns = rule.get('regex_patterns', {}).get('for_ignore', [])

test_lines = [
    "ac%id = gj.[ACCOUNT](true)",
    "and gj.[IN_FILE_HISTORY] = st.collection_id(true)",
]

print("Ignore-паттерны:")
for i, p in enumerate(ignore_patterns):
    print(f"  {i+1}. {p.get('pattern')}")

print("\nТест строк:")
for line in test_lines:
    print(f"\nСтрока: {line}")
    for i, info in enumerate(ignore_patterns):
        pattern = info.get('pattern', '')
        if re.search(pattern, line, re.IGNORECASE):
            print(f"  ИГНОРИРУЕТСЯ паттерном {i+1}: {pattern}")
            break
    else:
        print(f"  НЕ игнорируется")
