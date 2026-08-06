#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

# Тестируем паттерны напрямую
import re

patterns = [
    (r'\(\+\)', 'LEFT JOIN', True, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'(\w+)%?(\w+)\s*=\s*(\w+)\.\[(\w+)\]\(true\)', r'\1 = \3.\4', False, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'(\w+)\.\[(\w+)\]\(true\)', r'\1.\2', False, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'(\w+)\.(\w+)\(true\)', r'\1.\2', False, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'&collection\(true\)', r'&collection', False, 'v50.SQL.OUTERJOIN.п.1.1'),
]

test_lines = [
    "ac%id = gj.[ACCOUNT](true)",
    "gj.[IN_FILE_HISTORY] = st.collection_id(true)",
    "t1.id = t2.id(+)",
    "cr.[LIST_PAY] = fo&collection(true)",
]

print("Тест паттернов OUTERJOIN:")
print("="*80)

for line in test_lines:
    print(f"\nИсходный: {line}")
    result = line
    for pattern, replacement, case_sensitive, issue_type_code in patterns:
        flags = 0 if case_sensitive else re.IGNORECASE
        if re.search(pattern, result, flags):
            result = re.sub(pattern, replacement, result, flags=flags)
            print(f"  Паттерн: {pattern}")
            print(f"  Замена: {replacement}")
            print(f"  Результат: {result}")
            break

print("\n" + "="*80)
