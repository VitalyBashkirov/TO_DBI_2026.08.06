#!/usr/bin/env python3
"""
Автоматическое исправление проблемных конструкций PLPlus
Версия: v05 (с рубрикатором, игнорирование комментариев и строк)
"""
import re
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from analyzer.scanner import PLPlusScanner, Issue, read_file_with_encoding
from fixer.markdown_rubricator_loader_v3 import MarkdownRubricatorLoaderV3
from analyzer.sql_parser import apply_fix as sql_apply_fix
from fixer.variable_parser import DeterministicFixer, VariableParser
from rule_engine import get_rule_engine, FLAG_ORDER
# DS_056A: единый хелпер лексического разбора
from analyzer.lexer_state import LexerState, is_in_comment_or_string, advance_lexer_state

# DS_053_Уточнение_5 (задача B): расшифровки флагов — точно как на форме GUI
# (gui_app.py, подписи чекбоксов блока «Флаги детерминированного фикса»).
FIX_FLAG_DESCRIPTIONS = {
    'regex': 'чистые regex-правила',
    'hybrid': 'полудетерм. с algorithmic_hint',
    'ai_fallback': 'помечать needs_ai_fix',
    'ignore': 'не автофиксить, только лог',
    'backup': 'резервные regex-правила',
    'other': 'hybrid без algorithmic_hint',
}


def _fix_flags_block(flags: Dict[str, bool], indent: str = '  ') -> List[str]:
    """Блок «Флаги замены» с расшифровкой (выравнивание по «—»)."""
    width = max(len(f"{n}: {'V'}") for n in FLAG_ORDER)
    lines = [f"{indent}Флаги замены:"]
    for name in FLAG_ORDER:
        on = flags.get(name, False)
        left = f"{name}: {'V' if on else 'x'}"
        lines.append(f"{indent}  {left:<{width}} — {FIX_FLAG_DESCRIPTIONS.get(name, '')}")
    return lines
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Маппинг типов данных на префиксы типов
# ============================================================
TYPE_PREFIX_MAP = {
    'integer': 'i',
    'number': 'n',
    'numeric': 'n',
    'decimal': 'n',
    'bigint': 'n',
    'smallint': 'n',
    'pls_integer': 'n',
    'binary_integer': 'n',
    'varchar2': 'v',
    'varchar': 'v',
    'string': 'v',
    'char': 'v',
    'date': 'd',
    'date_time': 'd',
    'timestamp': 'd',
    'boolean': 'b',
    'ref': 'r',
    'rowtype': 'r',
    'record': 'rec',
    'table': 'tb',
    'clob': 'v',
    'blob': 'v',
    'long': 'v',
    'long_raw': 'v',
    'raw': 'v',
    'bfile': 'v',
}

# Запрещённые/плохие префиксы
BAD_PREFIXES = [
    'dp', 'dbg', 'debug', 'bad', 'badprefix', 'tmp', 'temp',
    'var', 'data', 'info', 'z_', 'x_', 'test', 'dummy'
]

# Зарезервированные префиксы (системные)
RESERVED_PREFIXES = ['sys_', 'dba_', 'pg_', '_temp', '_tmp', '_temp_', '_tmp_']

# Префиксы назначения (что это за переменная)
PURPOSE_PREFIX = 'v_'  # по умолчанию — локальная переменная

# ============================================================
# ДЕТЕРМИНИРОВАННЫЙ СЛОЙ: Таблица переименований переменных
# ============================================================
# Ключ: старое имя (без регистра). Значение: новое имя.
# Заполняется автоматически из объявлений, но можно задать явные правила.
# Типы переменных и соответствующие префиксы:
#   ref [TABLE]      → r   (v_rBranch)
#   &lib.tp_recXxx   → rec (v_recBrInfo)
#   varchar2/string  → v   (v_vFmt)
#   integer          → i   (v_iDp)

# Явные правила для специфичных типов (тип → префикс типа)
TYPE_RENAME_PREFIX = {
    'ref': 'r',
    'rowtype': 'r',
    'record': 'rec',
    'varchar2': 'v',
    'varchar': 'v',
    'string': 'v',
    'char': 'v',
    'integer': 'i',
    'number': 'n',
    'numeric': 'n',
    'decimal': 'n',
    'date': 'd',
    'timestamp': 'd',
    'date_time': 'd',
    'boolean': 'b',
    'table': 'tb',
    'clob': 'v',
    'blob': 'v',
    'long': 'v',
}

# Словарь известных неправильных префиксов → корректный смысл
# (для смысловой части CamelCase)
KNOWN_BAD_MEANINGS = {
    'lr': '',        # убрать лишний lr (v_lrLrBranch → v_rBranch)
    'lv': '',        # убрать лишний lv (lvRepPeriod → RepPeriod)
    'vv': 'v',       # v_vVDateRep → v_vDateRep (лишняя V)
}

# Известные соответствия «смысл → осмысленное имя»
# (для полного переименования по смыслу)
KNOWN_MEANING_MAP = {
    'Dp': 'Dp',          # debug_pipe
    'Dp1': 'Dp1',
    'Fmt': 'Fmt',
    'Fmt24': 'Fmt24',
    'FmtHMS': 'FmtHMS',
    'Branch': 'Branch',
    'BrInfo': 'BrInfo',
    'Param': 'Param',
    'DateRep': 'DateRep',
    'RepPeriod': 'RepPeriod',
    'P_FILE_XML': 'P_FILE_XML',
    'P_FILE_ZIP': 'P_FILE_ZIP',
}


def _capitalize_meaning(name: str) -> str:
    """
    Преобразует 'смысл' части имени в CamelCase с заглавной буквы.
    'dp' → 'Dp', 'fmt24' → 'Fmt24', 'user_name' → 'UserName', 'dp1' → 'Dp1'
    Сохраняет внутренние заглавные буквы (CamelCase): 'lvRepPeriod' → 'LvRepPeriod'
    """
    # Сначала заменяем _ на пробел и делаем title case
    result = ''.join(word.capitalize() for word in name.replace('_', ' ').split())
    # Капитализируем первую букву после цифр
    result = re.sub(r'(\d)([a-zA-Z])', lambda m: m.group(1) + m.group(2).upper(), result)
    # Сохраняем внутренние заглавные буквы из оригинального имени
    # Находим все заглавные буквы в оригинале и вставляем их в результат
    result = list(result)
    orig_upper = [c.isupper() for c in name]
    # Если в оригинале есть заглавные буквы кроме первой, сохраняем их
    if any(orig_upper[1:]):
        # Восстанавливаем заглавные буквы на тех же позициях
        for i, is_upper in enumerate(orig_upper):
            if is_upper and i > 0 and i < len(result):
                result[i] = result[i].upper()
    return ''.join(result)


def _build_bad_prefix_replacer():
    """
    Генерирует lambda-функцию для BAD_PREFIX.п.4.3.
    Формат: {назначение}{тип}{Смысл}
    Пример: dp integer → v_iDp, dp1 integer → v_iDp1
    """
    def replacer(match):
        full_match = match.group(0)
        # Разделяем имя переменной и тип
        parts = full_match.strip().split()
        if len(parts) < 2:
            return full_match
        
        var_name = parts[0]
        data_type = parts[1].lower()
        
        # Получаем префикс типа
        type_prefix = TYPE_PREFIX_MAP.get(data_type, 'v')
        
        # "Смысл" — всё имя переменной, превращаем в CamelCase
        # НЕ удаляем плохой префикс, так как он часть смысла
        meaning = var_name
        
        # Формируем новое имя: {назначение}{тип}{Смысл}
        new_name = PURPOSE_PREFIX + type_prefix + _capitalize_meaning(meaning)
        
        # Возвращаем с сохранением типа
        return new_name + ' ' + parts[1] + ' ' + ' '.join(parts[2:]) if len(parts) > 2 else new_name + ' ' + parts[1]
    
    return replacer


def _build_short_name_replacer():
    """
    Генерирует lambda-функцию для коротких имён (id, name, count и т.д.).
    Формат: {назначение}{тип}{Смысл}
    Пример: id integer → v_iId
    """
    def replacer(match):
        full_match = match.group(0)
        parts = full_match.strip().split()
        if len(parts) < 2:
            return full_match
        
        var_name = parts[0]
        data_type = parts[1].lower()
        
        type_prefix = TYPE_PREFIX_MAP.get(data_type, 'v')
        new_name = PURPOSE_PREFIX + type_prefix + _capitalize_meaning(var_name)
        
        return new_name + ' ' + parts[1] + ' ' + ' '.join(parts[2:]) if len(parts) > 2 else new_name + ' ' + parts[1]
    
    return replacer


def _build_prefix_type_replacer():
    """
    Генерирует lambda-функцию для PREFIX_TYPE.п.4.4.
    Добавляет {назначение}{тип} перед смыслом.
    Пример: dp integer → v_iDp integer
    """
    def replacer(match, purpose_prefix='v_'):
        full_match = match.group(0)
        parts = full_match.strip().split()
        if len(parts) < 2:
            return full_match
        
        var_name = parts[0]
        data_type = parts[1].lower()
        
        # Проверяем, есть ли уже правильный префикс
        # Если имя уже начинается с v_, p_, cn_, cur_ — пропускаем
        known_purposes = ['v_', 'p_', 'cn_', 'cur_', 'ret_']
        if any(var_name.startswith(p) for p in known_purposes):
            return full_match
        
        # Получаем префикс типа
        type_prefix = TYPE_PREFIX_MAP.get(data_type, 'v')
        
        # "Смысл" — всё имя переменной, превращаем в CamelCase
        meaning = _capitalize_meaning(var_name)
        
        # Формируем новое имя: {назначение}{тип}{Смысл}
        new_name = purpose_prefix + type_prefix + meaning
        
        # Сохраняем остальную часть строки (размерность, :=, значение и т.д.)
        rest = full_match[len(full_match.split()[0]):]
        
        return new_name + rest
    
    return replacer


def _build_function_params_replacer():
    """
    Генерирует lambda-функцию для параметров функций.
    Параметры получают префикс p_ вместо v_.
    Пример: v1 boolean → p_bCondition boolean
    """
    def replacer(match):
        full_match = match.group(0)
        parts = full_match.strip().split()
        if len(parts) < 2:
            return full_match
        
        var_name = parts[0]
        # Тип может быть с размерностью (varchar2(32767))
        data_type = parts[1].lower().split('(')[0]  # Убираем размерность для маппинга
        
        # Получаем префикс типа
        type_prefix = TYPE_PREFIX_MAP.get(data_type, 'v')
        
        # Для параметров используем p_ вместо v_
        purpose_prefix = 'p_'
        
        # "Смысл" — всё имя переменной, превращаем в CamelCase
        meaning = _capitalize_meaning(var_name)
        
        # Формируем новое имя: p_{тип}{Смысл}
        new_name = purpose_prefix + type_prefix + meaning
        
        # Сохраняем остальную часть строки (размерность, :=, значение и т.д.)
        rest = full_match[len(full_match.split()[0]):]
        
        return new_name + rest
    
    return replacer


