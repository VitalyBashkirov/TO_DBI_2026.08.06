#!/usr/bin/env python3
"""
Загрузчик рубрикатора v3.0.0
Использует JSON файлы: 4.RUBRICATOR_PROMPTS.json, 5.RUBRICATOR_PARSER_SQL.json
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class RubricatorRule:
    """Правило рубрикатора v3.0.0"""
    code: str
    short_description: str
    documentation_text: str
    plplus_materials_note: str
    search_prompt: str
    regex_patterns_search: List[Dict]  # patterns for_search
    regex_patterns_ignore: List[Dict]  # patterns for_ignore
    code_example_bad: List[str]  # Массив примеров
    code_example_good: Optional[str]
    fix_instruction: str
    priority: str
    category: str
    subcategory: str
    version: str = "3.0.0"


class MarkdownRubricatorLoaderV3:
    """Загрузчик рубрикатора v3.0.0"""
    
    def __init__(self, rubricator_dir: str = None):
        if rubricator_dir is None:
            rubricator_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор'
        else:
            rubricator_dir = Path(rubricator_dir)
        
        self.rubricator_dir = Path(rubricator_dir)
        self.rules: Dict[str, RubricatorRule] = {}
        self.metadata: Dict = {}
        
        self._load_prompts_json()
    
    def _load_prompts_json(self):
        """Загрузка 4.RUBRICATOR_PROMPTS.json"""
        file_path = self.rubricator_dir / '4.RUBRICATOR_PROMPTS.json'
        
        if not file_path.exists():
            print(f"[!] Файл не найден: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            self.metadata = {
                'version': data.get('version', 'unknown'),
                'based_on': data.get('based_on', ''),
                'last_updated': data.get('last_updated', ''),
                'total_rules': data.get('total_rules', 0)
            }
            
            # Парсинг правил
            rules_data = data.get('rules', {})
            for code, rule_dict in rules_data.items():
                # Преобразуем в RubricatorRule
                # code_example_bad может быть строкой или списком
                bad_examples = rule_dict.get('code_example_bad', '')
                if isinstance(bad_examples, str):
                    bad_examples = [bad_examples] if bad_examples else []
                # Добавляем дополнительные примеры
                for i in range(2, 5):
                    key = f'code_example_bad{i}'
                    if rule_dict.get(key):
                        bad_examples.append(rule_dict[key])
                
                # Паттерны поиска
                patterns_search = []
                patterns_ignore = []
                
                regex_data = rule_dict.get('regex_patterns', {})
                for_search = regex_data.get('for_search', [])
                for ignore in regex_data.get('for_ignore', []):
                    patterns_ignore.append(ignore)
                
                for pattern_obj in for_search:
                    patterns_search.append({
                        'pattern': pattern_obj.get('pattern', ''),
                        'description': pattern_obj.get('description', ''),
                        'flags': pattern_obj.get('flags', '')
                    })
                
                self.rules[code] = RubricatorRule(
                    code=rule_dict.get('code', code),
                    short_description=rule_dict.get('short_description', ''),
                    documentation_text=rule_dict.get('documentation_text', ''),
                    plplus_materials_note=rule_dict.get('plplus_materials_note', ''),
                    search_prompt=rule_dict.get('search_prompt', ''),
                    regex_patterns_search=patterns_search,
                    regex_patterns_ignore=patterns_ignore,
                    code_example_bad=bad_examples,
                    code_example_good=rule_dict.get('code_example_good', ''),
                    fix_instruction=rule_dict.get('fix_instruction', ''),
                    priority=rule_dict.get('priority', 'medium'),
                    category=rule_dict.get('category', 'Unknown'),
                    subcategory=rule_dict.get('subcategory', 'OTHER')
                )
            
            print(f"[OK] Загружено правил v3.0.0: {len(self.rules)}")
        
        except Exception as e:
            print(f"[!] Ошибка загрузки 4.RUBRICATOR_PROMPTS.json: {e}")
    
    def get_rule_by_code(self, code: str) -> Optional[RubricatorRule]:
        """Получить правило по коду"""
        return self.rules.get(code)
    
    def get_enabled_rules(self) -> List[RubricatorRule]:
        """Получить все активные правила (все в v3.0.0 активны)"""
        return list(self.rules.values())
    
    def get_rules_by_category(self, category: str) -> List[RubricatorRule]:
        """Получить правила по категории"""
        return [r for r in self.rules.values() if r.category.upper() == category.upper()]
    
    def get_rules_by_subcategory(self, subcategory: str) -> List[RubricatorRule]:
        """Получить правила по подкатегории"""
        return [r for r in self.rules.values() if r.subcategory.upper() == subcategory.upper()]
    
    def get_rules_by_priority(self, priority: str) -> List[RubricatorRule]:
        """Получить правила по приоритету"""
        return [r for r in self.rules.values() if r.priority.lower() == priority.lower()]
    
    def get_all_categories(self) -> List[str]:
        """Получить список всех категорий"""
        return sorted(set(r.category for r in self.rules.values()))
    
    def get_all_subcategories(self) -> List[str]:
        """Получить список всех подкатегорий"""
        return sorted(set(r.subcategory for r in self.rules.values()))
    
    def compile_search_regex(self, rule: RubricatorRule) -> Optional[re.Pattern]:
        """Скомпилировать регулярное выражение для поиска"""
        if not rule.regex_patterns_search:
            return None
        
        # Собираем все паттерны в один
        patterns = []
        for p in rule.regex_patterns_search:
            pattern = p.get('pattern', '')
            flags = p.get('flags', '')
            flag_value = 0
            if 'i' in flags.lower():
                flag_value |= re.IGNORECASE
            if pattern:
                patterns.append(f"(?:{pattern})")
        
        if not patterns:
            return None
        
        combined_pattern = '|'.join(patterns)
        
        try:
            return re.compile(combined_pattern, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            print(f"[!] Ошибка компиляции паттерна для {rule.code}: {e}")
            return None
    
    def compile_ignore_regex(self, rule: RubricatorRule) -> Optional[re.Pattern]:
        """Скомпилировать регулярное выражение для игнорирования"""
        if not rule.regex_patterns_ignore:
            return None
        
        patterns = []
        for p in rule.regex_patterns_ignore:
            pattern = p.get('pattern', '')
            flags = p.get('flags', '')
            flag_value = 0
            if 'i' in flags.lower():
                flag_value |= re.IGNORECASE
            if pattern:
                patterns.append(f"(?:{pattern})")
        
        if not patterns:
            return None
        
        combined_pattern = '|'.join(patterns)
        
        try:
            return re.compile(combined_pattern, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            print(f"[!] Ошибка компиляции паттерна ignore для {rule.code}: {e}")
            return None
    
    def should_ignore_line(self, line: str, rule: RubricatorRule) -> bool:
        """Проверить, следует ли игнорировать строку для данного правила"""
        ignore_regex = self.compile_ignore_regex(rule)
        if not ignore_regex:
            return False
        
        return bool(ignore_regex.search(line))
    
    def find_issues_in_code(self, code: str, rule: RubricatorRule) -> List[Dict]:
        """Найти проблемы в коде по правилам"""
        issues = []
        
        search_regex = self.compile_search_regex(rule)
        if not search_regex:
            return issues
        
        for match in search_regex.finditer(code):
            line_start = code.rfind('\n', 0, match.start()) + 1
            line_end = code.find('\n', match.start())
            if line_end == -1:
                line_end = len(code)
            
            line = code[line_start:line_end]
            
            # Проверяем, не следует ли игнорировать строку
            if self.should_ignore_line(line, rule):
                continue
            
            issues.append({
                'rule_code': rule.code,
                'start': match.start(),
                'end': match.end(),
                'match': match.group(),
                'line': line,
                'line_number': code[:match.start()].count('\n') + 1,
                'description': rule.short_description,
                'fix_instruction': rule.fix_instruction
            })
        
        return issues
    
    def print_to_log(self, log_func=None) -> str:
        """Вывод рубрикатора в журнал"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"РУБРИКАТОР v{self.metadata.get('version', 'unknown')}")
        lines.append(f"На основе: {self.metadata.get('based_on', 'Не указано')}")
        lines.append(f"Обновлено: {self.metadata.get('last_updated', 'Не указано')}")
        lines.append("=" * 80)
        
        # Категории
        categories = self.get_all_categories()
        lines.append(f"\nКАТЕГОРИИ ({len(categories)}):")
        lines.append("-" * 80)
        for cat in categories:
            rules_in_cat = len(self.get_rules_by_category(cat))
            lines.append(f"  {cat:<15} - {rules_in_cat} правил")
        
        # Правила
        lines.append(f"\nПРАВИЛА ({len(self.rules)}):")
        lines.append("-" * 80)
        lines.append(f"{'Код':<40} {'Приоритет':<10} {'Категория':<15} {'Описание'}")
        lines.append("-" * 80)
        
        for rule in sorted(self.rules.values(), key=lambda r: r.code):
            code_short = rule.code[:38] + '..' if len(rule.code) > 40 else rule.code
            cat_sub = f"{rule.category}.{rule.subcategory}" if rule.subcategory != 'OTHER' else rule.category
            cat_sub_short = cat_sub[:13] + '..' if len(cat_sub) > 15 else cat_sub
            desc_short = rule.short_description[:35] + '..' if len(rule.short_description) > 37 else rule.short_description
            lines.append(f"{code_short:<40} {rule.priority:<10} {cat_sub_short:<15} {desc_short}")
        
        # Статистика по приоритетам
        lines.append("\n" + "-" * 80)
        lines.append("СТАТИСТИКА ПО ПРИОРИТЕТАМ:")
        for priority in ['high', 'medium', 'low']:
            count = len(self.get_rules_by_priority(priority))
            lines.append(f"  {priority.upper():<10} - {count} правил")
        
        lines.append("=" * 80)
        
        result = '\n'.join(lines)
        
        if log_func:
            for line in lines:
                log_func(line)
        
        return result


def main():
    """Тестирование загрузчика"""
    loader = MarkdownRubricatorLoaderV3()
    
    print("\n=== Загрузчик рубрикатора v3.0.0 ===\n")
    
    def print_log(msg):
        print(msg)
    
    loader.print_to_log(print_log)
    
    # Тест поиска
    print("\n=== Тест поиска проблем ===\n")
    test_code = """
    select * from t1, t2 where t1.id = t2.id(+)
    where rownum = 1
    select decode(status, 1, 'A', 2, 'B') from t
    """
    
    rule = loader.get_rule_by_code('v50.SQL.OUTERJOIN.п.1.1')
    if rule:
        issues = loader.find_issues_in_code(test_code, rule)
        print(f"Найдено проблем для {rule.code}: {len(issues)}")
        for issue in issues:
            print(f"  - {issue['match']} (строка {issue['line_number']})")


if __name__ == '__main__':
    main()
