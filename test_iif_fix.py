#!/usr/bin/env python3
"""Тест исправления функции iif"""
import sys
sys.path.insert(0, 'SRC')
from fixer.code_fixer import _capitalize_meaning, _build_function_params_replacer
import re

# Тестируем _capitalize_meaning
print("Тест _capitalize_meaning:")
test_cases = [
    ('v1', 'V1'),
    ('v2', 'V2'),
    ('v3', 'V3'),
    ('dp', 'Dp'),
    ('dp1', 'Dp1'),
    ('fmt24', 'Fmt24'),
    ('lvRepPeriod', 'LvRepPeriod'),
    ('lrBranch', 'LrBranch'),
]
for name, expected in test_cases:
    result = _capitalize_meaning(name)
    status = '✓' if result == expected else '✗'
    print(f'  {status} {name:15} -> {result:15} (ожидалось: {expected})')

# Тестируем преобразование параметров функции
print("\nТест параметров функции:")
replacer = _build_function_params_replacer()

# Симулируем параметры функции
test_params = [
    ('v1 boolean', 'p_bV1 boolean'),
    ('v2 varchar2(32767)', 'p_vV2 varchar2(32767)'),
    ('v3 varchar2(32767)', 'p_vV3 varchar2(32767)'),
]

for param, expected in test_params:
    # Ищем параметр (с размерностью)
    pattern = r'(\w+)\s+(boolean|varchar2|string|number|integer|date|ref|rowtype)(?:\([^)]*\))?'
    match = re.search(pattern, param)
    if match:
        result = replacer(match)
        status = '✓' if result == expected else '✗'
        print(f'  {status} {param:25} -> {result:30} (ожидалось: {expected})')
