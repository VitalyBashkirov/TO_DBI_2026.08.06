#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест фиксера на конкретном файле
"""
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner, Issue
from pathlib import Path
import json

# Конфиг
config = {
    'paths': {
        'source_dir': 'F:/TO_DBI/PATCH_IN/patch_RV',
        'results_dir': 'F:/TO_DBI/PATCH_OUT/patch_RV',
        'logs_dir': 'SRC/logs'
    },
    'scan': {
        'recursive': True,
        'file_pattern': '**/*.plp',
        'exclude_patterns': ['.v????', '.bak', '.tmp']
    },
    'output': {
        'only_modified': False,
        'preserve_structure': True
    },
    'logging': {
        'level': 'Минимальный'
    }
}

# Сканируем
print("Сканирование...")
scanner = PLPlusScanner(config, selected_rules=['v50'])
issues = scanner.scan_file(Path('F:/TO_DBI/PATCH_IN/patch_RV/src/ENTITY/AC_FIN/PSH_311P_CHK.plp'))

print(f"\nНайдено проблем: {len(issues)}")
for issue in issues:
    if 'OUTERJOIN' in issue.issue_type:
        print(f"  Строка {issue.line_number}: {issue.description}")
        print(f"    Код: {issue.original_code.strip()}")

# Проверяем паттерны фиксера
print("\n" + "="*60)
print("Проверка паттернов фиксера для OUTERJOIN:")
print("="*60)

# Загружаем фиксер без рубрикатора
from fixer.code_fixer import PLPlusFixer

# Отключаем рубрикатор чтобы избежать ошибок
fixer_config = config.copy()
fixer = PLPlusFixer(fixer_config, 'test', use_rubricator=False)

print("\nПаттерны для v50.SQL.OUTERJOIN.п.1.1:")
for pattern_info in fixer.FIXES.get('v50.SQL.OUTERJOIN.п.1.1', []):
    pattern, replacement, case_sensitive, code = pattern_info
    print(f"  {pattern} -> {replacement}")
