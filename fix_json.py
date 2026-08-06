#!/usr/bin/env python3
"""Исправление ошибок экранирования в JSON файле рубрикатора"""
import json
import re

input_path = r'F:\TO_DBI\DATA\Рубрикатор\4.RUBRICATOR_PROMPTS.json'
output_path = r'F:\TO_DBI\DATA\Рубрикатор\4.RUBRICATOR_PROMPTS_fixed.json'

with open(input_path, 'r', encoding='cp1251') as f:
    content = f.read()

# Найти все строки с паттернами и проверить экранирование
lines = content.split('\n')
fixed_lines = []
fixes = []

for i, line in enumerate(lines, 1):
    original = line
    # Исправить одиночные обратные слэши внутри строк JSON (кроме валидных escape)
    # Находим содержимое между кавычками
    def fix_escapes(match):
        text = match.group(1)
        # Заменяем одиночные \ на \\
        # Сначала заменяем \\ на временный маркер
        text = text.replace('\\\\', '\x00TEMP\x00')
        # Заменяем одиночные \ на \\
        text = text.replace('\\', '\\\\')
        # Возвращаем временный маркер обратно
        text = text.replace('\x00TEMP\x00', '\\\\\\\\')
        return '"' + text + '"'
    
    # Применяем только к строкам с pattern или description
    if '"pattern"' in line or '"description"' in line or '"documentation_text"' in line:
        # Находим строки в кавычках
        new_line = re.sub(r'"((?:[^"\\]|\\.)*?)"', fix_escapes, line)
        if new_line != original:
            fixes.append(f'Line {i}: исправлено экранирование')
            line = new_line
    
    fixed_lines.append(line)

fixed_content = '\n'.join(fixed_lines)

# Пробуем парсить
for enc in ['cp1251', 'utf-8', 'utf-8-sig']:
    try:
        with open(output_path, 'w', encoding=enc) as f:
            f.write(fixed_content)
        
        with open(output_path, 'r', encoding=enc) as f:
            data = json.load(f)
        
        print(f'OK! Кодировка: {enc}')
        print(f'Всего правил: {len(data.get("rules", {}))}')
        print(f'Исправлений: {len(fixes)}')
        for fix in fixes[:10]:
            print(f'  {fix}')
        break
    except Exception as e:
        print(f'FAIL {enc}: {e}')
