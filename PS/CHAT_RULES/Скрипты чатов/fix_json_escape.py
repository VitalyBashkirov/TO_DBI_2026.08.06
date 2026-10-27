#!/usr/bin/env python3
"""Фикс regex escape в JSON"""
import json

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Заменяем одиночные backslash-b/w/s на двойные в patterns
# Это regex escape-последовательности которые JSON должен видеть как \\b \\w \\s
import re

# Находим все "pattern": "..." и исправляем
def fix_pattern(m):
    pattern = m.group(0)
    # Заменяем \b на \\b, \w на \\w, \s на \\s
    pattern = pattern.replace('\\b', '\\\\b')
    pattern = pattern.replace('\\w', '\\\\w')
    pattern = pattern.replace('\\s', '\\\\s')
    return pattern

# Применяем к содержимому между "pattern": " и "
content = re.sub(r'"pattern":\s*"[^"]*"', fix_pattern, content)

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'w', encoding='utf-8-sig') as f:
    f.write(content)

# Проверяем
try:
    json.load(open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', encoding='utf-8-sig'))
    print('JSON OK - валиден!')
except json.JSONDecodeError as e:
    print(f'JSON Error: {e}')
