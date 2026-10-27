#!/usr/bin/env python3
"""Финальная проверка исправлений"""
import sys
sys.path.insert(0, 'SRC')
from fixer.code_fixer import PLPlusFixer
from analyzer.scanner import PLPlusScanner
from pathlib import Path

# Создаём тестовый файл
test_code = '''dp1  integer:=0;

function iif(v1 boolean, v2 varchar2(32767), v3 varchar2(32767)) return varchar2(32767) is
begin if v1 then return v2; else return v3; end if; end;
'''

with open('test_final.plp', 'w', encoding='utf-8') as f:
    f.write(test_code)

config = {
    'paths': {'source_dir': 'F:/TO_DBI', 'results_dir': 'F:/TO_DBI/PATCH_OUT', 'logs_dir': 'SRC/logs'},
    'scan': {'exclude_patterns': ['.v', '.bak']}
}

scanner = PLPlusScanner(config, selected_rules=['v50'])
file_path = Path('test_final.plp')
issues = scanner.scan_file(file_path)

fixer = PLPlusFixer(config, iteration='v0056', use_rubricator=True)
success, count = fixer.fix_file(file_path, issues)

print('RESULT:')
with open('test_final.plp', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)
    
    # Проверяем
    checks = [
        ('v_iDp1' in content, 'dp1 -> v_iDp1'),
        ('p_bV1' in content and 'p_vV2' in content, 'parameters p_'),
        ('v_vResult' in content, 'v_vResult added'),
    ]
    
    print('\nCHECKS:')
    for check, desc in checks:
        status = 'OK' if check else 'FAIL'
        print(f'  [{status}] {desc}')
