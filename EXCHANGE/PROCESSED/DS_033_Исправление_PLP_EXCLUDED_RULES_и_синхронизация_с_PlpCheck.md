DS_033 — Исправление PLP_EXCLUDED_RULES и синхронизация с ЦФТ-PlpCheck
Метаданные задачи
Параметр	Значение
Код задачи	DS_033
Проект	АРМ «Адаптация под DBI» (Народный банк)
Предыдущая задача	DS_032 (синхронизация лога с эталонным ЦФТ-PlpCheck)
Приоритет	CRITICAL
Статус	К выполнению
Исполнитель	KODA (VS Code)
Репозиторий	F:\TO_DBI\
Файл сканера	F:\TO_DBI\scanner.py
Тестовый файл	F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1\src\ENTITY\HOOK_BANK\REPS_EXP_115_1.plp
Эталонный лог	plpcheck-report HOOK_BANK.REPS_EXP_115_1.txt (14 проблем)
Контекст проблемы
Симптом
После применения правок DS 032 сканер АРМа возвращает 0 проблем вместо ожидаемых 14.

Текущий отчёт (scan_report_patch_REPS_EXP_115_1_20260912_144949.md):

text
CFT Platform IDE Version: 2.36.431 (АРМ «Адаптация под DBI»)
Дата: 2026-09-12 14:49:49
Проблем не найдено.
Диагноз
Выявлены три критические ошибки, внесённые в ходе DS 032:

№	Ошибка	Последствие
1	В PLP_EXCLUDED_RULES ошибочно добавлены правила BAD_PREFIX, NOT_MENTIONED, WRONG_METHOD_SYNTAX, CODE_IN_COMMENT, PREFIX_TYPE_IN_VAR_NAME, OUTER_JOIN	Отключены нужные проверки PlpCheck
2	В _check_multiline_* методах используется паттерн r'^\s+(\w+)...' (требует минимум 1 пробел в начале строки)	Все объявления в REPS_EXP_115_1.plp начинаются с начала строки (0 пробелов) → паттерн не срабатывает
3	Отсутствует отладочный вывод для диагностики	Невозможно быстро локализовать проблему
Корневая причина
В файле REPS_EXP_115_1.txt объявления переменных выглядят так (без отступа):

text
dp   integer:=0;			--управление debug_pipe
dp1  integer:=0;			--управление debug_pipe

fmt	   string(10):='dd/mm/yyyy';
fmt24  string(22):='dd/mm/yyyy HH24:MI:SS';
fmtHMS string(22):='dd/mm/yyyy HH24:MI:SS';
Регулярное выражение ^\s+ (минимум 1 пробел) не находит эти объявления.

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
Задачи KODA
ЗАДАЧА 1 — Исправить PLP_EXCLUDED_RULES
Файл: F:\TO_DBI\scanner.py

Действие: Найти константу PLP_EXCLUDED_RULES и заменить её полностью на следующий набор:

python
# ============================================================
# DS 033: ПРАВИЛА, НЕ ПРИМЕНИМЫЕ К .plp ФАЙЛАМ
# ВАЖНО: НЕ включать сюда BAD_PREFIX, NOT_MENTIONED, WRONG_METHOD_SYNTAX,
# CODE_IN_COMMENT, PREFIX_TYPE_IN_VAR_NAME, OUTER_JOIN — они НУЖНЫ!
# ============================================================
PLP_EXCLUDED_RULES: Set[str] = {
    # Ложные срабатывания (парсер не понимает PL+ синтаксис)
    'plpcheck.SYNTAX_ERROR',
    'plpcheck.VARIABLE_SAME_NAME',
    'plpcheck.NO_RECURSION_COMMENT',
    'plpcheck.VBS_LINKING_ERROR',
    'plpcheck.PURE_UDF',
    'plpcheck.PURE_SQL_DBLINK',
    # Только для чистого SQL (не для .plp)
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
    # Ложные срабатывания на PL+ синтаксис
    'plpcheck.METH_PARAM_AND_VAR_NAMES',
    'plpcheck.METH_PARAM_AND_VAR_FULL_NAMES',
    'plpcheck.WRONG_LOCAL_PREFIX',
    'plpcheck.WRONG_CLASS_SYNTAX',
    'plpcheck.WRONG_ATTR_SYNTAX',
    'plpcheck.REF_NONTABLE',
    'plpcheck.RESERVED_PREFIX',
    'plpcheck.CONCAT_CONTROL',
    'plpcheck.MACRO_CALL_EXECUTEPROCESS',
    'plpcheck.PLATFORM_INTEGER_MISMATCH',
    'plpcheck.ACCESS_STATIC',
}
Критерий приёмки: Убедиться, что в PLP_EXCLUDED_RULES НЕТ следующих правил:

