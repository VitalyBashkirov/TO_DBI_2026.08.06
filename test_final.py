#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
from fixer.code_fixer import PLPlusFixer
from pathlib import Path
import shutil

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
        print(f"  Строка {issue.line_number}: {issue.description[:60]}...")

# Применяем фиксер
print("\n" + "="*80)
print("Применение фиксера...")
print("="*80)

fixer = PLPlusFixer(config, 'test_fix', use_rubricator=False)
results_dir = Path('F:/TO_DBI/PATCH_OUT/patch_RV')

# Копируем файл для тестирования
test_results_file = results_dir / 'PSH_311P_CHK_final_test.plp'
shutil.copy2(test_file, test_results_file)

# Применяем исправления
was_modified, fix_count = fixer.fix_file(test_results_file, issues)

print(f"\nРезультат:")
print(f"  Изменён: {was_modified}")
print(f"  Исправлено: {fix_count}")

# Читаем и показываем результат
if was_modified:
    print(f"\nСодержимое исправленного файла (строки 74-85):")
    with open(test_results_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[73:85], 74):  # Строки 74-85
            print(f"{i:4}: {line.rstrip()}")

# Удаляем тестовый файл
test_results_file.unlink(missing_ok=True)

print("\n" + "="*80)
print("Готово! Теперь запустите через GUI:")
print("  1. Сканировать (F5)")
print("  2. Исправить код (F6)")
print("="*80)
