#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
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
        'level': 'Подробный'
    }
}

# Создаём сканер
scanner = PLPlusScanner(config, selected_rules=['v50'])

print("Загруженные паттерны для v50.SQL.OUTERJOIN.п.1.1:")
for key, value in scanner.PATTERNS.items():
    if 'OUTERJOIN' in key:
        print(f"  {key}: {value[0][:50]}...")

print(f"\nВсего паттернов: {len(scanner.PATTERNS)}")
