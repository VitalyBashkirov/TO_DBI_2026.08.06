#!/usr/bin/env python3
"""
Автоматическое исправление проблемных конструкций PLPlus
Версия: v05 (с рубрикатором, игнорирование комментариев и строк)
"""
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from analyzer.scanner import PLPlusScanner, Issue
from fixer.markdown_rubricator_loader_v3 import MarkdownRubricatorLoaderV3
from analyzer.sql_parser import apply_fix as sql_apply_fix
import logging

logger = logging.getLogger(__name__)


class PLPlusFixer:
    """Исправлятель проблемных конструкций PLPlus"""
    
    def __init__(self, config: dict, iteration: str = 'v0001', use_rubricator: bool = True):
        self.config = config
        self.iteration = iteration
        self.changes_log: List[dict] = []
        self.stats = {}
        self.fixed_issues: List[dict] = []  # Детали всех исправлений
        self.rubricator: Optional[MarkdownRubricatorLoaderV3] = None
        self.fix_descriptions = {}  # Краткие описания из рубрикатора
        self.in_block_comment = False  # Состояние: внутри многострочного комментария /* */
        self.skipped_in_comment = 0  # Счётчик пропущенных из-за комментариев
        self.skipped_in_string = 0  # Счётчик пропущенных из-за строк
        self.skipped_details = []  # Детали пропущенных исправлений для подробного лога
        
        # Загрузка рубрикатора для получения кратких описаний
        if use_rubricator:
            try:
                rubricator_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор'
                self.rubricator = MarkdownRubricatorLoaderV3(str(rubricator_dir))
                self._load_fix_descriptions()
            except Exception as e:
                print(f"[!] Не удалось загрузить рубрикатор: {e}")
                print("Используется резервный набор правил")
        
        self.FIXES = self._get_default_fixes()
    
    def _load_fix_descriptions(self):
        """Загрузка кратких описаний из рубрикатора v3.0.0"""
        if not self.rubricator:
            return
        
        for rule in self.rubricator.get_enabled_rules():
            # Сохраняем краткое описание
            short_desc = rule.short_description
            self.fix_descriptions[rule.code] = short_desc
    
    def _get_default_fixes(self) -> Dict:
        """Резервный набор правил (если рубрикатор недоступен)"""
        return {
            # v50 - Формат сканера
            'v50.SQL.ROWNUM.п.1.2': [
                (r'WHERE\s+ROWNUM\s*=\s*1\b', 'FETCH FIRST 1 ROWS ONLY', True, 'v50.SQL.ROWNUM.п.1.2'),
                (r'WHERE\s+ROWNUM\s*<=\s*(\d+)', r'FETCH FIRST \1 ROWS ONLY', True, 'v50.SQL.ROWNUM.п.1.2'),
            ],
            'v50.STOR.DATE.п.2.2': [
                # Замена типа DATE на DATE_TIME (только bare date, не [DATE])
                (r'(?<!\[)\bdate\b', 'DATE_TIME', True, 'v50.STOR.DATE.п.2.2'),
            ],
            'v50.PROC.WHENOTHERS.п.3.5': [
                (r'(exception\s+when\s+others\s+then)\s*(null;)?', 
                 r'\1\n    ROLLBACK;\n    RAISE;', False, 'v50.PROC.WHENOTHERS.п.3.5'),
            ],
            'v50.SQL.OUTERJOIN.п.1.1': [
                # Паттерн для Oracle (+) - замена на LEFT JOIN (простая замена, требует ручного уточнения)
                (r'\(\+\)', 'LEFT JOIN', True, 'v50.SQL.OUTERJOIN.п.1.1'),
                # Паттерны для конструкций с (true) - удаление (true) с инструкцией по преобразованию в LEFT JOIN
                (r'(\w+)%?(\w+)\s*=\s*(\w+)\s*\.\s*\[(\w+)\]\s*\(true\)', r'--<ВАЖНО: преобразовать в LEFT JOIN: left join [TABLE] \3 on \1=\3.\4>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
                # collection_id(true) и подобные без квадратных скобок
                (r'(\w+)\s*\.\s*(\w+)\s*\(true\)', r'--<ВАЖНО: преобразовать в LEFT JOIN: left join [TABLE] \1 on условие>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
                # [REF](true) - с квадратными скобками
                (r'(\w+)\s*\.\s*\[(\w+)\]\s*\(true\)', r'\1.[\2] --<ВАЖНО: добавить LEFT JOIN вручную>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
                # &collection(true)
                (r'&collection\s*\(true\)', r'&collection --<ВАЖНО: добавить LEFT JOIN вручную>', False, 'v50.SQL.OUTERJOIN.п.1.1'),
            ],
            'v50.SQL.DECODE.п.1.6.1': [
                (r'\bDECODE\s*\(', 'CASE WHEN', True, 'v50.SQL.DECODE.п.1.6.1'),
            ],
            'v50.SQL.CONNECTBY.п.1.8': [
                (r'\bCONNECT\s+BY\b', 'WITH RECURSIVE', True, 'v50.SQL.CONNECTBY.п.1.8'),
            ],
            # тдс20240828
            'тдс20240828.п.1': [
                (r'\bSYSDATE\b', 'SYSTEM.OP_DATE', False, 'тдс20240828.п.1'),
            ],
            'тдс20240828.п.2': [
                (r'\bUSER\b(?!\s+FROM)', 'STDLIB.USERID', False, 'тдс20240828.п.2'),
            ],
            # тклоик20240828
            'тклоик20240828.КОДИРОВАНИЕ.п.3': [
                (r'\bVARCHAR\b(?!\d)', 'VARCHAR2', False, 'тклоик20240828.КОДИРОВАНИЕ.п.3'),
            ],
        }
    
    def _is_in_comment_or_string(self, line: str, match_start: int, match_end: int) -> bool:
        """
        Проверка, находится ли найденное совпадение в комментарии или строковом литерале.
        
        Варианты, которые нужно игнорировать:
        1. -- DateTimeEnd:=sysdate;         (строка полностью комментарий)
        2. tmp := 'DateTimeEnd:=sysdate';   (внутри строкового литерала)
        3. tmp := 'DateTimeEnd:=sysdate     (внутри многострочного строкового литерала)
        4. /** / DateTimeEnd:=sysdate; /**/ (внутри /* */)
        5. /* DateTimeEnd:=sysdate; */      (внутри /* */)
        6. /*                             (многострочный комментарий)
           DateTimeEnd:=sysdate;
           */
        
        Вариант для исправления:
        8. DateTimeEnd:=sysdate;            (реальный код)
        """
        # Проверка 1: Строка начинается с комментария -- (и не внутри строки)
        stripped = line.lstrip()
        if stripped.startswith('--'):
            # Проверяем, не внутри ли строки этот комментарий
            leading_ws_len = len(line) - len(stripped)
            before_comment = line[:leading_ws_len]
            if before_comment.count("'") % 2 == 0:
                return True  # Это комментарий
        
        # Проверка 2: Находим позицию совпадения относительно начала строки
        # Проверяем, есть ли перед совпадением '--' (однострочный комментарий)
        line_before_match = line[:match_start]
        
        # Если перед совпадением есть '--' и нет конца строки после него
        if '--' in line_before_match:
            comment_pos = line_before_match.rfind('--')
            # Проверяем, не внутри ли строки этот комментарий
            before_comment = line[:comment_pos]
            single_quotes = before_comment.count("'")
            # Если нечётное количество кавычек, значит '--' внутри строки
            if single_quotes % 2 == 0:
                return True  # Это комментарий
        
        # Проверка 3: Находимся ли внутри строкового литерала '...'
        # Считаем одинарные кавычки до позиции совпадения
        single_quotes_before = line[:match_start].count("'")
        if single_quotes_before % 2 == 1:
            return True  # Внутри строкового литерала
        
        # Проверка 4: Находимся ли внутри блочного комментария /* */
        # Используем состояние self.in_block_comment для многострочных комментариев
        before_match = line[:match_start]
        after_match = line[match_end:]
        
        # Считаем открывающие и закрывающие блочные комментарии до позиции совпадения
        opens_before = before_match.count('/*')
        closes_before = before_match.count('*/')
        
        # Если мы уже в блочном комментарии с предыдущей строки
        if self.in_block_comment:
            # Если есть закрывающий */ до позиции совпадения, выходим из комментария
            if closes_before > 0:
                # Проверяем, закрывает ли этот */ открывающий /* с этой строки
                first_close = before_match.find('*/')
                last_open_before_close = before_match[:first_close].rfind('/*')
                if last_open_before_close == -1:
                    # Этот */ закрывает комментарий с предыдущей строки
                    # Теперь проверяем, нет ли нового /* после */
                    remaining = before_match[first_close + 2:]
                    if '/*' not in remaining:
                        return False  # Выходим из блочного комментария
                    # Есть новый /*, снова в комментарии
            return True  # Всё ещё в блочном комментарии
        
        # Не в блочном комментарии с предыдущей строки
        # Проверяем, есть ли открывающий /* без закрывающего */ до позиции совпадения
        if opens_before > closes_before:
            # Есть открывающий /* без закрывающего */ до этой позиции
            # Проверяем, есть ли закрывающий */ после совпадения на этой строке
            total_closes = line.count('*/')
            if total_closes <= closes_before:
                # Нет закрывающего */ после совпадения на этой строке
                self.in_block_comment = True  # Запоминаем состояние
                return True  # Внутри блочного комментария
        
        return False
    
    def _update_block_comment_state(self, line: str):
        """Обновление состояния блочного комментария после обработки строки"""
        opens = line.count('/*')
        closes = line.count('*/')
        
        if self.in_block_comment:
            # Если в комментарии, закрывающий */ уменьшает счётчик
            if closes > 0:
                # Проверяем, закрывает ли */ открывающий /* с этой же строки
                # Ищем первый */ и последний /* перед ним
                first_close = line.find('*/')
                last_open_before_close = line[:first_close].rfind('/*')
                
                if last_open_before_close != -1:
                    # /* и */ на одной строке, это не закрывает внешний комментарий
                    # Проверяем оставшуюся часть строки
                    remaining = line[first_close + 2:]
                    if '*/' in remaining:
                        # Есть ещё закрывающий, уменьшаем
                        self.in_block_comment = False
                else:
                    # */ закрывает комментарий с предыдущей строки
                    # Проверяем, есть ли новый /* после */
                    remaining = line[first_close + 2:]
                    if '/*' in remaining:
                        self.in_block_comment = True  # Новый комментарий начался
                    else:
                        self.in_block_comment = False  # Вышли из комментария
        else:
            # Если не в комментарии, открывающий /* без закрывающего начинает комментарий
            if opens > closes:
                self.in_block_comment = True
    
    def _find_code_positions(self, line: str, pattern: str, flags: int = 0) -> List[Tuple[int, int, str]]:
        """
        Найти все позиции паттерна в коде, игнорируя комментарии и строки.
        Возвращает список кортежей (start, end, matched_text).
        """
        matches = []
        for match in re.finditer(pattern, line, flags):
            if not self._is_in_comment_or_string(line, match.start(), match.end()):
                matches.append((match.start(), match.end(), match.group()))
        return matches
    
    def apply_fix(self, line: str, issue: Issue, log_level: str = 'Минимальный') -> Tuple[str, bool]:
        """Применение исправления к строке с учётом комментариев и строк"""
        original = line.strip()
        
        # Пропускаем строки, которые являются комментариями
        if original.startswith('--'):
            return original, False
        
        if issue.issue_type not in self.FIXES:
            return original, False
        
        # 1. Сначала пытаемся исправить через SQL парсер
        try:
            sql_fixed = sql_apply_fix(original, issue.issue_type)
            if sql_fixed and sql_fixed != original:
                logger.debug(f"[FIXER] Исправлено через SQL парсер: {issue.issue_type}")
                logger.debug(f"  Было: {original}")
                logger.debug(f"  Стало: {sql_fixed}")
                
                # Формируем результат с комментариями
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                leading_whitespace = line[:len(line) - len(line.lstrip())]
                old_line_commented = f"{leading_whitespace}-- {original}" if not original.startswith('--') else f"{leading_whitespace}--{original}"
                
                short_desc = self.fix_descriptions.get(issue.issue_type, issue.issue_type)
                
                if log_level == 'Подробный':
                    prompt_line = self._get_prompt_line(issue, original)
                    marker_line = f"--(*){issue.issue_type} - {prompt_line}"
                else:
                    marker_line = f"--(*){issue.issue_type} - {short_desc}"
                
                modified = f"{marker_line}\n--OLD {timestamp}\n{old_line_commented}\n{sql_fixed}\n"
                return modified, True
        except Exception as e:
            logger.warning(f"[FIXER] Ошибка SQL парсера: {e}")
            # Продолжаем с fallback
        
        # 2. Если парсер не справился — используем старый метод
        return self._apply_fix_legacy(line, issue, log_level)
    
    def _apply_fix_legacy(self, line: str, issue: Issue, log_level: str) -> Tuple[str, bool]:
        """Применение исправления через старые правила (fallback)"""
        original = line.strip()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for pattern, replacement, case_sensitive, issue_type_code in self.FIXES[issue.issue_type]:
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Проверяем, есть ли совпадения вне комментариев и строк
            code_matches = self._find_code_positions(line, pattern, flags)
            
            if not code_matches:
                continue  # Нет совпадений в коде, пропускаем
            
            # Есть совпадения в коде, применяем исправление только к ним
            # Используем re.sub с callback для корректной обработки групп захвата
            new_line = line
            for start, end, matched_text in reversed(code_matches):  # reversed для сохранения позиций
                # Заменяем только найденное совпадение с обработкой групп
                segment = line[start:end]
                fixed_segment = re.sub(pattern, replacement, segment, flags=flags, count=1)
                new_line = new_line[:start] + fixed_segment + new_line[end:]
            
            if new_line != line:
                # Сохраняем отступы оригинальной строки для нового кода
                leading_whitespace = line[:len(line) - len(line.lstrip())]
                
                # Формируем закомментированную исходную строку - с отступами как в оригинале
                # Если строка уже начинается с --, не добавляем пробел после --
                if original.startswith('--'):
                    old_line_commented = f"{leading_whitespace}--{original}"
                else:
                    old_line_commented = f"{leading_whitespace}-- {original}"
                
                # Новый код с тем же отступом
                new_line_stripped = new_line.rstrip()
                
                # Получаем краткое описание из рубрикатора
                short_desc = self.fix_descriptions.get(issue_type_code, issue_type_code)
                
                # Формируем описание проблемы
                issue_description = self._get_issue_description(issue, log_level)
                
                # Формат меток в зависимости от уровня логирования:
                # Минимальный:
                # --(*)v50.X.Y - Описание
                # --OLD Дата, время
                # --<исходная строка>
                # новый код
                #
                # Подробный:
                # --(*)v50.X.Y - [ПРОМПТ] Проанализируй код: ... | Правило: ... | Описание: ... | Обоснование: ...
                # --OLD Дата время
                # --<исходная строка>
                # новый код
                
                if log_level == 'Подробный':
                    # Проанализированный код с полным описанием (одной строкой)
                    prompt_line = self._get_prompt_line(issue, original)
                    marker_line = f"--(*){issue_type_code} - {prompt_line}"
                    modified = f"{marker_line}\n--OLD {timestamp}\n{old_line_commented}\n{new_line_stripped}\n"
                else:
                    # Минимальный уровень - только краткое описание с меткой (*)
                    marker_line = f"--(*){issue_type_code} - {issue_description}"
                    modified = f"{marker_line}\n--OLD {timestamp}\n{old_line_commented}\n{new_line_stripped}\n"
                return modified, True
        
        return original, False
    
    def _get_issue_description(self, issue: Issue, log_level: str) -> str:
        """Формирование описания проблемы в зависимости от уровня логирования"""
        if log_level == 'Подробный':
            # Полное описание с анализом (одной строкой)
            return (f"{issue.description} | "
                   f"Правило: {issue.issue_type} | "
                   f"Обоснование: {issue.rubricator_full_description} | "
                   f"Заключение: Требуется исправление")
        else:
            # Минимальный уровень - только тип и краткое описание
            return f"{issue.description}"
    
    def _get_prompt_line(self, issue: Issue, original_code: str) -> str:
        """Формирование строки промпта для комментария"""
        return f"[ПРОМПТ] Проанализируй код: {original_code} | Правило: {issue.issue_type} | Описание: {issue.description} | Обоснование: {issue.rubricator_full_description} | Заключение: Требуется исправление"
    
    def fix_file(self, file_path: Path, issues: List[Issue]) -> Tuple[bool, int]:
        """
        Исправление одного файла.
        Возвращает кортеж (изменён_ли_файл, количество_исправлений).
        """
        if not issues:
            return False, 0
        
        # Сброс состояния блочного комментария в начале нового файла
        self.in_block_comment = False
        self.skipped_in_comment = 0
        self.skipped_in_string = 0
        self.skipped_details = []
        
        # Чтение файла с автоматическим определением кодировки
        try:
            from utils.encoding_utils import read_file_with_encoding
            content, used_encoding = read_file_with_encoding(file_path)
            lines = content.splitlines(keepends=True)
        except Exception as e:
            # Fallback: пробуем UTF-8
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        
        # Группировка проблем по строкам
        issues_by_line = {}
        for issue in issues:
            line_num = issue.line_number
            if line_num not in issues_by_line:
                issues_by_line[line_num] = []
            issues_by_line[line_num].append(issue)
        
        new_lines = []
        modified_count = 0
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for line_num, line in enumerate(lines, 1):
            if line_num in issues_by_line:
                # Есть проблемы в этой строке
                issue = issues_by_line[line_num][0]  # Берём первую проблему
                
                if issue.issue_type not in self.FIXES:
                    new_lines.append(line)
                    self._update_block_comment_state(line)
                    continue
            
                # Сохраняем оригинальную строку для использования в обоих блоках
                original = line.strip()
                
                # Применяем исправление с учётом комментариев и строк
                fixed_line, was_modified = self.apply_fix(line, issue, self.config.get('logging', {}).get('level', 'Минимальный'))
                
                if was_modified:
                    modified_count += 1
                    # Сохраняем детали исправления для отчёта
                    self.fixed_issues.append({
                        'file': str(file_path),
                        'line_num': line_num,
                        'issue_type': issue.issue_type,
                        'original_code': original,
                        'fixed_code': fixed_line.rstrip(),
                        'timestamp': timestamp
                    })
                    new_lines.append(fixed_line)
                else:
                    # Исправление не применено - проверяем причину
                    leading_ws = line[:len(line) - len(line.lstrip())]
                    
                    # Получаем краткое описание
                    short_desc = self.fix_descriptions.get(issue.issue_type, issue.issue_type)
                    
                    # Формируем закомментированную строку
                    if original.startswith('--'):
                        old_line_commented = f"{leading_ws}--{original}"
                    else:
                        old_line_commented = f"{leading_ws}-- {original}"
                    
                    # Формируем "исправленную" строку для отображения
                    for pattern, replacement, case_sensitive, issue_type_code in self.FIXES[issue.issue_type]:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        new_line = re.sub(pattern, replacement, line, flags=flags)
                        break
                    else:
                        new_line = line
                    
                    reason = "comment"
                    if original.startswith('--'):
                        self.skipped_in_comment += 1
                    elif "'" in line and line.count("'") % 2 == 1:
                        reason = "string"
                        self.skipped_in_string += 1
                    elif self.in_block_comment:
                        reason = "block_comment"
                        self.skipped_in_comment += 1
                    else:
                        self.skipped_in_comment += 1
                    
                    # Сохраняем детали для подробного лога
                    self.skipped_details.append({
                        'line_num': line_num,
                        'issue_type': issue.issue_type,
                        'short_desc': short_desc,
                        'original_code': original,
                        'commented_code': old_line_commented,
                        'new_code': new_line.rstrip(),
                        'reason': reason
                    })
                    
                    new_lines.append(line)
                    self._update_block_comment_state(line)
            else:
                # Нет проблем, оставляем как есть, но обновляем состояние блочного комментария
                new_lines.append(line)
                self._update_block_comment_state(line)
        
        # Проверяем, были ли реальные изменения
        if modified_count == 0:
            return False, 0
        
        # Записываем изменения только если были модификации (в UTF-8)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        # Статистика
        fixed_types = set(issue.issue_type for issue in issues if any(
            self._find_code_positions(lines[issue.line_number-1] if issue.line_number <= len(lines) else '', 
                                       self.FIXES.get(issue.issue_type, [])[0][0] if self.FIXES.get(issue.issue_type) else '',
                                       0 if self.FIXES.get(issue.issue_type) and len(self.FIXES[issue.issue_type]) > 0 else 0)
        ))
        
        for issue_type in fixed_types:
            if issue_type in self.FIXES:
                self.stats[issue_type] = self.stats.get(issue_type, 0) + 1
        
        if modified_count > 0:
            self.changes_log.append({
                'file': str(file_path),
                'iteration': self.iteration,
                'timestamp': datetime.now().isoformat(),
                'issues_fixed': modified_count,
                'types': list(fixed_types) if fixed_types else [issues[0].issue_type]
            })
        
        return True, modified_count
    
    def copy_directory_structure(self, source_dir: Path, results_dir: Path, log_callback=None):
        """Копирование структуры каталогов и файлов (кроме .plp)"""
        if not source_dir.exists():
            if log_callback:
                log_callback(f"  [!] Исходный каталог не найден: {source_dir}")
            return 0
        
        files_copied = 0
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                # Пропускаем .plp файлы
                if file_path.suffix.lower() == '.plp':
                    continue
            
                try:
                    rel_path = file_path.relative_to(source_dir)
                    dest_path = results_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    files_copied += 1
                    if log_callback:
                        log_callback(f"    Скопировано: {rel_path}")
                except Exception as e:
                    if log_callback:
                        log_callback(f"    [!] Ошибка копирования {file_path}: {e}")
        
        return files_copied
    
    def fix_directory(self, scanner: PLPlusScanner, results_dir: Path, log_callback=None, log_level: str = 'Минимальный'):
        """
        Исправление всех файлов в директории.
        log_callback - функция для вывода сообщений в журнал (опционально).
        log_level - уровень логирования ('Минимальный' или 'Подробный').
        """
        # Получаем паттерн файлов
        file_pattern = self.config.get('scan', {}).get('file_pattern', '**/*.plp')
        only_modified = self.config.get('output', {}).get('only_modified', False)
        preserve_structure = self.config.get('output', {}).get('preserve_structure', True)
        
        # Проверяем: пустой шаблон или *.* и не только модифицированные файлы
        should_copy_structure = (
            (not file_pattern or file_pattern == '*' or file_pattern == '*.*') and
            not only_modified and
            preserve_structure
        )
        
        issues_by_file = scanner.get_issues_by_file()
        files_modified = 0
        files_unchanged = 0
        total_files = len(issues_by_file)
        
        # Копируем структуру каталогов при пустом шаблоне
        if should_copy_structure:
            source_dir_str = self.config['paths']['source_dir']
            if len(source_dir_str) >= 2 and source_dir_str[1] == ':':
                source_dir_str = source_dir_str[0].upper() + source_dir_str[1:]
            source_dir = Path(source_dir_str)
            
            if log_callback:
                log_callback(f"\nКопирование структуры каталогов (без .plp файлов)...")
            else:
                print(f"\nКопирование структуры каталогов (без .plp файлов)...")
            
            files_copied = self.copy_directory_structure(source_dir, results_dir, log_callback)
            if log_callback:
                log_callback(f"Скопировано файлов: {files_copied}")
            else:
                print(f"Скопировано файлов: {files_copied}")
        
        if log_callback:
            log_callback(f"\nОбработка {total_files} файлов...")
        else:
            print(f"\nОбработка {total_files} файлов...")
        
        for idx, (file_path_str, issues) in enumerate(issues_by_file.items(), 1):
            if log_callback:
                log_callback(f"[{idx}/{total_files}] Обработка: {file_path_str}")
            else:
                print(f"[{idx}/{total_files}] Обработка: {file_path_str}")
            
            # Нормализация пути: буква диска в верхнем регистре
            source_dir_str = self.config['paths']['source_dir']
            if len(source_dir_str) >= 2 and source_dir_str[1] == ':':
                source_dir_str = source_dir_str[0].upper() + source_dir_str[1:]
            
            # Отладочный вывод
            if log_callback:
                log_callback(f"    source_dir: {source_dir_str}")
                log_callback(f"    file_path_str из issues: {file_path_str}")
            
            # file_path_str может быть абсолютным путём (теперь всегда абсолютный после изменения сканера)
            file_path = Path(file_path_str)
            
            # Если путь абсолютный — нормализуем и используем
            if file_path.is_absolute():
                file_path_str_normalized = str(file_path)
                if len(file_path_str_normalized) >= 2 and file_path_str_normalized[1] == ':':
                    file_path_str_normalized = file_path_str_normalized[0].upper() + file_path_str_normalized[1:]
                file_path = Path(file_path_str_normalized)
            else:
                # Относительный путь — пробуем несколько вариантов (резервный вариант)
                # 1. От source_dir
                candidate1 = Path(source_dir_str) / file_path_str
                # 2. От корня проекта (родительская директория от скрипта)
                project_root = Path(__file__).parent.parent.parent
                candidate2 = project_root / file_path_str
                # 3. От текущей рабочей директории
                candidate3 = Path.cwd() / file_path_str
                
                # Ищем существующий файл
                if candidate1.exists():
                    file_path = candidate1
                elif candidate2.exists():
                    file_path = candidate2
                elif candidate3.exists():
                    file_path = candidate3
                else:
                    # Файл не найден ни в одном из мест
                    if log_callback:
                        log_callback(f"    candidates: {candidate1}, {candidate2}, {candidate3}")
            
            if not file_path.exists():
                if log_callback:
                    log_callback(f"  [!] Файл не найден: {file_path}")
                    log_callback(f"      Абсолютный путь: {file_path.resolve() if file_path.is_absolute() else 'не абсолютный'}")
                else:
                    print(f"  [!] Файл не найден: {file_path}")
                continue
            
            if log_callback:
                log_callback(f"    Файл найден: {file_path}")
            
            # Вычисляем относительный путь от source_dir для сохранения в результатах
            # source_dir_str — это каталог из config (PATCH_OUT), но файл может быть в другом месте
            try:
                rel_file_path = str(file_path.relative_to(Path(source_dir_str)))
                if log_callback:
                    log_callback(f"    Относительный путь от source_dir: {rel_file_path}")
            except ValueError:
                # File_path не внутри source_dir — пробуем от корня проекта
                project_root = Path(__file__).parent.parent.parent
                try:
                    rel_file_path = str(file_path.relative_to(project_root))
                    if log_callback:
                        log_callback(f"    Относительный путь от проекта: {rel_file_path}")
                except ValueError:
                    # Если всё ещё не получается, используем относительный путь от PATCH_IN\patch_WORK или просто имя файла
                    # Пробуем извлечь путь относительно patch_WORK
                    patch_work = Path(__file__).parent.parent.parent / 'DATA' / 'patch_WORK'
                    try:
                        rel_file_path = str(file_path.relative_to(patch_work))
                        if log_callback:
                            log_callback(f"    Относительный путь от patch_WORK: {rel_file_path}")
                    except ValueError:
                        # Финальный вариант — имя файла
                        rel_file_path = file_path.name
                        if log_callback:
                            log_callback(f"    Используется имя файла: {rel_file_path}")
            
            if self.config['output']['preserve_structure']:
                results_path = results_dir / rel_file_path
            else:
                results_path = results_dir / file_path.name
            
            if log_callback:
                log_callback(f"    results_path: {results_path}")
            
            # Создаём директорию результатов (явно, перед всеми операциями)
            try:
                results_path.parent.mkdir(parents=True, exist_ok=True)
                if log_callback:
                    log_callback(f"    Каталог создан/проверен: {results_path.parent}")
                    log_callback(f"    results_path существует: {results_path.exists()}")
            except Exception as mkdir_err:
                if log_callback:
                    log_callback(f"    [!] Ошибка создания каталога: {mkdir_err}")
                else:
                    print(f"    [!] Ошибка создания каталога: {mkdir_err}")
                continue
            
            # Проверка: source_dir и results_dir не должны пересекаться
            source_dir_path = Path(source_dir_str).resolve()
            results_dir_resolved = results_dir.resolve()
            
            # Если results_dir внутри source_dir, используем отдельную копию
            if str(results_dir_resolved).startswith(str(source_dir_path)):
                if log_callback:
                    log_callback(f"    [!] results_dir внутри source_dir, используем temp_dir")
                # Создаём временный каталог вне source_dir
                temp_dir = Path(__file__).parent.parent.parent / 'temp_fix'
                temp_dir.mkdir(exist_ok=True)
                if self.config['output']['preserve_structure']:
                    results_path = temp_dir / file_path_str
                else:
                    results_path = temp_dir / file_path.name
                try:
                    results_path.parent.mkdir(parents=True, exist_ok=True)
                    if log_callback:
                        log_callback(f"    Новый results_path: {results_path}")
                except Exception as mkdir_err2:
                    if log_callback:
                        log_callback(f"    [!] Ошибка создания temp_dir: {mkdir_err2}")
                    else:
                        print(f"    [!] Ошибка создания temp_dir: {mkdir_err2}")
                    continue
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Алгоритм работы с файлами результатов:
            # 1. Если results_path существует → переименовать в *_timestamp*
            # 2. Если results_path не существует → создать копию оригинала с _timestamp
            # 3. В любом случае создать results_path на основе оригинала для исправления
            
            if results_path.exists():
                # Файл существует — переименовываем в *_timestamp*
                backup_path = results_path.parent / f"{results_path.stem}_{timestamp}{results_path.suffix}"
                results_path.rename(backup_path)
                if log_callback:
                    log_callback(f"  [!] Существующий файл переименован: {backup_path.name}")
            else:
                # Файла нет — создаём копию оригинала с меткой времени
                backup_path = results_path.parent / f"{results_path.stem}_{timestamp}{results_path.suffix}"
                shutil.copy2(file_path, backup_path)
                if log_callback:
                    log_callback(f"    Создана копия оригинала: {backup_path.name}")
            
            # В любом случае создаём results_path на основе оригинала для исправления
            shutil.copy2(file_path, results_path)
            if log_callback:
                log_callback(f"    Файл создан для исправления: {results_path.name}")
            
            # Исправляем файл (results_path уже содержит оригинал)
            was_modified, fix_count = self.fix_file(results_path, issues)
            
            if was_modified:
                files_modified += 1
                
                if log_callback:
                    log_callback(f"  [OK] Исправлено: {fix_count} проблем → {results_path.name}")
                    log_callback(f"      Копия оригинала: {backup_path.name}")
                else:
                    print(f"  [OK] Исправлено: {fix_count} проблем → {results_path.name}")
                    print(f"      Копия оригинала: {backup_path.name}")
            else:
                files_unchanged += 1
                # Удаляем только results_path (исправленный файл), так как изменений не было
                # backup_path (копия оригинала) остаётся
                results_path.unlink(missing_ok=True)
                
                # Формируем сообщение о причине пропуска
                skip_reason = ""
                if self.skipped_in_comment > 0:
                    skip_reason = f" (в комментариях: {self.skipped_in_comment})"
                if self.skipped_in_string > 0:
                    skip_reason += f" (в строках: {self.skipped_in_string})"
                
                if log_callback:
                    log_callback(f"  [i] Нет исправлений{skip_reason} (копия сохранена: {backup_path.name})")
                else:
                    print(f"  [i] Нет исправлений{skip_reason} (копия сохранена: {backup_path.name})")
                
                # При уровне "Подробный" выводим детали пропущенных исправлений
                if log_level == 'Подробный' and self.skipped_details:
                    log_callback(f"    Пропущенные конструкции:")
                    for detail in self.skipped_details:
                        log_callback(f"      [{detail['issue_type']}] {detail['short_desc']}")
                        log_callback(f"        Строка {detail['line_num']}: {detail['commented_code']}")
                        log_callback(f"        Должно быть: {detail['new_code']}")
                
                # Сбрасываем счётчики для следующего файла
                self.skipped_in_comment = 0
                self.skipped_in_string = 0
                self.skipped_details = []
        
        if log_callback:
            log_callback(f"\nГотово! Изменено файлов: {files_modified}/{total_files}")
            if files_unchanged > 0:
                log_callback(f"Пропущено файлов (без изменений): {files_unchanged}")
            
            # Итоговая статистика по видам кодов правил
            total_fixes = len(self.fixed_issues)
            total_rules = len(self.stats)
            sep = '=' * 70
            dash = '-' * 70
            log_callback(f"\n{sep}")
            log_callback('ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ')
            log_callback(sep)
            log_callback(f'Всего исправлено проблем:        {total_fixes}')
            log_callback(f'Всего видов кодов правил:       {total_rules}')
            log_callback(sep)
            log_callback('Распределение по кодам правил (по убыванию):')
            log_callback(dash)
            for rule_code, count in sorted(self.stats.items(), key=lambda x: (-x[1], x[0])):
                log_callback(f'  {rule_code}: {count}')
            log_callback(sep)
        else:
            print(f"\nГотово! Изменено файлов: {files_modified}/{total_files}")
            if files_unchanged > 0:
                print(f"Пропущено файлов (без изменений): {files_unchanged}")
            
            # Итоговая статистика по видам кодов правил в консоль
            total_fixes = len(self.fixed_issues)
            total_rules = len(self.stats)
            sep = '=' * 70
            dash = '-' * 70
            print(f"\n{sep}")
            print('ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ')
            print(sep)
            print(f'Всего исправлено проблем:        {total_fixes}')
            print(f'Всего видов кодов правил:       {total_rules}')
            print(sep)
            print('Распределение по кодам правил (по убыванию):')
            print(dash)
            for rule_code, count in sorted(self.stats.items(), key=lambda x: (-x[1], x[0])):
                print(f'  {rule_code}: {count}')
            print(sep)
        
        return files_modified
    
    def save_log(self, log_path: Path):
        """Сохранение лога изменений"""
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Группировка исправлений по файлам и типам
        by_file = {}
        for fix in self.fixed_issues:
            file_key = fix['file']
            if file_key not in by_file:
                by_file[file_key] = {}
            issue_type = fix['issue_type']
            if issue_type not in by_file[file_key]:
                by_file[file_key][issue_type] = []
            by_file[file_key][issue_type].append(fix)
        
        # Итоговая статистика по типам
        total_by_type = {}
        for file_types in by_file.values():
            for issue_type, fixes in file_types.items():
                total_by_type[issue_type] = total_by_type.get(issue_type, 0) + len(fixes)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("# Лог исправлений\n\n")
            f.write(f"Итерация: {self.iteration}\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Файлов изменено: {len(self.changes_log)}\n")
            f.write(f"Всего исправлено проблем: {len(self.fixed_issues)}\n\n")
            
            # Итоговая статистика по видам кодов правил
            total_fixes = len(self.fixed_issues)
            total_rules = len(total_by_type)
            f.write(f"{'=' * 70}\n")
            f.write("ИТОГОВАЯ СТАТИСТИКА ПО ВИДАМ КОДОВ ПРАВИЛ\n")
            f.write(f"{'=' * 70}\n")
            f.write(f"Всего исправлено проблем:        {total_fixes}\n")
            f.write(f"Всего видов кодов правил:       {total_rules}\n")
            f.write(f"{'=' * 70}\n")
            f.write("Распределение по кодам правил (по убыванию):\n")
            f.write(f"{'-' * 70}\n")
            for rule_code, count in sorted(total_by_type.items(), key=lambda x: (-x[1], x[0])):
                f.write(f"  {rule_code}: {count}\n")
            f.write(f"{'=' * 70}\n\n")
            f.write("---\n\n")

            f.write("## Детали по файлам:\n\n")
            for file_path, types_dict in sorted(by_file.items()):
                # Общее количество проблем в файле
                total_file_fixes = sum(len(fixes) for fixes in types_dict.values())

                f.write(f"### Файл: `{file_path}`\n\n")
                f.write(f"**Всего исправлено проблем:** {total_file_fixes}\n\n")
                
                # Статистика по типам для файла
                f.write("**Исправления по типам**:\n\n")
                for issue_type, fixes in sorted(types_dict.items(), key=lambda x: (-len(x[1]), x[0])):
                    f.write(f"- {issue_type}: {len(fixes)}\n")
                f.write("\n---\n\n")
                
                # Для каждого типа пишем детали
                for issue_type, fixes in types_dict.items():
                    # Получаем описание типа из рубрикатора
                    short_desc = self.fix_descriptions.get(issue_type, issue_type)
                    # Получаем теги из рубрикатора (в v3.0.0 нет тегов, используем subcategory)
                    tags_info = ""
                    full_desc = ""
                    if self.rubricator:
                        rubric_rule = self.rubricator.get_rule_by_code(issue_type)
                        if rubric_rule:
                            # В v3.0.0 нет тегов, используем subcategory
                            if rubric_rule.subcategory and rubric_rule.subcategory != 'OTHER':
                                tags_info = f" [КАТЕГОРИЯ] {rubric_rule.subcategory}"
                            full_desc = rubric_rule.documentation_text
                    
                    f.write(f"#### {issue_type}: {short_desc}{tags_info}\n\n")
                    if full_desc:
                        f.write(f"_Подробное описание: {full_desc}_\n\n")
                    
                    # Исходные и исправленные строки
                    for fix in fixes:
                        f.write(f">[{fix['line_num']}] {fix['original_code']}\n")
                        f.write(f"<[{fix['line_num']}] {fix['fixed_code']}\n\n")
            
            # Итоговая таблица изменений
            f.write("## Таблица изменений файлов\n\n")
            f.write("| Файл | Проблем исправлено |\n")
            f.write("|------|-------------------|\n")
            for change in self.changes_log:
                f.write(f"| `{change['file']}` | {change['issues_fixed']} |\n")
            
            f.write("\n## Детальная статистика по типам:\n\n")
            for issue_type, count in sorted(self.stats.items(), key=lambda x: (-x[1], x[0])):
                f.write(f"- {issue_type}: {count}\n")


def main():
    """Запуск исправления"""
    config_path = Path(__file__).parent.parent / 'settings.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Формирование структуры config если её нет
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
    if 'output' not in config:
        config['output'] = {
            'only_modified': config.get('only_modified', False),
            'preserve_structure': config.get('preserve_structure', True)
        }
    if 'logging' not in config:
        config['logging'] = {
            'level': config.get('log_level', 'Минимальный')
        }
    
    # Нормализация путей: буква диска в верхнем регистре
    for key in ['source_dir', 'results_dir', 'logs_dir']:
        if key in config['paths']:
            path_str = config['paths'][key]
            if len(path_str) >= 2 and path_str[1] == ':':
                config['paths'][key] = path_str[0].upper() + path_str[1:]
    
    # Отладочный вывод
    print(f"[DEBUG] source_dir: {config['paths']['source_dir']}")
    print(f"[DEBUG] results_dir (из config): {config['paths'].get('results_dir', 'не задан')}")
    
    scanner = PLPlusScanner(config)
    scanner.scan_directory()
    
    iteration = f"v{datetime.now().strftime('%Y%m%d%H%M%S')}"
    fixer = PLPlusFixer(config, iteration)
    
    # Формирование результата вне source_dir
    source_dir = Path(config['paths']['source_dir']).resolve()
    base_results = Path(config['paths']['results_dir']) if config['paths'].get('results_dir') else Path(__file__).parent.parent / 'RESULTS'
    results_dir = base_results.parent / f"patch_WORK_{iteration}"
    
    # Проверка: results_dir не должен быть внутри source_dir
    if str(results_dir.resolve()).startswith(str(source_dir)):
        results_dir = Path(__file__).parent.parent.parent / 'TO_DBI_RESULTS' / f"patch_WORK_{iteration}"
    
    print(f"[DEBUG] Итоговый results_dir: {results_dir}")
    
    files_modified = fixer.fix_directory(scanner, results_dir)
    
    log_path = Path(config['paths']['logs_dir']) / f'fix_log_{iteration}.md'
    fixer.save_log(log_path)
    
    print(f"\nРезультаты исправления:")
    print(f"  Файлов изменено: {files_modified}")
    print(f"  Результаты: {results_dir}")
    print(f"  Лог: {log_path}")


if __name__ == '__main__':
    main()