def _process_function_declaration(lines: List[str], start_line: int) -> Tuple[List[str], int]:
    """
    Обработка заголовка функции: преобразование параметров и добавление переменной возврата.
    Возвращает изменённые строки и индекс строки после функции.
    """
    # Собираем заголовок функции (строки до 'is')
    header_lines = []
    is_line_idx = -1
    for i in range(start_line, len(lines)):
        line = lines[i].strip()
        header_lines.append(lines[i])
        if 'is' in line.lower() and ('function' in line.lower() or 'method' in line.lower()):
            is_line_idx = i
            break
        elif 'is' in line.lower() and i > start_line:
            # 'is' может быть в отдельной строке
            is_line_idx = i
            break
    
    if is_line_idx == -1:
        return lines, start_line + 1
    
    # Парсим заголовок
    header_text = ''.join(header_lines)
    
    # Находим параметры между () и return (учитываем вложенные скобки в типах)
    # Pattern: (params) return type[(size)]
    param_match = re.search(r'\((.+?)\)\s+return\s+(\w+(?:\(\d+\))?)', header_text, re.IGNORECASE)
    if not param_match:
        return lines, is_line_idx + 1
    
    params_str = param_match.group(1)
    return_type = param_match.group(2)
    
    # Разделяем параметры
    params = [p.strip() for p in params_str.split(',')]
    new_params = []
    
    # Собираем имена параметров для замены в теле функции
    param_names = []
    
    for param in params:
        parts = param.split()
        if len(parts) >= 2:
            var_name = parts[0]
            data_type = parts[1].lower().split('(')[0]
            
            # Проверяем, есть ли уже правильный префикс
            if not any(var_name.startswith(p) for p in ['v_', 'p_', 'cn_', 'cur_']):
                type_prefix = TYPE_PREFIX_MAP.get(data_type, 'v')
                meaning = _capitalize_meaning(var_name)
                new_name = 'p_' + type_prefix + meaning
                new_params.append(new_name + ' ' + ' '.join(parts[1:]))
                param_names.append((var_name, new_name))
            else:
                new_params.append(param)
                param_names.append((var_name, var_name))
        else:
            new_params.append(param)
    
    # Формируем новый заголовок
    new_params_str = ', '.join(new_params)
    
    # Заменяем только параметры (между () и return), не затрагивая return type
    # Находим позицию параметров
    params_start = header_text.index('(')
    # Находим закрывающую скобку параметров (балансируем вложенные)
    depth = 0
    params_end = -1
    for i in range(params_start, len(header_text)):
        if header_text[i] == '(':
            depth += 1
        elif header_text[i] == ')':
            depth -= 1
            if depth == 0:
                params_end = i
                break
    
    if params_end == -1:
        return lines, is_line_idx + 1
    
    # Формируем новый заголовок
    new_header = header_text[:params_start + 1] + new_params_str + header_text[params_end:]
    
    # Обновляем строки заголовка
    for i in range(start_line, is_line_idx + 1):
        lines[i] = new_header if i == start_line else lines[i]
    
    # Обновляем строки заголовка
    for i in range(start_line, is_line_idx + 1):
        lines[i] = new_header if i == start_line else lines[i]
    
    # Добавляем переменную возврата после 'is'
    # Находим строку с 'is'
    is_line = lines[is_line_idx]
    indent = len(is_line) - len(is_line.lstrip())
    whitespace = ' ' * indent
    
    # Определяем тип возврата
    return_type_name = return_type.split('(')[0] if '(' in return_type else return_type
    type_prefix = TYPE_PREFIX_MAP.get(return_type_name.lower(), 'v')
    
    # Ищем осмысленное имя для возврата
    meaning = 'Result'
    new_return_var = f'v_{type_prefix}{meaning}'
    
    # Добавляем объявление после 'is'
    lines.insert(is_line_idx + 1, f'{whitespace}{new_return_var} {return_type};\n')
    
    return lines, is_line_idx + 2


def _process_function_body(lines: List[str], start_line: int, param_names: List[Tuple[str, str]]) -> List[str]:
    """
    Обработка тела функции: замена старых имён параметров на новые.
    """
    if not param_names:
        return lines
    
    # Находим конец функции (слово 'end')
    end_line = -1
    for i in range(start_line, len(lines)):
        if lines[i].strip().lower().startswith('end'):
            end_line = i
            break
    
    if end_line == -1:
        return lines
    
    # Заменяем имена параметров в теле функции
    for i in range(start_line, end_line):
        line = lines[i]
        for old_name, new_name in param_names:
            # Заменяем whole word
            line = re.sub(rf'\b{re.escape(old_name)}\b', new_name, line)
        lines[i] = line
    
    return lines


