#!/usr/bin/env python3
"""Исправление JSON - замена одиночных кавычек внутри строк на экранированные"""
import json

input_path = r'F:\TO_DBI\DATA\Рубрикатор\4.RUBRICATOR_PROMPTS.json'
output_path = r'F:\TO_DBI\DATA\Рубрикатор\4.RUBRICATOR_PROMPTS_fixed.json'

with open(input_path, 'r', encoding='cp1251') as f:
    content = f.read()

# Пробуем найти и исправить проблемные места
lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines, 1):
    original = line
    # Если строка содержит pattern с одиночными кавычками внутри
    if '"pattern"' in line and "'" in line:
        # Заменяем одиночные кавычки на escaped версии
        # Находим содержимое между кавычками после "pattern":
        import re
        match = re.search(r'("pattern"\s*:\s*)"(.*?)"', line)
        if match:
            prefix = match.group(1)
            pattern_text = match.group(2)
            # Экранируем одиночные кавычки
            new_pattern = pattern_text.replace("'", "\\'")
            line = f'{prefix}"{new_pattern}"'
            print(f'Line {i}: fixed quotes in pattern')
    
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
