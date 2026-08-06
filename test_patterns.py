# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

# Путь к файлу с паттернами
patterns_file = Path("RubricatorTemp/4.RUBRICATOR_PROMPTS.json")

# Путь к тестируемому файлу
test_file = Path("PATCH_IN/patch_RV/src/ENTITY/AC_FIN/PSH_311P_CHK.plp")

# Загружаем паттерны
with open(patterns_file, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

# Читаем тестируемый файл
with open(test_file, "r", encoding="utf-8-sig") as f:
    file_content = f.read()
    lines = file_content.split('\n')

# Правило для OUTERJOIN
rule = data["rules"]["v50.SQL.OUTERJOIN.п.1.1"]
patterns = rule["regex_patterns"]["for_search"]
ignore_patterns = rule["regex_patterns"]["for_ignore"]

print(f"Проверка файла: {test_file}")
print(f"Правило: {rule['code']}")
print(f"Описание: {rule['short_description']}")
print("=" * 80)

found_issues = []

for line_num, line in enumerate(lines, 1):
    for pattern_info in patterns:
        pattern = pattern_info["pattern"]
        flags = re.IGNORECASE if pattern_info.get("flags", "").lower() == "i" else 0
        
        if re.search(pattern, line, flags):
            # Проверяем ignore patterns
            is_ignored = False
            for ignore_info in ignore_patterns:
                ignore_pattern = ignore_info["pattern"]
                if re.search(ignore_pattern, line, flags):
                    is_ignored = True
                    break
            
            if not is_ignored:
                found_issues.append({
                    "line_num": line_num,
                    "line": line.strip(),
                    "pattern": pattern,
                    "description": pattern_info["description"]
                })

if found_issues:
    print(f"\nНайдено {len(found_issues)} проблем(ы):\n")
    for issue in found_issues:
        print(f"Строка {issue['line_num']}: {issue['description']}")
        print(f"  Код: {issue['line']}")
        print(f"  Паттерн: {issue['pattern']}")
        print()
else:
    print("\nПроблем не найдено.")

print("=" * 80)

# Дополнительно: проверяем каждый паттерн отдельно
print("\nДетальная проверка каждого паттерна:")
print("-" * 80)

for pattern_info in patterns:
    pattern = pattern_info["pattern"]
    flags = re.IGNORECASE if pattern_info.get("flags", "").lower() == "i" else 0
    
    matches = []
    for line_num, line in enumerate(lines, 1):
        if re.search(pattern, line, flags):
            matches.append((line_num, line.strip()))
    
    if matches:
        print(f"\nПаттерн: {pattern}")
        print(f"Описание: {pattern_info['description']}")
        print(f"Найдено {len(matches)} совпадений:")
        for line_num, line_text in matches:
            print(f"  Строка {line_num}: {line_text[:80]}")
    else:
        print(f"\nПаттерн: {pattern}")
        print(f"Описание: {pattern_info['description']}")
        print(f"Совпадений не найдено")
