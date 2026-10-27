#!/usr/bin/env python3
"""Генерация итогового отчёта"""
import json
from collections import Counter

with open('analysis_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('ИТОГОВЫЙ ОТЧЁТ ПО РУБРИКАТОРУ v5.0.1')
print('=' * 80)
print(f'Файлов отсканировано: {data["total_files"]}')
print(f'Всего проблем: {data["total_issues"]}')
print(f'Высокий приоритет: {data["high_issues_count"]}')

# Группировка по правилам
rule_counts = Counter()
file_counts = Counter()

for issue in data['issues']:
    rule_counts[issue['rule']] += 1
    file_counts[issue['file']] += 1

print('\n--- ПРОБЛЕМЫ ПО ПРАВИЛАМ ---')
for rule, count in rule_counts.most_common():
    print(f'  {rule}: {count}')

print('\n--- ФАЙЛЫ С БОЛЬШЕМ КОЛИЧЕСТВОМ ПРОБЛЕМ ---')
for file, count in file_counts.most_common(10):
    print(f'  {file}: {count}')

print('\n--- ПРИМЕРЫ ИСПРАВЛЕНИЙ ---')
print()

# v50.PROC.WHENOTHERS.п.3.5
print('[v50.PROC.WHENOTHERS.п.3.5] WHEN OTHERS без ROLLBACK/RAISE')
print('  Пример:')
for issue in data['issues']:
    if issue['rule'] == 'v50.PROC.WHENOTHERS.п.3.5':
        print(f'    Строка {issue["line"]}: {issue["code"]}')
        print(f'    Должно быть:')
        print(f'      exception when others then')
        print(f'        ROLLBACK;')
        print(f'        RAISE;')
        print()
        break

# v50.PROC.NATIVEID.п.3.26
print('[v50.PROC.NATIVEID.п.3.26] NativeID для метаданных')
print('  Пример:')
for issue in data['issues']:
    if issue['rule'] == 'v50.PROC.NATIVEID.п.3.26':
        print(f'    Строка {issue["line"]}: {issue["code"]}')
        print(f'    Должно быть: A_DocID varchar2(38); -- вместо number')
        print()
        break

print('\n--- СВОДКА ---')
print(f'1. WHEN OTHERS без ROLLBACK/RAISE: {rule_counts.get("v50.PROC.WHENOTHERS.п.3.5", 0)} случаев')
print(f'2. NativeID для метаданных: {rule_counts.get("v50.PROC.NATIVEID.п.3.26", 0)} случаев')
