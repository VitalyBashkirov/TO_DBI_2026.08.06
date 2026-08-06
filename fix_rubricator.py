#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Скрипт для обновления рубрикатора 4.RUBRICATOR_PROMPTS.json"""

import json
from pathlib import Path
import sys

# Путь к файлу рубрикатора (временная папка без кириллицы)
rubricator_path = Path(r'RubricatorTemp/4.RUBRICATOR_PROMPTS.json')
original_path = Path(r'DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json')

print(f"Чтение файла: {rubricator_path}")
with open(rubricator_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

rule_key = 'v50.SQL.OUTERJOIN.п.1.1'
rule = data['rules'][rule_key]

print("Обновление regex_patterns...")

patterns = rule['regex_patterns']['for_search']

# Добавляем паттерн для конструкции like: ac%id = gj.[ACCOUNT](true)
patterns.append({
    "pattern": "(\\w+)%?(\\w+)\\s*=\\s*(\\w+)\\.\\[(\\w+)\\]\\(true\\)",
    "description": "Конструкция like ac%id = gj.[ACCOUNT](true) с квадратными скобками",
    "flags": "i"
})

# Добавляем паттерн для поиска [КОЛОНКА](true) в любом месте
patterns.append({
    "pattern": "\\[(\\w+)\\]\\(true\\)",
    "description": "Любое использование [КОЛОНКА](true)",
    "flags": "i"
})

print(f"Всего паттернов для поиска: {len(patterns)}")

with open(rubricator_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Копируем обратно в оригинальную папку
import shutil
shutil.copy2(rubricator_path, original_path)

print(f"Файл скопирован в оригинальную папку: {original_path}")
print("Готово! Файл обновлен.")
