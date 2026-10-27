#!/usr/bin/env python3
"""Полный анализ всех .plp файлов по рубрикатору v5.0.1"""
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
from pathlib import Path
import json

# Конфигурация
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

# Создаём сканер
scanner = PLPlusScanner(config, selected_rules=['v50'])

print("=" * 100)
print("ПОЛНЫЙ АНАЛИЗ КОДА ПО РУБРИКАТОРУ v5.0.1")
print("=" * 100)
print(f"\nЗагружено правил из JSON: {len(scanner.PATTERNS)}")

# Собираем все .plp файлы
plp_files = list(Path('PATCH_IN').rglob('*.plp'))
print(f"Найдено .plp файлов: {len(plp_files)}")

# Сканируем все файлы
all_issues = []
files_scanned = 0

for plp_file in plp_files:
    try:
        issues = scanner.scan_file(plp_file)
        if issues:
            all_issues.extend(issues)
        files_scanned += 1
    except Exception as e:
        print(f"  [!] Ошибка сканирования {plp_file}: {e}")

print(f"\nОтсканировано файлов: {files_scanned}")
print(f"Всего проблем найдено: {len(all_issues)}")

# Группируем по приоритету
high_issues = [i for i in all_issues if i.issue_type.startswith('v50') or 'HIGH' in str(i.tags)]
medium_issues = [i for i in all_issues if not i.issue_type.startswith('v50') and 'HIGH' not in str(i.tags)]

print(f"\nВысокий приоритет (HIGH): {len(high_issues)}")
print(f"Средний/Низкий приоритет: {len(medium_issues)}")

# Выводим HIGH проблемы
print("\n" + "=" * 100)
print("ПРОБЕМЫ ВЫСОКОГО ПРИОРИТЕТА (HIGH):")
print("=" * 100)

for issue in sorted(high_issues, key=lambda x: (x.file_path, x.line_number)):
    print(f"\n[{issue.issue_type}]")
    print(f"  Файл: {issue.file_path}")
    print(f"  Строка: {issue.line_number}")
    print(f"  Описание: {issue.description}")
    print(f"  Код: {issue.original_code.strip()}")
    print(f"  Категория: {issue.category}")

# Сохраняем результаты
results = {
    'total_files': files_scanned,
    'total_issues': len(all_issues),
    'high_issues_count': len(high_issues),
    'issues': [
        {
            'file': issue.file_path,
            'line': issue.line_number,
            'rule': issue.issue_type,
            'description': issue.description,
            'code': issue.original_code,
            'category': issue.category
        }
        for issue in all_issues
    ]
}

with open('analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\nРезультаты сохранены в: analysis_results.json")
