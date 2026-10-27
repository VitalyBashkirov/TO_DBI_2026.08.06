#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

# Путь к файлу
json_path = Path('DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json')

with open(json_path, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

rules = data['rules']
print(f'Всего правил в JSON: {len(rules)}')
print('\nПравила по категориям:')

categories = {}
for rule_key, rule_data in sorted(rules.items()):
    category = rule_data.get('category', 'UNKNOWN')
    if category not in categories:
        categories[category] = []
    patterns_count = len(rule_data.get('regex_patterns', {}).get('for_search', []))
    categories[category].append((rule_key, patterns_count))

for category, rules_list in sorted(categories.items()):
    print(f'\n[{category}] - {len(rules_list)} правил:')
    for rule_key, patterns_count in rules_list:
        status = '[OK]' if patterns_count > 0 else '[NO PATTERNS]'
        print(f'  {status} {rule_key}: {patterns_count} паттернов')

# Проверка, какие правила загружает сканер
print('\n' + '='*60)
print('Проверка загрузки правил сканером:')
print('='*60)

import sys
sys.path.insert(0, 'SRC')
from analyzer.scanner import PLPlusScanner

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
loaded_rules = list(scanner.PATTERNS.keys())

print(f'\nЗагружено правил сканером: {len(loaded_rules)}')
print('\nЗагруженные правила:')
for rule in sorted(loaded_rules):
    print(f'  [LOADED] {rule}')

# Сравнение
print('\n' + '='*60)
print('Сравнение:')
print('='*60)
json_rules = set(rules.keys())
loaded_set = set(loaded_rules)

missing = json_rules - loaded_set
extra = loaded_set - json_rules

if missing:
    print(f'\n[WARNING] Правил в JSON нет в загруженных ({len(missing)}):')
    for r in sorted(missing):
        print(f'  - {r}')

if extra:
    print(f'\n[INFO] Правил в загруженных нет в JSON ({len(extra)}):')
    for r in sorted(extra):
        print(f'  - {r}')

if not missing and not extra:
    print('\n[OK] Все правила из JSON загружены успешно!')
