#!/usr/bin/env python3
"""Исправление JSON - корректная обработка экранирования"""
import json
import re

input_path = r'F:\TO_DBI\DATA\Рубрикатор\4.RUBRICATOR_PROMPTS.json'
output_path = r'F:\TO_DBI\DATA\Рубрикатор\4.RUBRICATOR_PROMPTS_fixed.json'

with open(input_path, 'r', encoding='cp1251') as f:
    content = f.read()

# Проблема: в regex паттернах используются одиночные обратные слэши
# которые не являются валидными JSON escape-последовательностями
# Нужно найти все строки с pattern и убедиться что обратные слэши корректны

lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines, 1):
    original = line
    
    # Исправляем строки с pattern
    if '"pattern"' in line:
        # Находим содержимое строки после "pattern": "
        match = re.search(r'("pattern"\s*:\s*)"(.*?)"(\s*,?\s*)$', line.strip())
        if match:
            prefix = match.group(1)
            pattern_text = match.group(2)
            suffix = match.group(3)
            
            # Проверяем и исправляем обратные слэши
            # В JSON строке каждый \ должен быть экранирован как \\
            # Но в regex паттерне \b должно стать \\\\b в JSON
            # А потом при чтении станет \\b что для regex значит \b
            
            # Заменяем одиночные \ на \\
            # Но сначала сохраняем уже экранированные \\
            new_pattern = pattern_text.replace('\\\\', '\x00DBL\x00')
            # Теперь заменяем одиночные \ на \\
            new_pattern = new_pattern.replace('\\', '\\\\')
            # Восстанавливаем \\
            new_pattern = new_pattern.replace('\x00DBL\x00', '\\\\\\\\')
            
            if new_pattern != pattern_text:
                line = f'{prefix}"{new_pattern}"{suffix}'
                print(f'Line {i}: fixed backslashes')
    
    fixed_lines.append(line)

fixed_content = '\n'.join(fixed_lines)

# Пробуем парсить
for enc in ['cp1251', 'utf-8']:
    try:
        with open(output_path, 'w', encoding=enc) as f:
            f.write(fixed_content)
        
        with open(output_path, 'r', encoding=enc) as f:
            data = json.load(f)
        
        print(f'OK! Кодировка: {enc}')
        print(f'Всего правил: {len(data.get("rules", {}))}')
        break
    except Exception as e:
        print(f'FAIL {enc}: {e}')
