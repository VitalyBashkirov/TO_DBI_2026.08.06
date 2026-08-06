#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест запуска АРМа с проверкой загрузки правил
"""
import sys
sys.path.insert(0, 'SRC')

from rubricator_prompts import RubricatorPrompts
from pathlib import Path

print("="*80)
print('ТЕСТ ЗАГРУЗКИ РУБРИКАТОРА')
print("="*80)

rubricator_dir = Path('DATA/Рубрикатор')
prompts = RubricatorPrompts(rubricator_dir)

if prompts.load():
    print(f"\n[OK] Рубрикатор загружен (версия {prompts.data.get('version', 'N/A')})")
    
    # Проверка конкретного правила
    code = 'v50.SQL.OUTERJOIN.п.1.1'
    rule = prompts.get_rule(code)
    
    if rule:
        print(f"\n[OK] Правило '{code}' найдено:")
        print(f"  Описание: {rule.get('short_description')}")
        print(f"  Категория: {rule.get('category')}")
        
        patterns = prompts.get_regex_patterns(code)
        if patterns:
            search_patterns = patterns.get('for_search', [])
            ignore_patterns = patterns.get('for_ignore', [])
            print(f"\n  Паттерны для поиска ({len(search_patterns)}):")
            for p in search_patterns:
                print(f"    - {p.get('pattern')}")
            
            print(f"\n  Ignore-паттерны ({len(ignore_patterns)}):")
            for p in ignore_patterns:
                print(f"    - {p.get('pattern')}")
        
        # Проверка поиска в тестовом файле
        test_file = Path('PATCH_IN/patch_RV/src/ENTITY/AC_FIN/PSH_311P_CHK.plp')
        if test_file.exists():
            print(f"\n[TEST] Поиск проблем в файле: {test_file}")
            results = prompts.search_code_in_file(test_file, code)
            print(f"  Найдено проблем: {len(results)}")
            for r in results:
                print(f"    Строка {r['line_number']}: {r['description']}")
                print(f"      Код: {r['line'][:80]}")
        else:
            print(f"\n[WARNING] Тестовый файл не найден: {test_file}")
    else:
        print(f"\n[ERROR] Правило '{code}' не найдено!")
else:
    print("\n[ERROR] Не удалось загрузить рубрикатор!")

print("\n" + "="*80)
