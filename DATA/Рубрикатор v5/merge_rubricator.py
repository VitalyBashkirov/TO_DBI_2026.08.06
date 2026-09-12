#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт объединения файлов рубрикатора 4a-4d в единый 4.RUBRICATOR_PROMPT v5.json
"""

import json
from pathlib import Path

# Путь к каталогу с рубрикатором
RUBRICATOR_DIR = Path(r"F:\TO_DBI\DATA\Рубрикатор v5")

# Список файлов для объединения
SOURCE_FILES = [
    RUBRICATOR_DIR / "4a.RUBRICATOR_PROMPT_v53.json",
    RUBRICATOR_DIR / "4b.RUBRICATOR_PROMPT_тдс20240828.json",
    RUBRICATOR_DIR / "4c.RUBRICATOR_PROMPT_тклоик20240828.json",
    RUBRICATOR_DIR / "4d.RUBRICATOR_PROMPT_PlpCheck.json",
]

# Итоговый файл
OUTPUT_FILE = RUBRICATOR_DIR / "4.RUBRICATOR_PROMPT v5.json"

def merge_rubricators():
    """Объединение файлов рубрикатора"""
    
    # Инициализация общего словаря
    merged_data = {
        "version": "5.3.0",
        "total_rules": 0,
        "based_on": "Объединение 4a-4d",
        "last_updated": "2026-08-21",
        "ai_analysis_enabled": True,
        "rules": {}
    }
    
    # Проходим по каждому файлу
    for file_path in SOURCE_FILES:
        if not file_path.exists():
            print(f"[WARN] Файл не найден: {file_path}")
            continue
        
        print(f"[INFO] Загрузка: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            # Если в файле есть правила, объединяем их
            if 'rules' in data and isinstance(data['rules'], dict):
                for rule_code, rule_data in data['rules'].items():
                    # Добавляем правило в общий словарь
                    merged_data['rules'][rule_code] = rule_data
                    
                    # Обновляем total_rules
                    merged_data['total_rules'] += 1
            
            # Сохраняем версию, если она есть
            if 'version' in data:
                merged_data['version'] = data['version']
            
            # Сохраняем источник (для справки)
            sources = merged_data.get('based_on', '')
            if isinstance(sources, str):
                merged_data['based_on'] = sources + ", " + data.get('source', file_path.stem)
                
        except json.JSONDecodeError as e:
            print(f"[ERROR] Ошибка JSON в файле {file_path.name}: {e}")
            print(f"       Пропускаем этот файл (или исправьте его вручную)")
            continue
        except Exception as e:
            print(f"[ERROR] Непредвиденная ошибка при чтении {file_path.name}: {e}")
            continue
    
    # Проверка: есть ли вообще правила
    if not merged_data['rules']:
        print("[ERROR] Не удалось загрузить ни одного правила!")
        return
    
    print(f"\n[INFO] Всего объединено правил: {merged_data['total_rules']}")
    
    # Сохраняем итоговый файл
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Файл создан: {OUTPUT_FILE}")
        print(f"[SUCCESS] Теперь программа сможет корректно загрузить все правила!")
    except Exception as e:
        print(f"[ERROR] Ошибка сохранения файла: {e}")

if __name__ == '__main__':
    merge_rubricators()