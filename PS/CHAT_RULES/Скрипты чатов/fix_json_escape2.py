#!/usr/bin/env python3
"""Фикс regex escape в JSON — полная версия"""
import json
import re

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# JSON требует чтобы regex \\b выглядел как \\\\b (два обратных слэша в JSON = один обратный слэш в строке)
# Проблемные паттерны:
# - \\\\w -> должно быть \\\\\\\\w
# - \\\\s -> должно быть \\\\\\\\s
# - \\\\b -> должно быть \\\\\\\\b
# Но edit_file уже поломал некоторые паттерны

# Сначала восстановим корректные regex из edit_file
# Заменяем неправильные экранирования

# Ищем паттерны между "pattern": " и " и исправляем
def fix_json_pattern(m):
    """Исправляем паттерн внутри JSON"""
    original = m.group(0)
    # Извлекаем содержимое между кавычками
    inner = original[11:-1]  # убираем '"pattern": "' и '"'
    
    # JSON regex escape:
    # \\b -> \\b (в JSON \\\\b = \\b в строке = regex \b)
    # \\\\w -> \\\\w (в JSON \\\\\\\\w = \\\\w в строке = regex \w)
    # Но edit_file сделал \\b вместо \\\\b
    
    # Заменяем одиночные \\b, \\w, \\s на двойные
    inner = re.sub(r'(?<=")\\b(?!")', '\\\\b', inner)
    inner = re.sub(r'(?<=")\\w(?!")', '\\\\w', inner)
    inner = re.sub(r'(?<=")\\s(?!")', '\\\\s', inner)
    
    # Также исправляем \\\\b (три обратных) -> \\\\\\\\b (четыре обратных)
    inner = inner.replace('\\\\\\b', '\\\\\\\\b')
    inner = inner.replace('\\\\\\w', '\\\\\\\\w')
    inner = inner.replace('\\\\\\s', '\\\\\\\\s')
    
    return '"pattern": "' + inner + '"'

content = re.sub(r'"pattern":\s*"[^"]*"', fix_json_pattern, content)

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'w', encoding='utf-8-sig') as f:
    f.write(content)

# Проверяем
try:
    json.load(open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', encoding='utf-8-sig'))
    print('JSON OK - валиден!')
except json.JSONDecodeError as e:
    print(f'JSON Error line {e.lineno}: {e.msg}')
    # Показываем проблемную строку
    with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    if e.lineno <= len(lines):
        print(f'Line {e.lineno}: {lines[e.lineno-1][:200]}')
