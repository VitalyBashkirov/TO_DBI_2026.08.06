#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка обработки всех правил рубрикатора
"""
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
from pathlib import Path
import json

print('='*80)
print('ФИНАЛЬНАЯ ПРОВЕРКА ОБРАБОТКИ ПРАВИЛ РУБРИКАТОРА')
print('='*80)

# Загрузка JSON
json_path = Path('DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json')
with open(json_path, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

json_rules = data['rules']
print(f'\n[1] Всего правил в JSON-файле: {len(json_rules)}')

# Загрузка сканера
config = {
    'paths': {
        'source_dir': 'F:/TO_DBI/PATCH_IN',
        'results_dir': 'F:/TO_DBI/PATCH_OUT',
        'logs_dir': 'SRC/logs'
    },
    'scan': {
        'exclude_patterns': ['.v', '.bak']
    }
}

scanner = PLPlusScanner(config, selected_rules=['v50'])
loaded_rules = scanner.PATTERNS

print(f'[2] Правил загружено сканером: {len(loaded_rules)}')

# Статистика по категориям
categories = {}
for rule_key in json_rules.keys():
    category = json_rules[rule_key].get('category', 'UNKNOWN')
    if category not in categories:
        categories[category] = {'total': 0, 'loaded': 0, 'no_patterns': 0}
    categories[category]['total'] += 1
    
    patterns_count = len(json_rules[rule_key].get('regex_patterns', {}).get('for_search', []))
    if patterns_count == 0:
        categories[category]['no_patterns'] += 1
    elif rule_key in loaded_rules:
        categories[category]['loaded'] += 1

print('\n[3] Статистика по категориям:')
print('-'*80)
print(f'{"Категория":<12} {"Всего":<8} {"Загружено":<12} {"Без паттернов":<15}')
print('-'*80)
for cat, stats in sorted(categories.items()):
    print(f'{cat:<12} {stats["total"]:<8} {stats["loaded"]:<12} {stats["no_patterns"]:<15}')

# Сравнение
json_set = set(json_rules.keys())
loaded_set = set(loaded_rules.keys())
missing = json_set - loaded_set
no_patterns = [k for k in json_set if len(json_rules[k].get('regex_patterns', {}).get('for_search', [])) == 0]

print('\n[4] Правила без паттернов (требуют ручного анализа):')
if no_patterns:
    for r in no_patterns:
        desc = json_rules[r].get('short_description', 'N/A')
        print(f'  - {r}: {desc}')
else:
    print('  Нет')

print('\n[5] Правила, которые не загружены (кроме без паттернов):')
missing_actual = missing - set(no_patterns)
if missing_actual:
    for r in missing_actual:
        print(f'  - {r}')
else:
    print('  Нет — все правила с паттернами загружены!')

# Проверка конкретного правила OUTERJOIN
print('\n[6] Проверка правила v50.SQL.OUTERJOIN.п.1.1:')
if 'v50.SQL.OUTERJOIN.п.1.1' in loaded_rules:
    pattern_data = loaded_rules['v50.SQL.OUTERJOIN.п.1.1']
    print(f'  [OK] Правило загружено')
    print(f'     Паттерн: {pattern_data[0]}')
    print(f'     Описание: {pattern_data[1]}')
else:
    print(f'  [ERROR] Правило НЕ загружено')

print('\n' + '='*80)
print('ИТОГ:')
print('='*80)
print(f'Всего правил в рубрикаторе: {len(json_rules)}')
print(f'Правил с паттернами: {len(json_rules) - len(no_patterns)}')
print(f'Правил загружено сканером: {len(loaded_rules)}')
print(f'Правил без паттернов (ручной анализ): {len(no_patterns)}')

if len(loaded_rules) == len(json_rules) - len(no_patterns):
    print('\n[OK] ВСЕ ПРАВИЛА С ПАТТЕРНАМИ ОБРАБАТЫВАЮТСЯ АВТОМАТИЧЕСКИ!')
    print('     Доработка не требуется.')
else:
    print(f'\n[WARNING] Внимание: {len(missing_actual)} правил не загружено')

print('='*80)
