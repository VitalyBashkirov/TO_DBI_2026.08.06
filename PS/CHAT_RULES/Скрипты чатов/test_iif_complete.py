#!/usr/bin/env python3
"""Полный тест исправления функции iif"""
import sys
sys.path.insert(0, 'SRC')
from fixer.code_fixer import _capitalize_meaning, _build_function_params_replacer
import re

print("=" * 80)
print("ТЕСТ ИСПРАВЛЕНИЯ ФУНКЦИИ IIF")
print("=" * 80)

# Тест 1: _capitalize_meaning
print("\n1. Тест _capitalize_meaning:")
test_cases = [
    ('v1', 'V1'),
    ('v2', 'V2'),
    ('v3', 'V3'),
    ('dp', 'Dp'),
    ('dp1', 'Dp1'),
]
for name, expected in test_cases:
    result = _capitalize_meaning(name)
    status = '✓' if result == expected else '✗'
    print(f'  {status} {name:10} -> {result:10} (ожидалось: {expected})')

# Тест 2: Параметры функции
print("\n2. Тест параметров функции (должны быть p_):")
replacer = _build_function_params_replacer()
test_params = [
    ('v1 boolean', 'p_bV1 boolean'),
    ('v2 varchar2(32767)', 'p_vV2 varchar2(32767)'),
    ('v3 varchar2(32767)', 'p_vV3 varchar2(32767)'),
]
for param, expected in test_params:
    pattern = r'(\w+)\s+(boolean|varchar2|string|number|integer|date|ref|rowtype)(?:\([^)]*\))?'
    match = re.search(pattern, param)
    if match:
        result = replacer(match)
        status = '✓' if result == expected else '✗'
        print(f'  {status} {param:25} -> {result:30} (ожидалось: {expected})')

# Тест 3: Локальные переменные (должны быть v_)
print("\n3. Тест локальных переменных (должны быть v_):")
from fixer.code_fixer import _build_prefix_type_replacer
local_replacer = _build_prefix_type_replacer()
test_locals = [
    ('dp integer', 'v_iDp integer'),
    ('fmt24 string', 'v_vFmt24 string'),
    ('lrBranch ref', 'v_lrLrBranch ref'),
]
for var, expected in test_locals:
    pattern = r'(\w+)\s+(integer|string|number|date|ref|rowtype|varchar2)\b'
    match = re.search(pattern, var)
    if match:
        result = local_replacer(match)
        status = '✓' if result == expected else '✗'
        print(f'  {status} {var:20} -> {result:25} (ожидалось: {expected})')

print("\n" + "=" * 80)
print("ИТОГ: Алгоритм требует доработки для:")
print("  1. Различения параметров (p_) и локальных переменных (v_)")
print("  2. Преобразования тела функции")
print("  3. Добавления переменной возврата в секцию DECLARE")
print("=" * 80)
