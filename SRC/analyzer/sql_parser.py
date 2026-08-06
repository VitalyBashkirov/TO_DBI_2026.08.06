                                                                                                                             #!/usr/bin/env python3
"""
SQL Parser - Автоматическое исправление кода по правилам из 5.RUBRICATOR_PARSER_SQL.json
"""
import re
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Кэш конфигурации
_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def load_config() -> Dict[str, Any]:
    """
    Загружает конфигурацию парсера из JSON-файла с кэшированием.
    
    Returns:
        Словарь с конфигурацией
    """
    global _CONFIG_CACHE
    
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    
    config_path = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор' / '5.RUBRICATOR_PARSER_SQL.json'
    
    if not config_path.exists():
        logger.warning(f"[PARSER] Конфигурация не найдена: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            _CONFIG_CACHE = json.load(f)
        logger.debug(f"[PARSER] Конфигурация загружена: {config_path.name} (версия {_CONFIG_CACHE.get('version', 'N/A')})")
        return _CONFIG_CACHE
    except Exception as e:
        logger.error(f"[PARSER] Ошибка загрузки конфигурации: {e}")
        return {}


def find_rule(rule_code: str) -> Optional[Dict[str, Any]]:
    """
    Находит правило по коду в конфигурации.
    
    Args:
        rule_code: Код правила (например, 'v50.SQL.OUTERJOIN.п.1.1')
        
    Returns:
        Словарь с правилом или None, если не найдено
    """
    config = load_config()
    rules = config.get('rules', [])
    
    for rule in rules:
        if rule.get('rule_code') == rule_code:
            return rule
    
    logger.debug(f"[PARSER] Правило не найдено: {rule_code}")
    return None


def apply_transform(match: re.Match, transform_template: str, named_mapping: Optional[Dict[str, str]] = None) -> str:
    """
    Применяет шаблон transform к найденному совпадению.
    
    Поддерживаемые плейсхолдеры:
        {1}, {2}, ... — группы захвата по номеру
        {left_table}, {right_table}, {left_column}, {right_column} — именованные (опционально)
        {limit}, {var_name}, {param_name} — для конкретных правил
    
    Args:
        match: Объект совпадения из re.Match
        transform_template: Шаблон преобразования
        named_mapping: Словарь для именованных групп (опционально)
        
    Returns:
        Преобразованная строка
    """
    result = transform_template
    
    # Замена нумерованных групп {1}, {2}, ...
    for i, group in enumerate(match.groups(), 1):
        placeholder = f'{{{i}}}'
        if placeholder in result:
            result = result.replace(placeholder, group or '')
    
    # Замена именованных групп
    if named_mapping:
        for name, value in named_mapping.items():
            placeholder = f'{{{name}}}'
            if placeholder in result:
                result = result.replace(placeholder, value or '')
    
    return result


def apply_fix(line: str, rule_code: str) -> Optional[str]:
    """
    Применяет исправление к строке кода на основе правила из 5.RUBRICATOR_PARSER_SQL.json.
    
    Args:
        line: Исходная строка кода
        rule_code: Код правила (например, 'v50.SQL.OUTERJOIN.п.1.1')
        
    Returns:
        Исправленная строка или None, если исправление не удалось
    """
    if not line or not rule_code:
        return None
    
    line_stripped = line.strip()
    
    # Находим правило
    rule = find_rule(rule_code)
    if not rule:
        logger.debug(f"[PARSER] Правило не найдено для {rule_code}")
        return None
    
    patterns = rule.get('patterns', [])
    if not patterns:
        logger.debug(f"[PARSER] Паттерны не найдены для {rule_code}")
        return None
    
    # Перебираем паттерны в порядке приоритета
    for pattern_def in patterns:
        pattern_name = pattern_def.get('name', 'unknown')
        regex = pattern_def.get('regex', '')
        transform_type = pattern_def.get('transform_type', 'regex')
        transform = pattern_def.get('transform', '')
        fallback_instruction = pattern_def.get('fallback_instruction', '')
        
        if not regex:
            continue
        
        try:
            # Ищем совпадение
            match = re.search(regex, line_stripped, re.IGNORECASE)
            
            if match:
                logger.debug(f"[PARSER] Применён паттерн '{pattern_name}' для {rule_code}")
                logger.debug(f"  Было: {line_stripped}")
                
                # Для гибридных паттернов без достаточного контекста возвращаем инструкцию
                if transform_type == 'hybrid' and not transform:
                    if fallback_instruction:
                        # Формируем комментарий с инструкцией
                        groups = match.groups()
                        instruction = fallback_instruction
                        
                        # Подставляем найденные значения в инструкцию
                        for i, group in enumerate(groups, 1):
                            instruction = instruction.replace(f'{{{i}}}', group or '')
                        
                        # Попытка извлечь алиас для более точной инструкции
                        if len(groups) >= 3:
                            right_alias = groups[2]  # Обычно 3-я группа - алиас
                            instruction = instruction.replace('{right_alias}', right_alias)
                        
                        result = f"{line_stripped}  {instruction}"
                        logger.debug(f"  Гибридный паттерн: возвращена инструкция")
                        return result
                
                # Применяем transform
                if transform:
                    # Создаём mapping для именованных групп
                    named_mapping = {}
                    groups = match.groups()
                    
                    # Стандартное маппирование для OUTER JOIN паттернов
                    if len(groups) >= 4:
                        named_mapping['left_table'] = groups[0]
                        named_mapping['left_column'] = groups[1]
                        named_mapping['right_table'] = groups[2]
                        named_mapping['right_column'] = groups[3]
                    
                    # Специфичное маппирование для PLPlus паттернов
                    if len(groups) >= 4 and 'plplus' in pattern_name.lower():
                        # Для паттерна: (\\w+)%?(\\w+)\\s*=\\s*(\\w+)\\.\\[(\\w+)\\]\\(true\\)
                        named_mapping['left_table'] = groups[0]
                        named_mapping['left_column'] = groups[1]
                        named_mapping['right_alias'] = groups[2]
                        named_mapping['right_table'] = groups[2]  # Используем алиас как имя таблицы (будет заменено вручную)
                        named_mapping['right_column'] = groups[3]
                    
                    # Для коллекций PLPlus
                    if len(groups) >= 3 and 'collection' in pattern_name.lower():
                        named_mapping['left_table'] = groups[0]
                        named_mapping['left_column'] = groups[1]
                        named_mapping['collection_alias'] = groups[2]
                        named_mapping['alias'] = groups[2]
                        # Для collection таблица неизвестна - используем алиас как placeholder
                        named_mapping['table'] = groups[2]  # Алиас вместо имени таблицы
                    
                    # Для ROWNUM паттернов
                    if len(groups) >= 1 and 'rownum' in pattern_name.lower():
                        named_mapping['limit'] = groups[0]
                    
                    # Для DATE паттернов
                    if len(groups) >= 1 and 'date' in pattern_name.lower():
                        named_mapping['var_name'] = groups[0]
                        named_mapping['param_name'] = groups[0]
                    
                    # Применяем transform
                    result = apply_transform(match, transform, named_mapping)
                    
                    # Проверка: если остались незаполненные плейсхолдеры - возвращаем fallback
                    if '{' in result and '}' in result:
                        # Есть незаполненные плейсхолдеры - используем fallback
                        if fallback_instruction:
                            instruction = fallback_instruction
                            # Подставляем известные значения
                            for key, value in named_mapping.items():
                                instruction = instruction.replace(f'{{{key}}}', value or '')
                            result = f"{line_stripped}  {instruction}"
                            logger.debug(f"  Гибридный паттерн: возвращена инструкция (остались плейсхолдеры)")
                            return result
                    
                    logger.debug(f"  Стало: {result}")
                    
                    # Если результат отличается от оригинала - возвращаем
                    if result != line_stripped:
                        return result
                    
        except re.error as e:
            logger.error(f"[PARSER] Ошибка регулярного выражения для {pattern_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"[PARSER] Ошибка при применении паттерна {pattern_name}: {e}")
            continue
    
    # Если ни один паттерн не сработал
    logger.debug(f"[PARSER] Ни один паттерн не совпал для {rule_code}")
    return None


def fix_line_with_fallback(line: str, rule_code: str) -> str:
    """
    Исправляет строку с использованием парсера и fallback-инструкций.
    
    Args:
        line: Исходная строка кода
        rule_code: Код правила
        
    Returns:
        Исправленная строка или исходная с комментарием
    """
    result = apply_fix(line, rule_code)
    
    if result and result != line.strip():
        return result
    
    # Если не удалось автоматически исправить - возвращаем с комментарием
    rule = find_rule(rule_code)
    if rule:
        patterns = rule.get('patterns', [])
        for pattern_def in patterns:
            fallback = pattern_def.get('fallback_instruction', '')
            if fallback:
                return f"{line.strip()}  {fallback}"
    
    # Если fallback инструкции нет - возвращаем оригинал
    return line


def process_line(line: str, issue_type: str) -> str:
    """
    Обрабатывает одну строку кода на основе типа проблемы.
    
    Args:
        line: Строка кода
        issue_type: Тип проблемы (например, 'v50.SQL.OUTERJOIN.п.1.1')
        
    Returns:
        Обработанная строка
    """
    return fix_line_with_fallback(line, issue_type)


def test_parser():
    """Тестирование парсера"""
    print("\n=== Тестирование SQL Parser ===\n")
    
    # Тест 1: Oracle outer join
    test_cases = [
        ('t1.id = t2.id(+)', 'v50.SQL.OUTERJOIN.п.1.1', 'left join t2 on t1.id = t2.id'),
        ('where rownum = 1', 'v50.SQL.ROWNUM.п.1.2', 'fetch first 1 rows only'),
        ('DateTimeEnd date', 'v50.STOR.DATE.п.2.2', 'DateTimeEnd date_time'),
        # Тесты из технического задания
        ('ac%id = gj.[ACCOUNT](true)', 'v50.SQL.OUTERJOIN.п.1.1', 'left join'),  # Гибридный паттерн
        ('cr.[LIST_PAY] = fo&collection(true)', 'v50.SQL.OUTERJOIN.п.1.1', 'left join'),  # Коллекция
    ]
    
    passed = 0
    failed = 0
    
    for line, rule_code, expected_keyword in test_cases:
        result = apply_fix(line, rule_code)
        if result and expected_keyword.lower() in result.lower():
            status = "[OK]"
            passed += 1
        else:
            status = "[FAIL]"
            failed += 1
        
        print(f"{status} Вход: {line}")
        print(f"  Правило: {rule_code}")
        print(f"  Результат: {result}")
        print(f"  Ожидается (ключевое слово): {expected_keyword}")
        print()

    print(f"\n=== Итоги: {passed} прошло, {failed} не прошло ===")
    return failed == 0


if __name__ == '__main__':
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    success = test_parser()
    sys.exit(0 if success else 1)
