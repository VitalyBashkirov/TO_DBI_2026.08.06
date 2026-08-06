#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

import re

patterns = [
    (r'\(\+\)', 'LEFT JOIN', True, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'(\w+)%?(\w+)\s*=\s*(\w+)\s*\.\s*\[(\w+)\]\s*\(true\)', r'\1 = \3.\4 --<ВАЖНО: добавить LEFT JOIN вручную>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'(\w+)\s*\.\s*\[(\w+)\]\s*\(true\)', r'\1.\2 --<ВАЖНО: добавить LEFT JOIN вручную>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'(\w+)\s*\.\s*(\w+)\s*\(true\)', r'\1.\2 --<ВАЖНО: добавить LEFT JOIN вручную>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
    (r'&collection\s*\(true\)', r'&collection --<ВАЖНО: добавить LEFT JOIN вручную>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
]

test_lines = [
    "ac%id = gj.[ACCOUNT](true)",
    "gj.[IN_FILE_HISTORY] = st.collection_id(true)",
    "t1.id = t2.id(+)",
    "cr.[LIST_PAY] = fo&collection(true)",
]

print("Тест паттернов OUTERJOIN (финальные):")
print("="*80)

for line in test_lines:
    print(f"\nИсходный: {line}")
    result = line
    for pattern, replacement, case_sensitive, issue_type_code in patterns:
        flags = 0 if case_sensitive else re.IGNORECASE
        if re.search(pattern, result, flags):
            result = re.sub(pattern, replacement, result, flags=flags)
            print(f"  Паттерн: {pattern}")
            print(f"  Результат: {result}")
            break

print("\n" + "="*80)
print("\nОжидаемый результат для ac%id = gj.[ACCOUNT](true):")
print("  left join [GNI_JOUR] gj on ac%id = gj.[ACCOUNT]")
print("\nНО! Автоматически это сделать нельзя — требуется ручной анализ контекста.")
print("Фиксер удаляет (true) и добавляет комментарий о необходимости ручного исправления.")
