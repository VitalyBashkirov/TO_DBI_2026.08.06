#!/usr/bin/env python3
"""
Генератор тестовых .plp файлов на основе всех рубрикаторов
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from fixer.markdown_rubricator_loader_v3 import MarkdownRubricatorLoaderV3


class TestGenerator:
    """Генератор тестовых файлов для правил рубрикатора v3.0.0"""
    
    def __init__(self, rubricator_dir: Path):
        self.rubricator_dir = rubricator_dir
        self.rubricator_v3 = MarkdownRubricatorLoaderV3(rubricator_dir)
        self._load_all()
    
    def _load_all(self):
        """Загружает все рубрикаторы (v3.0.0 - основной)"""
        # v3.0.0 загружается автоматически в __init__
        # Сохраняем для обратной совместимости
        self.fixes_md = list(self.rubricator_v3.rules.values())
        self.prompts_json = {'rules': {code: self._rule_to_dict(rule) for code, rule in self.rubricator_v3.rules.items()}}
        self.parser_json = self._load_parser_json_compat()
    
    def _rule_to_dict(self, rule) -> Dict:
        """Преобразует RubricatorRule в словарь для совместимости"""
        return {
            'code': rule.code,
            'short_description': rule.short_description,
            'category': rule.category,
            'code_example_bad': rule.code_example_bad[0] if rule.code_example_bad else '',
            'code_example_good': rule.code_example_good or '',
            'examples': {},
            'rules': {}
        }
    
    def _load_parser_json_compat(self) -> Dict:
        """Загрузка 5.RUBRICATOR_PARSER_SQL.json для совместимости"""
        file_path = self.rubricator_dir / '5.RUBRICATOR_PARSER_SQL.json'
        
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Ошибка загрузки 5.RUBRICATOR_PARSER_SQL.json: {e}")
            return {}
    
    def _load_fixes_md(self):
        """Загрузка данных из 3.RUBRICATOR_FIXES.md"""
        self.fixes_md = []
        file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            current_fix = {}
            for line in lines:
                if not line.strip() or line.startswith('#'):
                    continue
                
                if line.startswith('|') and not '|---' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 8:
                        try:
                            # Извлекаем теги из колонки "++"
                            plus_plus = parts[2].strip() if len(parts) > 2 else ''
                            tags = ''
                            if plus_plus and plus_plus[0] == '+':
                                remaining = plus_plus[1:]
                                if remaining.startswith('|'):
                                    parts_after_plus = remaining.split('|')
                                    if len(parts_after_plus) >= 2:
                                        tags = parts_after_plus[1].strip()
                            
                            current_fix = {
                                'n': parts[1].strip() if len(parts) > 1 else '',
                                'plus_plus': plus_plus,
                                'tags': tags,
                                'file_codes': parts[3].strip() if len(parts) > 3 else '',
                                'category': parts[4].strip() if len(parts) > 4 else '',
                                'short_desc': parts[5].strip() if len(parts) > 5 else '',
                                'full_desc': parts[6].strip() if len(parts) > 6 else '',
                                'example_code': parts[7].strip() if len(parts) > 7 else '',
                                'example_fixed': parts[8].strip() if len(parts) > 8 else '',
                                'should_generate': plus_plus.startswith('+')
                            }
                            
                            # Извлекаем код файла
                            if current_fix['file_codes']:
                                file_code = current_fix['file_codes'].split('.')[0].strip()
                                current_fix['file_code'] = file_code
                            
                            self.fixes_md.append(current_fix)
                            current_fix = {}
                        except Exception:
                            continue
        except Exception as e:
            print(f"[!] Ошибка загрузки 3.RUBRICATOR_FIXES.md: {e}")
    
    def _load_prompts_json(self):
        """Загрузка данных из 4.RUBRICATOR_PROMPTS.json"""
        self.prompts_json = {}
        file_path = self.rubricator_dir / '4.RUBRICATOR_PROMPTS.json'
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                self.prompts_json = json.load(f)
        except Exception as e:
            print(f"[!] Ошибка загрузки 4.RUBRICATOR_PROMPTS.json: {e}")
    
    def _load_parser_json(self):
        """Загрузка данных из 5.RUBRICATOR_PARSER_SQL.json"""
        self.parser_json = {}
        file_path = self.rubricator_dir / '5.RUBRICATOR_PARSER_SQL.json'
        
        if not file_path.exists():
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                self.parser_json = json.load(f)
        except Exception as e:
            print(f"[!] Ошибка загрузки 5.RUBRICATOR_PARSER_SQL.json: {e}")
    
    def get_all_rule_codes(self) -> List[str]:
        """Получить все коды правил из всех источников"""
        codes = set()
        
        # Из 3.RUBRICATOR_FIXES.md
        for fix in self.fixes_md:
            if fix.get('file_code'):
                codes.add(fix['file_code'])
        
        # Из 4.RUBRICATOR_PROMPTS.json
        rules = self.prompts_json.get('rules', {})
        codes.update(rules.keys())
        
        # Из 5.RUBRICATOR_PARSER_SQL.json
        rules = self.parser_json.get('rules', [])
        for rule in rules:
            if rule.get('rule_code'):
                codes.add(rule['rule_code'])
        
        return sorted(codes)
    
    def get_fix_metadata(self, rule_code: str) -> Optional[Dict]:
        """Получить метаданные правила из рубрикатора v3.0.0"""
        rule = self.rubricator_v3.get_rule_by_code(rule_code)
        if not rule:
            return None
    
        return {
            'code': rule.code,
            'category': rule.category,
            'short_desc': rule.short_description,
            'full_desc': rule.documentation_text,
            'example_code': rule.code_example_bad[0] if rule.code_example_bad else '',
            'example_fixed': rule.code_example_good or '',
            'priority': rule.priority,
            'subcategory': rule.subcategory
        }
    
    def get_rule_prompts(self, rule_code: str) -> Optional[Dict]:
        """Получить данные правила из рубрикатора v3.0.0"""
        rule = self.rubricator_v3.get_rule_by_code(rule_code)
        if not rule:
            return None
    
        return {
            'code': rule.code,
            'short_description': rule.short_description,
            'category': rule.category,
            'code_example_bad': rule.code_example_bad,
            'code_example_good': rule.code_example_good,
            'documentation_text': rule.documentation_text,
            'fix_instruction': rule.fix_instruction,
            'search_prompt': rule.search_prompt,
            'regex_patterns': {
                'for_search': rule.regex_patterns_search,
                'for_ignore': rule.regex_patterns_ignore
            }
        }
    
    def get_rule_patterns(self, rule_code: str) -> List[Dict]:
        """Получить паттерны правила из рубрикатора v3.0.0 (regex_patterns)"""
        rule = self.rubricator_v3.get_rule_by_code(rule_code)
        if not rule:
            return []
        
        # Преобразуем regex_patterns в формат паттернов
        patterns = []
        for p in rule.regex_patterns_search:
            patterns.append({
                'name': p.get('description', 'pattern'),
                'description': p.get('description', ''),
                'example_in': f"-- Паттерн: {p.get('pattern', '')}",
                'example_out': "-- Требуется ручное преобразование"
            })
        
        return patterns
    
    def generate_test_file(self, rule_code: str, output_dir: Path) -> Optional[Path]:
        """
        Генерирует тестовый .plp файл для указанного правила v3.0.0
        
        Args:
            rule_code: Код правила (например, 'v50.SQL.OUTERJOIN.п.1.1')
            output_dir: Каталог для сохранения
            
        Returns:
            Путь к созданному файлу или None
        """
        # Получаем данные из рубрикатора v3.0.0
        rule = self.rubricator_v3.get_rule_by_code(rule_code)
        
        if not rule:
            return None
    
        category = rule.category
        short_desc = rule.short_description
        subcategory = rule.subcategory if rule.subcategory != 'OTHER' else ''
        
        # Получаем паттерны
        patterns = self.get_rule_patterns(rule_code)
        
        # Формируем содержимое файла
        lines = []
        
        # Заголовок
        lines.append("--" + "=" * 70)
        lines.append(f"-- ТЕСТОВЫЙ ФАЙЛ ДЛЯ ПРАВИЛА: {rule_code}")
        lines.append(f"-- Описание: {short_desc}")
        lines.append(f"-- Категория: {category}")
        if subcategory:
            lines.append(f"-- Подкатегория: {subcategory}")
        lines.append(f"-- Приоритет: {rule.priority}")
        lines.append(f"-- Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("--" + "=" * 70)
        lines.append("")
        
        # Примеры из рубрикатора
        if rule.code_example_bad:
            lines.append("--" + "-" * 70)
            lines.append("-- = НЕПРАВИЛЬНЫЙ КОД (ДО ИСПРАВЛЕНИЯ) =")
            lines.append("--" + "-" * 70)
            for i, bad_example in enumerate(rule.code_example_bad):
                if i > 0:
                    lines.append("")
                    lines.append("-- Дополнительный пример:")
                lines.append(bad_example)
            lines.append("")
        
        if rule.code_example_good:
            lines.append("--" + "-" * 70)
            lines.append("-- = ПРАВИЛЬНЫЙ КОД (ПОСЛЕ ИСПРАВЛЕНИЯ) =")
            lines.append("--" + "-" * 70)
            lines.append(rule.code_example_good)
            lines.append("")
        
        # Инструкция по исправлению
        if rule.fix_instruction:
            lines.append("--" + "-" * 70)
            lines.append("-- = ИНСТРУКЦИЯ ПО ИСПРАВЛЕНИЮ =")
            lines.append("--" + "-" * 70)
            lines.append(rule.fix_instruction)
            lines.append("")
        
        # Дополнительные тесты из паттернов
        if patterns:
            lines.append("--" + "-" * 70)
            lines.append("-- = ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ (из паттернов) =")
            lines.append("--" + "-" * 70)
            
            for pattern in patterns:
                lines.append("")
                lines.append(f"-- Паттерн: {pattern.get('name', 'unknown')}")
                lines.append(f"-- Описание: {pattern.get('description', '')}")
                if pattern.get('example_in'):
                    lines.append(f"-- {pattern.get('example_in')}")
                if pattern.get('example_out'):
                    lines.append(f"-- {pattern.get('example_out')}")
        
            lines.append("")
        
        lines.append("--" + "=" * 70)
        lines.append("-- Конец файла")
        lines.append("--" + "=" * 70)
        
        # Сохраняем файл
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = rule_code.replace('.', '_').replace(' ', '_').replace(':', '_')
        file_name = f"test_{safe_name}.plp"
        file_path = output_dir / file_name
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return file_path
        except Exception as e:
            print(f"[!] Ошибка записи файла {file_path}: {e}")
            return None
    
        # 4. Формируем содержимое файла
        lines = []
        
        # Заголовок
        lines.append("--" + "=" * 60)
        lines.append(f"-- Тестовый файл для правила: {rule_code}")
        lines.append(f"-- Описание: {short_desc}")
        lines.append(f"-- Категория: {category}")
        lines.append(f"-- Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("--" + "=" * 60)
        lines.append("")
        
        # Неправильный код
        lines.append("--" + "-" * 60)
        lines.append("-- = НЕПРАВИЛЬНЫЙ КОД (ДО ИСПРАВЛЕНИЯ) =")
        lines.append("--" + "-" * 60)
        if example_bad:
            lines.append(example_bad)
        else:
            lines.append("-- Нет примера неправильного кода")
        lines.append("")
        
        # Правильный код
        lines.append("--" + "-" * 60)
        lines.append("-- = ПРАВИЛЬНЫЙ КОД (ПОСЛЕ ИСПРАВЛЕНИЯ) =")
        lines.append("--" + "-" * 60)
        if example_good:
            lines.append(example_good)
        else:
            lines.append("-- Нет примера правильного кода")
        lines.append("")
        
        # Дополнительные тесты из паттернов
        if patterns:
            lines.append("--" + "-" * 60)
            lines.append("-- = ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ (из паттернов SQL парсера) =")
            lines.append("--" + "-" * 60)
            
            for pattern in patterns:
                pattern_name = pattern.get('name', 'unknown')
                pattern_desc = pattern.get('description', '')
                example_in = pattern.get('example_in', '')
                example_out = pattern.get('example_out', '')
                
                lines.append("")
                lines.append(f"-- Паттерн: {pattern_name}")
                lines.append(f"-- Описание: {pattern_desc}")
                
                if example_in:
                    lines.append(f"-- Было: {example_in}")
                if example_out:
                    lines.append(f"-- Стало: {example_out}")
            
            lines.append("")
        
        # Примеры из JSON
        if prompts_data and 'examples' in prompts_data:
            examples = prompts_data['examples']
            if len(examples) > 1:  # Первый уже выведен выше
                lines.append("--" + "-" * 60)
                lines.append("-- = ДОПОЛНИТЕЛЬНЫЕ ПРИМЕРЫ (из JSON) =")
                lines.append("--" + "-" * 60)
                
                for example_name, example_data in list(examples.items())[1:]:
                    lines.append("")
                    lines.append(f"-- Пример: {example_name}")
                    if example_data.get('bad'):
                        lines.append(f"-- Было: {example_data['bad']}")
                    if example_data.get('good'):
                        lines.append(f"-- Стало: {example_data['good']}")
                
                lines.append("")
        
        lines.append("--" + "=" * 60)
        lines.append("-- Конец файла")
        lines.append("--" + "=" * 60)
        
        # 5. Сохраняем файл
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Безопасное имя файла
        safe_name = rule_code.replace('.', '_').replace(' ', '_').replace(':', '_')
        file_name = f"test_{safe_name}.plp"
        file_path = output_dir / file_name
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return file_path
        except Exception as e:
            print(f"[!] Ошибка записи файла {file_path}: {e}")
            return None
    
    def generate_all_tests(self, output_dir: Path, rule_codes: List[str] = None) -> List[Path]:
        """
        Генерирует тестовые файлы для всех указанных правил
        
        Args:
            output_dir: Каталог для сохранения
            rule_codes: Список кодов правил (если None - все доступные)
            
        Returns:
            Список путей к созданным файлам
        """
        if rule_codes is None:
            rule_codes = self.get_all_rule_codes()
        
        files = []
        for rule_code in rule_codes:
            try:
                file_path = self.generate_test_file(rule_code, output_dir)
                if file_path:
                    files.append(file_path)
            except Exception as e:
                print(f"[!] Ошибка генерации для {rule_code}: {e}")
        
        return files


def main():
    """Запуск генерации тестов"""
    rubricator_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор'
    output_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Тестовые файлы'
    
    print(f"\nГенератор тестовых файлов")
    print(f"Каталог рубрикаторов: {rubricator_dir}")
    print(f"Каталог вывода: {output_dir}")
    print()
    
    generator = TestGenerator(rubricator_dir)
    
    # Получаем все доступные правила
    all_rules = generator.get_all_rule_codes()
    print(f"Всего правил: {len(all_rules)}")
    print(f"Правила: {', '.join(all_rules[:10])}{'...' if len(all_rules) > 10 else ''}")
    print()
    
    # Генерируем тесты
    files = generator.generate_all_tests(output_dir)
    
    print(f"\nСоздано файлов: {len(files)}")
    for file_path in files:
        print(f"  - {file_path.name}")


if __name__ == '__main__':
    main()
