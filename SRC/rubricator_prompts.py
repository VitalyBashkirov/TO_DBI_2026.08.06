#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль работы с рубрикатором 4.RUBRICATOR_PROMPTS.json
Расширенные инструкции для поиска и исправления проблемных конструкций PL/Plus
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class RubricatorPrompts:
    """Класс для работы с файлом 4.RUBRICATOR_PROMPTS.json"""
    
    def __init__(self, rubricator_dir: Path):
        """
        Инициализация рубрикатора
        
        Args:
            rubricator_dir: Путь к каталогу рубрикатора
        """
        self.rubricator_dir = rubricator_dir
        self.prompts_file = rubricator_dir / '4.RUBRICATOR_PROMPTS.json'
        self.data: Dict[str, Any] = {}
        self.loaded = False
    
    def load(self) -> bool:
        """
        Загрузка данных из файла 4.RUBRICATOR_PROMPTS.json
        
        Returns:
            True если загрузка успешна, False иначе
        """
        try:
            if not self.prompts_file.exists():
                print(f"[WARN] Файл рубрикатора не найден: {self.prompts_file}")
                return False
            
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            self.loaded = True
            print(f"[INFO] Рубрикатор 4.RUBRICATOR_PROMPTS.json загружен (версия {self.data.get('version', 'N/A')})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка загрузки рубрикатора: {e}")
            self.loaded = False
            return False
    
    def get_rule(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Получение правила по коду
        
        Args:
            code: Код правила (например, 'v50.SQL.OUTERJOIN.п.1.1')
        
        Returns:
            Словарь с правилом или None если не найдено
        """
        if not self.loaded:
            return None
        
        rules = self.data.get('rules', {})
        return rules.get(code)
    
    def is_rule_enabled(self, code: str) -> bool:
        """
        Проверка включено ли правило
        
        Args:
            code: Код правила
        
        Returns:
            True если правило включено, False иначе
        """
        rule = self.get_rule(code)
        if not rule:
            return False
        
        # Проверяем наличие поля disabled
        return not rule.get('disabled', False)
    
    def get_search_prompt(self, code: str) -> Optional[str]:
        """
        Получение промпта для поиска проблемной конструкции
        
        Args:
            code: Код правила
        
        Returns:
            Текст промпта или None
        """
        rule = self.get_rule(code)
        if not rule:
            return None
        
        return rule.get('search_prompt')
    
    def get_fix_prompt(self, code: str) -> Optional[str]:
        """
        Получение промпта для исправления проблемы
        
        Args:
            code: Код правила
        
        Returns:
            Текст промпта или None
        """
        rule = self.get_rule(code)
        if not rule:
            return None
        
        return rule.get('fix_prompt')
    
    def get_test_generation_prompt(self, code: str) -> Optional[str]:
        """
        Получение промпта для генерации тестового файла
        
        Args:
            code: Код правила
        
        Returns:
            Текст промпта или None
        """
        rule = self.get_rule(code)
        if not rule:
            return None
        
        return rule.get('test_generation_prompt')
    
    def get_regex_patterns(self, code: str) -> Optional[Dict[str, List[Dict[str, str]]]]:
        """
        Получение регулярных выражений для поиска
        
        Args:
            code: Код правила
        
        Returns:
            Словарь с паттернами {'for_search': [...], 'for_ignore': [...]} или None
        """
        rule = self.get_rule(code)
        if not rule:
            return None
        
        return rule.get('regex_patterns')
    
    def get_examples(self, code: str) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Получение примеров "было/стало"
        
        Args:
            code: Код правила
        
        Returns:
            Словарь с примерами или None
        """
        rule = self.get_rule(code)
        if not rule:
            return None
        
        return rule.get('examples')
    
    def get_fix_instruction(self, code: str) -> Optional[str]:
        """
        Получение пошаговой инструкции по исправлению
        
        Args:
            code: Код правила
        
        Returns:
            Текст инструкции или None
        """
        rule = self.get_rule(code)
        if not rule:
            return None
        
        return rule.get('fix_instruction')
    
    def search_code_in_file(self, file_path: Path, code: str, log_callback=None) -> List[Dict[str, Any]]:
        """
        Поиск проблемных конструкций в файле по коду правила
        
        Args:
            file_path: Путь к файлу
            code: Код правила
            log_callback: Callback для логирования (опционально)
        
        Returns:
            Список найденных проблем: [{'line_number': N, 'line': '...', 'pattern': '...', 'description': '...'}]
        """
        if not self.loaded:
            if log_callback:
                log_callback("[WARN] Рубрикатор не загружен", 'warning')
            return []
        
        rule = self.get_rule(code)
        if not rule:
            if log_callback:
                log_callback(f"[WARN] Правило не найдено: {code}", 'warning')
            return []
        
        # Проверка отключения правила
        if rule.get('disabled', False):
            if log_callback:
                log_callback(f"[INFO] Правило отключено: {code}", 'info')
            return []
        
        patterns_config = self.get_regex_patterns(code)
        if not patterns_config:
            if log_callback:
                log_callback(f"[WARN] Паттерны не найдены для правила: {code}", 'warning')
            return []
        
        search_patterns = patterns_config.get('for_search', [])
        ignore_patterns = patterns_config.get('for_ignore', [])
        
        # Компилируем паттерны
        compiled_search = []
        for p in search_patterns:
            try:
                flags = re.IGNORECASE if p.get('flags', '').lower() == 'i' else 0
                compiled_search.append({
                    'pattern': re.compile(p['pattern'], flags),
                    'description': p.get('description', '')
                })
            except re.error as e:
                if log_callback:
                    log_callback(f"[ERROR] Ошибка компиляции паттерна: {e}", 'error')
        
        compiled_ignore = []
        for p in ignore_patterns:
            try:
                flags = re.IGNORECASE if p.get('flags', '').lower() == 'i' else 0
                compiled_ignore.append({
                    'pattern': re.compile(p['pattern'], flags),
                    'description': p.get('description', '')
                })
            except re.error as e:
                if log_callback:
                    log_callback(f"[ERROR] Ошибка компиляции игнорирующего паттерна: {e}", 'error')
        
        # Читаем файл
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            if log_callback:
                log_callback(f"[ERROR] Ошибка чтения файла: {e}", 'error')
            return []
        
        # Ищем проблемы
        results = []
        for line_num, line in enumerate(lines, 1):
            # Проверяем игнорирующие паттерны
            should_ignore = False
            for ignore in compiled_ignore:
                if ignore['pattern'].search(line):
                    should_ignore = True
                    break
            
            if should_ignore:
                continue
            
            # Ищем совпадения
            for search in compiled_search:
                match = search['pattern'].search(line)
                if match:
                    results.append({
                        'line_number': line_num,
                        'line': line.strip(),
                        'pattern': search['pattern'].pattern,
                        'description': search['description'],
                        'match_groups': match.groups()
                    })
        
        if log_callback and results:
            log_callback(f"  Найдено проблем: {len(results)} в файле {file_path.name}", 'info')
        
        return results
    
    def generate_test_file(self, code: str, output_dir: Path, log_callback=None) -> Optional[Path]:
        """
        Генерация тестового файла для правила
        
        Args:
            code: Код правила
            output_dir: Каталог для сохранения
            log_callback: Callback для логирования
        
        Returns:
            Путь к созданному файлу или None
        """
        if not self.loaded:
            if log_callback:
                log_callback("[WARN] Рубрикатор не загружен", 'warning')
            return None
        
        rule = self.get_rule(code)
        if not rule:
            if log_callback:
                log_callback(f"[WARN] Правило не найдено: {code}", 'warning')
            return None
        
        # Создаем каталог если не существует
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            if log_callback:
                log_callback(f"  Создан каталог: {output_dir}", 'info')
        
        # Получаем промпт для генерации
        test_prompt = self.get_test_generation_prompt(code)
        if not test_prompt:
            if log_callback:
                log_callback(f"[WARN] Промпт генерации не найден для правила: {code}", 'warning')
            return None
        
        # Получаем примеры
        examples = self.get_examples(code)
        if not examples:
            if log_callback:
                log_callback(f"[WARN] Примеры не найдены для правила: {code}", 'warning')
            return None
        
        # Получаем паттерны
        patterns_config = self.get_regex_patterns(code)
        
        # Генерируем содержимое файла
        content = self._generate_test_content(code, rule, examples, patterns_config)
        
        # Формируем имя файла
        timestamp = Path(__import__('datetime').datetime.now().strftime('%Y%m%d'))
        safe_code = code.replace('.', '_').replace(' ', '_').replace('п', 'p')
        file_name = f"test_{safe_code}_{timestamp}.plp"
        file_path = output_dir / file_name
        
        # Записываем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if log_callback:
            log_callback(f"  Создан тестовый файл: {file_path}", 'success')
        
        return file_path
    
    def _generate_test_content(self, code: str, rule: Dict, examples: Dict, patterns_config: Dict) -> str:
        """
        Генерация содержимого тестового файла
        
        Args:
            code: Код правила
            rule: Данные правила
            examples: Примеры "было/стало"
            patterns_config: Конфигурация паттернов
        
        Returns:
            Сгенерированный текст файла
        """
        lines = []
        
        # Заголовок
        lines.append(f"-- ====================================================")
        lines.append(f"-- Тестовый файл для проверки правила: {code}")
        lines.append(f"-- Дата генерации: {Path.__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"-- ====================================================")
        lines.append("")
        
        # Описание правила
        short_desc = rule.get('short_description', 'Описание недоступно')
        lines.append(f"-- {short_desc}")
        lines.append("")
        
        # Получаем паттерны для поиска
        search_patterns = patterns_config.get('for_search', []) if patterns_config else []
        
        # Добавляем тестовые конструкции для каждого паттерна
        line_counter = 10
        for i, pattern_info in enumerate(search_patterns, 1):
            pattern_desc = pattern_info.get('description', 'Описание недоступно')
            
            lines.append(f"-- Строка {line_counter}: Тест паттерна {i}")
            lines.append(f"-- Паттерн: {pattern_desc}")
            lines.append("")
            
            # Ищем пример для этого типа
            example_code = None
            for example_name, example_data in examples.items():
                if isinstance(example_data, dict):
                    bad_code = example_data.get('bad', '')
                    if bad_code:
                        example_code = bad_code
                        break
            
            if example_code:
                lines.append(f"-- Пример: {example_code}")
                lines.append("")
            
            # Добавляем placeholder для тестового кода
            lines.append(f"--TODO: Добавить тестовый код для паттерна {i}")
            lines.append(f"--TODO: {pattern_desc}")
            lines.append("")
            
            line_counter += 10
        
        # Добавляем корректные конструкции (для проверки ложных срабатываний)
        lines.append(f"-- ====================================================")
        lines.append(f"-- Корректные конструкции (для проверки ложных срабатываний)")
        lines.append(f"-- ====================================================")
        lines.append("")
        lines.append("--TODO: Добавить корректный код PL/Plus")
        lines.append("")
        
        # Блок begin/end
        lines.append("begin")
        lines.append("  exit; --<добавлено при генерации теста>")
        lines.append("end; --<добавлено при генерации теста>")
        
        return '\n'.join(lines)
    
    def get_all_rules(self) -> List[Dict[str, str]]:
        """
        Получение списка всех доступных правил
        
        Returns:
            Список словарей [{'code': '...', 'description': '...'}, ...]
        """
        if not self.loaded:
            return []
        
        rules = self.data.get('rules', {})
        result = []
        
        for code, rule_data in rules.items():
            result.append({
                'code': code,
                'description': rule_data.get('short_description', ''),
                'category': rule_data.get('category', ''),
                'priority': rule_data.get('priority', 'normal')
            })
        
        return result


# Тестовый запуск
if __name__ == '__main__':
    from pathlib import Path
    
    rubricator_dir = Path(__file__).parent.parent / 'DATA' / 'Рубрикатор'
    prompts = RubricatorPrompts(rubricator_dir)
    
    if prompts.load():
        print("\nДоступные правила:")
        for rule in prompts.get_all_rules():
            print(f"  {rule['code']}: {rule['description']}")
        
        # Проверка конкретного правила
        code = 'v50.SQL.OUTERJOIN.п.1.1'
        rule = prompts.get_rule(code)
        if rule:
            print(f"\nПравило {code}:")
            print(f"  Описание: {rule.get('short_description')}")
            print(f"  Категория: {rule.get('category')}")
            print(f"  Приоритет: {rule.get('priority')}")