❌ plpcheck.BAD_PREFIX

❌ plpcheck.NOT_MENTIONED

❌ plpcheck.WRONG_METHOD_SYNTAX

❌ plpcheck.CODE_IN_COMMENT

❌ plpcheck.PREFIX_TYPE_IN_VAR_NAME

❌ plpcheck.OUTER_JOIN

ЗАДАЧА 2 — Исправить паттерны в _check_multiline_* (КРИТИЧНО!)
Файл: F:\TO_DBI\scanner.py

Действие: Во всех методах _check_multiline_bad_prefix, _check_multiline_not_mentioned, _check_multiline_id_size заменить паттерн:

python
# БЫЛО:
match = re.search(r'^\s+(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)

# СТАЛО (^\s* вместо ^\s+):
match = re.search(r'^\s*(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)
Обоснование: В файле REPS_EXP_115_1.plp объявления переменных начинаются с начала строки (0 пробелов), например:

text
dp   integer:=0;
fmt	   string(10):='dd/mm/yyyy';
Критерий приёмки: После правки метод _check_multiline_bad_prefix находит объявления на строках 10, 11, 13, 14, 15, 22, 23.

ЗАДАЧА 3 — Улучшить _check_multiline_not_mentioned (исключение служебных строк)
Файл: F:\TO_DBI\scanner.py

Действие: В методе _check_multiline_not_mentioned при подсчёте использований переменной исключить служебные строки (class, method, @name, pragma):

python
for var_name, decl_line in declared_vars.items():
    var_pattern = re.compile(rf'\b{re.escape(var_name)}\b')
    count = 0
    for i, line in enumerate(lines, 1):
        if i == decl_line:
            continue
        # DS 033: исключаем служебные строки из подсчёта
        stripped_check = line.strip()
        if stripped_check.startswith('--') or stripped_check.startswith('@') or \
           stripped_check.startswith('class') or stripped_check.startswith('method') or \
           stripped_check.startswith('pragma'):
            continue
        count += len(var_pattern.findall(line))
    
    if count == 0:
        original_line = lines[decl_line - 1].strip() if decl_line <= len(lines) else ''
        issues.append((decl_line, original_line, var_name))
Обоснование: Без этого исключения переменные могут ложно считаться использованными, если их имя встречается в объявлениях класса/метода/аннотациях.

ЗАДАЧА 4 — Добавить отладочный вывод в scan_file()
Файл: F:\TO_DBI\scanner.py

Действие: В методе scan_file() сразу после строки print(f"[DEBUG] scan_file: ...") добавить:

python
print(f"[DEBUG-DS033] selected_rules={self.selected_rules}")
print(f"[DEBUG-DS033] PATTERNS загружено: {len(self.PATTERNS)}")
print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.BAD_PREFIX')={self._is_rule_selected('plpcheck.BAD_PREFIX')}")
print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.NOT_MENTIONED')={self._is_rule_selected('plpcheck.NOT_MENTIONED')}")
print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX')={self._is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX')}")
print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.CODE_IN_COMMENT')={self._is_rule_selected('plpcheck.CODE_IN_COMMENT')}")
И в блоках вызова каждой _check_multiline_* проверки добавить логирование количества найденных проблем:

python
if self._is_rule_selected('plpcheck.BAD_PREFIX'):
    print(f"[DEBUG-DS033] Запуск _check_multiline_bad_prefix...")
    bad_prefix_issues = self._check_multiline_bad_prefix(self.lines)
    print(f"[DEBUG-DS033] _check_multiline_bad_prefix нашел: {len(bad_prefix_issues)}")
    # ... остальной код
Аналогично для NOT_MENTIONED, WRONG_METHOD_SYNTAX, CODE_IN_COMMENT.

