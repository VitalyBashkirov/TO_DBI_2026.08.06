import json
import sys
sys.path.insert(0, 'F:/TO_DBI/SRC')

# Читаем текущий JSON
with open('F:/TO_DBI/DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Исправляем паттерны для BAD_PREFIX
data['rules']['v50.STYLE.BAD_PREFIX.п.4.3']['regex_patterns']['for_search'] = [
    {
        "pattern": "(?i)\\b(bad_|badprefix_|tmp_|temp_|var_|data_|info_)\\w+\\s+(varchar2|string|number|date|boolean|ref)",
        "description": "Плохой префикс переменной (bad_, tmp_, temp_, var_, data_, info_)"
    }
]

# Исправляем паттерны для PREFIX_TYPE
data['rules']['v50.STYLE.PREFIX_TYPE.п.4.4']['regex_patterns']['for_search'] = [
    {
        "pattern": "(?i)\\b(v_\\d|n_\\d|d_\\d|b_\\d)\\w+\\s+(varchar2|string)\\s*\\(",
        "description": "Неверный префикс для varchar2/string (должен быть v_)"
    },
    {
        "pattern": "(?i)\\b(v_|d_|b_)\\w+\\s+number\\s*;",
        "description": "Неверный префикс для number (должен быть n_)"
    },
    {
        "pattern": "(?i)\\b(v_|n_|b_)\\w+\\s+date\\s*;",
        "description": "Неверный префикс для date (должен быть d_)"
    },
    {
        "pattern": "(?i)\\b(n_|v_|d_|b_)\\w+\\s+(varchar2|string)\\s*\\(",
        "description": "Проверка префикса для varchar2/string"
    }
]

# Исправляем паттерны для NOT_MENTIONED
data['rules']['v50.STYLE.NOT_MENTIONED.п.4.8']['regex_patterns']['for_search'] = [
    {
        "pattern": "(?i)\\b\\w+\\s+(varchar2|string|number|date|boolean|ref)\\s*;",
        "description": "Объявление переменной (проверить наличие комментария)"
    }
]

# Записываем обратно
with open('F:/TO_DBI/DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Исправлены паттерны")

# Проверяем загрузку
from analyzer.scanner import PLPlusScanner
config = {'paths':{'source_dir':'F:/TO_DBI','results_dir':'F:/TO_DBI/PATCH_OUT'},'scan':{'recursive':True,'file_pattern':'**/*.plp','exclude_patterns':[]},'logging':{'level':'Минимальный'}}
scanner = PLPlusScanner(config)
style_patterns = [k for k in scanner.PATTERNS.keys() if 'STYLE' in k]
print(f"Загружено STYLE паттернов: {len(style_patterns)}")

# Проверяем на тестовом файле
from pathlib import Path
issues = scanner.scan_file(Path('F:/TO_DBI/test_style.plp'))
style_issues = [i for i in issues if 'STYLE' in i.issue_type]
print(f"Найдено STYLE проблем: {len(style_issues)}")
for i in style_issues[:10]:
    print(f"  Строка {i.line_number}: {i.issue_type} - {i.description}")
    print(f"    {i.original_code.strip()[:80]}")
