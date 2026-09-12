#!/usr/bin/env python3
"""
Сканер проблемных конструкций PLPlus для миграции на DBI
Версия: v06 - Полная поддержка рубрикатора v5.3.0 (объединенный 4.RUBRICATOR_PROMPT v5.json)
Отказ от v50. Полная поддержка сложных правил (тдс20240828.TRANS_ABORTED.стр.29 и др.)
"""
import re
import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set

# Импорт AI-анализатора для сложных правил
try:
    from analyzer.ai_analyzer import PLPlusAIAnalyzer, AIAnalysisResult
except ImportError:
    PLPlusAIAnalyzer = None
    AIAnalysisResult = None


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
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PLPlusScanner:
    """Сканер проблемных конструкций PLPlus - работа с 4.RUBRICATOR_PROMPT v5.json"""

    # Многострочные правила из нового рубрикатора (требуют анализа блока кода)
    MULTILINE_RULES: Set[str] = {
        'тдс20240828.TRANS_ABORTED.стр.29',  # WHEN OTHERS без ROLLBACK/RAISE
        'v53.PROC.WHENOTHERS.п.3.5',          # WHEN OTHERS без ROLLBACK/RAISE (аналог)
        'v53.PROC.NATIVEID.п.3.26',           # NativeID в NUMBER
        'v53.PROC.ID_SIZE.п.3.27',            # VARCHAR2(10) для ID
        'PlpCheck.STYLE.NOT_MENTIONED',       # Неиспользуемые переменные
        'тклоик20240828.VARCHAR_SIZE.стр.4',  # VARCHAR2/STRING без размера
        'тклоик20240828.NO_INTEGER_FOR_ID.стр.4' # INTEGER для ID
    }
    
    def __init__(self, config: dict, selected_rules: List[str] = None, rubricator_prompts=None):
        self.config = config
        self.selected_rules = selected_rules or []
        self.issues: List[Issue] = []
        self.stats: Dict[str, int] = {}
        self.in_block_comment = False
        self.lines = []  # для многострочного анализа
        self.file_path = None
        self.ai_results: List[AIAnalysisResult] = []  # Результаты AI-анализа
        self.ai_analyzer = None
        self.rubricator_prompts = rubricator_prompts  # Объект рубрикатора
        
        # Загрузка паттернов из рубрикатора
        self.PATTERNS = self._load_patterns_from_rubricator()
    
        # Инициализация AI-анализатора если доступен
        if PLPlusAIAnalyzer and hasattr(self, '_rubricator_rules'):
            self.ai_analyzer = PLPlusAIAnalyzer(self._rubricator_rules)
    
    def _is_hint_comment(self, line: str, pos: int) -> bool:
        """Проверка, является ли комментарий подсказкой оптимизатора /*+ ... */"""
        hint_start = line.find('/*+', pos)
        if hint_start != -1:
            hint_end = line.find('*/', hint_start)
            if hint_end != -1:
                return True
        return False
    
    def _is_in_comment_or_string(self, line: str, match_start: int, match_end: int) -> bool:
        """Проверка, находится ли найденное совпадение в комментарии или строковом литерале."""
        if self._is_hint_comment(line, match_start):
            return False
        
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
    
    def _find_code_positions(self, line: str, pattern: str, flags: int = 0) -> List[Tuple[int, int, str]]:
        """Найти все позиции паттерна в коде, игнорируя комментарии и строки."""
        pattern_clean = re.sub(r'\(\?([imsx]+)\)', lambda m: '', pattern)
        
        if '(?i' in pattern and not (flags & re.IGNORECASE):
            flags |= re.IGNORECASE
        
        matches = []
        for match in re.finditer(pattern_clean, line, flags):
            if not self._is_in_comment_or_string(line, match.start(), match.end()):
                matches.append((match.start(), match.end(), match.group()))
        return matches
    
    def _load_patterns_from_rubricator(self) -> Dict:
        """Загрузка паттернов из объединенного 4.RUBRICATOR_PROMPT v5.json"""
        patterns = {}
        ignore_patterns_map = {}
        self._rubricator_rules = {}
        
        # DS 023: отладочный вывод фильтрации
        DEBUG_FILTER = True
        dbg_loaded, dbg_skipped = [], []
        
        if self.rubricator_prompts and self.rubricator_prompts.loaded:
            all_rules = self.rubricator_prompts.get_all_rules()
            
            if DEBUG_FILTER:
                print(f"[DEBUG] selected_rules: {self.selected_rules}")
            
            # DS 024: предупреждение при пустом selected_rules — будут загружены ВСЕ правила
            if not self.selected_rules:
                print("[WARN] selected_rules пуст! Загружаются ВСЕ правила (332). "
                      "Если это не ожидаемое поведение — проверьте фильтрацию по файлам/приоритетам в gui_app.py.")
            
            for rule_info in all_rules:
                rule_key = rule_info['code']
                rule_data = self.rubricator_prompts.get_rule(rule_key)
                if not rule_data:
                    continue
                
                # Определяем источник (v53, тдс20240828, тклоик20240828, PlpCheck)
                file_code = rule_key.split('.')[0]
                
                # Фильтрация по выбранным файлам (DS 021, DS 016: регистронезависимо)
                # selected_rules содержит КОДЫ ФАЙЛОВ рубрикатора (v53, PlpCheck, тдс20240828, тклоик20240828),
                # а file_code - префикс правила. Сопоставляем через маппинг код файла -> префиксы правил.
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
                        # DS 024: selected_rules может содержать и КОДЫ ФАЙЛОВ ('v53', 'PlpCheck'),
                        # и КОДЫ ПРАВИЛ ('v53.SQL.OUTERJOIN.п.1.1') после приоритетной фильтрации.
                        if fc_lower in file_to_prefixes:
                            allowed_prefixes.update(file_to_prefixes[fc_lower])
                        else:
                            # Код правила: разрешаем префикс файла этого правила
                            allowed_prefixes.add(fc_lower.split('.')[0])
                    if file_code_lower not in allowed_prefixes:
                        if DEBUG_FILTER:
                            dbg_skipped.append(rule_key)
                            if len(dbg_skipped) <= 10:
                                print(f"[DEBUG] ПРОПУЩЕНО: {rule_key} (file_code: {file_code}, allowed_prefixes: {sorted(allowed_prefixes)})")
                        continue
                    else:
                        if DEBUG_FILTER:
                            dbg_loaded.append(rule_key)
                            if len(dbg_loaded) <= 10:
                                print(f"[DEBUG] ЗАГРУЖЕНО: {rule_key} (file_code_lower: {file_code_lower})")
                
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
                # DS 023: итоговая статистика фильтрации
                if DEBUG_FILTER:
                    import collections
                    loaded_by_prefix = collections.Counter(k.split('.')[0] for k in patterns.keys())
                    skipped_by_prefix = collections.Counter(k.split('.')[0] for k in dbg_skipped)
                    print(f"[DEBUG] Всего загружено правил: {len(dbg_loaded)}, пропущено фильтром: {len(dbg_skipped)}")
                    print(f"[DEBUG] Загружено по префиксам: {dict(loaded_by_prefix)}")
                    print(f"[DEBUG] Пропущено по префиксам: {dict(skipped_by_prefix)}")
                    print(f"[DEBUG] Всего загружено паттернов: {len(patterns)}")
                self.ignore_patterns_map = ignore_patterns_map
                return patterns
        
        print(f"[WARN] Рубрикатор не загружен или не содержит правил. Сканирование будет пропущено.")
        self.ignore_patterns_map = {}
        return {}
    
    def _is_rule_selected(self, rule_code: str) -> bool:
        """Проверка, выбран ли файл рубрикатора для данного правила (DS 022).
        
        Многострочные проверки захардкожены с кодами правил; здесь определяется
        файл рубрикатора по префиксу правила и проверяется его выбор.
        """
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
        # Регистронезависимое сравнение (DS 016)
        selected_lower = [s.lower() for s in self.selected_rules]
        return file_code.lower() in selected_lower
    
    def _check_multiline_when_others(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Многострочный поиск WHEN OTHERS без ROLLBACK/RAISE (тдс20240828.TRANS_ABORTED.стр.29)"""
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
    
    def _check_multiline_nativeid(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Поиск присваивания %id в NUMBER переменную (v53.PROC.NATIVEID.п.3.26)"""
        issues = []
        number_vars = {}
        for i, line in enumerate(lines):
            match = re.search(r'(\w+)\s+NUMBER\s*;', line, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                number_vars[var_name] = i + 1
        
        for var_name, decl_line in number_vars.items():
            for i, line in enumerate(lines):
                if re.search(rf'{var_name}\s*:=\s*\w+%id', line, re.IGNORECASE):
                    issues.append((i + 1, line.strip()))
        return issues
    
    def _check_multiline_id_size(self, lines: List[str]) -> List[Tuple[int, str, int]]:
        """Поиск VARCHAR2(10) для ID бизнес-данных (v53.PROC.ID_SIZE.п.3.27)"""
        issues = []
        for i, line in enumerate(lines):
            match = re.search(r'(\w+)\s+(?:VARCHAR2|STRING)\s*\((\d+)\)\s*;', line, re.IGNORECASE)
            if match:
                size = int(match.group(2))
                if size < 20:
                    var_name = match.group(1)
                    for j, next_line in enumerate(lines[i:], i):
                        if re.search(rf'{var_name}\s*:=\s*\w+%id', next_line, re.IGNORECASE):
                            issues.append((i + 1, line.strip(), size))
                            break
        return issues
    
    def _check_multiline_not_mentioned(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Поиск объявленных, но неиспользуемых переменных (PlpCheck.STYLE.NOT_MENTIONED)"""
        issues = []
        excluded = {'class', 'method', 'execute', 'begin', 'if', 'then', 'else', 'end', 'return', 
                   'function', 'is', 'pragma', 'include', 'macro', 'ref', 'string', 'number', 
                   'integer', 'varchar2', 'date', 'boolean', 'timestamp', 'in', 'out', 'null',
                   'true', 'false', 'not', 'and', 'or', 'like', 'between', 'case', 'when',
                   'select', 'from', 'where', 'update', 'insert', 'delete', 'create', 'drop',
                   'alter', 'table', 'index', 'view', 'procedure', 'trigger', 'sequence',
                   'exception', 'others', 'raise', 'rollback', 'commit', 'savepoint',
                   'loop', 'while', 'for', 'fetch', 'into', 'open', 'close', 'exit',
                   'dbms', 'utl', 'sys', 'systools'}
        
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
        
        full_code = ''.join(lines)
        for var_name, decl_line in declared_vars.items():
            var_pattern = re.compile(rf'\b{re.escape(var_name)}\b')
            count = 0
            for i, line in enumerate(lines, 1):
                if i != decl_line:
                    count += len(var_pattern.findall(line))
            
            if count == 0:
                issues.append((decl_line, f"{var_name} объявлена, но не используется"))
        
        return issues
    
    def _check_multiline_varchar_size(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Поиск VARCHAR2/STRING без размера (тклоик20240828.VARCHAR_SIZE.стр.4)"""
        issues = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('@') or stripped.startswith('class'):
                continue
            # Ищем переменную с типом VARCHAR2/STRING но без размерности
            match = re.search(r'\b\w+\s+(varchar2|string)\s*[;(]', line, re.IGNORECASE)
            if match:
                # Проверяем, что нет скобок с размером сразу после типа
                if not re.search(r'(varchar2|string)\s*\(\d+\)', line, re.IGNORECASE):
                    issues.append((i + 1, line.strip()))
        return issues
    
    def _check_multiline_integer_id(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Поиск INTEGER для ID экземпляров (тклоик20240828.NO_INTEGER_FOR_ID.стр.4)"""
        issues = []
        for i, line in enumerate(lines):
            match = re.search(r'\b\w+\s+integer\s*[;(]', line, re.IGNORECASE)
            if match:
                issues.append((i + 1, line.strip()))
        return issues
    
    def scan_file(self, file_path: Path, log_callback=None) -> List[Issue]:
        """Сканирование одного файла"""
        issues = []
        self.in_block_comment = False
        self.file_path = file_path
        
        # DS 023: отладочный вывод
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
            
            # ========== ОДНОСТРОЧНЫЙ ПОИСК ==========
            for line_num, line in enumerate(self.lines, 1):
                original_line = line
                stripped = original_line.strip()
                
                self._update_block_comment_state(line)
                
                if stripped.startswith('--'):
                    continue
                
                issues_found_on_line = 0
                
                for issue_type, pattern_data in self.PATTERNS.items():
                    if not isinstance(pattern_data, tuple) or len(pattern_data) < 3:
                        continue
                    
                    base_issue_type = issue_type.rsplit('.[', 1)[0] if '.[' in issue_type else issue_type
                    
                    if len(pattern_data) >= 9:
                        pattern, description, category, tags, full_description, example_code, example_fixed, rubricator_line, flags = pattern_data
                    elif len(pattern_data) >= 8:
                        pattern, description, category, tags, full_description, example_code, example_fixed, rubricator_line = pattern_data[:8]
                        flags = 0
                    else:
                        pattern, description, category = pattern_data[:3]
                        tags, full_description, example_code, example_fixed, rubricator_line, flags = [], '', '', '', '', 0
                    
                    search_flags = flags if flags else re.IGNORECASE
                    code_matches = self._find_code_positions(original_line, pattern, search_flags)
                    
                    for match_start, match_end, matched_text in code_matches:
                        is_ignored = False
                        ignore_list = self.ignore_patterns_map.get(base_issue_type, [])
                        
                        for ignore_pattern in ignore_list:
                            if not isinstance(ignore_pattern, str):
                                continue
                            if ignore_pattern and re.search(ignore_pattern, original_line, re.IGNORECASE):
                                is_ignored = True
                                break
                        
                        if is_ignored:
                            continue
                        
                        source_dir_str = self.config['paths']['source_dir']
                        if len(source_dir_str) >= 2 and source_dir_str[1] == ':':
                            source_dir_str = source_dir_str[0].upper() + source_dir_str[1:]
                        
                        absolute_file_path = str(file_path.resolve())
                        if len(absolute_file_path) >= 2 and absolute_file_path[1] == ':':
                            absolute_file_path = absolute_file_path[0].upper() + absolute_file_path[1:]
                        
                        issue = Issue(
                            file_path=absolute_file_path,
                            line_number=line_num,
                            issue_type=base_issue_type,
                            description=description,
                            original_code=original_line[:200],
                            category=category,
                            rubricator_code=base_issue_type,
                            rubricator_full_description=full_description,
                            rubricator_example_code=example_code,
                            rubricator_example_fixed=example_fixed,
                            tags=tags
                        )
                        issues.append(issue)
                        issues_found_on_line += 1
                        
                        if log_callback:
                            log_callback(f"    [ПАРСЕР SQL] Обработано правило: {base_issue_type}", 'info')
                            log_callback(f"  Строка {line_num} >>> {original_line.strip()}", 'info')
                            
                            tags_str = f"[ТЕГИ] {', '.join(tags)}" if tags else ""
                            log_callback(f"    {tags_str} [КОД] {issue_type}: {description}", 'warning')
                            
                            prompt = f"Проанализируй код: {original_line.strip()} | Правило: {issue_type} | Описание: {description}"
                            log_callback(f"    [ПРОМПТ] {prompt}", 'info')
                            if example_fixed:
                                log_callback(f"    Пример исправления: {example_fixed}", 'success')
                
                if log_callback and issues_found_on_line > 0:
                    log_callback(f"  [ПАРСЕР SQL] Строка {line_num}: найдено {issues_found_on_line} проблем(ы)", 'info')
            
            # ========== МНОГОСТРОЧНЫЙ ПОИСК ==========
            if log_callback:
                log_callback(f"\n  [МНОГОСТРОЧНЫЙ АНАЛИЗ] Проверка сложных правил...", 'info')
            
            # 1. WHEN OTHERS без ROLLBACK/RAISE (тдс20240828.TRANS_ABORTED.стр.29) — DS 022: фильтр
            if self._is_rule_selected('тдс20240828.TRANS_ABORTED.стр.29') or \
               self._is_rule_selected('v53.PROC.WHENOTHERS.п.3.5'):
                multiline_issues = self._check_multiline_when_others(self.lines)
                for line_num, bad_code in multiline_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='тдс20240828.TRANS_ABORTED.стр.29',
                        description='WHEN OTHERS без ROLLBACK/RAISE',
                        original_code=bad_code[:200],
                        category='PROC',
                        rubricator_code='тдс20240828.TRANS_ABORTED.стр.29',
                        rubricator_full_description='В PostgreSQL после ошибки транзакция прерывается.',
                        rubricator_example_code='exception when others then null;',
                        rubricator_example_fixed='exception when others then &rb(point1); raise;',
                        tags=['transaction', 'aborted', 'rollback']
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено WHEN OTHERS без обработки в строке {line_num}", 'warning')
            
            # 2. NativeID: присваивание %id в NUMBER (v53.PROC.NATIVEID.п.3.26) — DS 022: фильтр
            if self._is_rule_selected('v53.PROC.NATIVEID.п.3.26'):
                nativeid_issues = self._check_multiline_nativeid(self.lines)
                for line_num, bad_code in nativeid_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='v53.PROC.NATIVEID.п.3.26',
                        description='NativeID для метаданных (NUMBER переменная для %id)',
                        original_code=bad_code[:200],
                        category='PROC',
                        rubricator_code='v53.PROC.NATIVEID.п.3.26',
                        rubricator_full_description='Идентификаторы операций и представлений стали строками, не числами.',
                        rubricator_example_code='v_id number; v_id := rMeth%id;',
                        rubricator_example_fixed='v_id varchar2(100); v_id := rMeth%id;',
                        tags=['nativeid', 'identifiers']
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено присваивание %id в NUMBER в строке {line_num}", 'warning')
            
            # 3. ID_SIZE: VARCHAR2(10) для ID бизнес-данных (v53.PROC.ID_SIZE.п.3.27) — DS 022: фильтр
            if self._is_rule_selected('v53.PROC.ID_SIZE.п.3.27'):
                id_size_issues = self._check_multiline_id_size(self.lines)
                for line_num, bad_code, size in id_size_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='v53.PROC.ID_SIZE.п.3.27',
                        description=f'VARCHAR2({size}) слишком мало для ID бизнес-данных (требуется >=20)',
                        original_code=bad_code[:200],
                        category='PROC',
                        rubricator_code='v53.PROC.ID_SIZE.п.3.27',
                        rubricator_full_description='ID бизнес-данных должны иметь VARCHAR2(38) или больше.',
                        rubricator_example_code=f'v_id varchar2(10);',
                        rubricator_example_fixed='v_id varchar2(38);',
                        tags=['id', 'size', 'varchar2']
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено {bad_code} в строке {line_num}", 'warning')
            
            # 4. NOT_MENTIONED: неиспользуемые переменные (PlpCheck.STYLE.NOT_MENTIONED) — DS 022: фильтр
            if self._is_rule_selected('PlpCheck.STYLE.NOT_MENTIONED'):
                not_mentioned_issues = self._check_multiline_not_mentioned(self.lines)
                for line_num, description in not_mentioned_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='PlpCheck.STYLE.NOT_MENTIONED',
                        description=description,
                        original_code=self.lines[line_num - 1][:200] if line_num <= len(self.lines) else '',
                        category='STYLE',
                        rubricator_code='PlpCheck.STYLE.NOT_MENTIONED',
                        rubricator_full_description='Объявленные, но неиспользуемые переменные увеличивают размер кода и вносят путаницу.',
                        rubricator_example_code='tmp_data number;',
                        rubricator_example_fixed='',
                        tags=['unused', 'variables']
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено неиспользуемое объявление в строке {line_num}", 'warning')
            
            # 5. VARCHAR2/STRING без размера (тклоик20240828.VARCHAR_SIZE.стр.4) — DS 022: фильтр
            if self._is_rule_selected('тклоик20240828.VARCHAR_SIZE.стр.4'):
                varchar_size_issues = self._check_multiline_varchar_size(self.lines)
                for line_num, bad_code in varchar_size_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='тклоик20240828.VARCHAR_SIZE.стр.4',
                        description='VARCHAR2/STRING без указания размера',
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='тклоик20240828.VARCHAR_SIZE.стр.4',
                        rubricator_full_description='При использовании параметров и переменных типа VARCHAR2 и STRING указывайте их размерность!',
                        rubricator_example_code='v_name varchar2;',
                        rubricator_example_fixed='v_name varchar2(255);',
                        tags=['varchar2', 'size']
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено объявление без размера в строке {line_num}", 'warning')
            
            # 6. INTEGER для ID экземпляров (тклоик20240828.NO_INTEGER_FOR_ID.стр.4) — DS 022: фильтр
            if self._is_rule_selected('тклоик20240828.NO_INTEGER_FOR_ID.стр.4'):
                integer_id_issues = self._check_multiline_integer_id(self.lines)
                for line_num, bad_code in integer_id_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='тклоик20240828.NO_INTEGER_FOR_ID.стр.4',
                        description='INTEGER для ID экземпляров',
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='тклоик20240828.NO_INTEGER_FOR_ID.стр.4',
                        rubricator_full_description='ID экземпляров имеют тип number, значения могут принимать больше, чем 2147483647.',
                        rubricator_example_code='v_id integer;',
                        rubricator_example_fixed='v_id number;',
                        tags=['integer', 'id']
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено INTEGER в строке {line_num}", 'warning')
            
            # ========== ФАЗА 2: AI-АНАЛИЗ СЛОЖНЫХ ПРАВИЛ ==========
            if self.ai_analyzer and hasattr(self, '_rubricator_rules'):
                ai_rules_count = len(self.ai_analyzer.ai_rules) if hasattr(self.ai_analyzer, 'ai_rules') else 0
                if log_callback:
                    log_callback(f"\n  [AI-АНАЛИЗ] Анализ контекста для {ai_rules_count} сложных правил...", 'info')
                
                ai_candidates = []
                for issue in issues:
                    rule_code = issue.issue_type
                    if self.ai_analyzer and rule_code in self.ai_analyzer.ai_rules:
                        ai_candidates.append({
                            'rule_code': rule_code,
                            'line_number': issue.line_number,
                            'original_code': issue.original_code
                        })
                
                if ai_candidates:
                    if log_callback:
                        log_callback(f"    Найдено {len(ai_candidates)} потенциальных проблем для AI-анализа", 'info')
                    
                    ai_results = self.ai_analyzer.analyze_file(
                        file_path, self.lines, ai_candidates
                    )
                    
                    self.ai_results.extend(ai_results)
                    
                    for result in ai_results:
                        if log_callback:
                            log_callback(f"\n    --- [ПРАВИЛО: {result.rule_code}] [ПРИОРИТЕТ: {result.priority}] [ТИП_АНАЛИЗА: AI] ---", 'warning')
                            log_callback(f"    [СТРОКА: {result.line_number}]", 'info')
                            log_callback(f"    [ИСХОДНЫЙ_КОД: {result.original_code}]", 'info')
                            log_callback(f"    [СТЕПЕНИ_АНАЛИЗА: {result.steps_summary}]", 'info')
                            log_callback(f"    [ОБОСНОВАНИЕ: {result.reasoning}]", 'info')
                            log_callback(f"    [ИСПРАВЛЕНИЕ: {result.fixed_code}]", 'success')
                            log_callback(f"    [УВЕРЕННОСТЬ: {result.confidence:.0%}]", 'info')
                            log_callback(f"    ---", 'warning')
                else:
                    if log_callback:
                        log_callback(f"    Нет проблем, требующих AI-анализа", 'info')
            
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при чтении {file_path}: {e}\n{traceback.format_exc()}"
            print(error_msg)
            if log_callback:
                log_callback(f"  Ошибка: {e}", 'error')
        
        self.issues.extend(issues)
        return issues
    
    def scan_directory(self, log_callback=None) -> Dict[str, int]:
        """Сканирование всех .plp файлов"""
        # DS 023: отладочный вывод общего количества загруженных паттернов
        print(f"[DEBUG] scan_directory: Всего загружено паттернов: {len(self.PATTERNS)}")
        
        source_dir_str = self.config['paths']['source_dir']
        if len(source_dir_str) >= 2 and source_dir_str[1] == ':':
            source_dir_str = source_dir_str[0].upper() + source_dir_str[1:]
        source_dir = Path(source_dir_str)
        
        file_pattern = self.config['scan'].get('file_pattern', '**/*.plp')
        
        if not file_pattern or file_pattern == '*' or file_pattern == '*.*':
            file_pattern = '**/*.plp'
        
        recursive = self.config['scan'].get('recursive', True)
        
        stats = {}
        files_scanned = 0
        
        if recursive:
            file_finder = source_dir.rglob
        else:
            file_finder = source_dir.glob
        
        all_files = [f for f in file_finder(file_pattern) if not self._should_exclude(f)]
        total_files = len(all_files)
        
        if log_callback and total_files > 0:
            log_callback(f"\nВсего файлов для сканирования: {total_files}", 'info')
        
        for plp_file in all_files:
            file_issues = self.scan_file(plp_file, log_callback=log_callback)
            files_scanned += 1
            
            if log_callback:
                file_name = plp_file.name
                if len(file_issues) > 0:
                    log_callback(f"\n[{files_scanned}/{total_files}] Результаты сканирования файла {file_name}", 'info')
                    log_callback(f"  Проблемных конструкций: {len(file_issues)}", 'info')
                    
                    issues_by_type = {}
                    for issue in file_issues:
                        issue_type = issue.issue_type
                        issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
                    
                    log_callback(f"\nПроблемы по типам:", 'info')
                    for issue_type, count in sorted(issues_by_type.items(), key=lambda x: (-x[1], x[0])):
                        log_callback(f"  {issue_type}: {count}", 'info')
            
            for issue in file_issues:
                stats[issue.issue_type] = stats.get(issue.issue_type, 0) + 1
            
            if log_callback and total_files > 0:
                progress = min(100, int((files_scanned / total_files) * 100))
                if files_scanned % max(1, total_files // 10) == 0 or files_scanned == total_files:
                    log_callback(f"  Прогресс: {files_scanned}/{total_files} ({progress}%)", 'info')
        
        if log_callback:
            total_issues = len(self.issues)
            total_rules = len(stats)
            ai_count = len(self.ai_results)
            sep = '=' * 70
            dash = '-' * 70
            log_callback(f"\n{sep}", 'info')
            log_callback('ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ', 'info')
            log_callback(sep, 'info')
            log_callback(f'Всего файлов просканировано:    {files_scanned}', 'info')
            log_callback(f'Всего проблем найдено:         {total_issues}', 'info')
            log_callback(f'Всего видов кодов правил:      {total_rules}', 'info')
            if ai_count > 0:
                log_callback(f'Из них с AI-анализом:          {ai_count}', 'info')
            log_callback(sep, 'info')
            log_callback('Распределение по кодам правил (по убыванию):', 'info')
            log_callback(dash, 'info')
            for rule_code, count in sorted(stats.items(), key=lambda x: (-x[1], x[0])):
                log_callback(f'  {rule_code}: {count}', 'info')
            log_callback(sep, 'info')
        
        return {
            'files_scanned': files_scanned,
            'total_issues': len(self.issues),
            'by_type': stats
        }
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Проверка исключений"""
        if file_path.suffix.lower() != '.plp':
            return True
        
        file_path_str = str(file_path)
        if len(file_path_str) >= 2 and file_path_str[1] == ':':
            file_path_str = file_path_str[0].upper() + file_path_str[1:]
        for pattern in self.config['scan']['exclude_patterns']:
            if pattern in file_path_str:
                return True
        return False
    
    def get_issues_by_file(self) -> Dict[str, List[Issue]]:
        """Возвращает словарь с проблемами, сгруппированными по файлам"""
        by_file = {}
        for issue in self.issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)
        return by_file
        
    def _parse_class_and_method(self, file_path) -> Tuple[str, str, str]:
        """Парсинг имени класса, метода и секции из файла (DS 025)"""
        class_name = "UNKNOWN"
        method_name = "UNKNOWN"
        section = "PRIVATE"
        
        try:
            content, _ = read_file_with_encoding(Path(file_path))
            # Ищем класс
            class_match = re.search(r'\bclass\s+(\w+)', content)
            if class_match:
                class_name = class_match.group(1)
            # Ищем метод
            method_match = re.search(r'\bmethod\s+(\w+)\s+is', content, re.IGNORECASE)
            if method_match:
                method_name = method_match.group(1)
            # Ищем секцию (PRIVATE / EXECUTE / VALIDATE / PUBLIC)
            section_match = re.search(r'\b(PRIVATE|EXECUTE|VALIDATE|PUBLIC)\b', content)
            if section_match:
                section = section_match.group(1)
        except Exception:
            pass
        
        return class_name, method_name, section
    
    def _get_severity_level(self, issue_type: str) -> str:
        """Определение уровня на основе типа проблемы (DS 025)"""
        # HIGH-правила → ERROR_STYLE
        high_rules = [
            'CONNECTBY2WITH', 'ROWNUM', 'OBLIGATORY_IN_OTHERS',
            'JSON_TYPES', 'OUTER_JOIN', 'NVL_IN_SELECT',
            'DIRECT_COMPARISON_WITH_NULL', 'PURE_SQL_DBLINK',
            'UPDATE_DELETE_BY_SUBQUERY', 'TRANS_ABORTED'
        ]
        # MEDIUM → WARNING_STYLE
        # LOW → INFO_STYLE
        for rule in high_rules:
            if rule in issue_type.upper():
                return 'ERROR_STYLE'
        return 'WARNING_STYLE'
    
    def generate_report(self, output_path: Path):
        """Генерация отчёта. DS 025: если расширение .html - генерируется HTML-таблица
        в формате дистрибутивного PlpCheck-отчёта, иначе - прежний Markdown."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # DS 025: HTML-отчёт в формате дистрибутивного PlpCheck
        if output_path.suffix.lower() == '.html':
            self._generate_html_report(output_path)
            return
        
        by_file = {}
        for issue in self.issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)
        
        # DS 029: Markdown-отчёт в формате дистрибутивного PlpCheck-лога
        # (одна строка на проблему: КЛАСС.МЕТОД.СЕКЦИЯ:СТРОКА ТИП: ОПИСАНИЕ)
        if not self.issues:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("PlpCheck Отчёт\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Проблем не найдено.\n")
            print(f"Отчёт сохранён: {output_path}")
            return
        
        # Кэш метаданных по файлам
        meta_cache = {}
        
        # Формируем строки: {КЛАСС}.{МЕТОД}.{СЕКЦИЯ}:{СТРОКА} {ТИП}: {ОПИСАНИЕ} | ПЛАН: {ИСПРАВЛЕНИЕ}
        report_lines = []
        for issue in self.issues:
            fp = issue.file_path
            if fp not in meta_cache:
                meta_cache[fp] = self._parse_class_and_method(fp)
            class_name, method_name, section = meta_cache[fp]
            
            plan = self._generate_plan(issue.issue_type, issue.description)
            report_lines.append(
                f"{class_name}.{method_name}.{section}:{issue.line_number} "
                f"{issue.issue_type}: {issue.description} | ПЛАН: {plan}"
            )
        
        # Сортировка по классу, методу, строке (строка извлекается из начала строки отчёта)
        def _sort_key(s):
            # Формат: КЛАСС.МЕТОД.СЕКЦИЯ:СТРОКА ...
            try:
                loc, rest = s.split(' ', 1)
                cls_meth_sec, line_str = loc.rsplit(':', 1)
                return (cls_meth_sec, int(line_str))
            except (ValueError, IndexError):
                return (s, 0)
        
        report_lines.sort(key=_sort_key)
        
        # DS 030: удаление дубликатов (сохраняем порядок сортировки)
        unique_lines = []
        seen = set()
        for line in report_lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("PlpCheck Отчёт\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего проблем: {len(report_lines)}\n")
            f.write(f"Уникальных проблем: {len(unique_lines)}\n")
            f.write(f"Всего файлов: {len(meta_cache)}\n\n")
            f.write("\n".join(unique_lines))
            f.write("\n")
        
        print(f"Отчёт сохранён: {output_path}")
    
    def _generate_html_report(self, output_path: Path):
        """Генерация HTML-отчёта в формате дистрибутивного PlpCheck-отчёта (DS 025).
        
        Таблица: # | Класс | Метод | Секция | Строка | Тип | Уровень | Описание
        Сортировка: класс (алфавитно) -> метод (алфавитно) -> строка (по возрастанию).
        """
        import html as html_module
        
        # Кэш парсинга класс/метод/секция по файлам
        parsed_cache = {}
        
        rows = []
        for issue in self.issues:
            fp = issue.file_path
            if fp not in parsed_cache:
                parsed_cache[fp] = self._parse_class_and_method(fp)
            class_name, method_name, section = parsed_cache[fp]
            severity = self._get_severity_level(issue.issue_type)
            plan_data = self._generate_issue_with_plan(issue, len(rows), parsed_cache)
            rows.append({
                'class': class_name,
                'method': method_name,
                'section': section,
                'line': issue.line_number,
                'type': issue.issue_type,
                'level': severity,
                'description': issue.description,
                'plan': plan_data['plan'],
                'corrected_lines': plan_data['corrected_lines'],
                'new_lines': plan_data['new_lines'],
            })
        
        # Сортировка: класс -> метод -> строка
        rows.sort(key=lambda r: (r['class'], r['method'], r['line']))
        
        # Статистика
        by_level = {}
        for r in rows:
            by_level[r['level']] = by_level.get(r['level'], 0) + 1
        
        stats_rows = ''.join(
            f'<tr><td>{html_module.escape(k)}</td><td>{v}</td></tr>'
            for k, v in sorted(by_level.items())
        )
        
        body_rows = []
        for i, r in enumerate(rows, 1):
            css = 'error' if r['level'] == 'ERROR_STYLE' else ('warning' if r['level'] == 'WARNING_STYLE' else 'info')
            
            # Формируем строку ПЛАН с информацией об исправлениях
            plan_html = html_module.escape(r['plan'])
            if r['corrected_lines'] or r['new_lines']:
                plan_html += '<br>'
                if r['corrected_lines']:
                    plan_html += '<small><b>ИСПРАВЛЯЕМЫЕ:</b><br>'
                    for line_num, code in r['corrected_lines']:
                        plan_html += f'{line_num}: {html_module.escape(code)}<br>'
                    plan_html += '</small>'
                if r['new_lines']:
                    plan_html += '<small><b>НОВЫЕ:</b><br>'
                    for line_num, code in r['new_lines']:
                        plan_html += f'{line_num}: {html_module.escape(code)}<br>'
                    plan_html += '</small>'
            
            body_rows.append(
                f'<tr class="{css}">'
                f'<td>{i}</td>'
                f'<td>{html_module.escape(str(r["class"]))}</td>'
                f'<td>{html_module.escape(str(r["method"]))}</td>'
                f'<td>{html_module.escape(str(r["section"]))}</td>'
                f'<td>{r["line"]}</td>'
                f'<td>{html_module.escape(str(r["type"]))}</td>'
                f'<td>{html_module.escape(r["level"])}</td>'
                f'<td>{html_module.escape(str(r["description"]))}</td>'
                f'<td>{plan_html}</td>'
                f'</tr>'
            )
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PlpCheck Отчёт</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #fafafa; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; background: #fff; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 6px 10px; text-align: left; font-size: 13px; }}
        th {{ background: #2c3e50; color: #fff; position: sticky; top: 0; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        tr.error td {{ background: #fadbd8; }}
        tr.warning td {{ background: #fdebd0; }}
        tr.info td {{ background: #d6eaf8; }}
        .meta {{ color: #7f8c8d; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>PlpCheck Отчёт</h1>
    <p class="meta">Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &nbsp;|&nbsp;
       Всего найдено проблем: {len(rows)} &nbsp;|&nbsp;
       Всего файлов: {len(parsed_cache)}</p>
    <h2>Статистика</h2>
    <table>
        <thead><tr><th>Уровень</th><th>Количество</th></tr></thead>
        <tbody>{stats_rows}</tbody>
    </table>
    <h2>Проблемы</h2>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Класс</th>
                <th>Метод</th>
                <th>Секция</th>
                <th>Строка</th>
                <th>Тип</th>
                <th>Уровень</th>
                <th>Описание</th>
                <th>ПЛАН</th>
            </tr>
        </thead>
        <tbody>
            {chr(10).join(body_rows)}
        </tbody>
    </table>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML-отчёт сохранён: {output_path}")
    
    def _generate_plan(self, issue_type: str, description: str = '') -> str:
        """Генерация текста ПЛАНА на основе типа правила (DS 028)."""
        issue_type_lower = issue_type.lower()
        if 'bad_prefix' in issue_type_lower:
            import re
            match = re.search(r'переименуйте в ["\']([^"\']+)["\']', description, re.IGNORECASE)
            if match:
                return f'Переименовать в "{match.group(1)}"'
            return 'Переименовать в корректный префикс'
        
        if 'not_mentioned' in issue_type_lower:
            return 'Удалить объявление'
        
        if 'code_in_comment' in issue_type_lower:
            return 'Удалить закомментированный код'
        
        if 'wrong_method_syntax' in issue_type_lower:
            return 'Исправить синтаксис'
        
        if 'prefix_type_in_var_name' in issue_type_lower:
            return 'Добавить префикс типа'
        
        if 'syntax_error' in issue_type_lower:
            return 'Исправить синтаксическую ошибку'
        
        if 'pure_sql_dblink' in issue_type_lower:
            return 'Заменить на прикладную таблицу'
        
        if 'pure_udf' in issue_type_lower or 'udf' in issue_type_lower:
            return 'Вынести UDF в процедурный код'
        
        if 'outer_join' in issue_type_lower:
            return 'Заменить на ANSI JOIN'
        
        if 'rownum' in issue_type_lower:
            return 'Заменить на FETCH'
        
        if 'direct_comparison' in issue_type_lower:
            return 'Исправить сравнение с NULL'
        
        if 'update_delete_by_subquery' in issue_type_lower:
            return 'Заменить на прикладную таблицу'
        
        if 'connectby2with' in issue_type_lower:
            return 'Заменить на CONNECT BY PRIOR'
        
        return 'Исправить по описанию'
    
    def _apply_fix(self, issue_type: str, original_code: str, description: str = '') -> str:
        """Применение исправления к строке кода (DS 028)."""
        issue_type_lower = issue_type.lower()
        stripped = original_code.strip()
        
        if 'code_in_comment' in issue_type_lower:
            if stripped.startswith('--'):
                return '-- (удалено)'
            return original_code
        
        if 'not_mentioned' in issue_type_lower:
            if stripped and not stripped.startswith('--'):
                return '-- ' + original_code
            return original_code
        
        if 'bad_prefix' in issue_type_lower:
            import re
            # Ищем имя в description (если есть), иначе в original_code
            new_name = None
            if description:
                match = re.search(r'переименуйте в ["\']([^"\']+)["\']', description, re.IGNORECASE)
            else:
                match = re.search(r'переименуйте в ["\']([^"\']+)["\']', original_code, re.IGNORECASE)
            if match:
                new_name = match.group(1)
            else:
                # Попробуем извлечь из original_code если это объявление
                match = re.search(r'(v_\w+)', original_code)
                if match:
                    new_name = 'v_new'  # Fallback
                    # Если description есть, ищем там
                    if description:
                        match = re.search(r'переименуйте в ["\']([^"\']+)["\']', description, re.IGNORECASE)
                        if match:
                            new_name = match.group(1)
            
            if new_name:
                original_code = re.sub(r'\b(v_\w+)\b', new_name, original_code, count=1)
                return original_code
            return original_code
        
        return original_code
    
    def _generate_issue_with_plan(self, issue, idx, parsed_cache, html_escape=None):
        """Генерация строки отчёта с ПЛАНом (DS 028).
        
        Возвращает кортеж (plan, corrected_lines, new_lines)
        """
        plan = self._generate_plan(issue.issue_type, issue.description)
        
        # Определяем диапазон строк (пока поддерживаем одиночные строки)
        start_line = issue.line_number
        end_line = issue.line_number
        
        # Применяем исправление к оригинальному коду (передаём description для bad_prefix)
        corrected_code = self._apply_fix(issue.issue_type, issue.original_code, issue.description)
        
        corrected_lines = [(start_line, issue.original_code)]
        new_lines = [(end_line, corrected_code)] if corrected_code != issue.original_code else []
        
        return {
            'plan': plan,
            'start_line': start_line,
            'end_line': end_line,
            'corrected_lines': corrected_lines,
            'new_lines': new_lines,
        }


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