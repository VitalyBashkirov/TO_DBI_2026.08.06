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

# Сканируем
print("Сканирование...")
scanner = PLPlusScanner(config, selected_rules=['v50'])
test_file = Path('F:/TO_DBI/PATCH_IN/patch_RV/src/ENTITY/AC_FIN/PSH_311P_CHK.plp')
issues = scanner.scan_file(test_file)

print(f"\nНайдено проблем: {len(issues)}")
for issue in issues:
    print(f"  Строка {issue.line_number}: {issue.issue_type}")
    print(f"    Код: {issue.original_code.strip()[:80]}")