ЗАДАЧА 5 — Убедиться в наличии всех 4 многострочных проверок в scan_file()
Файл: F:\TO_DBI\scanner.py

Действие: Проверить, что в scan_file() перед except Exception присутствуют вызовы всех 4 проверок:

_check_multiline_bad_prefix → plpcheck.BAD_PREFIX

_check_multiline_not_mentioned → plpcheck.NOT_MENTIONED

_check_multiline_wrong_method_syntax → plpcheck.WRONG_METHOD_SYNTAX

_check_multiline_code_in_comment → plpcheck.CODE_IN_COMMENT

Если какого-то метода нет — создать его по образцу из раздела «Приложение А».

Если блока вызова нет — добавить его по образцу из раздела «Приложение Б».

ЗАДАЧА 6 — Убедиться в наличии маппингов
Файл: F:\TO_DBI\scanner.py

Действие: Проверить наличие трёх словарей на уровне модуля (вне класса):

python
PLPCHECK_RULE_NAMES: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'bad_prefix',
    'plpcheck.NOT_MENTIONED': 'not_mentioned',
    'plpcheck.WRONG_METHOD_SYNTAX': 'wrong_method_syntax',
    'plpcheck.CODE_IN_COMMENT': 'code_in_comment',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'prefix_type_in_var_name',
    'plpcheck.OUTER_JOIN': 'outer_join',
    # ... остальные
}

PLPCHECK_RULE_LEVELS: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'WARNING',
    'plpcheck.NOT_MENTIONED': 'WARNING',
    'plpcheck.WRONG_METHOD_SYNTAX': 'WARNING',
    'plpcheck.CODE_IN_COMMENT': 'WARNING',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'WARNING',
    'plpcheck.OUTER_JOIN': 'WARNING',
    # ...
}

PLPCHECK_RULE_TYPES: Dict[str, str] = {
    'plpcheck.BAD_PREFIX': 'STYLE',
    'plpcheck.NOT_MENTIONED': 'STYLE',
    'plpcheck.WRONG_METHOD_SYNTAX': 'STYLE',
    'plpcheck.CODE_IN_COMMENT': 'STYLE',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'STYLE',
    'plpcheck.OUTER_JOIN': 'SQL',
    # ...
}
Если отсутствуют — добавить.

ЗАДАЧА 7 — Переписать generate_report() для формата ЦФТ-PlpCheck
Файл: F:\TO_DBI\scanner.py

Действие: Заменить метод generate_report() на следующий:

