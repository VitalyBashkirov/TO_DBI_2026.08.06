#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
from fixer.code_fixer import PLPlusFixer
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
    if 'OUTERJOIN' in issue.issue_type:
        print(f"  Строка {issue.line_number}: {issue.description}")
        print(f"    Код: {issue.original_code.strip()}")

# Применяем фиксер
print("\n" + "="*80)
print("Применение фиксера...")
print("="*80)

fixer = PLPlusFixer(config, 'test_fix', use_rubricator=False)
results_dir = Path('F:/TO_DBI/PATCH_OUT/patch_RV')

# Проверяем строки 74 и 75 отдельно
test_lines = [
    ("ac%id = gj.[ACCOUNT](true)", 74),
    ("and gj.[IN_FILE_HISTORY] = st.collection_id(true)", 75),
]

for line_text, line_num in test_lines:
    print(f"\nСтрока {line_num}: {line_text}")
    # Создаем Issue
    from analyzer.scanner import Issue
    issue = Issue(
        line_number=line_num,
        original_code=line_text,
        description="test",
        issue_type="v50.SQL.OUTERJOIN.п.1.1",
        rubricator_full_description="test",
        file_path=str(test_file),
        category="SQL"
    )
    
    # Применяем исправление
    fixed_line, was_modified = fixer.apply_fix(line_text + "\n", issue, 'Подробный')
    print(f"  Исправлено: {was_modified}")
    print(f"  Результат:")
    for i, line in enumerate(fixed_line.split('\n'), 1):
        if line:
            print(f"    {line}")
