#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Scanner — Альтернативный алгоритм сканирования для АРМ "Адаптация под DBI"
Полностью независимый модуль. Может запускаться:
  • Из командной строки:  python analyzer/deep_scanner.py -s <каталог>
  • Из АРМ:               DeepScanner(...).run()

Режим DeepThink: при включении выводит детальную информацию о поиске паттернов
"""
import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class DeepScanner:
    """Независимый сканер (Алгоритм Deep)"""

    def __init__(self,
                 source_dir: str,
                 result_dir: str = None,
                 file_pattern: str = "**/*.plp",
                 recursive: bool = True,
                 log_level: str = "Минимальный",
                 selected_rules: list = None,
                 rubricator_dir: str = None,
                 rubricator_loaded: bool = False,
                 deep_think: bool = False,
                 log_callback=None,
                 progress_callback=None,
                 status_callback=None):
        self.source_dir = Path(source_dir) if source_dir else None
        self.result_dir = Path(result_dir) if result_dir else None
        self.file_pattern = file_pattern if file_pattern and file_pattern not in ['*', '*.*'] else '**/*.plp'
        self.recursive = recursive
        self.log_level = log_level
        self.selected_rules = selected_rules or []
        self.rubricator_loaded = rubricator_loaded
        self.deep_think = deep_think  # Режим детальной отладки

        # Каталог рубрикатора: по умолчанию относительно проекта
        if rubricator_dir:
            self.rubricator_dir = Path(rubricator_dir)
        else:
            self.rubricator_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор'

        # Callback'и (для GUI — передаются извне, для CLI — print/pass)
        self.log_cb = log_callback or self._default_log
        self.progress_cb = progress_callback or self._default_progress
        self.status_cb = status_callback or self._default_status

        self.rubricator_files: Dict[str, str] = {}
        self.rubricator_fixes: Dict[str, Dict] = {}
        self._load_rubricator_files()
        self._load_rubricator_fixes()

    # ───────────────────────────────────────────────
    # Callback-заглушки для консольного режима
    # ───────────────────────────────────────────────
    @staticmethod
    def _default_log(message: str, level: str = 'info'):
        ts = datetime.now().strftime('%H:%M:%S')
        prefix = {'error': '[ERROR]', 'warning': '[WARN]', 'success': '[OK]', 'debug': '[DEBUG]', 'info': ''}.get(level, '')
        if prefix:
            print(f"[{ts}] {prefix} {message}")
        else:
            print(f"[{ts}] {message}")

    @staticmethod
    def _default_progress(percent: int):
        pass

    @staticmethod
    def _default_status(message: str):
        print(f"STATUS: {message}")

    # ───────────────────────────────────────────────
    # Внутренние утилиты
    # ───────────────────────────────────────────────
    def log(self, message: str, level: str = 'info'):
        self.log_cb(message, level)

    def log_deep_think(self, message: str):
        """Вывод в режиме DeepThink"""
        if self.deep_think:
            self.log(f"[DEEP_THINK] {message}", 'debug')

    def _log_separator(self, title: str = None):
        sep = "=" * 80
        if title:
            self.log(sep, 'info')
            self.log(title, 'info')
            self.log(sep, 'info')
        else:
            self.log(sep, 'info')

    def set_progress(self, value: int):
        self.progress_cb(value)

    def set_status(self, message: str):
        self.status_cb(message)

    def _load_rubricator_files(self):
        """Загрузка 1.RUBRICATOR_FILES.md"""
        try:
            file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or line.startswith('|---'):
                            continue
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 5:
                            code = parts[3]
                            name = parts[4]
                            if code and not code.startswith('N') and not code.startswith('№'):
                                self.rubricator_files[code] = name
        except Exception as e:
            self.log(f"[!] Не удалось загрузить список файлов рубрикатора: {e}", 'warning')

    def _load_rubricator_fixes(self):
        """Загрузка 3.RUBRICATOR_FIXES.md с правилами исправлений"""
        try:
            file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                in_table = False
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Пропускаем заголовок таблицы и разделитель
                    if '|-|' in line or 'Коды Файла' in line:
                        in_table = True
                        continue
                    
                    if in_table and line.startswith('|'):
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 9:
                            # |N|++|Код|Пункт/Стр.|Теги|Короткое описание|Подробное описание|Пример кода|Пример исправленного
                            # [0, 1,  2,  3,         4,    5,              6,                7,          8]
                            plus_plus = parts[1].strip() if len(parts) > 1 else ''
                            # Пропускаем отключённые исправления (1-й символ "-")
                            if plus_plus and plus_plus[0] == '-':
                                continue
                        
                            code = parts[2].strip() if len(parts) > 2 else ''
                            tags_str = parts[4].strip() if len(parts) > 4 else ''
                            short_desc = parts[5].strip() if len(parts) > 5 else ''
                            full_desc = parts[6].strip() if len(parts) > 6 else ''
                            example_code = parts[7].strip() if len(parts) > 7 else ''
                            example_fixed = parts[8].strip() if len(parts) > 8 else ''
                            
                            # Парсим теги
                            tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []
                            
                            if code and code not in ('N', '№', ''):
                                self.rubricator_fixes[code] = {
                                    'code': code,
                                    'short_description': short_desc,
                                    'full_description': full_desc,
                                    'example_code': example_code,
                                    'example_fixed': example_fixed,
                                    'tags': tags,
                                    'parsed': self._parse_rule_code(code)
                                }
        except Exception as e:
            self.log(f"[!] Не удалось загрузить правила рубрикатора: {e}", 'warning')
            self._generate_default_rules()

    def _parse_rule_code(self, code: str) -> Dict:
        """Разбор кода правила: v50.SQL.OUTERJOIN.п.1.1 или тдс20240828.STOR.DATE.стр.8"""
        parts = code.split('.')
        result = {
            'file_code': parts[0] if len(parts) > 0 else '',
            'category': parts[1] if len(parts) > 1 else '',
            'rule_name': parts[2] if len(parts) > 2 else '',
            'reference': parts[3] if len(parts) > 3 else ''
        }
        return result

    def _generate_default_rules(self):
        """Генерация правил по умолчанию, если рубрикатор не загружен"""
        self.rubricator_fixes = {
            'v50.SQL.OUTERJOIN.п.1.1': {
                'code': 'v50.SQL.OUTERJOIN.п.1.1',
                'short_description': 'Замена (+) на LEFT/RIGHT JOIN',
                'full_description': 'В Oracle используется оператор (+) для внешнего соединения. В PostgreSQL и ANSI SQL его нет. Заменить на явные LEFT JOIN или RIGHT JOIN с условием ON.',
                'example_code': 'select * from t1, t2 where t1.id = t2.id(+)',
                'example_fixed': 'select * from t1 left join t2 on t1.id = t2.id',
                'tags': ['outer join', 'oracle', 'ansi'],
                'parsed': {'file_code': 'v50', 'category': 'SQL', 'rule_name': 'OUTERJOIN', 'reference': 'п.1.1'}
            },
            'v50.SQL.ROWNUM.п.1.2': {
                'code': 'v50.SQL.ROWNUM.п.1.2',
                'short_description': 'Замена rownum на FETCH FIRST',
                'full_description': 'Псевдоколонка rownum не поддерживается в PostgreSQL. Использовать FETCH FIRST N ROWS ONLY. Для сдвига выборки использовать OFFSET ON.',
                'example_code': 'select * from t where rownum = 1',
                'example_fixed': 'select * from t fetch first 1 rows only',
                'tags': ['rownum', 'limit', 'offset'],
                'parsed': {'file_code': 'v50', 'category': 'SQL', 'rule_name': 'ROWNUM', 'reference': 'п.1.2'}
            },
            'v50.STOR.DATE.п.2.2': {
                'code': 'v50.STOR.DATE.п.2.2',
                'short_description': 'Замена DATE на DATE_TIME',
                'full_description': 'В PostgreSQL тип DATE не хранит время. Использовать тип DATE_TIME (timestamp(0)). Для арифметики применять INTERVAL.',
                'example_code': 'DateTimeEnd date;',
                'example_fixed': 'DateTimeEnd date_time;',
                'tags': ['date', 'type', 'timestamp'],
                'parsed': {'file_code': 'v50', 'category': 'STOR', 'rule_name': 'DATE', 'reference': 'п.2.2'}
            },
            'v50.SQL.DECODE.п.1.6.1': {
                'code': 'v50.SQL.DECODE.п.1.6.1',
                'short_description': 'Замена DECODE на CASE',
                'full_description': 'Функция DECODE специфична для Oracle. Заменять на ANSI-конструкцию CASE WHEN ... THEN ... ELSE ... END.',
                'example_code': "select decode(status,1,'A',2,'B','?') from t",
                'example_fixed': "select case status when 1 then 'A' when 2 then 'B' else '?' end from t",
                'tags': ['decode', 'case', 'conditional'],
                'parsed': {'file_code': 'v50', 'category': 'SQL', 'rule_name': 'DECODE', 'reference': 'п.1.6.1'}
            },
            'v50.SQL.CONNECTBY.п.1.8': {
                'code': 'v50.SQL.CONNECTBY.п.1.8',
                'short_description': 'Замена CONNECT BY на WITH RECURSIVE',
                'full_description': 'Иерархические запросы с CONNECT BY не поддерживаются. Использовать рекурсивные CTE: WITH RECURSIVE.',
                'example_code': 'select * from t connect by prior id = parent_id',
                'example_fixed': 'with recursive t as (select * from t where parent_id is null union all select t2.* from t t1 join t t2 on t1.id = t2.parent_id) select * from t',
                'tags': ['hierarchical', 'connect by', 'cte'],
                'parsed': {'file_code': 'v50', 'category': 'SQL', 'rule_name': 'CONNECTBY', 'reference': 'п.1.8'}
            },
            'v50.PROC.WHENOTHERS.п.3.5': {
                'code': 'v50.PROC.WHENOTHERS.п.3.5',
                'short_description': 'WHEN OTHERS без ROLLBACK/RAISE',
                'full_description': 'В PostgreSQL после ошибки транзакция прерывается. В WHEN OTHERS обязательно делать ROLLBACK (до savepoint) или RAISE.',
                'example_code': 'exception when others then null;',
                'example_fixed': 'exception when others then rollback; raise;',
                'tags': ['exception', 'rollback', 'raise'],
                'parsed': {'file_code': 'v50', 'category': 'PROC', 'rule_name': 'WHENOTHERS', 'reference': 'п.3.5'}
            },
        }

    def _is_rule_selected(self, rule_code: str) -> bool:
        """Проверка, выбрано ли правило пользователем"""
        if not self.selected_rules:
            return True
        for selected in self.selected_rules:
            if selected in rule_code or rule_code.startswith(selected):
                return True
        return False

    def load_rubricator(self):
        """Вывод содержимого рубрикатора в лог (аналог load_rubricator_on_start)"""
        self.set_status("Загрузка рубрикатора...")
        self.log("Загрузка рубрикатора...", 'info')

        if not self.rubricator_dir.exists():
            self.log(f"[!] Каталог рубрикатора не найден: {self.rubricator_dir}", 'error')
            self.set_status("Готово")
            return

        for fname, lines_cnt in [('1.RUBRICATOR_FILES.md', 30),
                                 ('2.RUBRICATOR_CATEGORIES.md', 30),
                                 ('3.RUBRICATOR_FIXES.md', 50)]:
            fpath = self.rubricator_dir / fname
            if fpath.exists():
                self.log(f"# {fpath}", 'info')
                with open(fpath, 'r', encoding='utf-8') as f:
                    for line in list(f)[:lines_cnt]:
                        self.log(line.rstrip(), 'info')
                self.log("", 'info')

        # Вывод выбранных правил
        self.log("ВЫБРАННЫЕ ПРАВИЛА:", 'info')
        selected_count = 0
        for code, fix in self.rubricator_fixes.items():
            if self._is_rule_selected(code):
                selected_count += 1
                tags_str = ', '.join(fix.get('tags', []))[:40]
                self.log(f"  [+] {code}: {fix['short_description']} [{tags_str}]", 'info')
        self.log(f"\nВсего выбрано правил: {selected_count}", 'info')

        self.rubricator_loaded = True
        self.log("Рубрикатор загружен успешно", 'success')
        self.set_status("Готово")

    # ───────────────────────────────────────────────
    # Получение паттернов для сканера
    # ───────────────────────────────────────────────
    def _get_pattern_for_rule(self, rule_code: str, rule_info: Dict) -> Optional[tuple]:
        """Получение regex-паттерна для правила"""
        parsed = rule_info.get('parsed', {})
        rule_name = parsed.get('rule_name', '').upper()
        reference = parsed.get('reference', '')
        tags = rule_info.get('tags', [])
        short_desc = rule_info.get('short_description', '')
        full_desc = rule_info.get('full_description', short_desc)  # По умолчанию короткое описание
        example_code = rule_info.get('example_code', '')
        example_fixed = rule_info.get('example_fixed', '')
        
        self.log_deep_think(f"Анализ правила: {rule_code}")
        self.log_deep_think(f"  rule_name: {rule_name}, reference: {reference}")
        
        # DATE правило: особый паттерн для поиска объявления типа DATE
        if 'DATE' in rule_name and ('п.2.2' in reference or 'п.2.2' in rule_code):
            pattern = r'(?<!\[)\bdate\b(?!\s*\[)'
            self.log_deep_think(f"  -> DATE правило. Паттерн: {pattern}")
            self.log_deep_think(f"  -> Описание: {short_desc}")
            return (pattern, short_desc, 'PL/SQL', tags, full_desc, example_code, example_fixed)
        
        # OUTER JOIN
        if 'OUTERJOIN' in rule_name:
            pattern = r'\(\+\)'
            self.log_deep_think(f"  -> OUTERJOIN правило. Паттерн: {pattern}")
            return (pattern, short_desc, 'SQL', tags, full_desc, example_code, example_fixed)
        
        # ROWNUM
        if 'ROWNUM' in rule_name:
            pattern = r'\bROWNUM\b'
            self.log_deep_think(f"  -> ROWNUM правило. Паттерн: {pattern}")
            return (pattern, short_desc, 'SQL', tags, full_desc, example_code, example_fixed)
        
        # DECODE
        if 'DECODE' in rule_name:
            pattern = r'\bDECODE\s*\('
            self.log_deep_think(f"  -> DECODE правило. Паттерн: {pattern}")
            return (pattern, short_desc, 'SQL', tags, full_desc, example_code, example_fixed)
        
        # CONNECT BY
        if 'CONNECTBY' in rule_name or 'CONNECT' in rule_name:
            pattern = r'\bCONNECT\s+BY\b'
            self.log_deep_think(f"  -> CONNECT BY правило. Паттерн: {pattern}")
            return (pattern, short_desc, 'SQL', tags, full_desc, example_code, example_fixed)
        
        # WHEN OTHERS
        if 'WHENOTHERS' in rule_name:
            pattern = r'WHEN\s+OTHERS'
            self.log_deep_think(f"  -> WHEN OTHERS правило. Паттерн: {pattern}")
            return (pattern, short_desc, 'PL/SQL', tags, full_desc, example_code, example_fixed)
        
        self.log_deep_think(f"  -> Нет соответствия для правила {rule_code}")
        return None

    def _get_selected_patterns(self) -> Dict:
        """Получение паттернов только для выбранных правил"""
        patterns = {}
        self.log_deep_think("=" * 60)
        self.log_deep_think("ГЕНЕРАЦИЯ ПАТТЕРНОВ ДЛЯ ВЫБРАННЫХ ПРАВИЛ")
        self.log_deep_think("=" * 60)
        
        for code, fix in self.rubricator_fixes.items():
            if self._is_rule_selected(code):
                pattern = self._get_pattern_for_rule(code, fix)
                if pattern:
                    patterns[code] = pattern
                    self.log_deep_think(f"✓ Добавлен паттерн для {code}")
                else:
                    self.log_deep_think(f"✗ Не удалось создать паттерн для {code}")
        
        self.log_deep_think(f"\nВсего паттернов: {len(patterns)}")
        return patterns

    # ───────────────────────────────────────────────
    # Сканирование с детальным выводом
    # ───────────────────────────────────────────────
    def scan_file_with_details(self, scanner, file_path: Path) -> List:
        """Сканирование файла с детальным выводом для отладки"""
        issues = []
        date_pattern_code = 'v50.STOR.DATE.п.2.2'
        
        self.log_deep_think(f"\n--- Сканирование файла: {file_path.name} ---")
        
        try:
            # Чтение файла с автоматическим определением кодировки
            from utils.encoding_utils import read_file_with_encoding
            try:
                content, used_encoding = read_file_with_encoding(file_path)
                lines = content.splitlines(keepends=True)
                self.log_deep_think(f"  Кодировка файла: {used_encoding}")
            except Exception as encoding_err:
                self.log_deep_think(f"  Ошибка определения кодировки: {encoding_err}, пробуем UTF-8")
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                original_line = line.rstrip('\n')
                stripped = original_line.strip()
                
                # Пропускаем пустые строки и комментарии
                if not stripped or stripped.startswith('--'):
                    continue
                
                # Специальная обработка для DATE правила
                if date_pattern_code in scanner.PATTERNS:
                    pattern_data = scanner.PATTERNS[date_pattern_code]
                    if len(pattern_data) >= 3:
                        pattern, desc, category = pattern_data[:3]
                    else:
                        continue
                    
                    # Ищем совпадения
                    for match in re.finditer(pattern, original_line, re.IGNORECASE):
                        match_start = match.start()
                        match_end = match.end()
                        matched_text = match.group()
                        
                        # Проверяем, не внутри ли комментария
                        if '--' in original_line[:match_start]:
                            comment_pos = original_line[:match_start].rfind('--')
                            before_comment = original_line[:comment_pos].count("'") % 2 == 0
                            if before_comment:
                                self.log_deep_think(f"  Строка {line_num}: Пропущено (в комментарии)")
                                continue
                        
                        # Проверяем, что это объявление переменной
                        after = original_line[match_end:].strip()
                        is_declaration = after.startswith(';') or after.startswith(':=') or not after
                        
                        if is_declaration:
                            self.log(f"[DEBUG] Строка {line_num}: найдено '{matched_text}' -> {desc}", 'debug')
                            self.log_deep_think(f"  Строка {line_num}: '{original_line[:100]}'")
                            self.log_deep_think(f"    Паттерн: {pattern}")
                            self.log_deep_think(f"    Совпадение: '{matched_text}' на позиции {match_start}-{match_end}")
                            self.log_deep_think(f"    Контекст после: '{after[:30]}'")
                            self.log_deep_think(f"    РЕЗУЛЬТАТ: НАЙДЕНО!")
                            
                            issues.append(scanner._create_issue(
                                str(file_path.relative_to(self.source_dir) if self.source_dir in file_path.parents else str(file_path)),
                                line_num,
                                date_pattern_code,
                                desc,
                                stripped[:200],
                                category,
                                matched_text
                            ))
                        else:
                            self.log_deep_think(f"  Строка {line_num}: найдено '{matched_text}', но не объявление переменной (after='{after[:20]}')")
        
        except Exception as e:
            self.log(f"Ошибка при чтении {file_path}: {e}", 'error')
        
        return issues

    # ───────────────────────────────────────────────
    # Основной алгоритм
    # ───────────────────────────────────────────────
    def run(self):
        """Запуск Deep-сканирования"""
        if not self.source_dir or not self.source_dir.exists():
            raise ValueError(f"Укажите корректный исходный каталог! {self.source_dir}")

        self.set_progress(0)
        self.set_status("Сканирование (Deep)...")
        self._log_separator("НАЧАЛО СКАНИРОВАНИЯ (Алгоритм Deep)")

        # Конфигурация для PLPlusScanner
        config = {
            'paths': {
                'source_dir': str(self.source_dir),
                'results_dir': str(self.result_dir) if self.result_dir else '',
                'logs_dir': str(Path(__file__).parent.parent.parent / 'logs_Deep')
            },
            'scan': {
                'recursive': self.recursive,
                'file_pattern': self.file_pattern,
                'exclude_patterns': ['.v????', '.bak', '.tmp']
            },
            'logging': {
                'level': self.log_level
            }
        }

        # Получаем паттерны для выбранных правил
        patterns = self._get_selected_patterns()
        
        self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА Deep ({len(patterns)}):", 'info')
        for code in patterns.keys():
            self.log(f"  [+] {code}", 'info')

        if not self.rubricator_loaded:
            self.load_rubricator()

        self.set_progress(5)

        # Импорт здесь, чтобы модуль можно было импортировать без зависимостей
        from analyzer.scanner import PLPlusScanner
        
        # Создаём сканер с пользовательскими паттернами
        scanner = PLPlusScanner(config, list(patterns.keys()))
        
        # Добавляем метод _create_issue, если его нет
        if not hasattr(scanner, '_create_issue'):
            def _create_issue(self, file_path, line_num, issue_type, description, original_code, category, match_text=''):
                from analyzer.scanner import Issue
                return Issue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type=issue_type,
                    description=description,
                    original_code=original_code,
                    category=category
                )
            scanner._create_issue = _create_issue.__get__(scanner)
        
        scanner.PATTERNS = patterns

        self.set_progress(10)
        self.set_status("Сканирование файлов...")
        
        # Поиск файлов
        if self.recursive:
            file_finder = self.source_dir.rglob
        else:
            file_finder = self.source_dir.glob
        
        files_scanned = 0
        total_issues = 0
        issues_by_type = {}
        issues_list = []
        
        for plp_file in file_finder(self.file_pattern):
            # Проверка расширения: только .plp файлы
            if plp_file.suffix.lower() != '.plp':
                continue
            
            # Проверка исключений
            exclude = False
            for pattern in config['scan']['exclude_patterns']:
                if pattern in str(plp_file):
                    exclude = True
                    break
            if exclude:
                continue
            
            files_scanned += 1
            self.log_deep_think(f"\n[{files_scanned}] Обработка: {plp_file.name}")
            
            # Используем сканер для всех правил (включая DATE)
            file_issues = scanner.scan_file(plp_file)
            
            for issue in file_issues:
                issues_list.append(issue)
                total_issues += 1
                issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1
            
            self.set_progress(min(10 + int(50 * files_scanned / max(1, files_scanned)), 60))
        
        self.log(f"\n[Deep 1/3] Сканирование файлов...", 'info')
        self.log(f"  Найдено *.plp файлов: {files_scanned}", 'info')
        self.log(f"  Проблемных конструкций: {total_issues}", 'info')
        
        if self.deep_think and total_issues > 0:
            self.log_deep_think(f"\n=== ДЕТАЛИ НАЙДЕННЫХ ПРОБЛЕМ ===")
            for issue in issues_list:
                self.log_deep_think(f"  {issue.file_path}:{issue.line_number} -> {issue.issue_type}")

        self.set_progress(70)
        self.set_status("Генерация отчёта...")

        # Генерация отчёта вручную
        source_name = self.source_dir.name
        logs_dir = Path(config['paths']['logs_dir'])
        logs_dir.mkdir(parents=True, exist_ok=True)
        output_path = logs_dir / f'Deep_scan_report_{source_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Отчёт Deep Scanner\n\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Исходный каталог: {self.source_dir}\n")
            f.write(f"Всего найдено проблем: {total_issues}\n\n")
            
            for issue_type, count in issues_by_type.items():
                f.write(f"## {issue_type}: {count} проблем\n")
                for issue in issues_list:
                    if issue.issue_type == issue_type:
                        f.write(f"- `{issue.file_path}`:{issue.line_number}\n")
                        f.write(f"  ```\n  {issue.original_code}\n  ```\n")
                f.write("\n")

        self.log(f"\n[Deep 2/3] Результаты сканирования:", 'info')
        self.log(f"  Найдено *.plp файлов: {files_scanned}", 'info')
        self.log(f"  Проблемных конструкций: {total_issues}", 'info')

        self.log(f"\n[Deep 3/3] Проблемы по типам:", 'info')
        for issue_type, count in issues_by_type.items():
            pattern_data = patterns.get(issue_type, (None, issue_type, None, None))
            short_desc = pattern_data[1] if len(pattern_data) > 1 else issue_type
            self.log(f"  {issue_type}: {count} ({short_desc})", 'info')

        self.log(f"\nОтчёт Deep сохранён: {output_path}", 'success')

        self.set_progress(100)
        self._log_separator("СКАНИРОВАНИЕ (Алгоритм Deep) ЗАВЕРШЕНО УСПЕШНО")
        self.set_status("Готово")

        return {'files_scanned': files_scanned, 'total_issues': total_issues, 'by_type': issues_by_type}, output_path


# ═══════════════════════════════════════════════════
# Точка входа для запуска из командной строки
# ═══════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description='Deep Scanner — Альтернативный алгоритм сканирования PLPlus для DBI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python analyzer/deep_scanner.py -s F:/TO_DBI/DATA/patch_WORK
  python analyzer/deep_scanner.py -s F:/TO_DBI/DATA/patch_WORK --rules v50
  python analyzer/deep_scanner.py -s F:/TO_DBI/DATA/patch_WORK --deep-think
        """
    )
    parser.add_argument('-s', '--source_dir', required=True,
                        help='Исходный каталог для сканирования')
    parser.add_argument('-r', '--result_dir', default='',
                        help='Каталог результатов (опционально)')
    parser.add_argument('-p', '--pattern', default='**/*.plp',
                        help='Шаблон файлов (по умолчанию: **/*.plp)')
    parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                        help='Не сканировать подкаталоги')
    parser.add_argument('-l', '--log_level', default='Подробный',
                        choices=['Минимальный', 'Подробный'],
                        help='Уровень логирования')
    parser.add_argument('--rubricator_dir', default='',
                        help='Каталог рубрикатора (по умолчанию: ../DATA/Рубрикатор)')
    parser.add_argument('--rules', nargs='+', default=None,
                        help='Коды выбранных правил (например: v50 тдс20240828)')
    parser.add_argument('--deep-think', action='store_true',
                        help='Включить режим детальной отладки DeepThink')

    args = parser.parse_args()

    # Нормализация путей: буква диска в верхнем регистре
    source_dir = args.source_dir
    if len(source_dir) >= 2 and source_dir[1] == ':':
        source_dir = source_dir[0].upper() + source_dir[1:]
    
    result_dir = args.result_dir
    if result_dir and len(result_dir) >= 2 and result_dir[1] == ':':
        result_dir = result_dir[0].upper() + result_dir[1:]
    
    # Преобразуем rules в список, если указаны
    selected_rules = args.rules if args.rules else ['v50']

    scanner = DeepScanner(
        source_dir=source_dir,
        result_dir=result_dir or None,
        file_pattern=args.pattern,
        recursive=args.recursive,
        log_level=args.log_level,
        selected_rules=selected_rules,
        rubricator_dir=args.rubricator_dir or None,
        rubricator_loaded=False,
        deep_think=args.deep_think
    )

    try:
        scanner.run()
    except Exception as e:
        print(f"\nОШИБКА: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()