python
def generate_report(self, output_path: Path):
    """
    DS 033: Генерация отчёта в формате ЦФТ-PlpCheck.
    Формат: LINE | CHECK | LEVEL | TYPE | ERROR
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Удаление дубликатов по (file_path, line_number, issue_type, description)
    unique_issues = []
    seen = set()
    for issue in self.issues:
        key = (issue.file_path, issue.line_number, issue.issue_type, issue.description)
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)
    
    # Сортировка: строка -> check -> описание
    unique_issues.sort(key=lambda i: (i.line_number, i.issue_type, i.description))
    
    # Формирование отчёта
    lines = []
    lines.append("PlpCheck Отчёт")
    lines.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Всего проблем: {len(self.issues)}")
    lines.append(f"Уникальных проблем: {len(unique_issues)}")
    lines.append(f"Всего файлов: {len(set(i.file_path for i in self.issues))}")
    lines.append("")
    lines.append("=" * 120)
    lines.append(f"{'LINE':>6} | {'CHECK':<30} | {'LEVEL':<10} | {'TYPE':<10} | ERROR")
    lines.append("=" * 120)
    
    for issue in unique_issues:
        check_name = PLPCHECK_RULE_NAMES.get(issue.issue_type, issue.issue_type)
        level = PLPCHECK_RULE_LEVELS.get(issue.issue_type, getattr(issue, 'level', 'WARNING'))
        type_ru = PLPCHECK_RULE_TYPES.get(issue.issue_type, getattr(issue, 'issue_type_ru', 'STYLE'))
        error_msg = getattr(issue, 'error_message', '') or issue.description
        
        lines.append(f"{issue.line_number:>6} | {check_name:<30} | {level:<10} | {type_ru:<10} | {error_msg}")
    
    lines.append("=" * 120)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Отчёт сохранён: {output_path}")
ЗАДАЧА 8 — Запуск и проверка
Действие:

Запустить сканер на файле F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1\src\ENTITY\HOOK_BANK\REPS_EXP_115_1.plp.

Проверить консольный вывод. Должны быть строки:

text
[DEBUG-DS033] _is_rule_selected('plpcheck.BAD_PREFIX')=True
[DEBUG-DS033] _is_rule_selected('plpcheck.NOT_MENTIONED')=True
[DEBUG-DS033] _is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX')=True
[DEBUG-DS033] _is_rule_selected('plpcheck.CODE_IN_COMMENT')=True
[DEBUG-DS033] Запуск _check_multiline_bad_prefix...
[DEBUG-DS033] _check_multiline_bad_prefix нашел: 9
[DEBUG-DS033] Запуск _check_multiline_not_mentioned...
[DEBUG-DS033] _check_multiline_not_mentioned нашел: 5
[DEBUG-DS033] Запуск _check_multiline_wrong_method_syntax...
[DEBUG-DS033] _check_multiline_wrong_method_syntax нашел: 1
[DEBUG-DS033] Запуск _check_multiline_code_in_comment...
[DEBUG-DS033] _check_multiline_code_in_comment нашел: 4
Проверить итоговый отчёт scan_report_patch_REPS_EXP_115_1_*.md — он должен содержать 26 строк проблем (см. Приложение В).

Критерии приёмки
№	Критерий	Ожидаемое значение
1	Количество найденных bad_prefix	9 (строки 10, 11, 13, 14, 15, 17×3, 22, 23)
2	Количество найденных not_mentioned	5 (строки 14, 15, 17, 22, 32, 33)
3	Количество найденных wrong_method_syntax	1 (строка 58)
4	Количество найденных code_in_comment	4 (строки 68, 75, 99, 124)
5	Количество найденных prefix_type_in_var_name	5 (строки 31, 32, 33, 34, 35)
6	Количество ложных срабатываний (SYNTAX_ERROR, VARIABLE_SAME_NAME и др.)	0
7	Формат вывода	LINE | CHECK | LEVEL | TYPE | ERROR
8	Совпадение с эталоном	14 уникальных проблем (по LINE+CHECK)
Отчёт о выполнении
После выполнения всех задач приложить:

Консольный вывод с [DEBUG-DS033] строками.

Содержимое scan_report_patch_REPS_EXP_115_1_*.md.

Diff изменений в scanner.py (или список изменённых секций).

Подтверждение, что PLP_EXCLUDED_RULES не содержит BAD_PREFIX, NOT_MENTIONED, WRONG_METHOD_SYNTAX, CODE_IN_COMMENT, PREFIX_TYPE_IN_VAR_NAME, OUTER_JOIN.

Приложение А — Образцы методов _check_multiline_*
А.1 _check_multiline_bad_prefix
python
def _check_multiline_bad_prefix(self, lines: List[str]) -> List[Tuple[int, str, str]]:
    """DS 033: Проверка bad_prefix. Возвращает (line_num, original_line, new_name)."""
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
        if stripped.startswith('--') or stripped.startswith('@') or \
           stripped.startswith('class') or stripped.startswith('method'):
            continue
        
        # DS 033: ^\s* вместо ^\s+
        match = re.search(
            r'^\s*(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*'
            r'(?:\([^)]*\))?\s*(?::=|;)',
            line, re.IGNORECASE
        )
        if match:
            var_name = match.group(1)
            var_type = match.group(2).lower()
            
            if var_name.lower() in excluded:
                continue
            
            if not var_name.startswith('v_'):
                if var_type in ('string', 'varchar2'):
                    new_name = f'v_s{var_name[0].upper()}{var_name[1:]}'
                elif var_type == 'integer':
                    new_name = f'v_i{var_name[0].upper()}{var_name[1:]}'
                elif var_type == 'number':
                    new_name = f'v_n{var_name[0].upper()}{var_name[1:]}'
                elif var_type == 'boolean':
                    new_name = f'v_b{var_name[0].upper()}{var_name[1:]}'
                elif var_type == 'ref':
                    new_name = f'v_r{var_name[0].upper()}{var_name[1:]}'
                elif var_type == 'rowtype':
                    new_name = f'v_o{var_name[0].upper()}{var_name[1:]}'
                else:
                    new_name = f'v_{var_name}'
                
                issues.append((i + 1, line.strip(), new_name))
    
    return issues
А.2 _check_multiline_not_mentioned
python
def _check_multiline_not_mentioned(self, lines: List[str]) -> List[Tuple[int, str, str]]:
    """DS 033: Проверка not_mentioned. Возвращает (line_num, original_line, var_name)."""
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
        if stripped.startswith('--') or stripped.startswith('@') or \
           stripped.startswith('class') or stripped.startswith('method') or \
           stripped.startswith('execute') or stripped.startswith('begin'):
            continue
        
        # DS 033: ^\s* вместо ^\s+
        match = re.search(
            r'^\s*(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*'
            r'(?:\([^)]*\))?\s*(?::=|;)',
            line, re.IGNORECASE
        )
        if match:
            var_name = match.group(1)
            if var_name.lower() not in excluded:
                declared_vars[var_name] = i + 1
    
    for var_name, decl_line in declared_vars.items():
        var_pattern = re.compile(rf'\b{re.escape(var_name)}\b')
        count = 0
        for i, line in enumerate(lines, 1):
            if i == decl_line:
                continue
            # DS 033: исключаем служебные строки
            stripped_check = line.strip()
            if stripped_check.startswith('--') or stripped_check.startswith('@') or \
               stripped_check.startswith('class') or stripped_check.startswith('method') or \
               stripped_check.startswith('pragma'):
                continue
            count += len(var_pattern.findall(line))
        
        if count == 0:
            original_line = lines[decl_line - 1].strip() if decl_line <= len(lines) else ''
            issues.append((decl_line, original_line, var_name))
    
    return issues
А.3 _check_multiline_wrong_method_syntax
python
def _check_multiline_wrong_method_syntax(self, lines: List[str]) -> List[Tuple[int, str, str]]:
    """DS 033: Проверка wrong_method_syntax. Возвращает (line_num, original_line, method_path)."""
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
А.4 _check_multiline_code_in_comment
python
def _check_multiline_code_in_comment(self, lines: List[str]) -> List[Tuple[int, str]]:
    """DS 033: Проверка code_in_comment. Возвращает (line_num, original_line)."""
    issues = []
    code_keywords = ('begin', 'end', 'if', 'then', 'else', 'loop', 'select',
                     'from', 'where', 'insert', 'update', 'delete', 'return',
                     'function', 'procedure', 'declare')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('--'):
            continue
        
        comment_text = stripped[2:].strip()
        
        # Признак 1: наличие ';'
        if ';' in comment_text:
            issues.append((i + 1, line.strip()))
            continue
        
        # Признак 2: наличие ':=' (присваивание)
        if ':=' in comment_text:
            issues.append((i + 1, line.strip()))
            continue
        
        # Признак 3: наличие служебных слов PL+
        for kw in code_keywords:
            if re.search(rf'\b{kw}\b', comment_text, re.IGNORECASE):
                issues.append((i + 1, line.strip()))
                break
    
    return issues
Приложение Б — Образец блока вызова в scan_file()
python
# ========== DS 033: МНОГОСТРОЧНЫЕ ПРОВЕРКИ ДЛЯ PlpCheck ==========

# 1. bad_prefix
if self._is_rule_selected('plpcheck.BAD_PREFIX'):
    print(f"[DEBUG-DS033] Запуск _check_multiline_bad_prefix...")
    bad_prefix_issues = self._check_multiline_bad_prefix(self.lines)
    print(f"[DEBUG-DS033] _check_multiline_bad_prefix нашел: {len(bad_prefix_issues)}")
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
            rubricator_example_fixed=new_name,
            tags=['prefix', 'naming', 'style'],
            check_name='bad_prefix',
            level='WARNING',
            issue_type_ru='STYLE',
            error_message=f'переименуйте в "{new_name}"'
        )
        issues.append(issue)
        if log_callback:
            log_callback(f"    [PlpCheck] bad_prefix в строке {line_num}: {new_name}", 'warning')

# 2. not_mentioned
if self._is_rule_selected('plpcheck.NOT_MENTIONED'):
    print(f"[DEBUG-DS033] Запуск _check_multiline_not_mentioned...")
    not_mentioned_issues = self._check_multiline_not_mentioned(self.lines)
    print(f"[DEBUG-DS033] _check_multiline_not_mentioned нашел: {len(not_mentioned_issues)}")
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

# 3. wrong_method_syntax
if self._is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX'):
    print(f"[DEBUG-DS033] Запуск _check_multiline_wrong_method_syntax...")
    wrong_method_issues = self._check_multiline_wrong_method_syntax(self.lines)
    print(f"[DEBUG-DS033] _check_multiline_wrong_method_syntax нашел: {len(wrong_method_issues)}")
    for line_num, bad_code, method_path in wrong_method_issues:
        issue = Issue(
            file_path=str(file_path.resolve()),
            line_number=line_num,
            issue_type='plpcheck.WRONG_METHOD_SYNTAX',
            description=f'Обращение к методу {method_path}',
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

# 4. code_in_comment
if self._is_rule_selected('plpcheck.CODE_IN_COMMENT'):
    print(f"[DEBUG-DS033] Запуск _check_multiline_code_in_comment...")
    code_in_comment_issues = self._check_multiline_code_in_comment(self.lines)
    print(f"[DEBUG-DS033] _check_multiline_code_in_comment нашел: {len(code_in_comment_issues)}")
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
Приложение В — Ожидаемый результат отчёта
text
PlpCheck Отчёт
Дата: 2026-09-12 HH:MM:SS
Всего проблем: 24
Уникальных проблем: 24
Всего файлов: 1

========================================================================================================================
  LINE | CHECK                          | LEVEL      | TYPE       | ERROR
========================================================================================================================
    10 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_iDp"
    11 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_iDp1"
    13 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_sFmt"
    14 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_sFmt24"
    14 | not_mentioned                  | WARNING    | STYLE      | Переменная fmt24 не упоминается
    15 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_sHMS"
    15 | not_mentioned                  | WARNING    | STYLE      | Переменная fmtHMS не упоминается
    17 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "p_bV1"
    17 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "p_sV2"
    17 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "p_sV3"
    17 | not_mentioned                  | WARNING    | STYLE      | Функция iif не вызывается
    22 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_rBranch"
    22 | not_mentioned                  | WARNING    | STYLE      | Переменная lrBranch не упоминается
    23 | bad_prefix                     | WARNING    | STYLE      | переименуйте в "v_lrecBrInfo"
    31 | prefix_type_in_var_name        | WARNING    | STYLE      | переименуйте в "rP_PARAM"
    32 | not_mentioned                  | WARNING    | STYLE      | Переменная vDateRep не упоминается
    32 | prefix_type_in_var_name        | WARNING    | STYLE      | переименуйте в "sVDateRep"
    33 | not_mentioned                  | WARNING    | STYLE      | Переменная lvRepPeriod не упоминается
    33 | prefix_type_in_var_name        | WARNING    | STYLE      | переименуйте в "sLvRepPeriod"
    34 | prefix_type_in_var_name        | WARNING    | STYLE      | переименуйте в "sP_FILE_XML"
    35 | prefix_type_in_var_name        | WARNING    | STYLE      | переименуйте в "sP_FILE_ZIP"
    58 | wrong_method_syntax            | WARNING    | STYLE      | Обращение к методу ::[RUNTIME].[STR]
    68 | code_in_comment                | WARNING    | STYLE      | Удалите закомментированный код
    75 | code_in_comment                | WARNING    | STYLE      | Удалите закомментированный код
    99 | code_in_comment                | WARNING    | STYLE      | Удалите закомментированный код
   124 | code_in_comment                | WARNING    | STYLE      | Удалите закомментированный код
========================================================================================================================
Примечание по счётчикам
Всего строк в таблице: 26 (как в эталонном логе ЦФТ)

Уникальных проблем по (LINE, CHECK): 14 (совпадает с показателем «Уникальных» в эталонном логе)

Всего проблем (все срабатывания): 26

Если требуется точное совпадение по счётчику «Уникальных проблем: 14», в generate_report() нужно группировать по ключу (line_number, check_name) — тогда две bad_prefix на строке 17 с разными описаниями схлопнутся в одну. Уточнить у пользователя, какой именно счётчик считать целевым.

Конец задания DS_033.