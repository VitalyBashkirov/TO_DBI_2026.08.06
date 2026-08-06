# -*- coding: utf-8 -*-
import json
from pathlib import Path

path = Path("RubricatorTemp/4.RUBRICATOR_PROMPTS.json")

with open(path, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

rule = data["rules"]["v50.SQL.OUTERJOIN.п.1.1"]
patterns = rule["regex_patterns"]["for_search"]

# Добавляем новый паттерн
new_pattern = {
    "pattern": "(\\w+)%?(\\w+)\\s*=\\s*(\\w+)\\.\\[(\\w+)\\]\\(true\\)",
    "description": "Конструкция like ac%id = gj.[ACCOUNT](true)",
    "flags": "i"
}

patterns.append(new_pattern)
print(f"Добавлен паттерн. Всего паттернов: {len(patterns)}")

# Сохраняем
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Копируем обратно
import shutil
shutil.copy2(path, "DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json")
print("Файл обновлен и скопирован обратно")
