#!/usr/bin/env python3
"""
Сканер проблемных конструкций PLPlus для миграции на DBI
Версия: v04 - исправленная (многострочный поиск, поддержка hints, улучшенные паттерны)
"""
import re
import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import re
import json

# Импорт AI-анализатора для сложных правил v3.3.0
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
    """Сканер проблемных конструкций PLPlus - исправленная версия"""
    
    # Паттерны по умолчанию (если рубрикатор не загружен)
    DEFAULT_PATTERNS = {
        'v50.SQL.OUTERJOIN.п.1.1': (r'\(\+\)', 'Oracle outer join (+) -> LEFT JOIN', 'SQL', ['outer join', 'oracle', 'ansi'],
                                   'В Oracle используется оператор (+) для внешнего соединения.',
                                   'select * from t1, t2 where t1.id = t2.id(+)',
                                   'select * from t1 left join t2 on t1.id = t2.id'),
        'v50.SQL.ROWNUM.п.1.2': (r'\bROWNUM\s*[=<>]', 'ROWNUM -> FETCH FIRST', 'SQL', ['rownum', 'limit', 'offset'],
                                'Псевдоколонка rownum не поддерживается в PostgreSQL.',
                                  'select * from t where rownum = 1',
                                'select * from t fetch first 1 rows only'),
        'v50.PROC.WHENOTHERS.п.3.5': (r'exception\s+when\s+others\s+then', 
                    'WHEN OTHERS без ROLLBACK/RAISE', 'PL/SQL', ['exception', 'rollback', 'raise'],
                    'В PostgreSQL после ошибки транзакция прерывается.',
                    'exception when others then null;',
                    'exception when others then rollback; raise;'),
    }
    
    # Многострочные правила (требуют анализа блока)
    MULTILINE_RULES: Set[str] = {
        'v50.PROC.WHENOTHERS.п.3.5',
        'v50.PROC.NATIVEID.п.3.26',
        'v50.PROC.ID_SIZE.п.3.27',
    }
    
    def __init__(self, config: dict, selected_rules: List[str] = None):
        self.config = config
        self.selected_rules = selected_rules or []
        self.issues: List[Issue] = []
        self.stats: Dict[str, int] = {}
        self.in_block_comment = False
        self.lines = []  # для многострочного анализа
        self.file_path = None
        self.ai_results: List[AIAnalysisResult] = []  # Результаты AI-анализа
        self.ai_analyzer = None  # AI-анализатор (инициализируется при загрузке рубрикатора)
    
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
        """
        Проверка, находится ли найденное совпадение в комментарии или строковом литерале.
        Исключение: подсказки оптимизатора /*+ ... */ НЕ игнорируются.
        """
        # Проверка 1: подсказка оптимизатора - НЕ ИГНОРИРУЕМ
        if self._is_hint_comment(line, match_start):
            return False
        
        # Проверка 2: Строка полностью комментарий (начинается с --)
        stripped = line.lstrip()
        if stripped.startswith('--'):
            return True
        
        # Проверка 3: Однострочный комментарий перед совпадением
        line_before_match = line[:match_start]
        if '--' in line_before_match:
            comment_pos = line_before_match.rfind('--')
            before_comment = line[:comment_pos]
            if before_comment.count("'") % 2 == 0:
                return True
        
        # Проверка 4: Внутри строкового литерала '...'
        single_quotes_before = line[:match_start].count("'")
        if single_quotes_before % 2 == 1:
            return True
        
        # Проверка 5: Внутри блочного комментария /* */
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
        """Обновление состояния блочного комментария после обработки строки"""
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
        # Извлекаем inline-флаги из паттерна (например, (?i) в середине)
        # и перемещаем их в начало или убираем
        pattern_clean = re.sub(r'\(\?([imsx]+)\)', lambda m: '', pattern)
        
        # Проверяем есть ли inline-флаг (?i) и добавляем re.IGNORECASE
        if '(?i' in pattern and not (flags & re.IGNORECASE):
            flags |= re.IGNORECASE
        
        matches = []
        for match in re.finditer(pattern_clean, line, flags):
            if not self._is_in_comment_or_string(line, match.start(), match.end()):
                matches.append((match.start(), match.end(), match.group()))
        return matches
    
    def _check_multiline_when_others(self, lines: List[str], start_idx: int = 0) -> List[Tuple[int, str]]:
        """Многострочный поиск для WHEN OTHERS без ROLLBACK/RAISE"""
        issues = []
        for i, line in enumerate(lines):
            if re.search(r'when\s+others\s+then', line, re.IGNORECASE):
                # Ищем следующие строки до END;
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
        """Поиск присваивания %id в NUMBER переменную"""
        issues = []
        # Сначала находим объявления NUMBER переменных
        number_vars = {}
        for i, line in enumerate(lines):
            match = re.search(r'(\w+)\s+NUMBER\s*;', line, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                number_vars[var_name] = i + 1
        
        # Затем ищем присваивания %id этим переменным
        for var_name, decl_line in number_vars.items():
            for i, line in enumerate(lines):
                if re.search(rf'{var_name}\s*:=\s*\w+%id', line, re.IGNORECASE):
                    issues.append((i + 1, line.strip()))
        return issues
    
    def _check_multiline_id_size(self, lines: List[str]) -> List[Tuple[int, str, int]]:
        """Поиск VARCHAR2(10) для ID бизнес-данных"""
        issues = []
        for i, line in enumerate(lines):
            # Ищем объявление VARCHAR2(10) или меньше
            match = re.search(r'(\w+)\s+(?:VARCHAR2|STRING)\s*\((\d+)\)\s*;', line, re.IGNORECASE)
            if match:
                size = int(match.group(2))
                if size < 20:
                    var_name = match.group(1)
                    # Ищем присваивание %id этой переменной
                    for j, next_line in enumerate(lines[i:], i):
                        if re.search(rf'{var_name}\s*:=\s*\w+%id', next_line, re.IGNORECASE):
                            issues.append((i + 1, line.strip(), size))
                            break
        return issues
    
    def _load_patterns_from_rubricator(self) -> Dict:
        """Загрузка паттернов из рубрикатора v3.3.0 с поддержкой AI-анализа"""
        patterns = {}
        ignore_patterns_map = {}
        self._rubricator_rules = {}  # Сохраняем полные правила для AI-анализа
        
        json_rubricator_path = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор' / '4.RUBRICATOR_PROMPTS.json'
        
        if json_rubricator_path.exists():
            try:
                # Пробуем разные кодировки: cp1251, utf-8-sig, utf-8
                for encoding in ['cp1251', 'utf-8-sig', 'utf-8']:
                    try:
                        with open(json_rubricator_path, 'r', encoding=encoding) as f:
                            data = json.load(f)
                        break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                else:
                    raise Exception("Не удалось прочитать файл в кодировке UTF-8 или CP1251")
                
                rules = data.get('rules', {})
                
                for rule_key, rule_data in rules.items():
                    file_code = rule_key.split('.')[0]
                    if self.selected_rules and file_code not in self.selected_rules:
                        continue
                    
                    regex_patterns = rule_data.get('regex_patterns', {}).get('for_search', [])
                    ignore_patterns = rule_data.get('regex_patterns', {}).get('for_ignore', [])
                    
                    if not regex_patterns:
                        continue
                    
                    category = rule_data.get('category', 'SQL')
                    tags = rule_data.get('plplus_references', [])
                    full_description = rule_data.get('documentation_text', '')
                    example_code = rule_data.get('code_example_bad', '')
                    example_fixed = rule_data.get('code_example_bad3', '') or rule_data.get('code_example_bad2', '') or ''
                    
                    if not example_fixed:
                        examples = rule_data.get('examples', {})
                        if examples:
                            example_key = list(examples.keys())[0]
                            example_fixed = examples[example_key].get('good', '')
                            example_code = examples[example_key].get('bad', '')
                    
                    # Сохраняем полное правило для AI-анализа
                    self._rubricator_rules[rule_key] = rule_data
                    
                    # Сохраняем ignore-паттерны отдельно
                    ignore_patterns_map[rule_key] = ignore_patterns
                    
                    for idx, pattern_info in enumerate(regex_patterns):
                        pattern = pattern_info.get('pattern', '')
                        description = pattern_info.get('description', '')
                        flags_str = pattern_info.get('flags', '')
                        
                        if not pattern:
                            continue
                        
                        unique_key = f"{rule_key}.[{idx}]"
                        
                        # Преобразуем флаги из строки в объект re
                        flags = 0
                        if 'i' in flags_str.lower():
                            flags |= re.IGNORECASE
                        
                        patterns[unique_key] = (pattern, description, category, tags, 
                                               full_description, example_code, example_fixed, '', flags)
                        
                if patterns:
                    print(f"[INFO] Загружено {len(patterns)} паттернов из JSON-рубрикатора")
                    # Сохраняем ignore-паттерны как атрибут сканера
                    self.ignore_patterns_map = ignore_patterns_map
                    return patterns
            except Exception as e:
                print(f"[!] Не удалось загрузить паттерны из JSON-рубрикатора: {e}")
        
        print(f"[INFO] Используется {len(self.DEFAULT_PATTERNS)} паттернов по умолчанию")
        self.ignore_patterns_map = {}
        return self.DEFAULT_PATTERNS
    
    def scan_file(self, file_path: Path, log_callback=None) -> List[Issue]:
        """Сканирование одного файла с поддержкой многострочных правил"""
        issues = []
        self.in_block_comment = False
        self.file_path = file_path
        
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
                    # Пропускаем если pattern_data не является tuple (некорректные данные)
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
                    
                    # Используем флаги из паттерна (по умолчанию re.IGNORECASE)
                    search_flags = flags if flags else re.IGNORECASE
                    code_matches = self._find_code_positions(original_line, pattern, search_flags)
                    
                    for match_start, match_end, matched_text in code_matches:
                        # Проверяем ignore-паттерны
                        is_ignored = False
                        ignore_list = self.ignore_patterns_map.get(base_issue_type, [])
                        
                        for ignore_pattern in ignore_list:
                            # Пропускаем если ignore_pattern не строка
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
            
            # 1. WHEN OTHERS без ROLLBACK/RAISE
            multiline_issues = self._check_multiline_when_others(self.lines, 0)
            for line_num, bad_code in multiline_issues:
                issue = Issue(
                    file_path=str(file_path.resolve()),
                    line_number=line_num,
                    issue_type='v50.PROC.WHENOTHERS.п.3.5',
                    description='WHEN OTHERS без ROLLBACK/RAISE',
                    original_code=bad_code[:200],
                    category='PROC',
                    rubricator_code='v50.PROC.WHENOTHERS.п.3.5',
                    rubricator_full_description='В PostgreSQL после ошибки транзакция прерывается.',
                    rubricator_example_code='exception when others then null;',
                    rubricator_example_fixed='exception when others then rollback; raise;',
                    tags=['exception', 'rollback', 'raise']
                )
                issues.append(issue)
                if log_callback:
                    log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено WHEN OTHERS без обработки в строке {line_num}", 'warning')
            
            # 2. NativeID: присваивание %id в NUMBER
            nativeid_issues = self._check_multiline_nativeid(self.lines)
            for line_num, bad_code in nativeid_issues:
                issue = Issue(
                    file_path=str(file_path.resolve()),
                    line_number=line_num,
                    issue_type='v50.PROC.NATIVEID.п.3.26',
                    description='NativeID для метаданных (NUMBER переменная для %id)',
                    original_code=bad_code[:200],
                    category='PROC',
                    rubricator_code='v50.PROC.NATIVEID.п.3.26',
                    rubricator_full_description='Идентификаторы операций и представлений стали строками, не числами.',
                    rubricator_example_code='v_id number; v_id := rMeth%id;',
                    rubricator_example_fixed='v_id varchar2(100); v_id := rMeth%id;',
                    tags=['nativeid', 'identifiers']
                )
                issues.append(issue)
                if log_callback:
                    log_callback(f"    [МНОГОСТРОЧНЫЙ] Найдено присваивание %id в NUMBER в строке {line_num}", 'warning')
            
            # ========== ФАЗА 2: AI-АНАЛИЗ СЛОЖНЫХ ПРАВИЛ ==========
            if self.ai_analyzer and hasattr(self, '_rubricator_rules'):
                if log_callback:
                    log_callback(f"\n  [AI-АНАЛИЗ] Анализ контекста для {len(self.ai_rules)} сложных правил...", 'info')
                
                # Собираем потенциальные проблемы для AI-анализа
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
                    
                    # Выполняем AI-анализ
                    ai_results = self.ai_analyzer.analyze_file(
                        file_path, self.lines, ai_candidates
                    )
                    
                    # Сохраняем результаты
                    self.ai_results.extend(ai_results)
                    
                    # Выводим результаты AI-анализа
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
        
        # Сохраняем найденные проблемы в общий список
        self.issues.extend(issues)
        return issues
    
    def scan_directory(self, log_callback=None) -> Dict[str, int]:
        """Сканирование всех .plp файлов"""
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
            # issues уже добавлены в self.issues внутри scan_file
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
        
        # ИТОГОВАЯ СТАТИСТИКА ПО ВСЕМ ФАЙЛАМ
        if log_callback:
            total_issues = len(self.issues)
            total_rules = len(stats)
            ai_count = len(self.ai_results)
            log_callback(f"\n{'=' * 70}", 'info')
            log_callback('ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ', 'info')
            log_callback(f'{'=' * 70}', 'info')
            log_callback(f'Всего файлов просканировано:    {files_scanned}', 'info')
            log_callback(f'Всего проблем найдено:         {total_issues}', 'info')
            log_callback(f'Всего видов кодов правил:      {total_rules}', 'info')
            if ai_count > 0:
                log_callback(f'Из них с AI-анализом:          {ai_count}', 'info')
            log_callback(f'{'=' * 70}', 'info')
            log_callback('Распределение по кодам правил (по убыванию):', 'info')
            log_callback(f'{'-' * 70}', 'info')
            for rule_code, count in sorted(stats.items(), key=lambda x: (-x[1], x[0])):
                log_callback(f'  {rule_code}: {count}', 'info')
            log_callback(f'{'=' * 70}', 'info')
        
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
        """Возвращает словарь с проблемами, сгруппированными по файлам
        
        Returns:
            Dict[str, List[Issue]]: ключ - путь к файлу, значение - список проблем
        """
        by_file = {}
        for issue in self.issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)
        return by_file
        
    def generate_report(self, output_path: Path):
        """Генерация отчёта"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        by_file = {}
        for issue in self.issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)
        
        total_by_type = {}
        for issue in self.issues:
            issue_type = issue.issue_type
            total_by_type[issue_type] = total_by_type.get(issue_type, 0) + 1
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Отчёт анализа PLPlus кода\n\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего найдено проблем: {len(self.issues)}\n")
            f.write(f"Всего файлов: {len(by_file)}\n\n")
            
            # ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ
            total_rules = len(total_by_type)
            f.write(f"{'=' * 70}\n")
            f.write("ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ\n")
            f.write(f"{'=' * 70}\n")
            f.write(f"Всего найдено проблем:          {len(self.issues)}\n")
            f.write(f"Всего файлов:                   {len(by_file)}\n")
            f.write(f"Всего видов кодов правил:       {total_rules}\n")
            f.write(f"{'=' * 70}\n")
            f.write("Распределение по кодам правил (по убыванию):\n")
            f.write(f"{'-' * 70}\n")
            for issue_type, count in sorted(total_by_type.items(), key=lambda x: (-x[1], x[0])):
                f.write(f"  {issue_type}: {count}\n")
            f.write(f"{'=' * 70}\n\n")
            
            f.write("---\n\n")
            
            # СЕКЦИЯ AI-АНАЛИЗА
            if self.ai_results:
                f.write("## Результаты AI-анализа сложных правил\n\n")
                f.write(f"**Всего проанализировано:** {len(self.ai_results)}\n\n")
                
                for result in self.ai_results:
                    f.write(f"### {result.rule_code}\n\n")
                    f.write(f"- **Приоритет:** {result.priority}\n")
                    f.write(f"- **Строка:** {result.line_number}\n")
                    f.write(f"- **Уверенность:** {result.confidence:.0%}\n")
                    f.write(f"- **Степени анализа:** {result.steps_summary}\n\n")
                    f.write(f"**Исходный код:**\n```plp\n{result.original_code}\n```\n\n")
                    f.write(f"**Обоснование:** {result.reasoning}\n\n")
                    f.write(f"**Предложенное исправление:**\n```plp\n{result.fixed_code}\n```\n\n")
                    f.write("---\n\n")
        
            for file_path, issues in sorted(by_file.items()):
                file_by_type = {}
                for issue in issues:
                    issue_type = issue.issue_type
                    file_by_type[issue_type] = file_by_type.get(issue_type, 0) + 1
                
                f.write(f"## Файл: {file_path}\n\n")
                f.write(f"**Всего проблем в файле:** {len(issues)}\n\n")
                
                f.write("**Проблемы по типам**:\n\n")
                for issue_type, count in sorted(file_by_type.items(), key=lambda x: (-x[1], x[0])):
                    f.write(f"- {issue_type}: {count}\n")
                f.write("\n---\n\n")
                
                for issue in issues:
                    f.write(f"### Строка {issue.line_number}\n\n")
                    f.write(f"**Проблема:** {issue.issue_type} - {issue.description}\n\n")
                    f.write(f"```plp\n{issue.original_code}\n```\n\n")
                    
                    # Попытка автоматического исправления
                    fixed_code = issue.original_code
                    if issue.issue_type == 'v50.SQL.OUTERJOIN.п.1.1':
                        fixed_code = re.sub(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)\(\+\)', 
                                            r'\1 left join \3 on \1.\2 = \3.\4', 
                                            issue.original_code, flags=re.IGNORECASE)
                    elif 'ROWNUM' in issue.issue_type:
                        fixed_code = re.sub(r'rownum\s*=\s*(\d+)', r'fetch first \1 rows only', 
                                            issue.original_code, flags=re.IGNORECASE)
                        fixed_code = re.sub(r'rownum\s*<=\s*(\d+)', r'fetch first \1 rows only', 
                                            fixed_code, flags=re.IGNORECASE)
                    elif 'EMPTY_STRING' in issue.issue_type:
                        fixed_code = re.sub(r"=\s*''", 'is null', issue.original_code)
                        fixed_code = re.sub(r":=\s*''", ':= null', fixed_code)
                    elif 'EXECUTE' in issue.issue_type:
                        fixed_code = re.sub(r"(Z#\w+)", r'"\1"', issue.original_code)
                    
                    f.write(f"**Было  :** `{issue.original_code}`\n")
                    f.write(f"**Станет:** `{fixed_code}`\n\n")
                    f.write("---\n\n")
        
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


def main():
    """Запуск сканера"""
    config_path = Path(__file__).parent.parent / 'settings.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if 'paths' not in config:
        config['paths'] = {
            'source_dir': config.get('source_dir', ''),
            'results_dir': config.get('result_dir', ''),
            'logs_dir': str(Path(__file__).parent.parent / 'logs')
        }
    if 'scan' not in config:
        config['scan'] = {
            'recursive': config.get('recursive', True),
            'file_pattern': config.get('file_pattern', '**/*.plp'),
            'exclude_patterns': ['.v????', '.bak', '.tmp']
        }
    if 'logging' not in config:
        config['logging'] = {
            'level': config.get('log_level', 'Минимальный')
        }
    
    for key in ['source_dir', 'results_dir', 'logs_dir']:
        if key in config['paths']:
            path_str = config['paths'][key]
            if len(path_str) >= 2 and path_str[1] == ':':
                config['paths'][key] = path_str[0].upper() + path_str[1:]
    
    scanner = PLPlusScanner(config)
    stats = scanner.scan_directory()
    
    output_path = Path(config['paths']['logs_dir']) / f'scan_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    scanner.generate_report(output_path)
    
    # Вывод итоговой статистики в консоль
    total_issues = stats['total_issues']
    total_rules = len(stats['by_type'])
    print(f"\n{'=' * 70}")
    print('ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ')
    print(f'{'=' * 70}')
    print(f'Всего файлов просканировано:    {stats["files_scanned"]}')
    print(f'Всего проблем найдено:         {total_issues}')
    print(f'Всего видов кодов правил:      {total_rules}')
    print(f'{'=' * 70}')
    print('Распределение по кодам правил (по убыванию):')
    print(f'{'-' * 70}')
    for rule_code, count in sorted(stats['by_type'].items(), key=lambda x: (-x[1], x[0])):
        print(f'  {rule_code}: {count}')
    print(f'{'=' * 70}')
    
    print(f"\nРезультаты сканирования:")
    print(f"  Файлов: {stats['files_scanned']}")
    print(f"  Проблем: {stats['total_issues']}")
    print(f"  Отчёт: {output_path}")


if __name__ == '__main__':
    main()