#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

import re

# Тестируем паттерны напрямую
test_line = "and gj.[IN_FILE_HISTORY] = st.collection_id(true)"

patterns = [
    r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)\(\+\)',
    r'(\w+)\.(\w+)\(\+\)\s*=\s*(\w+)\.(\w+)',
    r'&collection\(true\)',
    r'(\w+)\.\[(\w+)\]\(true\)',
    r'(\w+)\.\[(\w+)\]\(false\)',
    r'(\w+)\.(\w+)\(true\)',
    r'(\w+)%?(\w+)\s*=\s*(\w+)\.\[(\w+)\]\(true\)',
]

print(f"Тест строки: {test_line}")
print("="*60)

for i, pattern in enumerate(patterns):
    match = re.search(pattern, test_line, re.IGNORECASE)
    if match:
        print(f"Паттерн {i}: {pattern}")
        print(f"  Match: {match.group()}")
        print(f"  Groups: {match.groups()}")
    else:
        print(f"Паттерн {i}: НЕТ СОВПАДЕНИЯ")