class PLPlusFixer:
    """Исправлятель проблемных конструкций PLPlus"""

    # DS_056A: совместимый алиас для lexer_state.in_block_comment
    @property
    def in_block_comment(self):
        return self.lexer_state.in_block_comment

    @in_block_comment.setter
    def in_block_comment(self, val):
        self.lexer_state.in_block_comment = val

    def __init__(self, config: dict, iteration: str = 'v0001', use_rubricator: bool = True, clean_output: bool = False):
        self.config = config
        self.iteration = iteration
        self.changes_log: List[dict] = []
        self.stats = {}
        self.fixed_issues: List[dict] = []  # Детали всех исправлений
        self.rubricator: Optional[MarkdownRubricatorLoaderV3] = None
        self.fix_descriptions = {}  # Краткие описания из рубрикатора
        self.lexer_state = LexerState()  # DS_056A: единое лексическое состояние
        self.skipped_in_comment = 0  # Счётчик пропущенных из-за комментариев
        self.skipped_in_string = 0  # Счётчик пропущенных из-за строк
        self.skipped_details = []  # Детали пропущенных исправлений для подробного лога
        self.fix_only_found = config.get('output', {}).get('fix_only_found', False)  # Флаг режима вывода
        self.clean_output = clean_output  # Флаг чистого вывода (без маркеров)

        # DS_053: единый RuleEngine + флаги-чекбоксы замены.
        # По умолчанию включены regex, hybrid и backup — чтобы конвейер реально
        # исправлял при вызове вне GUI. GUI передаёт явные флаги.
        self.rule_engine = get_rule_engine()
        self.flags = {
            'regex': True, 'hybrid': True, 'ai_fallback': False,
            'ignore': False, 'backup': True, 'other': False,
        }
        # Сводные данные для лога scan_VVxVVx_*.md (собираются в fix_directory).
        self.scan_log_data = []  # [{file, plan, line_logs:[...], stats:{}}]
        self.verify_stats = {
            'total_files': 0, 'total_fixes': 0,
            'fixed': 0, 'needs_manual': 0, 'needs_ai_fix': 0,
            'by_rule': {}, 'top_rules': [],
        }
        
        # Загрузка рубрикатора для получения кратких описаний
        if use_rubricator:
            try:
                rubricator_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор v5'
                self.rubricator = MarkdownRubricatorLoaderV3(str(rubricator_dir))
                self._load_fix_descriptions()
            except Exception as e:
                print(f"[!] Не удалось загрузить рубрикатор: {e}")
                print("Используется резервный набор правил")
        
        self.FIXES = self._get_default_fixes()
    
    def _load_fix_descriptions(self):
        """Загрузка кратких описаний из рубрикатора v5.0.0"""
        if not self.rubricator:
            return
        
        for rule in self.rubricator.get_enabled_rules():
            # Сохраняем краткое описание
            short_desc = rule.short_description
            self.fix_descriptions[rule.code] = short_desc

    # ============================================================
    # ДЕТЕРМИНИРОВАННЫЙ СЛОЙ: Поиск и переименование переменных
    # ============================================================

    @staticmethod
    def _extract_declared_variables(lines: List[str]) -> Dict[str, Tuple[str, int]]:
        """
        Находит объявления переменных в секции объявлений.
        Возвращает: {имя_переменной: (данные_для_анализа, номер_строки)}
        
        Работает посимвольно, не полагаясь на состояние:
        - Пропускает pragma, @, комментарии, заголовки методов/функций, begin/end
        - Собирает строки вида:  имя  тип [размер] [:= значение];
        """
        declared = {}
        in_block_comment = False
        
        # Типы, которые однозначно относятся к объявлениям переменных
        known_types = (
            'varchar2', 'varchar', 'string', 'number', 'numeric', 'decimal',
            'integer', 'bigint', 'smallint', 'pls_integer', 'binary_integer',
            'date', 'timestamp', 'date_time', 'boolean', 'char', 'clob', 'blob',
            'long', 'long raw', 'raw', 'bfile',
        )
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Обработка многострочных комментариев
            if in_block_comment:
                if '*/' in stripped:
                    in_block_comment = False
                continue
            if '/*' in stripped:
                in_block_comment = True
                # Если в той же строке есть закрытие, не пропускаем остальное
                if '*/' not in stripped:
                    continue
            
            # Пропускаем служебные строки
            if not stripped:
                continue
            if stripped.startswith(('pragma', '@', '--', '/*', '*', '-------------------')):
                continue
            if stripped.lower().startswith(('begin', 'end', 'is', 'execute is')):
                continue
            if stripped.lower().startswith(('method ', 'function ')):
                continue
            if '=>' in stripped:
                continue
            # Строки с параметрами подпрограмм (содержат , или ) в конце)
            if stripped.endswith(',') or stripped.endswith(')'):
                continue
            
            # Отбрасываем вызовы методов и операторы
            if ' := ' in stripped or ':=' in stripped:
                # Объявления могут содержать := (v_iDp integer:=0;)
                # Проверяем: имя + известный тип перед ':=' ИЛИ [TYPE]
                before_value = stripped.split(':=')[0].strip()
                m_head = re.match(r'^([A-Za-z_]\w*)\s+(.+)$', before_value)
                if m_head:
                    data_part = m_head.group(2).strip()
                    # Тип должен быть известным или [TYPE] или ref или &
                    is_known = (
                        any(data_part.lower().startswith(t) for t in known_types) or
                        data_part.startswith('[') or
                        'ref' in data_part.lower().split()[0:1] or
                        data_part.startswith('&')
                    )
                    if is_known:
                        declared[m_head.group(1)] = (before_value, i)
                continue
            
            # Объявление: имя за которым следует тип (без :=)
            m = re.match(r'^(\s*)([A-Za-z_]\w*)\s+(.+?)\s*;?\s*$', stripped)
            if not m:
                continue
            
            var_name = m.group(2)
            data_part = m.group(3).strip()
            
            # Исключаем строки, где data_part — операторы/ключевые слова
            if data_part.lower().startswith(('pragma', 'is', 'return', 'ref ')) and data_part.lower() != 'ref [':
                pass
            
            # Определяем, является ли строка объявлением
            is_decl = False
            if '&' in data_part and 'tp_rec' in data_part.lower():
                is_decl = True  # lrecBrInfo &lib_cl.tp_recBranchInfo
            elif data_part.startswith('['):
                is_decl = True  # P_FILE_XML [STRING_1000]
            elif any(data_part.lower().startswith(t) for t in known_types):
                is_decl = True  # v_iDp integer
            elif data_part.lower().startswith('ref'):
                is_decl = True  # P_PARAM ref [REPS_PARAMS]
            
            # Пропускаем уже корректные имена, но только после проверки типа
            if is_decl:
                declared[var_name] = (f"{var_name} {data_part}", i)
        
        return declared

    @staticmethod
    def _determine_prefix(data_type: str) -> str:
        """Определяет префикс типа для переменной из строки типа (может содержать имя, размерность, значение)"""
        dt = data_type.strip()
        
        # Обработка ref [TABLE] → r (приоритет над [])
        if 'ref' in dt.lower().split()[0:1] or dt.lower().startswith('ref'):
            return 'r'
        
        # Обработка &lib_cl.tp_recBranchInfo → record
        if '&' in dt and 'tp_rec' in dt.lower():
            return 'rec'
        
        # Обработка типа через [TYPE] (P_FILE_XML [STRING_1000])
        if '[' in dt:
            m = re.search(r'\[(\w+)', dt)
            if m:
                type_name = m.group(1).lower()
                if type_name == 'string':
                    return 'v'
                return TYPE_RENAME_PREFIX.get(type_name, 'v')
        
        # Убираем имя переменной, если передана полная строка (двойной пробел)
        dt_clean = dt
        m_name = re.match(r'^[A-Za-z_]\w*\s+', dt)
        if m_name:
            dt_clean = dt[m_name.end():]
        
        # Обычный тип: varchar2(32767):=0 → varchar2
        m_type = re.match(r'([A-Za-z_]+)', dt_clean)
        if m_type:
            type_name = m_type.group(1).lower()
            # rowtype
            if type_name.endswith('%rowtype'):
                return 'r'
            # Присваивание := : убираем для типа
            return TYPE_RENAME_PREFIX.get(type_name, 'v')
        
        return 'v'

    @staticmethod
    def _clean_meaning(var_name: str) -> str:
        """
        Очищает смысловую часть имени от лишних префиксов.
        v_lrLrBranch → Branch, lrecBrInfo → BrInfo, v_vVDateRep → DateRep,
        v_vLvRepPeriod → RepPeriod, lvRepPeriod → RepPeriod.
        """
        meaning = var_name
        
        # Убираем префиксы назначения
        for p in ['v_', 'p_', 'cn_', 'cur_', 'ret_']:
            if meaning.startswith(p):
                meaning = meaning[len(p):]
                break
        
        # Убираем префикс типа (если он есть)
        # v_vFmt24 → убираем v_ после v_
        for p in ['lrec', 'lr', 'ri', 'rv', 'rr', 'rd', 'rb', 'rtb', 'i_', 'v_', 'n_', 'd_', 'b_', 'r_', 'rec_', 'tb_', 'c_']:
            if meaning.startswith(p):
                meaning = meaning[len(p):]
                break
        
        # Повторный тип-префикс без подчёркивания: v_vVDateRep → после v_ = vVDateRep, снимаем v → VDateRep
        while len(meaning) > 1 and meaning[0].lower() in ('v', 'l') and meaning[1].isupper():
            meaning = meaning[1:]
        # Убираем известные плохие префиксы (после цикла, чтобы поймать LvRepPeriod)
        # lvRepPeriod → RepPeriod (учёт регистра LvRepPeriod)
        if meaning[:2].lower() == 'lv' and len(meaning) > 2 and meaning[2].isupper():
            meaning = meaning[2:]
        # lrBranch → Branch (lr для ref устарел)
        if meaning[:2].lower() == 'lr' and len(meaning) > 2 and meaning[2].isupper():
            meaning = meaning[2:]
        # VDateRep → DateRep (лишняя V — дублированный префикс varchar)
        if meaning.startswith('V') and len(meaning) > 1 and meaning[1].isalpha():
            meaning = meaning[1:]
            # Пере-капитализируем первую букву
            if meaning:
                meaning = meaning[0].upper() + meaning[1:]
        
        # Значение полностью в верхнем регистре P_FILE_XML → PFileXml (CamelCase),
        # НО только если НЕ начинается с P_ (это обрабатывается отдельно для ref)
        if '_' in meaning and meaning.isupper() and not meaning.startswith('P_'):
            meaning = ''.join(word.capitalize() for word in meaning.split('_'))
        
        # Капитализируем первую букву
        if meaning:
            meaning = meaning[0].upper() + meaning[1:]
        
        return meaning or var_name

    def _build_rename_map(self, lines: List[str]) -> Dict[str, str]:
        """
        Строит карту переименований переменных: {старое_имя: новое_имя}.
        Анализирует объявления и применяет правило {назначение}{тип}{Смысл}.
        """
        declared = self._extract_declared_variables(lines)
        rename_map = {}
        
        for var_name, (decl_text, line_num) in declared.items():
            # Разбираем объявление: имя + тип
            # decl_text = "v_iDp integer" или "P_PARAM ref [REPS_PARAMS]" или "P_FILE_XML [STRING_1000]"
            parts = decl_text.split(None, 1)  # split на имя и остаток
            if len(parts) < 2:
                continue
            
            var_name_actual = parts[0]
            data_type = parts[1].strip()
            
            # Определяем префикс типа
            type_prefix = self._determine_prefix(data_type)
            
            # Если имя уже корректно (v_{тип}...) — пропускаем
            if var_name_actual.startswith(f'v_{type_prefix}'):
                # Дополнительная проверка: после префикса идёт заглавная буква
                rest = var_name_actual[len(f'v_{type_prefix}'):]
                if rest and rest[0].isupper():
                    # Проверяем, что смысл не содержит плохих префиксов (VDateRep, LvRepPeriod)
                    if rest == self._clean_meaning(rest):
                        continue  # Уже корректно
            
            # Определяем смысловую часть
            meaning = self._clean_meaning(var_name_actual)
            
            # Для ref-типа: если смысл начинается с P_, убираем P_ (P_PARAM → Param)
            if type_prefix == 'r' and meaning.startswith('P_'):
                meaning = meaning[2:]
                # P_PARAM → PARAM → Param (CamelCase)
                if meaning:
                    meaning = meaning.capitalize()
            
            # Формируем новое имя: v_{тип}{Смысл}
            new_name = f'v_{type_prefix}{meaning}'
            
            # Проверяем, что новое имя отличается от старого
            if new_name != var_name_actual:
                rename_map[var_name_actual] = new_name
        
        return rename_map

    def _update_references(self, lines: List[str], rename_map: Dict[str, str]) -> List[str]:
        """
        Обновляет все ссылки на переименованные переменные в строках кода.
        Заменяет старые имена на новые по границам слов, НЕ затрагивая строковые литералы.
        Исключение: строки &debug(...) — там литералы отражают имена переменных и тоже обновляются.
        Сначала длинные имена (чтобы P_FILE_XML заменился раньше P_FILE).
        """
        if not rename_map:
            return lines
        
        # Сортируем по длине имени (от длинных к коротким)
        sorted_names = sorted(rename_map, key=len, reverse=True)
        
        new_lines = []
        for line in lines:
            new_line = line
            # Для &debug(...) — обновляем и внутри строковых литералов (отладочные сообщения)
            is_debug_line = '&debug' in line
            for old_name in sorted_names:
                new_name = rename_map[old_name]
                if is_debug_line:
                    new_line = re.sub(rf'\b{re.escape(old_name)}\b', new_name, new_line)
                else:
                    new_line = self._replace_outside_quotes(new_line, old_name, new_name)
            new_lines.append(new_line)
        
        return new_lines

    @staticmethod
    def _replace_outside_quotes(line: str, old_name: str, new_name: str) -> str:
        """
        Заменяет old_name на new_name по границам слов, игнорируя строковые литералы '...'.
        Разбивает строку на сегменты вне/внутри одинарных кавычек и заменяет только вне.
        """
        # Разбиваем, сохраняя литералы с кавычками
        parts = re.split(r"('[^']*')", line)
        result = []
        for part in parts:
            if len(part) >= 2 and part.startswith("'") and part.endswith("'"):
                # Строковый литерал — не трогаем
                result.append(part)
            else:
                result.append(re.sub(rf'\b{re.escape(old_name)}\b', new_name, part))
        return ''.join(result)

    def _fix_wrong_methods(self, lines: List[str]) -> List[str]:
        """
        Исправляет обращения к методам в формате ::[CLASS].[method] (PlpCheck.STYLE.WRONG_METHOD.п.4.14).
        Детерминированные замены известных обращений, не затрагивая строковые литералы.
        """
        # Словарь известных обращений: (старое_обращение, новое_обращение)
        method_map = [
            ('[str].get_str_par', '::[RUNTIME].[STR].get_str_par'),
            ('[string].get_str_par', '::[RUNTIME].[STR].get_str_par'),
            ('str.get_str_par', '::[RUNTIME].[STR].get_str_par'),
            ('[str]', '::[RUNTIME].[STR]'),
            ('::[RUNTIME].[STR].Set_Par', '::[RUNTIME].[STR].Set_Par'),  # уже корректно
        ]
        
        new_lines = []
        for line in lines:
            new_line = line
            for old_call, new_call in method_map:
                if old_call in new_line:
                    new_line = new_line.replace(old_call, new_call)
            new_lines.append(new_line)
        
        return new_lines

    def _remove_unused_variables(self, lines: List[str], rename_map: Dict[str, str]) -> List[str]:
        """
        Удаляет объявления переменных, которые нигде не используются (правило NOT_MENTIONED.п.4.8).
        Анализирует вхождения нового имени в теле (после _update_references).
        """
        if not rename_map:
            return lines
        
        # Собираем текст тела (после begin) для проверки использования
        # Используем ВСЕ номера строк, кроме строк объявлений
        body_text_parts = []
        decl_line_numbers = set()
        
        # Найдём объявления (строки с префиксами)
        for i, line in enumerate(lines):
            stripped = line.strip()
            for old_name in rename_map:
                new_name = rename_map[old_name]
                # Строка объявления: начинается с нового имени + тип
                m = re.match(rf'^{re.escape(new_name)}\b', stripped)
                if m and not stripped.startswith(('--', 'pragma', '@')):
                    decl_line_numbers.add(i)
                    break
        
        for i, line in enumerate(lines):
            if i not in decl_line_numbers:
                body_text_parts.append(line)
        body_text = '\n'.join(body_text_parts)
        
        # Для каждой переменной проверяем использование нового имени вне объявления
        unused = set()
        for old_name, new_name in rename_map.items():
            if not re.search(rf'\b{re.escape(new_name)}\b', body_text):
                unused.add(old_name)
        
        if not unused:
            return lines
        
        # Удаляем объявления неиспользуемых переменных (по новым именам)
        new_lines = []
        for line in lines:
            stripped = line.strip()
            is_unused_decl = False
            for old_name in unused:
                new_name = rename_map[old_name]
                m = re.match(rf'^(\s*){re.escape(new_name)}\b', stripped)
                if m and not stripped.startswith(('--', 'pragma', '@')):
                    is_unused_decl = True
                    break
            if not is_unused_decl:
                new_lines.append(line)
        
        return new_lines

    def _validate_fix(self, lines: List[str], old_names: List[str]) -> List[str]:
        """
        Валидация результата: проверяет, что в коде не осталось старых имён переменных.
        Игнорирует вхождения в комментариях и строковых литералах (кроме &debug).
        Возвращает список предупреждений.
        """
        warnings = []
        
        for old_name in old_names:
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith('--'):
                    continue  # Пропускаем комментарии
                
                # Для &debug — имена в литералах должны быть заменены
                if '&debug' in line:
                    if re.search(rf'\b{re.escape(old_name)}\b', line):
                        warnings.append(f"Строка {i}: обнаружено старое имя '{old_name}' в &debug")
                    continue
                
                # Для остальных строк — проверяем только вне литералов
                parts = re.split(r"('[^']*')", line)
                for part in parts:
                    if len(part) >= 2 and part.startswith("'") and part.endswith("'"):
                        continue  # Строковый литерал — пропускаем
                    if re.search(rf'\b{re.escape(old_name)}\b', part):
                        warnings.append(f"Строка {i}: обнаружено старое имя '{old_name}'")
                        break
        
        return warnings

    def _log_warnings(self, warnings: List[str], file_path: Path):
        """Логирует предупреждения валидации"""
        for warning in warnings:
            logger.warning(f"[FIXER] Валидация {file_path.name}: {warning}")
            self.fixed_issues.append({
                'file': str(file_path),
                'line_num': 0,
                'issue_type': 'PlpCheck.STYLE.REFERENCE_UPDATE',
                'original_code': warning,
                'fixed_code': 'Требуется ручное исправление',
                'timestamp': datetime.now().isoformat()
            })

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
            
            # PlpCheck.STYLE - стилистические правила (BAD_PREFIX, PREFIX_TYPE, WRONG_METHOD, CODE_IN_COMMENT, NOT_MENTIONED)
            # Формат имени: {назначение}{тип}{Смысл}
            # Назначение: v_ = локальная, p_ = параметр, cn_ = константа, cur_ = курсор
            # Тип: i/n = integer/number, v = varchar2/string, d = date, b = boolean, lr = ref, lrec = record, tb = table
            # Смысл: оставшаяся часть имени с заглавной буквы
            'PlpCheck.STYLE.BAD_PREFIX.п.4.3': [
                # bad_prefix: переменные с недопустимыми префиксами (dp, dbg, tmp, var, data, info и т.д.)
                (r'(?i)\b(dp|dbg|debug|bad|badprefix|tmp|temp|var|data|info|z_|x_|test|dummy)\w*\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\s*raw|raw|bfile|timestamp|date_time)',
                 _build_bad_prefix_replacer(), False, 'PlpCheck.STYLE.BAD_PREFIX.п.4.3'),
                # bad_prefix: короткие имена (id, name, code, count и т.д.) без префикса типа
                (r'(?i)\b(id|name|code|type|status|date|count|num|val|data|desc|title)\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\s*raw|raw|bfile|timestamp|date_time)',
                 _build_short_name_replacer(), False, 'PlpCheck.STYLE.BAD_PREFIX.п.4.3'),
                # bad_suf: переменные с неправильным суффиксом _s
                (r'\b(\w+)_s\b(?!\s*:)', r'v_\1', False, 'PlpCheck.STYLE.BAD_PREFIX.п.4.3'),
                # bad_suf: префикс p_..._s -> p_...
                (r'\bp_(\w+)_s\b(?!\s*:)', r'p_\1', False, 'PlpCheck.STYLE.BAD_PREFIX.п.4.3'),
            ],
            'PlpCheck.STYLE.PREFIX_TYPE.п.4.4': [
                # Переменная без префикса типа — добавляем {назначение}{тип}{Смысл}
                # Пример: dp integer := 0; → v_iDp integer := 0;
                #         name varchar2(100); → v_vName varchar2(100);
                #         count number; → v_nCount number;
                (r'(?i)\b([a-z][a-z0-9]*)\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\s*raw|raw|bfile|timestamp|date_time)\b',
                 _build_prefix_type_replacer(), False, 'PlpCheck.STYLE.PREFIX_TYPE.п.4.4'),
            ],
            'PlpCheck.STYLE.WRONG_METHOD.п.4.14': [
                # Обращение к методу должно быть в формате [RUNTIME].[METHOD] или ::[CLASS].[METHOD]
                (r'(\w+)\s*\(true\)', r'[RUNTIME]{\1}', False, 'PlpCheck.STYLE.WRONG_METHOD.п.4.14'),
                (r'(\w+)\s*\(false\)', r'[RUNTIME]{\1}', False, 'PlpCheck.STYLE.WRONG_METHOD.п.4.14'),
            ],
            'PlpCheck.STYLE.CODE_IN_COMMENT.п.4.6': [
                # Удаление закомментированного кода — требует ручного подтверждения
            ],
            'PlpCheck.STYLE.NOT_MENTIONED.п.4.8': [
                # Неиспользуемые переменные — требует анализа потока данных
            ],
        }
    
    def _is_in_comment_or_string(self, line: str, match_start: int, match_end: int) -> bool:
        """
        Проверка, находится ли найденное совпадение в комментарии или строковом литерале.

        DS_056A: делегирует в единый хелпер analyzer.lexer_state.
        НЕ мутирует self.lexer_state — читает состояние НАЧАЛА строки.
        Состояние переноса обновляет advance_lexer_state (один раз на строку,
        см. _apply_issue_fixes).

        Для строк с &debug(...) включается debug_mode: литералы внутри такой
        строки считаются кодом (сохраняется прежнее поведение _update_renamed_vars).
        """
        debug_mode = '&debug' in line
        return is_in_comment_or_string(
            line, match_start, match_end, self.lexer_state, debug_mode=debug_mode
        )

    def _update_block_comment_state(self, line: str):
        """Обновление лексического состояния после обработки строки (1 раз на строку)."""
        advance_lexer_state(line, self.lexer_state)
    
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
    
    
    def apply_fix(self, line: str, issue: Issue, log_level: str = 'Минимальный', fix_only_found: bool = False) -> Tuple[str, bool]:
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
                
                # Если clean_output=True - возвращаем только исправленный код без маркеров
                if self.clean_output:
                    return f"{line[:len(line) - len(line.lstrip())]}{sql_fixed}", True
                
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
                
                if fix_only_found:
                    # Формат: --NEW дата время новый_код\nстарый_код (без комментирования)
                    modified = f"{marker_line}\n--NEW {timestamp} {sql_fixed}\n{leading_whitespace}{original}\n"
                else:
                    modified = f"{marker_line}\n--OLD {timestamp}\n{old_line_commented}\n{sql_fixed}\n"
                return modified, True
        except Exception as e:
            logger.warning(f"[FIXER] Ошибка SQL парсера: {e}")
            # Продолжаем с fallback
        
        # 2. Если парсер не справился — используем старый метод
        return self._apply_fix_legacy(line, issue, log_level, fix_only_found)
    
    def _apply_fix_legacy(self, line: str, issue: Issue, log_level: str, fix_only_found: bool = False) -> Tuple[str, bool]:
        """Применение исправления через старые правила (fallback)"""
        original = line.strip()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for pattern, replacement, case_sensitive, issue_type_code in self.FIXES[issue.issue_type]:
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Пропускаем правила без replacement (требуют ручного анализа)
            if replacement is None:
                continue
            
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
                
                # Если clean_output=True - возвращаем только исправленный код без маркеров
                if self.clean_output:
                    return f"{leading_whitespace}{new_line.rstrip()}\n", True
                
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
                    if fix_only_found:
                        # Формат: --NEW дата время новый_код\nстарый_код (без комментирования)
                        modified = f"{marker_line}\n--NEW {timestamp} {new_line_stripped}\n{leading_whitespace}{original}\n"
                    else:
                        modified = f"{marker_line}\n--OLD {timestamp}\n{old_line_commented}\n{new_line_stripped}\n"
                else:
                    # Минимальный уровень - только краткое описание с меткой (*)
                    marker_line = f"--(*){issue_type_code} - {issue_description}"
                    if fix_only_found:
                        # Формат: --NEW дата время новый_код\nстарый_код (без комментирования)
                        modified = f"{marker_line}\n--NEW {timestamp} {new_line_stripped}\n{leading_whitespace}{original}\n"
                    else:
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
    
    # ============================================================
    # DS_053: детерминированный конвейер исправления по issues сканера
    # ============================================================

    def _apply_backup_fix(self, line: str, code: str) -> Optional[str]:
        """Применить резервные regex-правила self.FIXES[code] к строке.

        Обрабатываются только строковые замены (лямбда-правила стилей
        обрабатывает DeterministicFixer). Возвращает изменённую строку или None.
        """
        if code not in self.FIXES:
            return None
        new_line = line
        for pattern, replacement, case_sensitive, _code in self.FIXES[code]:
            if replacement is None or callable(replacement):
                continue
            flags = 0 if case_sensitive else re.IGNORECASE
            matches = self._find_code_positions(new_line, pattern, flags)
            if not matches:
                continue
            for start, end, matched_text in reversed(matches):
                segment = new_line[start:end]
                fixed_segment = re.sub(pattern, replacement, segment, flags=flags, count=1)
                new_line = new_line[:start] + fixed_segment + new_line[end:]
        return new_line if new_line != line else None

    def _apply_issue_fixes(self, lines: List[str],
                           issues: List[Issue],
                           dry_run: bool = False) -> Tuple[List[str], List[dict]]:
        """Применить детерминированные исправления по списку issues сканера.

        Порядок для каждой строки: sql_parser/RuleEngine (regex+hybrid) →
        backup self.FIXES. Каждое следующее правило применяется к текущему
        (уже изменённому) состоянию строки.

        DS_053_Уточнение_4 (задача B): метод всегда работает с КОПИЕЙ lines
        в памяти и сам по себе ничего не пишет на диск (запись результата
        выполняет вызывающий код — fix_file). Параметр dry_run=True —
        явная симуляция: вернуть (new_lines, changes) без каких-либо
        побочных эффектов (используется прогнозом при «Сканировать»).

        Возвращает (обновлённые lines, changes). Каждая change:
        {line_number, rule_code, bucket, kind, before, after}.
        """
        # Группировка issues по номеру строки с сохранением порядка обнаружения.
        by_line: Dict[int, List[Issue]] = {}
        for issue in issues:
            by_line.setdefault(issue.line_number, []).append(issue)

        new_lines = list(lines)
        changes: List[dict] = []

        # DS_073: multiline-правила (replace_scope: "multiline", DS_072c) —
        # применяются ПЕРВЫМИ, до построчного прохода (бриф §3.4: иначе
        # построчный apply_fix может «испортить» строку до multiline).
        # Вариант C: окно — Issue.block_start/block_end (DS_069), fallback —
        # весь файл. После успешной multiline-замены issue помечается
        # обработанной (идемпотентность, §3.5) и исключается из построчного
        # прохода (by_line).
        handled_multiline: set = set()

        def _rule_has_multiline(code: str) -> bool:
            rule = self.rule_engine.get_rule(code)
            if not rule:
                return False
            return any(pt.get('replace_scope') == 'multiline'
                       for pt in rule.get('patterns', []))

        for issue in issues:
            code = issue.issue_type
            if code in handled_multiline:
                continue
            if not _rule_has_multiline(code):
                continue
            if not (self.rule_engine.has_rule(code)
                    and self.rule_engine.rule_enabled(code, self.flags)):
                continue
            # Окно (Вариант C): block_start/block_end, иначе весь файл.
            b_start = getattr(issue, 'block_start', 0) or 0
            b_end = getattr(issue, 'block_end', 0) or 0
            if b_start > 0 and b_end >= b_start:
                start_idx = max(0, b_start - 1)
                end_idx = min(len(new_lines), b_end)
            else:
                start_idx, end_idx = 0, len(new_lines)
            block_text = ''.join(new_lines[start_idx:end_idx])
            res = self.rule_engine.apply_fix_multiline(
                text=block_text, rule_code=code, flags=self.flags)
            if res:
                new_text, bucket, kind = res
                if new_text != block_text:
                    new_block_lines = new_text.splitlines(keepends=True)
                    # Выравниваем длину окна (замена может добавить строки).
                    new_lines[start_idx:end_idx] = new_block_lines
                    changes.append({
                        'line_number': issue.line_number,
                        'rule_code': code,
                        'bucket': bucket,
                        'kind': kind,
                        'before': block_text,
                        'after': new_text,
                    })
                    # Идемпотентность: правило обработано (все его issues
                    # исключаются из построчного прохода ниже).
                    handled_multiline.add(code)
                    break  # окно/нумерация строк изменилась — пересобираем

        # Построчный проход: multiline-issues исключены (обработаны выше).
        by_line = {}
        for issue in issues:
            if issue.issue_type in handled_multiline:
                continue
            by_line.setdefault(issue.line_number, []).append(issue)

        # DS_056A: лексическое состояние переносим между строками в исходном
        # порядке. advance_lexer_state — ровно один раз на строку (в конце итерации),
        # после всех is_in_comment_or_string для этой строки (вызываются внутри
        # применения фиксов через _find_code_positions).
        self.lexer_state = LexerState()
        for idx in range(len(new_lines)):
            line_number = idx + 1
            if line_number in by_line:
                raw = new_lines[idx]
                # Разделяем перевод строки, отступ и тело.
                # Важно: сначала отделяем trailing '\n', затем lstrip только тела
                # (иначе для строки '	\n' lstrip() съест и '\n', и перевод
                # задвоится при сборке).
                trailing = '\n' if raw.endswith('\n') else ''
                core = raw[:-1] if trailing else raw
                body = core.lstrip()
                leading_ws = core[:len(core) - len(body)]

                current = body
                for issue in by_line[line_number]:
                    code = issue.issue_type
                    fixed = None
                    bucket = None
                    kind = None

                    # a. sql_parser / RuleEngine (regex + hybrid + other)
                    if self.rule_engine.has_rule(code) and self.rule_engine.rule_enabled(code, self.flags):
                        res = self.rule_engine.apply_fix(current, code, self.flags)
                        if res:
                            fixed, bucket, kind = res

                    # b. backup self.FIXES
                    if fixed is None and self.flags.get('backup', False):
                        b = self._apply_backup_fix(current, code)
                        if b:
                            fixed, bucket, kind = b, 'backup', 'transform'

                    if fixed is not None and fixed != current:
                        changes.append({
                            'line_number': line_number,
                            'rule_code': code,
                            'bucket': bucket,
                            'kind': kind,
                            'before': current,
                            'after': fixed,
                        })
                        current = fixed

                new_lines[idx] = leading_ws + current + trailing

            # Ровно один раз на строку — состояние считаем по ИСХОДНОЙ строке.
            advance_lexer_state(lines[idx], self.lexer_state)

        return new_lines, changes

    def _verify_file(self, results_path: Path,
                     issues_before: List[Issue]) -> Dict[str, int]:
        """Верификация повторным сканом исправленного файла (DS_053).

        Сравнивает число проблем по кодам правил до/после. fixed = исчезнувшие,
        remaining = оставшиеся (needs_manual или needs_ai_fix). Никогда не
        помечает проблему исправленной, если она осталась.
        """
        verify_scanner = getattr(self, '_verify_scanner', None)
        after_issues: List[Issue] = []
        if verify_scanner is not None:
            try:
                after_issues = verify_scanner.scan_file(Path(results_path)) or []
            except Exception as e:
                logger.warning(f"[FIXER] Ошибка верификации {results_path}: {e}")

        before_by_rule: Dict[str, int] = {}
        for it in issues_before:
            before_by_rule[it.issue_type] = before_by_rule.get(it.issue_type, 0) + 1
        after_by_rule: Dict[str, int] = {}
        for it in after_issues:
            after_by_rule[it.issue_type] = after_by_rule.get(it.issue_type, 0) + 1

        result = {
            'fixed': 0, 'needs_manual': 0, 'needs_ai_fix': 0,
            'by_rule': {}, 'remaining_by_rule': {},
        }
        ai_on = self.flags.get('ai_fallback', False)
        for code, bcount in before_by_rule.items():
            acount = after_by_rule.get(code, 0)
            fixed = max(0, bcount - acount)
            remaining = acount
            result['fixed'] += fixed
            result['by_rule'][code] = fixed
            if remaining:
                if ai_on:
                    result['needs_ai_fix'] += remaining
                else:
                    result['needs_manual'] += remaining
                result['remaining_by_rule'][code] = remaining
        # Правила, появившиеся после фикса (побочные) — тоже needs_manual.
        for code, acount in after_by_rule.items():
            if code not in before_by_rule and acount:
                if ai_on:
                    result['needs_ai_fix'] += acount
                else:
                    result['needs_manual'] += acount
                result['remaining_by_rule'][code] = acount
        return result

    def fix_file(self, file_path: Path, issues: List[Issue]) -> Tuple[bool, int]:
        """
        Исправление одного файла (детерминированный конвейер DS_053).

        Порядок: issue-fixes (SQL/RuleEngine → backup) → DeterministicFixer
        (переменные). Возвращает (изменён_ли_файл, количество_исправлений).
        """
        # Читаем файл с определением кодировки.
        try:
            text, enc = read_file_with_encoding(Path(file_path))
        except Exception as e:
            logger.warning(f"[FIXER] Не удалось прочитать {file_path}: {e}")
            text, enc = None, 'utf-8'
        if text is None:
            text = ''

        # DS_053_Уточнение: BOM на выходе — только если он был на входе.
        # utf-8-sig при записи всегда добавляет BOM, что ломает файлы без BOM.
        try:
            has_bom = Path(file_path).read_bytes().startswith(b'\xef\xbb\xbf')
        except Exception:
            has_bom = enc == 'utf-8-sig'
        if enc == 'utf-8-sig' and not has_bom:
            enc = 'utf-8'

        lines = text.splitlines(keepends=True)

        # 1. Детерминированные исправления по issues (SQL + backup).
        lines, issue_changes = self._apply_issue_fixes(lines, issues)

        # Сохраняем изменения по issues обратно в файл результата.
        if issue_changes:
            try:
                with open(file_path, 'w', encoding=enc, newline='') as f:
                    f.write(''.join(lines))
            except Exception as e:
                logger.warning(f"[FIXER] Не удалось записать {file_path}: {e}")

        # 2. DeterministicFixer (переименование переменных, неиспользуемые).
        det_fixer = DeterministicFixer()
        result = det_fixer.fix_file(str(file_path))
        det_changes = result.get('changes', [])

        # Статистика и changelog по исправлениям issues.
        for ch in issue_changes:
            self.stats[ch['rule_code']] = self.stats.get(ch['rule_code'], 0) + 1
            self.fixed_issues.append({
                'file': str(file_path),
                'line_num': ch['line_number'],
                'issue_type': ch['rule_code'],
                'bucket': ch['bucket'],
                'kind': ch['kind'],
                'original_code': ch['before'],
                'fixed_code': ch['after'],
                'timestamp': datetime.now().isoformat(),
            })

        # Статистика по правкам DeterministicFixer (как раньше).
        if result.get('modified', False):
            for change in det_changes:
                if 'old_name' in change:
                    self.stats['PlpCheck.STYLE.PREFIX_TYPE.п.4.4'] = self.stats.get('PlpCheck.STYLE.PREFIX_TYPE.п.4.4', 0) + change.get('count', 0)
                elif 'deleted' in change:
                    self.stats['PlpCheck.STYLE.NOT_MENTIONED.п.4.8'] = self.stats.get('PlpCheck.STYLE.NOT_MENTIONED.п.4.8', 0) + change.get('count', 0)

        if issue_changes or result.get('modified', False):
            self.changes_log.append({
                'file': str(file_path),
                'iteration': self.iteration,
                'timestamp': datetime.now().isoformat(),
                'issues_fixed': len(issue_changes) + len(det_changes),
                'types': sorted({ch['rule_code'] for ch in issue_changes}),
            })

        return (bool(issue_changes) or result.get('modified', False),
                len(issue_changes) + len(det_changes))
    
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
    
    def fix_directory(self, scanner: PLPlusScanner, results_dir: Path, log_callback=None, log_level: str = 'Минимальный', fix_only_found: bool = False):
        """
        Исправление всех файлов в директории.
        log_callback - функция для вывода сообщений в журнал (опционально).
        log_level - уровень логирования ('Минимальный' или 'Подробный').
        fix_only_found - если True, выводить только найденные строки в специальном формате.
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

        # DS_053: verification-сканер (тот же конфиг/правила, что и основной)
        # для повторного скана исправленных файлов.
        try:
            self._verify_scanner = PLPlusScanner(
                scanner.config,
                scanner.selected_rules,
                scanner.rubricator_prompts,
                scanner.plpcheck_categories,
            )
        except Exception as e:
            logger.warning(f"[FIXER] Не удалось создать verification-сканер: {e}")
            self._verify_scanner = None
        # Сброс сводной статистики верификации и данных лога.
        self.verify_stats = {
            'total_files': total_files, 'total_fixes': 0,
            'fixed': 0, 'needs_manual': 0, 'needs_ai_fix': 0,
            'by_rule': {}, 'top_rules': [],
        }
        self.scan_log_data = []
        
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

            # DS_053: верификация повторным сканом + сбор данных для лога.
            verify = self._verify_file(results_path, issues)
            self.verify_stats['fixed'] += verify['fixed']
            self.verify_stats['needs_manual'] += verify['needs_manual']
            self.verify_stats['needs_ai_fix'] += verify['needs_ai_fix']
            for code, cnt in verify['by_rule'].items():
                self.verify_stats['by_rule'][code] = self.verify_stats['by_rule'].get(code, 0) + cnt
            self.verify_stats['total_fixes'] += fix_count

            # Исправления «было/стало» текущего файла (из fixed_issues).
            line_logs = [
                {'line_number': fx['line_num'], 'rule_code': fx['issue_type'],
                 'bucket': fx.get('bucket', ''), 'kind': fx.get('kind', ''),
                 'before': fx['original_code'], 'after': fx['fixed_code']}
                for fx in self.fixed_issues if fx['file'] == str(results_path)
            ]
            self.scan_log_data.append({
                'file': str(results_path),
                'plan': sorted({it.issue_type for it in issues}),
                'line_logs': line_logs,
                'stats': dict(verify['by_rule']),
                'remaining_by_rule': dict(verify['remaining_by_rule']),
                'fixed': verify['fixed'],
                'needs_manual': verify['needs_manual'],
                'needs_ai_fix': verify['needs_ai_fix'],
            })

            if log_callback:
                log_callback(f"    Верификация: fixed={verify['fixed']}, "
                             f"needs_manual={verify['needs_manual']}, "
                             f"needs_ai_fix={verify['needs_ai_fix']}")

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
                # Файл результата остаётся как копия оригинала (даже если нет изменений)
                
                # Формируем сообщение о причине пропуска
                skip_reason = ""
                if self.skipped_in_comment > 0:
                    skip_reason = f" (в комментариях: {self.skipped_in_comment})"
                if self.skipped_in_string > 0:
                    skip_reason += f" (в строках: {self.skipped_in_string})"
                
                if log_callback:
                    log_callback(f"  [i] Нет исправлений{skip_reason} (файл сохранён: {results_path.name})")
                else:
                    print(f"  [i] Нет исправлений{skip_reason} (файл сохранён: {results_path.name})")
                
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

    def save_scan_log(self, logs_dir: Path, source_name: str,
                      timestamp: Optional[str] = None) -> Optional[Path]:
        """Запись лога сканирования/фиксации scan_VVxVVx_<source>_<timestamp>.md.

        VVxVVx — подпись флагов (V — выбран, x — нет) в порядке FLAG_ORDER.
        Для каждого файла: PLAN (коды правил), блоки «было/стало» с кодом
        правила (КР) и номером строки, статистика fixed/needs_manual/
        needs_ai_fix и остаток по правилам. В конце — сводка.
        """
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            logs_dir = Path(logs_dir)
            logs_dir.mkdir(parents=True, exist_ok=True)
            fname = self.rule_engine.log_name(source_name, timestamp, self.flags)
            log_path = logs_dir / fname
            # Гарантируем существование каталога именно для финального пути
            # (robustness на случай иного каталога в log_path).
            os.makedirs(os.path.dirname(str(log_path)), exist_ok=True)
        except Exception as e:
            logger.warning(f"[FIXER] Не удалось сформировать путь лога: {e}")
            return None

        vs = self.verify_stats

        lines: List[str] = []
        lines.append(f"Отчёт сканирования: {fname}")
        lines.append("")
        lines.append("Активные рубрикаторы и флаги:")
        lines.append(f"  Рубрикаторы: 4.RUBRICATOR_PROMPT v5.json, "
                     f"5.RUBRICATOR_PARSER_SQL v5.json ({getattr(self.rule_engine, 'version', 'N/A')})")
        lines.append("")
        # DS_053_Уточнение_5 (задача B): блок флагов с расшифровкой.
        lines.extend(_fix_flags_block(self.flags, indent='  '))
        lines.append("")
        lines.append(f"**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Источник**: {source_name}")
        lines.append("")

        # Сводная статистика.
        lines.append("Сводная статистика:")
        lines.append("")
        lines.append(f"  Всего файлов: {vs.get('total_files', len(self.scan_log_data))}")
        lines.append(f"  Всего исправлений: {vs.get('total_fixes', 0)}")
        lines.append(f"  Подтверждено исправлено (повторный скан): {vs.get('fixed', 0)}")
        lines.append(f"  needs_manual: {vs.get('needs_manual', 0)}")
        lines.append(f"  needs_ai_fix: {vs.get('needs_ai_fix', 0)}")
        top = sorted(vs.get('by_rule', {}).items(), key=lambda x: -x[1])[:5]
        if top:
            lines.append("  Топ-5 правил: " + ", ".join(f"{c} ({n})" for c, n in top))
        lines.append("")

        # DS_053_Уточнение_2 (задача D): МД — максимальная длина кода правила
        # среди правил текущего прогона (все КР, попавшие в line_logs).
        # Используется для выравнивания колонок «>» и нового кода (Схема A).
        all_codes = [ll.get('rule_code', '')
                     for fd in self.scan_log_data for ll in fd.get('line_logs', [])]
        md = max((len(c) for c in all_codes), default=0)
        before_dots = '.' * (md + 1)

        # Детализация по файлам.
        lines.append("## Файлы")
        lines.append("")
        for fd in self.scan_log_data:
            fname_disp = Path(fd['file']).name
            lines.append(f"### {fname_disp}")
            lines.append("")
            plan = fd.get('plan', [])
            lines.append(f"**PLAN**: {', '.join(f'`{c}`' for c in plan) if plan else '—'}")
            lines.append("")
            # Устойчивая сортировка по номеру строки (порядок правил внутри
            # строки сохраняется).
            line_logs = sorted(fd.get('line_logs', []), key=lambda x: x['line_number'])
            if line_logs:
                # Группировка по номеру строки; блоки НЕ разделять пустыми
                # строками (Схема A). Одна строка «до» (исходник) + по одной
                # строке «после» на каждое правило строки.
                i = 0
                while i < len(line_logs):
                    ln = line_logs[i]['line_number']
                    group = []
                    while i < len(line_logs) and line_logs[i]['line_number'] == ln:
                        group.append(line_logs[i])
                        i += 1
                    lines.append(f"Строка {ln}:")
                    first_before = (group[0].get('before', '') or '').rstrip()
                    lines.append(f"{before_dots}> {first_before}")
                    for ll in group:
                        after = (ll.get('after', '') or '').rstrip()
                        tag = f"<{ll['rule_code']}>".ljust(md + 2)
                        lines.append(f"{tag} {after}")
                lines.append("")
            else:
                lines.append("_Детерминированных исправлений по строкам нет._")
                lines.append("")
            stats = fd.get('stats', {})
            lines.append("Статистика по файлу:")
            for code, cnt in sorted(stats.items(), key=lambda x: (-x[1], x[0])):
                if cnt:
                    lines.append(f"  {code}: {cnt}")
            lines.append(f"  needs_ai_fix: {fd.get('needs_ai_fix', 0)}")
            lines.append(f"  needs_manual: {fd.get('needs_manual', 0)}")
            lines.append("")
            rem = fd.get('remaining_by_rule', {})
            if rem:
                lines.append("**Остаток по правилам (не исправлено)**:")
                lines.append("")
                for code, cnt in sorted(rem.items(), key=lambda x: (-x[1], x[0])):
                    lines.append(f"- `{code}`: {cnt}")
                lines.append("")

        try:
            text = '\r\n'.join(lines) + '\r\n'
            with open(log_path, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
            return log_path
        except Exception as e:
            logger.warning(f"[FIXER] Не удалось записать лог {log_path}: {e}")
            return None

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
                    # Получаем теги из рубрикатора (в v5.0.0 есть tags, используем их)
                    tags_info = ""
                    full_desc = ""
                    if self.rubricator:
                        rubric_rule = self.rubricator.get_rule_by_code(issue_type)
                        if rubric_rule:
                            # В v5.0.0 есть category — используем её
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
            'exclude_patterns': ['.bak', '.tmp']
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


def parse_koda_response(response: str, clean_mode: bool = False) -> dict:
    """
    Разбирает ответ KODA на код и журнал изменений
    
    Args:
        response: полный ответ KODA
        clean_mode: если True, возвращает только чистый код
        
    Returns:
        dict: {'code': исправленный код, 'changelog': журнал изменений}
    """
    if not clean_mode or not response:
        return {'code': response or '', 'changelog': None}
    
    code = response
    changelog = None
    
    # Ищем маркер начала журнала
    changelog_marker = '### Журнал изменений'
    if changelog_marker in response:
        parts = response.split(changelog_marker, 1)
        code = parts[0].strip()
        changelog = changelog_marker + parts[1]
    
    # Очищаем код от маркеров изменений
    # 1. Удаляем --(*)PlpCheck.*
    code = re.sub(r'--\(\*\)PlpCheck\.[^\n]*\n', '', code)
    
    # 2. Удаляем --OLD <дата>
    code = re.sub(r'--OLD \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\n', '', code)
    
    # 3. Удаляем строки вида "--- old code"
    code = re.sub(r'^--- [^\n]*\n', '', code, flags=re.MULTILINE)
    
    # 4. Удаляем маркеры <<< и >>> (включая возможное пространство перед ними и в конце строки)
    code = re.sub(r'\s*<<<\s*\n', '', code)
    code = re.sub(r'\s*>>>\s*\n', '', code)
    
    # 5. Удаляем строки с -- старый код (но оставляем комментарии с --)
    # Удаляем только строки вида "-- <код>", оставляем "-- комментарий"
    code = re.sub(r'^-- [a-zA-Z0-9_\[\]\(\)\.:=\s,|\'\"]+\n', '', code, flags=re.MULTILINE)
    
    # 6. Удаляем >>> в конце строки (после кода)
    code = re.sub(r'\s*>>>\s*$', '', code, flags=re.MULTILINE)
    
    # 7. Удаляем пустые строки в начале и конце
    code = code.strip()
    
    # 8. Удаляем дубликаты пустых строк (более 2 подряд)
    code = re.sub(r'\n{3,}', '\n\n', code)
    
    return {
        'code': code,
        'changelog': changelog
    }


def generate_changelog(issues: List, changes: List[dict], filename: str = '') -> str:
    """
    Генерирует журнал изменений на основе найденных проблем и примененных исправлений
    
    Args:
        issues: список найденных проблем
        changes: список примененных изменений
        filename: имя обработанного файла
        
    Returns:
        str: отформатированный журнал в Markdown
    """
    from datetime import datetime
    
    changelog = f"""# Журнал изменений
