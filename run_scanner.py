#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
from pathlib import Path
import json

config = json.load(open('SRC/settings.json', encoding='utf-8'))
config['paths'] = {
    'source_dir': config['source_dir'],
    'results_dir': config['result_dir'],
    'logs_dir': 'SRC/logs'
}
config['scan'] = {
    'exclude_patterns': ['.v', '.bak']
}

scanner = PLPlusScanner(config, selected_rules=config.get('selected_rules', []))
stats = scanner.scan_directory()

print(f'\nРезультаты сканирования:')
print(f'  Файлов: {stats["files_scanned"]}')
print(f'  Проблем: {stats["total_issues"]}')
print(f'\nПроблемы по типам:')
for issue_type, count in stats.get('by_type', {}).items():
    print(f'  {issue_type}: {count}')

# Проверяем нахождение gj.[ACCOUNT](true)
print('\n' + '=' * 60)
print('Проверка нахождения конструкции gj.[ACCOUNT](true):')
print('=' * 60)
outerjoin_issues = [i for i in scanner.issues if 'OUTERJOIN' in i.issue_type]
for issue in outerjoin_issues:
    if '[ACCOUNT](true)' in issue.original_code or 'collection_id(true)' in issue.original_code:
        print(f'  [OK] Строка {issue.line_number}: {issue.description}')
        print(f'       Код: {issue.original_code.strip()}')
