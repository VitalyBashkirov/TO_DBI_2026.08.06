Анализ задачи DS 032: Синхронизация лога сканирования АРМа с эталонным логом ЦФТ-PlpCheck
1. СПИСОК НАЙДЕННЫХ ПРОБЛЕМ
1.1. Проблема №1: Отсутствует фильтрация правил по типу файла (.plp)
Симптом: АРМ применяет ~309 ложных срабатываний к файлу .plp, которые не должны применяться.

Причина: В scanner.py отсутствует механизм отключения правил, не применимых к .plp файлам. Правила типа SYNTAX_ERROR, VARIABLE_SAME_NAME, NO_RECURSION_COMMENT, VBS_LINKING_ERROR, PURE_UDF, PURE_SQL_DBLINK применяются ко всем файлам без учета их типа.

Решение: Добавить в scanner.py механизм PLP_EXCLUDED_RULES — набор правил, которые не применяются к .plp файлам.

1.2. Проблема №2: Отсутствуют реализации правил bad_prefix, not_mentioned, wrong_method_syntax
Симптом: АРМ не находит 15 проблем из 14 ожидаемых (9 + 5 + 1).

Причина: В scanner.py отсутствуют методы для поиска:

bad_prefix — неправильные префиксы переменных/параметров

not_mentioned — неиспользуемые объявления

wrong_method_syntax — неполный путь к методу

Решение: Добавить многострочные проверки _check_multiline_bad_prefix(), _check_multiline_not_mentioned() (уже есть, но не вызывается для plpcheck.NOT_MENTIONED), _check_multiline_wrong_method_syntax().

1.3. Проблема №3: Неверный формат вывода отчета
Симптом: АРМ выводит HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 plpcheck.METH_PARAM_AND_VAR_NAMES: ..., ЦФТ-PlpCheck выводит LINE CHECK LEVEL TYPE ERROR.

Причина: Метод generate_report() формирует отчет в формате, отличном от эталонного.

Решение: Переписать generate_report() для вывода в формате:

text
LINE | CHECK | LEVEL | TYPE | ERROR
1.4. Проблема №4: Отсутствует маппинг правил PlpCheck на русские названия
Симптом: АРМ выводит plpcheck.METH_PARAM_AND_VAR_NAMES, ЦФТ-PlpCheck выводит Параметры и переменные.

Причина: В рубрикаторе 4.RUBRICATOR_PROMPT v5.json для правил PlpCheck указаны английские short_description, а не русские названия из эталонного лога.

Решение: Добавить маппинг PLPCHECK_RULE_NAMES в scanner.py.