**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Файл:** {filename}
**Всего изменений:** {len(changes)}

## Журнал изменений
| № | Строка | Правило | Было | Стало | Обоснование |
|---|--------|---------|------|-------|-------------|
"""
    
    for idx, change in enumerate(changes, 1):
        line_num = change.get('line', 'N/A')
        rule = change.get('rule', 'N/A')
        old_code = change.get('old', 'N/A')
        new_code = change.get('new', 'N/A')
        reason = change.get('reason', 'N/A')
        
        changelog += f"| {idx} | {line_num} | {rule} | {old_code} | {new_code} | {reason} |\n"
    
    # Статистика по приоритетам
    high = sum(1 for i in issues if getattr(i, 'priority', 'MEDIUM') == 'HIGH')
    medium = sum(1 for i in issues if getattr(i, 'priority', 'MEDIUM') == 'MEDIUM')
    low = sum(1 for i in issues if getattr(i, 'priority', 'MEDIUM') == 'LOW')
    
    changelog += f"""
## Статистика
- **Всего изменений:** {len(changes)}
- **HIGH:** {high}
- **MEDIUM:** {medium}
- **LOW:** {low}
"""
    
    return changelog


if __name__ == '__main__':
    main()


# ============================================================
# DS_053_Уточнение_3 (задача A): лог scan_VVxVVx_* при «Сканировать»
# ============================================================

def get_backup_fix_codes() -> List[str]:
    """Коды backup-правил (без инстанцирования фиксерa)."""
    try:
        return list(PLPlusFixer._get_default_fixes(None).keys())
    except Exception:
        return []


def save_scan_only_log(logs_dir: Path, source_name: str, flags: Dict[str, bool],
                       scanner: 'PLPlusScanner', config: Dict,
                       timestamp: Optional[str] = None,
                       log_level: str = 'Минимальный',
                       report_stats_min_files: int = 10) -> Optional[Path]:
    """DS_053_Уточнение_4 (задача A): лог scan_VVxVVx_<source>_<ts>.md при
    «Сканировать» — ПРОГНОЗ исправлений (симуляция конвейера без записи).

    - issues сканера прогоняются через тот же детерминированный конвейер,
      что при фиксе (_apply_issue_fixes: RuleEngine regex+hybrid → backup
      FIXES), в памяти (dry-run): исходный файл НЕ изменяется;
    - лог: заголовок (рубрикаторы, флаги, дата, источник) + режим
      «прогноз исправлений, без записи» + PLAN (сработавшие КР-коды) +
      блок «Прогноз:» с парами «> было / <КР> станет» по Схеме A
      (DS_053_Уточнение_2, задача D) + статистика по сработавшим правилам;
    - если ни один флаг не активен: заголовок + пометка «флаги не выбраны»,
      имя файла — scan_xxxxxx_... (все флаги = x).

    Args:
        logs_dir: каталог логов (F:\TO_DBI\logs).
        source_name: имя источника (каталог сканирования).
        flags: текущие 6 флагов.
        scanner: сканер с результатами (issues) сканирования.
        config: конфиг (как у сканера; нужен для инстанса фиксерa).
    """
    eng = get_rule_engine()
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        logs_dir = Path(logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)
        fname = eng.log_name(source_name, timestamp, flags)
        log_path = logs_dir / fname
        os.makedirs(os.path.dirname(str(log_path)), exist_ok=True)
    except Exception as e:
        logger.warning(f"[FIXER] Не удалось сформировать путь scan-only лога: {e}")
        return None

    any_flag = eng.any_replacement_flag(flags)
    lines: List[str] = []
    lines.append(f"Отчёт сканирования: {fname}")
    lines.append("")
    # DS_059_Уточнение_B: блок «Активные рубрикаторы и флаги» — точно как в
    # scan_report_*: переиспользуем _generate_active_rubricators_lines
    # сканера (рубрикаторы ВКЛ/ВЫКЛ + подкатегории PlpCheck + флаги с
    # расшифровками). Фолбэк — прежний заголовок с именами файлов.
    try:
        lines.extend(scanner._generate_active_rubricators_lines())
    except Exception as e:
        logger.warning(f"[FIXER] Блок рубрикаторов из сканера недоступен: {e}")
        lines.append("Активные рубрикаторы и флаги:")
        lines.append(f"  Рубрикаторы: 4.RUBRICATOR_PROMPT v5.json, "
                     f"5.RUBRICATOR_PARSER_SQL v5.json ({getattr(eng, 'version', 'N/A')})")
        lines.append("")
        # DS_053_Уточнение_5 (задача B): блок флагов с расшифровкой.
        lines.extend(_fix_flags_block(flags, indent='  '))
    lines.append("")
    lines.append(f"**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Источник**: {source_name}")
    lines.append("")
    lines.append("Режим: сканирование (прогноз исправлений, без записи)")
    lines.append("")

    if not any_flag:
        # Ни один флаг не активен: пустой лог с пометкой.
        lines.append("Флаги не выбраны.")
        lines.append("")
    else:
        # --- Симуляция конвейера (dry-run, без записи в файлы) ---
        sim_fixer = PLPlusFixer(config, 'scan_forecast')
        sim_fixer.flags = dict(flags)
        issues_by_file = scanner.get_issues_by_file()
        source_dir_str = str(config.get('paths', {}).get('source_dir', '') or '')
        sim_files: List[Dict] = []
        skipped: List[str] = []  # диагностика пропусков (DS_053_Уточнение_5)
        for file_path_str, issues in issues_by_file.items():
            if not issues:
                continue
            fp = Path(file_path_str)
            if not fp.exists():
                # Устойчивый резолвинг (DS_053_Уточнение_5, задача A):
                # путь из issues может не существовать в контексте АРМ
                # (другой диск/регистр/относительный путь). Пробуем варианты.
                candidates = [
                    fp.resolve() if fp.is_absolute() else None,
                    Path(source_dir_str) / fp if source_dir_str else None,
                    Path(source_dir_str) / fp.name if source_dir_str else None,
                ]
                found = None
                for cand in candidates:
                    try:
                        if cand and cand.exists():
                            found = cand
                            break
                    except OSError:
                        continue
                if not found and source_dir_str:
                    # Поиск по имени файла в source_dir (один уровень рекурсии
                    # допустим: набор файлов небольшой).
                    try:
                        matches = list(Path(source_dir_str).rglob(fp.name))
                        if matches:
                            found = matches[0]
                    except OSError:
                        pass
                if not found:
                    skipped.append(f"{file_path_str}: файл не найден ({len(issues)} issues)")
                    continue
                fp = found
            try:
                text, enc = read_file_with_encoding(fp)
            except Exception as e:
                skipped.append(f"{fp}: ошибка чтения ({e})")
                continue
            file_lines = (text or '').splitlines(keepends=True)
            # dry-run: изменения только в памяти (copy of lines), файл не
            # перезаписывается — прогноз не трогает исходник.
            _, changes = sim_fixer._apply_issue_fixes(
                list(file_lines), issues, dry_run=True)
            sim_files.append({'file': str(fp), 'changes': changes})
            # Прогноз не пишет статистику в общий state фиксерa —
            # собираем локально.

        if skipped:
            lines.append("_Пропущенные файлы (диагностика):_")
            lines.append("")
            for s in skipped:
                lines.append(f"  - {s}")
            lines.append("")

        # Сводка по всем файлам.
        all_changes = [ch for sf in sim_files for ch in sf['changes']]
        plan_codes = sorted({ch['rule_code'] for ch in all_changes})

        # Дефект 4 (DS_066 §3.4, вариант A): PLAN = ВСЕ issues из scan_report_*.
        # DS_067 §3: колонка LINE — ПЕРВАЯ, сортировка по LINE. DS_067_Уточнение_A
        # §3.3: внутри одного LINE — порядок по № из scan_report_* (= порядок
        # обнаружения в scanner.issues; стабильная сортировка сохраняет его).
        # Пометка [auto] — правило сработало в dry-run конвейера, [ignore] —
        # найдено сканером, но не автофиксится.
        plan_codes_set = set(plan_codes)
        seen_keys = set()
        dedup_issues = []
        for iss in scanner.issues:
            key = (iss.file_path, iss.line_number, iss.issue_type, iss.description)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            dedup_issues.append(iss)
        plan_rows = []
        # DS_067_Уточнение_B: порядок внутри LINE — по № из scan_report_*,
        # т.е. по ключу сортировки отчёта сканера (scanner.generate_report):
        # (line, not_mentioned первым, алфавит check) — см. scanner.py:2008.
        def _plan_sort_key(iss):
            nm_first = 0 if iss.issue_type.lower().endswith('not_mentioned') else 1
            return (iss.line_number, nm_first, iss.issue_type)
        for iss in sorted(dedup_issues, key=_plan_sort_key):
            try:
                action = scanner._generate_plan(iss.issue_type, iss.description)
            except Exception:
                action = 'Исправить по описанию'
            tag = '[auto]' if iss.issue_type in plan_codes_set else '[ignore]'
            # DS_067: LINE первой колонкой; действие уже со стрелкой «> »
            plan_rows.append(f"{iss.line_number} {tag} {action}")
        lines.append("PLAN:")
        lines.append("LINE AUTO ДЕЙСТВИЕ")
        lines.extend(plan_rows)
        lines.append("")
        lines.append(f"Правил в PLAN: {len(plan_rows)}")
        lines.append("")

        # DS_059_Уточнение_D: пояснение о правилах в ignore — найдены
        # сканером, но не автофиксятся конвейером (нет детерминированного
        # transform в PARSER_SQL либо корзина ignore).
        all_issue_codes = {it.issue_type for iss in issues_by_file.values()
                           for it in iss}
        ignored_codes = sorted(c for c in all_issue_codes
                               if c not in set(plan_codes))
        if ignored_codes:
            lines.append(f"Правил в ignore (не автофиксятся): {len(ignored_codes)}")
            for c in ignored_codes:
                lines.append(f"  {c}")
            lines.append("")

        # DS_067 §4: «Прогноз» — ВСЕ строки-мишени из scan_report_* (по LINE),
        # цепочка правил на строку. Итоговый текст: auto — из dry-run changes;
        # not_mentioned / code_in_comment — «(удалить строку)» (заглушка §5.2,
        # диапазона в Issue нет), цепочка обрывается; переименования — замена
        # match_fragment на новое имя из действия PLAN; иначе — заглушка AI
        # (§5.1, needs_ai_fix в Issue нет).
        # МКР = max(len(код)) + 1 — по кодам правил файла (формат B, §4.4).
        dedup_by_file: Dict[str, List] = {}
        for iss in dedup_issues:
            dedup_by_file.setdefault(iss.file_path, []).append(iss)

        for sf in sim_files:
            fpath = sf['file']
            f_issues = dedup_by_file.get(fpath) or dedup_by_file.get(
                str(Path(fpath).resolve()), [])
            if not f_issues:
                # Устойчивый резолвинг: сравнение по имени файла (DS_053_Уточнение_5)
                fname = Path(fpath).name
                for k, v in dedup_by_file.items():
                    if Path(k).name == fname:
                        f_issues = v
                        break
            if not f_issues:
                continue
            # Полный текст строк файла (для строки 1 блока).
            try:
                ftext, _ = read_file_with_encoding(Path(fpath))
                f_lines = (ftext or '').splitlines()
            except Exception:
                f_lines = []
            # Очередь dry-run изменений по (line, code) — по порядку.
            changes_q: Dict[Tuple[int, str], List[Dict]] = {}
            for ch in sf['changes']:
                changes_q.setdefault((ch['line_number'], ch['rule_code']),
                                     []).append(ch)

            lines.append(f"### {Path(fpath).name}")
            lines.append("")
            lines.append("Прогноз:")
            # МКР по кодам правил файла (все issues, формат B — полный код).
            mkr = max((len(i.issue_type) for i in f_issues), default=0) + 1
            # Группировка по LINE (одна строка = один блок, §4.3 п.2). Внутри
            # LINE — порядок по № из scan_report_* (§3.2: ключ сортировки
            # отчёта сканера — not_mentioned первым, затем алфавит check).
            by_line: Dict[int, List] = {}
            for iss in sorted(f_issues, key=_plan_sort_key):
                by_line.setdefault(iss.line_number, []).append(iss)
            for ln in sorted(by_line):
                group = by_line[ln]

                def _is_delete(iss, action=None):
                    """DS_067_Уточнение_A §3.1: issue с действием удаления."""
                    itl = iss.issue_type.lower()
                    if 'not_mentioned' in itl or 'code_in_comment' in itl:
                        return True
                    act = action
                    if act is None:
                        try:
                            act = scanner._generate_plan(iss.issue_type,
                                                         iss.description)
                        except Exception:
                            act = ''
                    return 'удалить' in act.lower()

                # §3.1: приоритет удаления — если среди issues строки есть
                # удаление, выводим ТОЛЬКО его (первое по №); переименования в
                # удаляемой строке не имеют смысла.
                delete_idx = None
                for di, d_iss in enumerate(group):
                    if _is_delete(d_iss):
                        delete_idx = di
                        break
                if delete_idx is not None:
                    group = [group[delete_idx]]

                # Строка 1 блока: полный текст строки (без обрезки, §4.3 п.5).
                src_text = (f_lines[ln - 1].strip() if ln - 1 < len(f_lines)
                            else (group[0].original_code or '').strip())
                lines.append(f"Строка {ln}:")
                lines.append(f"{'.' * mkr}> {src_text}")
                # Цепочка правил (по порядку из scan_report_*).
                current = src_text
                for iss in group:
                    code = iss.issue_type
                    # a. dry-run change (auto) — итоговый текст после конвейера.
                    q = changes_q.get((ln, code))
                    after = None
                    if q:
                        after = (q.pop(0).get('after') or '').strip()
                    if after is not None:
                        current = after
                        result_text = after
                    else:
                        itl = code.lower()
                        try:
                            action = scanner._generate_plan(code, iss.description)
                        except Exception:
                            action = ''
                        # b. удаление — заглушка диапазона (§5.2) + обрыв цепочки.
                        if _is_delete(iss, action):
                            # §3.4: not_mentioned → «(удалить объявление)»,
                            # code_in_comment → «(удалить строку)».
                            if 'not_mentioned' in itl:
                                result_text = '(удалить объявление)'
                            else:
                                # DS_069 §3.3: многострочный блок /* ... */ —
                                # «(удалить диапазон строк N–M)»; иначе строка.
                                if (iss.issue_type.lower().endswith('code_in_comment')
                                        and getattr(iss, 'block_end', 0)
                                        > getattr(iss, 'block_start', 0)):
                                    result_text = (f'(удалить диапазон строк '
                                                   f'{iss.block_start}–{iss.block_end})')
                                else:
                                    result_text = '(удалить строку)'
                        else:
                            # c. переименование: замена match_fragment на новое имя.
                            m = re.search(r'Переименовать в ["\']([^"\']+)["\']',
                                          action)
                            old = getattr(iss, 'match_fragment', '') or ''
                            if m and old:
                                new_text = re.sub(
                                    rf'\b{re.escape(old)}\b', m.group(1),
                                    current, count=1)
                                if new_text != current:
                                    current = new_text
                                    result_text = new_text
                                else:
                                    result_text = (
                                        '[AI] Требуется AI-анализ: <не реализовано>')
                            else:
                                # d. заглушка AI (§5.1).
                                result_text = ('[AI] Требуется AI-анализ: '
                                               '<не реализовано>')
                    # Строка N: <[код][пробелы]> [пробел]<итоговый текст> (§4.2).
                    pad = max(mkr - 1 - len(code), 0)
                    lines.append(f"<{code}{' ' * pad}> {result_text}")
                lines.append("")  # пустая строка между блоками (§4.3 п.6)
            # Статистика по файлу: ВСЕ коды issues, убывание, при равенстве —
            # алфавит (§4.5).
            f_stats: Dict[str, int] = {}
            for iss in f_issues:
                f_stats[iss.issue_type] = f_stats.get(iss.issue_type, 0) + 1
            lines.append("Статистика по файлу:")
            for code, cnt in sorted(f_stats.items(), key=lambda x: (-x[1], x[0])):
                lines.append(f"  {code}: {cnt}")
            lines.append("")

        # Итоговая статистика (§4.5): по всем файлам сканирования.
        # DS_075 §3.1: счётчики режимов (scan-only: Исправлено=0, forecast —
        # число dry-run изменений, В AI — дедуп-issues минус forecast).
        _forecast = len(all_changes)
        _ai = max(0, len(dedup_issues) - _forecast)
        # DS_077: две строки проблем (с дублями + после дедупа), условно
        _issues_before_dedup = getattr(scanner, 'issues_before_dedup', 0)
        if _issues_before_dedup != len(dedup_issues):
            lines.append(f"Всего проблем (с дублями): {_issues_before_dedup}")
        lines.append(f"Всего проблем: {len(dedup_issues)}")
        lines.append(f"Прогноз исправлений: {_forecast}")
        lines.append("Исправлено: 0")
        lines.append(f"В AI: {_ai}")
        # DS_076 §4.1–4.2: три унифицированные метрики файлов (как в
        # scan_report_*): всего / с проблемами / с dry-run changes.
        # «Всего файлов» — scanner.total_files (найдено после _should_exclude);
        # при прерывании — «Обработано файлов» = scanner.files_scanned.
        # Фолбэк (scan_directory не вызывался): len(sim_files).
        _files_total = getattr(scanner, 'total_files', 0) or len(sim_files)
        _files_issues = len(dedup_by_file)
        _files_changed = len([sf for sf in sim_files if sf['changes']])
        if getattr(scanner, 'abort_percent', None) is not None:
            lines.append(f"Обработано файлов: "
                         f"{getattr(scanner, 'files_scanned', 0) or _files_total}")
        else:
            lines.append(f"Всего файлов: {_files_total}")
        lines.append(f"Файлов с проблемами: {_files_issues}")
        lines.append(f"Файлов с изменениями: {_files_changed}")
        lines.append("")
        # DS_075 §3.2: топ-файлы (2 лидера) при «Подробный» + файлов >= порог.
        try:
            _top = scanner._top_files_lines(log_level, report_stats_min_files)
            if _top:
                lines.extend(_top)
        except Exception as e:
            logger.warning(f"[FIXER] Топ-файлы в scan-only логе недоступны: {e}")
        lines.append("")

    try:
        text = '\r\n'.join(lines) + '\r\n'
        with open(log_path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        return log_path
    except Exception as e:
        logger.warning(f"[FIXER] Не удалось записать scan-only лог {log_path}: {e}")
        return None