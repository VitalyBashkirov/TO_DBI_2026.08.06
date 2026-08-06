#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'SRC')

from rubricator_prompts import RubricatorPrompts
from pathlib import Path

rubricator_dir = Path('DATA/Рубрикатор')
prompts = RubricatorPrompts(rubricator_dir)

if prompts.load():
    code = 'v50.SQL.OUTERJOIN.п.1.1'
    test_file = Path('PATCH_IN/patch_RV/src/ENTITY/AC_FIN/PSH_311P_CHK.plp')
    
    print(f"\nПоиск проблем в файле: {test_file}")
    results = prompts.search_code_in_file(test_file, code)
    print(f"Найдено проблем: {len(results)}")
    for r in results:
        print(f"  Строка {r['line_number']}: {r['description']}")
        print(f"    Код: {r['line'][:100]}")
else:
    print("Не удалось загрузить рубрикатор!")
