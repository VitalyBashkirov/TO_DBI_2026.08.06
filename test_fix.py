#!/usr/bin/env python3
"""Проверка исправлений PlpCheck-правил"""
import sys
sys.path.insert(0, 'SRC')
from fixer.code_fixer import PLPlusFixer
from analyzer.scanner import PLPlusScanner
from pathlib import Path

config = {
    'paths': {'source_dir': 'F:/TO_DBI/PATCH_IN', 'results_dir': 'F:/TO_DBI/PATCH_OUT', 'logs_dir': 'SRC/logs'},
    'scan': {'exclude_patterns': ['.v', '.bak']}
}

# Сначала сканируем
scanner = PLPlusScanner(config, selected_rules=['v50'])
file_path = Path('PATCH_IN/patch_REPS_EXP_115_1/src/ENTITY/HOOK_BANK/REPS_EXP_115_1.plp')
issues = scanner.scan_file(file_path)

print(f'Найдено проблем: {len(issues)}')
for issue in issues[:5]:
    print(f'  [{issue.issue_type}] Строка {issue.line_number}: {issue.description}')
print('  ...')

# Затем исправляем
fixer = PLPlusFixer(config, iteration='v0001', use_rubricator=True)
success, count = fixer.fix_file(file_path, issues)

print(f'\nИсправлено проблем: {count}')
print(f'Успешно: {success}')