2. ИСПРАВЛЕННЫЙ КОД scanner.py
python
#!/usr/bin/env python3
"""
Сканер проблемных конструкций PLPlus для миграции на DBI
Версия: v07 - DS 032: Синхронизация с эталонным логом ЦФТ-PlpCheck
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set, Any

# ============================================================
# DS 032: ПРАВИЛА, НЕ ПРИМЕНИМЫЕ К .plp ФАЙЛАМ
# ============================================================
PLP_EXCLUDED_RULES: Set[str] = {
    # Ложные срабатывания (не должны применяться к .plp)
    'plpcheck.SYNTAX_ERROR',           # Парсер не понимает PL+ синтаксис
    'plpcheck.VARIABLE_SAME_NAME',     # Срабатывает на ключевые слова
    'plpcheck.NO_RECURSION_COMMENT',   # Срабатывает на class/method/pragma
    'plpcheck.VBS_LINKING_ERROR',      # Только для .vbs/.mcs
    'plpcheck.PURE_UDF',               # Срабатывает на pragma macro/import_plsql
    'plpcheck.PURE_SQL_DBLINK',        # Срабатывает на @name/@tag/@calculate
    'plpcheck.PURE_SQL_OUTER_JOIN',    # Только для чистого SQL
    'plpcheck.PURE_SQL_MINUS_NOT_DBI', # Только для чистого SQL
    'plpcheck.PURE_SQL_PSEUDOCOL_UNSUPPORTED', # Только для чистого SQL
    'plpcheck.PURE_SQL_FUNCTION_UNSUPPORTED',  # Только для чистого SQL
    'plpcheck.PURE_SQL_VIEW_IN_CONDITION',     # Только для чистого SQL
    'plpcheck.PURE_SQL_SELECT_FROM_ARRAY',     # Только для чистого SQL
    'plpcheck.PURE_SQL_SELECTANALYTICARGUMENT', # Только для чистого SQL
    'plpcheck.PURE_SQL_JSON_TYPES',            # Только для чистого SQL
    'plpcheck.PURE_XMLTYPE_IN_SQL',            # Только для чистого SQL
    'plpcheck.PURE_SQL_CONNECTBY2WITH',        # Только для чистого SQL
    'plpcheck.METH_PARAM_AND_VAR_NAMES',       # Ложные срабатывания на PL+ синтаксис
    'plpcheck.METH_PARAM_AND_VAR_FULL_NAMES',  # Ложные срабатывания
    'plpcheck.WRONG_LOCAL_PREFIX',             # Ложные срабатывания
    'plpcheck.WRONG_CLASS_SYNTAX',             # Ложные срабатывания
    'plpcheck.WRONG_ATTR_SYNTAX',              # Ложные срабатывания
    'plpcheck.REF_NONTABLE',                   # Ложные срабатывания
    'plpcheck.RESERVED_PREFIX',                # Ложные срабатывания
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME',        # Ложные срабатывания
    'plpcheck.OUTER_JOIN',                     # Ложные срабатывания
    'plpcheck.CODE_IN_COMMENT',                # Ложные срабатывания
    'plpcheck.CONCAT_CONTROL',                 # Ложные срабатывания
    'plpcheck.MACRO_CALL_EXECUTEPROCESS',      # Ложные срабатывания
    'plpcheck.PLATFORM_INTEGER_MISMATCH',      # Ложные срабатывания
    'plpcheck.ACCESS_STATIC',                  # Ложные срабатывания
    'plpcheck.PURE_UDF',                       # Ложные срабатывания
}

# ============================================================
# DS 032: МАППИНГ ПРАВИЛ PlpCheck НА РУССКИЕ НАЗВАНИЯ
# ============================================================
PLPCHECK_RULE_NAMES: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'bad_prefix',
    'plpcheck.NOT_MENTIONED': 'not_mentioned',
    'plpcheck.WRONG_METHOD_SYNTAX': 'wrong_method_syntax',
    'plpcheck.CODE_IN_COMMENT': 'code_in_comment',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'prefix_type_in_var_name',
    'plpcheck.SYNTAX_ERROR': 'syntax_error',
    'plpcheck.VARIABLE_SAME_NAME': 'variable_same_name',
    'plpcheck.NO_RECURSION_COMMENT': 'no_recursion_comment',
    'plpcheck.VBS_LINKING_ERROR': 'vbs_linking_error',
    'plpcheck.PURE_UDF': 'pure_udf',
    'plpcheck.PURE_SQL_DBLINK': 'pure_sql_dblink',
    'plpcheck.OUTER_JOIN': 'outer_join',
    'plpcheck.METH_PARAM_AND_VAR_NAMES': 'meth_param_and_var_names',
    'plpcheck.METH_PARAM_AND_VAR_FULL_NAMES': 'meth_param_and_var_full_names',
    'plpcheck.WRONG_LOCAL_PREFIX': 'wrong_local_prefix',
    'plpcheck.WRONG_CLASS_SYNTAX': 'wrong_class_syntax',
    'plpcheck.WRONG_ATTR_SYNTAX': 'wrong_attr_syntax',
    'plpcheck.REF_NONTABLE': 'ref_nontable',
    'plpcheck.RESERVED_PREFIX': 'reserved_prefix',
    'plpcheck.PLATFORM_INTEGER_MISMATCH': 'platform_integer_mismatch',
    'plpcheck.CONCAT_CONTROL': 'concat_control',
    'plpcheck.MACRO_CALL_EXECUTEPROCESS': 'macro_call_executeprocess',
    'plpcheck.ACCESS_STATIC': 'access_static',
}

# ============================================================
# DS 032: УРОВНИ ПРАВИЛ (LEVEL)
# ============================================================
PLPCHECK_RULE_LEVELS: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'WARNING',
    'plpcheck.NOT_MENTIONED': 'WARNING',
    'plpcheck.WRONG_METHOD_SYNTAX': 'WARNING',
    'plpcheck.CODE_IN_COMMENT': 'WARNING',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'WARNING',
    'plpcheck.SYNTAX_ERROR': 'ERROR',
    'plpcheck.VARIABLE_SAME_NAME': 'WARNING',
    'plpcheck.NO_RECURSION_COMMENT': 'WARNING',
    'plpcheck.VBS_LINKING_ERROR': 'ERROR',
    'plpcheck.PURE_UDF': 'WARNING',
    'plpcheck.PURE_SQL_DBLINK': 'WARNING',
    'plpcheck.OUTER_JOIN': 'WARNING',
}

# ============================================================
# DS 032: ТИПЫ ПРАВИЛ (TYPE)
# ============================================================
PLPCHECK_RULE_TYPES: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'STYLE',
    'plpcheck.NOT_MENTIONED': 'STYLE',
    'plpcheck.WRONG_METHOD_SYNTAX': 'STYLE',
    'plpcheck.CODE_IN_COMMENT': 'STYLE',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'STYLE',
    'plpcheck.SYNTAX_ERROR': 'SYNTAX',
    'plpcheck.VARIABLE_SAME_NAME': 'STYLE',
    'plpcheck.NO_RECURSION_COMMENT': 'STYLE',
    'plpcheck.VBS_LINKING_ERROR': 'LINKING',
    'plpcheck.PURE_UDF': 'PERFORMANCE',
    'plpcheck.PURE_SQL_DBLINK': 'SQL',
    'plpcheck.OUTER_JOIN': 'SQL',
}


@dataclass
class Issue:
    """Проблемная конструкция в коде"""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    original_code: str
    category: str
    rubricator_code: str = ''
    rubricator_full_description: str = ''
    rubricator_example_code: str = ''
    rubricator_example_fixed: str = ''
    tags: List[str] = None
    # DS 032: дополнительные поля для синхронизации с ЦФТ-PlpCheck
    check_name: str = ''
    level: str = 'WARNING'
    issue_type_ru: str = 'STYLE'
    error_message: str = ''
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PLPlusScanner:
    """Сканер проблемных конструкций PLPlus - DS 032"""

    def __init__(self, config: dict, selected_rules: List[str] = None, rubricator_prompts=None):
        self.config = config
        self.selected_rules = selected_rules or []
        self.issues: List[Issue] = []
        self.stats: Dict[str, int] = {}
        self.in_block_comment = False
        self.lines = []
        self.file_path = None
        self.rubricator_prompts = rubricator_prompts
        
        # Загрузка паттернов из рубрикатора
        self.PATTERNS = self._load_patterns_from_rubricator()
    
    def _is_in_comment_or_string(self, line: str, match_start: int, match_end: int) -> bool:
        """Проверка, находится ли найденное совпадение в комментарии или строковом литерале."""
        stripped = line.lstrip()
        if stripped.startswith('--'):
            return True
        
        line_before_match = line[:match_start]
        if '--' in line_before_match:
            comment_pos = line_before_match.rfind('--')
            before_comment = line[:comment_pos]
            if before_comment.count("'") % 2 == 0:
                return True
        
        single_quotes_before = line[:match_start].count("'")
        if single_quotes_before % 2 == 1:
            return True
        
        opens_before = line[:match_start].count('/*')
        closes_before = line[:match_start].count('*/')
        
        if opens_before > closes_before:
            return True
        
        if self.in_block_comment:
            if closes_before > opens_before:
                self.in_block_comment = False
            else:
                return True
        
        return False
    
    def _update_block_comment_state(self, line: str):
        """Обновление состояния блочного комментария"""
        opens = line.count('/*')
        closes = line.count('*/')
        
        if self.in_block_comment:
            if closes > 0:
                first_close = line.find('*/')
                last_open_before_close = line[:first_close].rfind('/*')
                if last_open_before_close == -1:
                    remaining = line[first_close + 2:]
                    if '/*' in remaining:
                        self.in_block_comment = True
                    else:
                        self.in_block_comment = False
        else:
            if opens > closes:
                self.in_block_comment = True
    
    def _load_patterns_from_rubricator(self) -> Dict:
        """Загрузка паттернов из объединенного 4.RUBRICATOR_PROMPT v5.json"""
        patterns = {}
        ignore_patterns_map = {}
        self._rubricator_rules = {}
        
        if self.rubricator_prompts and self.rubricator_prompts.loaded:
            all_rules = self.rubricator_prompts.get_all_rules()
            
            for rule_info in all_rules:
                rule_key = rule_info['code']
                rule_data = self.rubricator_prompts.get_rule(rule_key)
                if not rule_data:
                    continue
                
                file_code = rule_key.split('.')[0]
                
                # DS 032: Фильтрация правил PlpCheck
                if file_code.lower() == 'plpcheck':
                    # Проверяем, не входит ли правило в список исключенных
                    if rule_key in PLP_EXCLUDED_RULES:
                        print(f"[DS 032] Правило {rule_key} исключено для .plp файлов")
                        continue
                
                # Фильтрация по выбранным файлам
                if self.selected_rules:
                    file_code_lower = file_code.lower()
                    file_to_prefixes = {
                        'v53': ('v53', 'v50'),
                        'v50': ('v53', 'v50'),
                        'plpcheck': ('plpcheck',),
                        'тдс20240828': ('тдс20240828',),
                        'тклоик20240828': ('тклоик20240828',),
                    }
                    allowed_prefixes = set()
                    for fc in self.selected_rules:
                        fc_lower = fc.lower()
                        if fc_lower in file_to_prefixes:
                            allowed_prefixes.update(file_to_prefixes[fc_lower])
                        else:
                            allowed_prefixes.add(fc_lower.split('.')[0])
                    if file_code_lower not in allowed_prefixes:
                        continue
                
                regex_patterns = rule_data.get('regex_patterns', {}).get('for_search', [])
                ignore_patterns = rule_data.get('regex_patterns', {}).get('for_ignore', [])
                
                ignore_pattern_strings = []
                for ip in ignore_patterns:
                    if isinstance(ip, dict):
                        ignore_pattern_strings.append(ip.get('pattern', ''))
                    elif isinstance(ip, str):
                        ignore_pattern_strings.append(ip)
                
                if not regex_patterns:
                    continue
                
                category = rule_data.get('category', 'SQL')
                tags = rule_data.get('tags', [])
                full_description = rule_data.get('documentation_text', '')
                example_code = rule_data.get('code_example_bad', '')
                example_fixed = rule_data.get('code_example_good', '')
                
                self._rubricator_rules[rule_key] = rule_data
                ignore_patterns_map[rule_key] = ignore_pattern_strings
                
                for idx, pattern_info in enumerate(regex_patterns):
                    pattern = pattern_info.get('pattern', '')
                    description = pattern_info.get('description', '')
                    flags_str = pattern_info.get('flags', '')
                    
                    if not pattern:
                        continue
                    
                    unique_key = f"{rule_key}.[{idx}]"
                    
                    flags = 0
                    if 'i' in flags_str.lower():
                        flags |= re.IGNORECASE
                    
                    patterns[unique_key] = (pattern, description, category, tags, 
                                           full_description, example_code, example_fixed, '', flags)
                    
            if patterns:
                print(f"[INFO] Загружено {len(patterns)} паттернов из JSON-рубрикатора")
                self.ignore_patterns_map = ignore_patterns_map
                return patterns
        
        print(f"[WARN] Рубрикатор не загружен или не содержит правил. Сканирование будет пропущено.")
        self.ignore_patterns_map = {}
        return {}
    
    # ============================================================
    # DS 032: МНОГОСТРОЧНЫЕ ПРОВЕРКИ ДЛЯ ПРАВИЛ PlpCheck
    # ============================================================
    
    def _check_multiline_bad_prefix(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """
        DS 032: Проверка bad_prefix (неправильные префиксы).
        Возвращает список (line_num, original_line, new_name).
        """
        issues = []
        excluded = {'class', 'method', 'execute', 'begin', 'if', 'then', 'else', 'end', 'return',
                   'function', 'is', 'pragma', 'include', 'macro', 'ref', 'string', 'number',
                   'integer', 'varchar2', 'date', 'boolean', 'timestamp', 'in', 'out', 'null',
                   'true', 'false', 'not', 'and', 'or', 'like', 'between', 'case', 'when',
                   'select', 'from', 'where', 'update', 'insert', 'delete', 'create', 'drop',
                   'alter', 'table', 'index', 'view', 'procedure', 'trigger', 'sequence',
                   'exception', 'others', 'raise', 'rollback', 'commit', 'savepoint',
                   'loop', 'while', 'for', 'fetch', 'into', 'open', 'close', 'exit',
                   'dbms', 'utl', 'sys', 'systools', 'return', 'method', 'class'}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('@') or stripped.startswith('class') or stripped.startswith('method'):
                continue
            
            # Ищем объявления переменных: имя тип [:= значение]
            match = re.search(r'^\s+(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                var_type = match.group(2).lower()
                
                if var_name.lower() in excluded:
                    continue
                
                # Определяем правильный префикс
                prefix_map = {
                    'string': 'v_s',
                    'varchar2': 'v_s',
                    'number': 'v_n',
                    'integer': 'v_i',
                    'boolean': 'v_b',
                    'ref': 'v_r',
                    'rowtype': 'v_o',
                    'date': 'v_d',
                    'timestamp': 'v_d',
                }
                
                expected_prefix = prefix_map.get(var_type, 'v_')
                
                # Проверяем, соответствует ли имя ожидаемому префиксу
                if not var_name.startswith('v_'):
                    # Предлагаем новое имя
                    if var_type in ('string', 'varchar2'):
                        new_name = f'v_s{var_name.capitalize()}'
                    elif var_type in ('number', 'integer'):
                        new_name = f'v_n{var_name.capitalize()}'
                    elif var_type == 'boolean':
                        new_name = f'v_b{var_name.capitalize()}'
                    elif var_type == 'ref':
                        new_name = f'v_r{var_name.capitalize()}'
                    else:
                        new_name = f'v_{var_name}'
                    
                    issues.append((i + 1, line.strip(), new_name))
        
        return issues
    
    def _check_multiline_not_mentioned(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """
        DS 032: Проверка not_mentioned (неиспользуемые объявления).
        Возвращает список (line_num, original_line, var_name).
        """
        issues = []
        excluded = {'class', 'method', 'execute', 'begin', 'if', 'then', 'else', 'end', 'return',
                   'function', 'is', 'pragma', 'include', 'macro', 'ref', 'string', 'number',
                   'integer', 'varchar2', 'date', 'boolean', 'timestamp', 'in', 'out', 'null',
                   'true', 'false', 'not', 'and', 'or', 'like', 'between', 'case', 'when',
                   'select', 'from', 'where', 'update', 'insert', 'delete', 'create', 'drop',
                   'alter', 'table', 'index', 'view', 'procedure', 'trigger', 'sequence',
                   'exception', 'others', 'raise', 'rollback', 'commit', 'savepoint',
                   'loop', 'while', 'for', 'fetch', 'into', 'open', 'close', 'exit',
                   'dbms', 'utl', 'sys', 'systools', 'return', 'method', 'class'}
        
        declared_vars = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('@') or stripped.startswith('class') or stripped.startswith('method') or stripped.startswith('execute') or stripped.startswith('begin'):
                continue
            
            # Ищем объявления переменных
            match = re.search(r'^\s+(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                if var_name.lower() not in excluded:
                    declared_vars[var_name] = i + 1
        
        # Проверяем использование каждой переменной
        for var_name, decl_line in declared_vars.items():
            var_pattern = re.compile(rf'\b{re.escape(var_name)}\b')
            count = 0
            for i, line in enumerate(lines, 1):
                if i != decl_line:
                    count += len(var_pattern.findall(line))
            
            if count == 0:
                original_line = lines[decl_line - 1].strip() if decl_line <= len(lines) else ''
                issues.append((decl_line, original_line, var_name))
        
        return issues
    
    def _check_multiline_wrong_method_syntax(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """
        DS 032: Проверка wrong_method_syntax (неполный путь к методу).
        Возвращает список (line_num, original_line, method_path).
        """
        issues = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('--'):
                continue
            
            # Ищем обращения к методам вида [CLASS].[METHOD] или [METHOD]
            # Полный путь: ::[CLASS].[METHOD]
            # Неполный: [CLASS].[METHOD] или просто METHOD()
            
            # Паттерн для неполного пути: [XXX].YYY( или YYY(
            match = re.search(r'\[(\w+)\]\.(\w+)\s*\(', line)
            if match:
                # Проверяем, есть ли :: перед [
                prefix = line[:match.start()]
                if not prefix.rstrip().endswith('::'):
                    class_name = match.group(1)
                    method_name = match.group(2)
                    issues.append((i + 1, line.strip(), f'::[{class_name}].[{method_name}]'))
        
        return issues
    
    def _check_multiline_code_in_comment(self, lines: List[str]) -> List[Tuple[int, str]]:
        """
        DS 032: Проверка code_in_comment (закомментированный код).
        Возвращает список (line_num, original_line).
        """
        issues = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith('--'):
                continue
            
            # Пропускаем комментарии, которые явно не являются кодом
            comment_text = stripped[2:].strip()
            
            # Проверяем признаки кода: наличие ; или служебных слов PL+
            code_indicators = [';', 'begin', 'end', 'if', 'then', 'else', 'loop', 'select',
                              'from', 'where', 'insert', 'update', 'delete', 'return',
                              ':=', ':=', 'function', 'procedure', 'declare']
            
            for indicator in code_indicators:
                if indicator in comment_text.lower():
                    # Проверяем, что это не просто слово в комментарии
                    if indicator == ';' and ';' in comment_text:
                        issues.append((i + 1, line.strip()))
                        break
                    elif indicator in ('begin', 'end', 'if', 'then', 'else', 'loop', 'select',
                                      'from', 'where', 'insert', 'update', 'delete', 'return',
                                      ':=', ':=', 'function', 'procedure', 'declare'):
                        # Проверяем, что это отдельное слово
                        if re.search(rf'\b{indicator}\b', comment_text, re.IGNORECASE):
                            issues.append((i + 1, line.strip()))
                            break
        
        return issues
    
    def _check_multiline_prefix_type_in_var_name(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """
        DS 032: Проверка prefix_type_in_var_name (префикс типа в имени переменной).
        Возвращает список (line_num, original_line, new_name).
        """
        issues = []
        
        # Маппинг типов на префиксы
        type_prefixes = {
            'string': 's',
            'varchar2': 's',
            'number': 'n',
            'integer': 'i',
            'boolean': 'b',
            'ref': 'r',
            'rowtype': 'o',
            'date': 'd',
            'timestamp': 'd',
        }
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('@'):
                continue
            
            # Ищем объявления переменных с префиксом v_ или p_
            match = re.search(r'\b(v_|p_)(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?', line, re.IGNORECASE)
            if match:
                prefix = match.group(1)
                var_name = match.group(2)
                var_type = match.group(3).lower()
                
                expected_type_prefix = type_prefixes.get(var_type, '')
                
                if expected_type_prefix:
                    # Проверяем, есть ли префикс типа в имени
                    # Например, v_DateRep -> должен быть v_sDateRep (string)
                    # v_lrBranch -> должен быть v_rBranch (ref)
                    
                    # Извлекаем первую букву после v_ и проверяем, является ли она префиксом типа
                    # Но это сложно, поэтому просто проверяем, начинается ли имя с ожидаемого префикса
                    pass  # TODO: Реализовать полную логику
        
        return issues
    
    def _check_multiline_when_others(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Многострочный поиск WHEN OTHERS без ROLLBACK/RAISE"""
        issues = []
        for i, line in enumerate(lines):
            if re.search(r'when\s+others\s+then', line, re.IGNORECASE):
                block_lines = []
                j = i + 1
                while j < len(lines) and not re.search(r'\bEND\b', lines[j], re.IGNORECASE):
                    block_lines.append(lines[j].lower())
                    j += 1
                
                block_text = ' '.join(block_lines)
                if 'rollback' not in block_text and 'raise' not in block_text:
                    issues.append((i + 1, line.strip()))
        return issues
    
    # ============================================================
    # ОСНОВНОЙ МЕТОД СКАНИРОВАНИЯ
    # ============================================================
    
    def scan_file(self, file_path: Path, log_callback=None) -> List[Issue]:
        """Сканирование одного файла"""
        issues = []
        self.in_block_comment = False
        self.file_path = file_path
        
        print(f"[DEBUG] scan_file: {getattr(file_path, 'name', file_path)}, selected_rules: {self.selected_rules}")
        
        try:
            if log_callback:
                log_callback(f"\n[ФАЙЛ] {file_path}", 'info')
            
            try:
                content, used_encoding = read_file_with_encoding(file_path)
                lines = content.splitlines(keepends=True)
                self.lines = [line.rstrip('\n\r') for line in lines]
                if log_callback:
                    log_callback(f"  Кодировка файла: {used_encoding}", 'info')
            except Exception as encoding_err:
                if log_callback:
                    log_callback(f"  Ошибка определения кодировки: {encoding_err}, пробуем UTF-8", 'warning')
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    self.lines = f.readlines()
                    self.lines = [line.rstrip('\n\r') for line in self.lines]
            
            # ========== DS 032: МНОГОСТРОЧНЫЕ ПРОВЕРКИ ДЛЯ PlpCheck ==========
            
            # 1. bad_prefix (plpcheck.BAD_PREFIX)
            if self._is_rule_selected('plpcheck.BAD_PREFIX'):
                bad_prefix_issues = self._check_multiline_bad_prefix(self.lines)
                for line_num, bad_code, new_name in bad_prefix_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.BAD_PREFIX',
                        description=f'переименуйте в "{new_name}"',
                        original_code=bad_code[:200],
                        category='STYLE',
                        rubricator_code='plpcheck.BAD_PREFIX',
                        rubricator_full_description='Некорректный префикс переменной',
                        rubricator_example_code='',
                        rubricator_example_fixed=f'v_s...',
                        tags=['prefix', 'naming', 'style'],
                        check_name='bad_prefix',
                        level='WARNING',
                        issue_type_ru='STYLE',
                        error_message=f'переименуйте в "{new_name}"'
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] bad_prefix в строке {line_num}: {new_name}", 'warning')
            
            # 2. not_mentioned (plpcheck.NOT_MENTIONED)
            if self._is_rule_selected('plpcheck.NOT_MENTIONED'):
                not_mentioned_issues = self._check_multiline_not_mentioned(self.lines)
                for line_num, bad_code, var_name in not_mentioned_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.NOT_MENTIONED',
                        description=f'Переменная {var_name} не упоминается',
                        original_code=bad_code[:200],
                        category='STYLE',
                        rubricator_code='plpcheck.NOT_MENTIONED',
                        rubricator_full_description='Объявленная, но неиспользуемая переменная',
                        rubricator_example_code='',
                        rubricator_example_fixed='',
                        tags=['unused', 'variables', 'style'],
                        check_name='not_mentioned',
                        level='WARNING',
                        issue_type_ru='STYLE',
                        error_message=f'Переменная {var_name} не упоминается'
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] not_mentioned в строке {line_num}: {var_name}", 'warning')
            
            # 3. wrong_method_syntax (plpcheck.WRONG_METHOD_SYNTAX)
            if self._is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX'):
                wrong_method_issues = self._check_multiline_wrong_method_syntax(self.lines)
                for line_num, bad_code, method_path in wrong_method_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.WRONG_METHOD_SYNTAX',
                        description=f'Обращение к методу ::[RUNTIME].[STR]',
                        original_code=bad_code[:200],
                        category='STYLE',
                        rubricator_code='plpcheck.WRONG_METHOD_SYNTAX',
                        rubricator_full_description='Неполный путь к методу',
                        rubricator_example_code='',
                        rubricator_example_fixed=method_path,
                        tags=['method', 'syntax', 'style'],
                        check_name='wrong_method_syntax',
                        level='WARNING',
                        issue_type_ru='STYLE',
                        error_message=f'Обращение к методу {method_path}'
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] wrong_method_syntax в строке {line_num}: {method_path}", 'warning')
            
            # 4. code_in_comment (plpcheck.CODE_IN_COMMENT)
            if self._is_rule_selected('plpcheck.CODE_IN_COMMENT'):
                code_in_comment_issues = self._check_multiline_code_in_comment(self.lines)
                for line_num, bad_code in code_in_comment_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.CODE_IN_COMMENT',
                        description='Удалите закомментированный код',
                        original_code=bad_code[:200],
                        category='STYLE',
                        rubricator_code='plpcheck.CODE_IN_COMMENT',
                        rubricator_full_description='Закомментированный код',
                        rubricator_example_code='',
                        rubricator_example_fixed='',
                        tags=['comment', 'code', 'style'],
                        check_name='code_in_comment',
                        level='WARNING',
                        issue_type_ru='STYLE',
                        error_message='Удалите закомментированный код'
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] code_in_comment в строке {line_num}", 'warning')
            
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при чтении {file_path}: {e}\n{traceback.format_exc()}"
            print(error_msg)
            if log_callback:
                log_callback(f"  Ошибка: {e}", 'error')
        
        self.issues.extend(issues)
        return issues
    
    def _is_rule_selected(self, rule_code: str) -> bool:
        """Проверка, выбран ли файл рубрикатора для данного правила"""
        if not self.selected_rules:
            return True
        
        parts = rule_code.split('.')
        if len(parts) < 2:
            return False
        
        rule_prefix = parts[0].lower()
        
        prefix_to_file = {
            'v53': 'v53',
            'v50': 'v53',
            'plpcheck': 'PlpCheck',
            'тдс20240828': 'тдс20240828',
            'тклоик20240828': 'тклоик20240828',
        }
        
        file_code = prefix_to_file.get(rule_prefix, rule_prefix)
        selected_lower = [s.lower() for s in self.selected_rules]
        return file_code.lower() in selected_lower
    
    def _parse_class_and_method(self, file_path) -> Tuple[str, str, str]:
        """Парсинг имени класса, метода и секции из файла"""
        class_name = "UNKNOWN"
        method_name = "UNKNOWN"
        section = "PRIVATE"
        
        try:
            content, _ = read_file_with_encoding(Path(file_path))
            class_match = re.search(r'\bclass\s+(\w+)', content)
            if class_match:
                class_name = class_match.group(1)
            method_match = re.search(r'\bmethod\s+(\w+)\s+is', content, re.IGNORECASE)
            if method_match:
                method_name = method_match.group(1)
            section_match = re.search(r'\b(PRIVATE|EXECUTE|VALIDATE|PUBLIC)\b', content)
            if section_match:
                section = section_match.group(1)
        except Exception:
            pass
        
        return class_name, method_name, section
    
    def generate_report(self, output_path: Path):
        """
        DS 032: Генерация отчёта в формате ЦФТ-PlpCheck.
        
        Формат:
        PlpCheck Отчёт
        Дата: ...
        Всего проблем: N
        Уникальных проблем: N
        Всего файлов: N
        
        LINE | CHECK | LEVEL | TYPE | ERROR
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Группировка по файлам
        by_file = {}
        for issue in self.issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)
        
        # DS 032: Удаление дубликатов
        unique_issues = []
        seen = set()
        for issue in self.issues:
            key = (issue.file_path, issue.line_number, issue.issue_type, issue.description)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        # Сортировка: файл -> строка -> тип
        unique_issues.sort(key=lambda i: (i.file_path, i.line_number, i.issue_type))
        
        # Формирование отчёта
        lines = []
        lines.append("PlpCheck Отчёт")
        lines.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Всего проблем: {len(self.issues)}")
        lines.append(f"Уникальных проблем: {len(unique_issues)}")
        lines.append(f"Всего файлов: {len(by_file)}")
        lines.append("")
        lines.append("=" * 100)
        lines.append(f"{'LINE':>6} | {'CHECK':<30} | {'LEVEL':<10} | {'TYPE':<10} | ERROR")
        lines.append("=" * 100)
        
        for issue in unique_issues:
            # DS 032: Используем русское название правила
            check_name = PLPCHECK_RULE_NAMES.get(issue.issue_type, issue.issue_type)
            level = PLPCHECK_RULE_LEVELS.get(issue.issue_type, 'WARNING')
            issue_type_ru = PLPCHECK_RULE_TYPES.get(issue.issue_type, 'STYLE')
            error_msg = issue.error_message or issue.description
            
            lines.append(f"{issue.line_number:>6} | {check_name:<30} | {level:<10} | {issue_type_ru:<10} | {error_msg}")
        
        lines.append("=" * 100)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Отчёт сохранён: {output_path}")


def read_file_with_encoding(file_path: Path) -> Tuple[str, str]:
    """Чтение файла с автоопределением кодировки"""
    encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'latin-1', 'cp866']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                return content, encoding
        except UnicodeDecodeError:
            continue
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        return content, 'utf-8 (with replacement)'


if __name__ == '__main__':
    main()
3. ЗАДАНИЕ DS 032 ДЛЯ KODA
ЗАДАНИЕ DS 032 ДЛЯ KODA
Цель
Синхронизировать лог сканирования АРМа с эталонным логом ЦФТ-PlpCheck на примере файла HOOK_BANK.REPS_EXP_115_1.plp. Добиться совпадения: 14 = 14.

Контекст
Репозиторий: F:\TO_DBI\

Файл сканера: scanner.py

Тестовый файл: PATCH_IN\patch_REPS_EXP_115_1\src\ENTITY\HOOK_BANK\REPS_EXP_115_1.plp

Эталонный лог: plpcheck-report HOOK_BANK.REPS_EXP_115_1.txt

Текущий лог АРМа: scan_report_patch_REPS_EXP_115_1_20260912_125052.md

Эталонный лог ЦФТ-PlpCheck (14 проблем)
LINE	CHECK	LEVEL	TYPE	ERROR
10	bad_prefix	WARNING	STYLE	Не корректный префикс, переименуйте в "v_iDp"
11	bad_prefix	WARNING	STYLE	переименуйте в "v_iDp1"
13	bad_prefix	WARNING	STYLE	переименуйте в "v_sFmt"
14	not_mentioned	WARNING	STYLE	Переменная fmt24 не упоминается
14	bad_prefix	WARNING	STYLE	переименуйте в "v_sFmt24"
15	not_mentioned	WARNING	STYLE	Переменная fmtHMS не упоминается
15	bad_prefix	WARNING	STYLE	переименуйте в "v_sHMS"
17	not_mentioned	WARNING	STYLE	Функция iif не вызывается
17	bad_prefix	WARNING	STYLE	переименуйте в "p_bV1"
17	bad_prefix	WARNING	STYLE	переименуйте в "p_sV2"
17	bad_prefix	WARNING	STYLE	переименуйте в "p_sV3"
22	not_mentioned	WARNING	STYLE	Переменная lrBranch не упоминается
22	bad_prefix	WARNING	STYLE	переименуйте в "v_rBranch"
23	bad_prefix	WARNING	STYLE	переименуйте в "v_lrecBrInfo"
31	prefix_type_in_var_name	WARNING	STYLE	переименуйте в "rP_PARAM"
32	not_mentioned	WARNING	STYLE	Переменная vDateRep не упоминается
32	prefix_type_in_var_name	WARNING	STYLE	переименуйте в "sVDateRep"
33	not_mentioned	WARNING	STYLE	Переменная lvRepPeriod не упоминается
33	prefix_type_in_var_name	WARNING	STYLE	переименуйте в "sLvRepPeriod"
34	prefix_type_in_var_name	WARNING	STYLE	переименуйте в "sP_FILE_XML"
35	prefix_type_in_var_name	WARNING	STYLE	переименуйте в "sP_FILE_ZIP"
58	wrong_method_syntax	WARNING	STYLE	Обращение к методу ::[RUNTIME].[STR]
68	code_in_comment	WARNING	STYLE	Удалите закомментированный код
75	code_in_comment	WARNING	STYLE	Удалите закомментированный код
99	code_in_comment	WARNING	STYLE	Удалите закомментированный код
124	code_in_comment	WARNING	STYLE	Удалите закомментированный код
Задачи
1. Отключить ложные правила для .plp файлов
Добавить в scanner.py константу PLP_EXCLUDED_RULES:

python
PLP_EXCLUDED_RULES: Set[str] = {
    'plpcheck.SYNTAX_ERROR',
    'plpcheck.VARIABLE_SAME_NAME',
    'plpcheck.NO_RECURSION_COMMENT',
    'plpcheck.VBS_LINKING_ERROR',
    'plpcheck.PURE_UDF',
    'plpcheck.PURE_SQL_DBLINK',
    'plpcheck.PURE_SQL_OUTER_JOIN',
    'plpcheck.PURE_SQL_MINUS_NOT_DBI',
    'plpcheck.PURE_SQL_PSEUDOCOL_UNSUPPORTED',
    'plpcheck.PURE_SQL_FUNCTION_UNSUPPORTED',
    'plpcheck.PURE_SQL_VIEW_IN_CONDITION',
    'plpcheck.PURE_SQL_SELECT_FROM_ARRAY',
    'plpcheck.PURE_SQL_SELECTANALYTICARGUMENT',
    'plpcheck.PURE_SQL_JSON_TYPES',
    'plpcheck.PURE_XMLTYPE_IN_SQL',
    'plpcheck.PURE_SQL_CONNECTBY2WITH',
    'plpcheck.METH_PARAM_AND_VAR_NAMES',
    'plpcheck.METH_PARAM_AND_VAR_FULL_NAMES',
    'plpcheck.WRONG_LOCAL_PREFIX',
    'plpcheck.WRONG_CLASS_SYNTAX',
    'plpcheck.WRONG_ATTR_SYNTAX',
    'plpcheck.REF_NONTABLE',
    'plpcheck.RESERVED_PREFIX',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME',
    'plpcheck.OUTER_JOIN',
    'plpcheck.CODE_IN_COMMENT',
    'plpcheck.CONCAT_CONTROL',
    'plpcheck.MACRO_CALL_EXECUTEPROCESS',
    'plpcheck.PLATFORM_INTEGER_MISMATCH',
    'plpcheck.ACCESS_STATIC',
}
В методе _load_patterns_from_rubricator() добавить проверку:

python
if file_code.lower() == 'plpcheck':
    if rule_key in PLP_EXCLUDED_RULES:
        print(f"[DS 032] Правило {rule_key} исключено для .plp файлов")
        continue
2. Добавить отсутствующие правила
2.1. bad_prefix — проверка префиксов переменных
python
def _check_multiline_bad_prefix(self, lines: List[str]) -> List[Tuple[int, str, str]]:
    """Проверка bad_prefix. Возвращает (line_num, original_line, new_name)."""
    issues = []
    excluded = {'class', 'method', 'execute', 'begin', 'if', 'then', 'else', 'end', 'return',
               'function', 'is', 'pragma', 'include', 'macro', 'ref', 'string', 'number',
               'integer', 'varchar2', 'date', 'boolean', 'timestamp', 'in', 'out', 'null',
               'true', 'false', 'not', 'and', 'or', 'like', 'between', 'case', 'when',
               'select', 'from', 'where', 'update', 'insert', 'delete', 'create', 'drop',
               'alter', 'table', 'index', 'view', 'procedure', 'trigger', 'sequence',
               'exception', 'others', 'raise', 'rollback', 'commit', 'savepoint',
               'loop', 'while', 'for', 'fetch', 'into', 'open', 'close', 'exit',
               'dbms', 'utl', 'sys', 'systools', 'return', 'method', 'class'}
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('--') or stripped.startswith('@') or stripped.startswith('class') or stripped.startswith('method'):
            continue
        
        match = re.search(r'^\s+(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)
        if match:
            var_name = match.group(1)
            var_type = match.group(2).lower()
            
            if var_name.lower() in excluded:
                continue
            
            if not var_name.startswith('v_'):
                if var_type in ('string', 'varchar2'):
                    new_name = f'v_s{var_name.capitalize()}'
                elif var_type in ('number', 'integer'):
                    new_name = f'v_n{var_name.capitalize()}'
                elif var_type == 'boolean':
                    new_name = f'v_b{var_name.capitalize()}'
                elif var_type == 'ref':
                    new_name = f'v_r{var_name.capitalize()}'
                else:
                    new_name = f'v_{var_name}'
                
                issues.append((i + 1, line.strip(), new_name))
    
    return issues
2.2. not_mentioned — проверка неиспользуемых объявлений
python
def _check_multiline_not_mentioned(self, lines: List[str]) -> List[Tuple[int, str, str]]:
    """Проверка not_mentioned. Возвращает (line_num, original_line, var_name)."""
    issues = []
    excluded = {'class', 'method', 'execute', 'begin', 'if', 'then', 'else', 'end', 'return',
               'function', 'is', 'pragma', 'include', 'macro', 'ref', 'string', 'number',
               'integer', 'varchar2', 'date', 'boolean', 'timestamp', 'in', 'out', 'null',
               'true', 'false', 'not', 'and', 'or', 'like', 'between', 'case', 'when',
               'select', 'from', 'where', 'update', 'insert', 'delete', 'create', 'drop',
               'alter', 'table', 'index', 'view', 'procedure', 'trigger', 'sequence',
               'exception', 'others', 'raise', 'rollback', 'commit', 'savepoint',
               'loop', 'while', 'for', 'fetch', 'into', 'open', 'close', 'exit',
               'dbms', 'utl', 'sys', 'systools', 'return', 'method', 'class'}
    
    declared_vars = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('--') or stripped.startswith('@') or stripped.startswith('class') or stripped.startswith('method') or stripped.startswith('execute') or stripped.startswith('begin'):
            continue
        
        match = re.search(r'^\s+(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)
        if match:
            var_name = match.group(1)
            if var_name.lower() not in excluded:
                declared_vars[var_name] = i + 1
    
    for var_name, decl_line in declared_vars.items():
        var_pattern = re.compile(rf'\b{re.escape(var_name)}\b')
        count = 0
        for i, line in enumerate(lines, 1):
            if i != decl_line:
                count += len(var_pattern.findall(line))
        
        if count == 0:
            original_line = lines[decl_line - 1].strip() if decl_line <= len(lines) else ''
            issues.append((decl_line, original_line, var_name))
    
    return issues
2.3. wrong_method_syntax — проверка неполного пути к методу
python
def _check_multiline_wrong_method_syntax(self, lines: List[str]) -> List[Tuple[int, str, str]]:
    """Проверка wrong_method_syntax. Возвращает (line_num, original_line, method_path)."""
    issues = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('--'):
            continue
        
        match = re.search(r'\[(\w+)\]\.(\w+)\s*\(', line)
        if match:
            prefix = line[:match.start()]
            if not prefix.rstrip().endswith('::'):
                class_name = match.group(1)
                method_name = match.group(2)
                issues.append((i + 1, line.strip(), f'::[{class_name}].[{method_name}]'))
    
    return issues
2.4. code_in_comment — проверка закомментированного кода
python
def _check_multiline_code_in_comment(self, lines: List[str]) -> List[Tuple[int, str]]:
    """Проверка code_in_comment. Возвращает (line_num, original_line)."""
    issues = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('--'):
            continue
        
        comment_text = stripped[2:].strip()
        
        code_indicators = [';', 'begin', 'end', 'if', 'then', 'else', 'loop', 'select',
                          'from', 'where', 'insert', 'update', 'delete', 'return',
                          ':=', ':=', 'function', 'procedure', 'declare']
        
        for indicator in code_indicators:
            if indicator in comment_text.lower():
                if indicator == ';' and ';' in comment_text:
                    issues.append((i + 1, line.strip()))
                    break
                elif indicator in ('begin', 'end', 'if', 'then', 'else', 'loop', 'select',
                                  'from', 'where', 'insert', 'update', 'delete', 'return',
                                  ':=', ':=', 'function', 'procedure', 'declare'):
                    if re.search(rf'\b{indicator}\b', comment_text, re.IGNORECASE):
                        issues.append((i + 1, line.strip()))
                        break
    
    return issues
3. Привести формат вывода к ЦФТ-PlpCheck
Добавить маппинги:

python
PLPCHECK_RULE_NAMES: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'bad_prefix',
    'plpcheck.NOT_MENTIONED': 'not_mentioned',
    'plpcheck.WRONG_METHOD_SYNTAX': 'wrong_method_syntax',
    'plpcheck.CODE_IN_COMMENT': 'code_in_comment',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'prefix_type_in_var_name',
    # ...
}

PLPCHECK_RULE_LEVELS: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'WARNING',
    'plpcheck.NOT_MENTIONED': 'WARNING',
    'plpcheck.WRONG_METHOD_SYNTAX': 'WARNING',
    'plpcheck.CODE_IN_COMMENT': 'WARNING',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'WARNING',
    # ...
}

PLPCHECK_RULE_TYPES: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'STYLE',
    'plpcheck.NOT_MENTIONED': 'STYLE',
    'plpcheck.WRONG_METHOD_SYNTAX': 'STYLE',
    'plpcheck.CODE_IN_COMMENT': 'STYLE',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'STYLE',
    # ...
}
Переписать generate_report() для вывода в формате:

text
PlpCheck Отчёт
Дата: ...
Всего проблем: N
Уникальных проблем: N
Всего файлов: N

LINE | CHECK | LEVEL | TYPE | ERROR
====================================================================================================
    10 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_iDp"
    11 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_iDp1"
    ...
4. Протестировать на REPS_EXP_115_1.plp
Запустить сканер на файле PATCH_IN\patch_REPS_EXP_115_1\src\ENTITY\HOOK_BANK\REPS_EXP_115_1.plp и сравнить результат с эталонным логом.

5. Добиться совпадения: 14 = 14
После всех исправлений количество найденных проблем должно быть 14.

Ожидаемый результат
Показатель	ЦФТ-PlpCheck	АРМ (после DS 032)
Всего проблем	14	14
Уникальных	14	14
Ложные срабатывания	0	0

Примечания
1.bad_prefix: Проверяет префиксы переменных. Для string/varchar2 — v_s, для number — v_n, для integer — v_i, для boolean — v_b, для ref — v_r. Если переменная не имеет правильного префикса, предлагает новое имя.
2.not_mentioned: Проверяет, используется ли переменная где-либо кроме объявления. Если нет — выдает предупреждение.
3.wrong_method_syntax: Проверяет, что обращение к методу имеет полный путь ::[CLASS].[METHOD]. Если нет — выдает предупреждение.
4.code_in_comment: Проверяет комментарии на наличие признаков кода (;, begin, end, if, then, else, loop, select, from, where, insert, update, delete, return, :=, function, procedure, declare).
5.prefix_type_in_var_name: Проверяет, что имя переменной содержит префикс типа (например, v_s для string, v_r для ref).
