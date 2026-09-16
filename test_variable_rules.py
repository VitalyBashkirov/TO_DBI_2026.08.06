#!/usr/bin/env python3
"""Полный тест правил переменных v5.0.0"""
import sys
sys.path.insert(0, 'SRC')

from analyzer.scanner import PLPlusScanner
from fixer.code_fixer import PLPlusFixer
from dataclasses import dataclass
from pathlib import Path
import tempfile
import os

@dataclass
class Issue:
    file_path: str
    line_number: int
    issue_type: str
    description: str
    original_code: str
    category: str = ''
    rubricator_code: str = ''
    rubricator_full_description: str = ''
    rubricator_example_code: str = ''
    rubricator_example_fixed: str = ''
    tags: list = None
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

# Тестовый код
test_code = """-- Тест переменных
dp integer := 0;
fmt24 date := sysdate;
name varchar2(100) := 'test';
count number := 10;
user_id number;
json_data varchar2(4000);
bad_var number := 1;
tmp_data date;
p_param integer;
v_existing boolean := true;
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.plp', delete=False, encoding='utf-8') as f:
    f.write(test_code)
    temp_file = f.name

try:
    config = {
        'paths': {'source_dir': 'F:/TO_DBI/PATCH_IN', 'results_dir': 'F:/TO_DBI/PATCH_OUT', 'logs_dir': 'SRC/logs'},
        'scan': {'exclude_patterns': ['.v', '.bak']}
    }
    
    scanner = PLPlusScanner(config, selected_rules=['v50'])
    issues = scanner.scan_file(Path(temp_file))
    
    print("=" * 90)
    print("СКАНИРОВАНИЕ — НАЙДЕНО ПРОБЛЕМ:")
    print("=" * 90)
    
    issues_by_line = {}
    for issue in issues:
        if 'PlpCheck.STYLE.BAD_PREFIX' in issue.issue_type or 'PlpCheck.STYLE.PREFIX_TYPE' in issue.issue_type:
            ln = issue.line_number
            if ln not in issues_by_line:
                issues_by_line[ln] = []
            issues_by_line[ln].append(issue)
    
    for ln, iss_list in sorted(issues_by_line.items()):
        print(f"\nСтрока {ln}: {test_code.split(chr(10))[ln-1].strip()}")
        for iss in iss_list:
            print(f"  [{iss.issue_type}] {iss.description}")
    
    # Применяем исправления
    fixer = PLPlusFixer(config, use_rubricator=False)
    
    print("\n" + "=" * 90)
    print("ИСПРАВЛЕНИЯ:")
    print("=" * 90)
    
    applied = {}
    for ln, iss_list in sorted(issues_by_line.items()):
        line = test_code.split('\n')[ln - 1]
        # Берём первое применимое исправление
        for issue in iss_list:
            fixed, was_modified = fixer._apply_fix_legacy(line, issue, 'Минимальный', False)
            if was_modified:
                applied[ln] = (line.strip(), fixed.strip())
                break
    
    for ln, (old, new) in sorted(applied.items()):
        print(f"\nСтрока {ln}:")
        print(f"  Было: {old}")
        print(f"  Стало: {new}")

finally:
    os.unlink(temp_file)
