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

# DS_056A: единый хелпер лексического разбора
from analyzer.lexer_state import (
    LexerState,
    is_in_comment_or_string,
    advance_lexer_state,
    is_line_fully_in_comment_or_string,
)

# ============================================================
# DS 042 (Приложение Б): константа отладки уровня модуля.
# True — включить отладочные принты [DS_042-DEBUG]; False — отключить.
# ============================================================
DEBUG_FILTER = True


# ============================================================
# DS 032: ПРАВИЛА PlpCheck, НЕ ПРИМЕНИМЫЕ К .plp ФАЙЛАМ
# ============================================================
# Эти правила дают ложные срабатывания на процедурном PL+ коде (.plp):
# либо относятся только к чистому SQL, либо реализованы отдельными
# многострочными проверками ЦФТ-стиля (см. _check_plp_*).
PLP_EXCLUDED_RULES: Set[str] = {
    # Ложные срабатывания на PL+ синтаксис
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
    'plpcheck.CONCAT_CONTROL',
    'plpcheck.MACRO_CALL_EXECUTEPROCESS',
    'plpcheck.PLATFORM_INTEGER_MISMATCH',
    'plpcheck.ACCESS_STATIC',
    # DS 033: ВАЖНО — BAD_PREFIX, NOT_MENTIONED, WRONG_METHOD_SYNTAX,
    # CODE_IN_COMMENT, PREFIX_TYPE_IN_VAR_NAME, OUTER_JOIN НЕ включены сюда
    # (см. PLP_MULTILINE_IMPLEMENTED_RULES ниже)
}

# ============================================================
# DS 033: ПРАВИЛА С ТОЧНЫМИ МНОГОСТРОЧНЫМИ РЕАЛИЗАЦИЯМИ
# ============================================================
# Эти правила АКТИВНЫ и проверяются точными многострочными функциями
# _check_plp_* в scan_file(). Их regex-паттерны из рубрикатора здесь
# НЕ применяются, чтобы не дублировать срабатывания и не давать ложных
# находок (проверено на REPS_EXP_115_1.plp: regex-путь давал 41 проблему
# вместо 26 и ложный outer_join).
PLP_MULTILINE_IMPLEMENTED_RULES: Set[str] = {
    'plpcheck.BAD_PREFIX',            # _check_plp_bad_prefix
    'plpcheck.NOT_MENTIONED',         # _check_plp_not_mentioned
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME',  # _check_plp_prefix_type_in_var_name
    'plpcheck.WRONG_METHOD_SYNTAX',   # _check_plp_wrong_method_syntax
    'plpcheck.CODE_IN_COMMENT',       # _check_plp_code_in_comment
    'plpcheck.OUTER_JOIN',            # точная проверка планируется; regex даёт ложные срабатывания на PL+
}

# ============================================================
# DS 032: МАППИНГ ПРАВИЛ PlpCheck НА КОРОТКИЕ ИМЕНА (CHECK)
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
# DS 032 / DS 044: ТИПЫ ПРАВИЛ (TYPE) — синхронизированы с эталоном ЦФТ-PlpCheck
# Значения — список затронутых технологий (STYLE, DBI, JAVA, PLSQL, ...)
# через запятую, как в колонке TYPE отчёта report_all.html.
# ============================================================
PLPCHECK_RULE_TYPES: Dict[str, str] = {
    # --- STYLE (одиночный) ---
    'plpcheck.BAD_PREFIX': 'STYLE',
    'plpcheck.NOT_MENTIONED': 'STYLE',
    'plpcheck.CODE_IN_COMMENT': 'STYLE',
    'plpcheck.WRONG_METHOD_SYNTAX': 'STYLE',
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'STYLE',
    'plpcheck.VALIDATE_DEFAULT_TWICE': 'STYLE',
    'plpcheck.VALIDATE_ELSE_INFO': 'STYLE',
    'plpcheck.EXIST_ALL_OR_COLLECTIONS': 'STYLE',
    'plpcheck.STRING_AS_CLASS': 'STYLE',
    'plpcheck.RESERVED_PREFIX': 'STYLE',
    'plpcheck.METH_PARAM_AND_VAR_NAMES': 'STYLE',
    'plpcheck.METH_PARAM_AND_VAR_FULL_NAMES': 'STYLE',
    'plpcheck.FUNCTIONS_IN_BODY_OR_VALIDATE': 'STYLE',
    'plpcheck.VARIABLE_SAME_NAME': 'STYLE',
    'plpcheck.WRONG_REF_SYNTAX': 'STYLE',
    'plpcheck.WRONG_CLASS_SYNTAX': 'STYLE',
    'plpcheck.WRONG_ATTR_SYNTAX': 'STYLE',
    'plpcheck.WRONG_LOCAL_PREFIX': 'STYLE',
    'plpcheck.GLOBAL_VAR': 'STYLE',
    'plpcheck.IF_EXIT_TO_EXIT_WHEN': 'STYLE',
    'plpcheck.RAISE_IN_OTHERS': 'STYLE',
    'plpcheck.TRIVIAL_EXCEPTION_HANDLER': 'STYLE',
    'plpcheck.NATIONAL_CURRENCY': 'STYLE',
    'plpcheck.CONCAT_CONTROL': 'STYLE',
    'plpcheck.ACCESS_STATIC': 'STYLE',
    'plpcheck.PLATFORM_INTEGER_MISMATCH': 'STYLE',
    # --- DBI (одиночный) ---
    'plpcheck.DIRECT_COMPARISON_WITH_NULL': 'DBI',
    'plpcheck.SYSTEM_VIEWS': 'DBI',
    'plpcheck.OUTER_JOIN': 'DBI',
    'plpcheck.SUBOPTIMAL_QUERY_WROWNUM': 'DBI',
    'plpcheck.OBLIGATORY_IN_OTHERS': 'DBI',
    'plpcheck.ROWNUM': 'DBI',
    'plpcheck.UPDATE_DELETE_BY_SUBQUERY': 'DBI',
    'plpcheck.REF_NONTABLE': 'DBI',
    'plpcheck.NOT_CLOSED_CURSOR': 'DBI',
    'plpcheck.NOT_CLOSED_FILE': 'DBI',
    'plpcheck.NOT_HANDLED_CURSOR_EXCEPTIONS': 'DBI',
    'plpcheck.MATCHING_TYPES': 'DBI',
    'plpcheck.CONNECTBY2WITH': 'DBI',
    'plpcheck.SELECTANALYTICARGUMENT': 'DBI',
    'plpcheck.PURE_SQL_DBLINK': 'DBI',
    'plpcheck.MACRO_CALL_EXECUTEPROCESS': 'DBI',
    # --- Составные типы ---
    'plpcheck.NO_RECURSION_COMMENT': 'DBI,JAVA,PLSQL',
    'plpcheck.UDF': 'DBI,JAVA,PLSQL',
    'plpcheck.PURE_UDF': 'DBI,JAVA,PLSQL',
    'plpcheck.SIZELESS': 'JAVA,PLSQL',
    'plpcheck.NOT_RETURN_STATEMENT': 'JAVA,PLSQL',
    'plpcheck.ANALYTIC_AND_FETCH_BAD_USE': 'JAVA,PLSQL',
    'plpcheck.SAVEPOINT_ROLLBACK_USAGE': 'PLSQL,STYLE',
    'plpcheck.INSERT_PLSQL': 'JAVA',
    'plpcheck.GOTO': 'JAVA',
    'plpcheck.REGEXP_DIFF_IN_JAVA': 'DBI,JAVA',
    'plpcheck.SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP': 'DBI,JAVA',
    'plpcheck.CALL_STACK_ANALYSIS': 'DBI,JAVA',
    'plpcheck.DEREFERENCE_IN_LOOP': 'PLSQL',
    # --- Прочие ---
    'plpcheck.SYNTAX_ERROR': 'SYNTAX',
    'plpcheck.VBS_LINKING_ERROR': 'LINKING',
}

# ============================================================
# DS 032: СООТВЕТСТВИЕ ТИПА ПЕРЕМЕННОЙ И ПРЕФИКСНОЙ БУКВЫ
# ============================================================
PLP_TYPE_LETTERS: Dict[str, str] = {
    'number': 'n',
    'integer': 'i',
    'boolean': 'b',
    'ref': 'r',
    'string': 's',
    'varchar2': 's',
    'date': 'd',
    'timestamp': 'd',
    'rowtype': 'o',
    'record': 'o',
    'table': 't',
    'varray': 't',
}


# ============================================================
# DS 036: МАППИНГ ПРАВИЛ PlpCheck НА 7 КАТЕГОРИЙ + OTHER
# (категории из 2.RUBRICATOR_CATEGORIES v5.md, №31-37)
# ============================================================
# Эвристика (вариант A из DS 036):
#   category DBI + subcategory DBI.PURE_SQL -> SQL.CHECKS
#   category DBI (прочие)                   -> DBI.ADAPTATION
#   category WEB                            -> WEB.ADAPTATION
#   category DEV + subcategory DEV.NAMING   -> STYLE.PREFIXES
#   category DEV + subcategory DEV.STYLE    -> STYLE.PREFIXES
#   правило PREFIX_TYPE_IN_VAR_NAME         -> STYLE.PREFIX_COMBINATION
#   остальные                               -> OTHER
PLPCHECK_RULE_TO_CATEGORY: Dict[str, str] = {
    # --- STYLE.PREFIXES (DEV.NAMING + DEV.STYLE) ---
    'plpcheck.BAD_PREFIX': 'STYLE.PREFIXES',
    'plpcheck.RESERVED_PREFIX': 'STYLE.PREFIXES',
    'plpcheck.WRONG_LOCAL_PREFIX': 'STYLE.PREFIXES',
    'plpcheck.METH_PARAM_AND_VAR_NAMES': 'STYLE.PREFIXES',
    'plpcheck.METH_PARAM_AND_VAR_FULL_NAMES': 'STYLE.PREFIXES',
    'plpcheck.USES_RIP_OBJECT': 'STYLE.PREFIXES',
    'plpcheck.CODE_IN_COMMENT': 'STYLE.PREFIXES',
    'plpcheck.NOT_MENTIONED': 'STYLE.PREFIXES',
    'plpcheck.WRONG_METHOD_SYNTAX': 'STYLE.PREFIXES',
    'plpcheck.WRONG_ATTR_SYNTAX': 'STYLE.PREFIXES',
    'plpcheck.WRONG_CLASS_SYNTAX': 'STYLE.PREFIXES',
    'plpcheck.WRONG_REF_SYNTAX': 'STYLE.PREFIXES',
    'plpcheck.FUNCRETURNKEYWORD': 'STYLE.PREFIXES',
    'plpcheck.FUNCTIONS_IN_BODY_OR_VALIDATE': 'STYLE.PREFIXES',
    'plpcheck.GLOBAL_VAR': 'STYLE.PREFIXES',
    'plpcheck.IF_EXIT_TO_EXIT_WHEN': 'STYLE.PREFIXES',
    'plpcheck.NO_RECURSION_COMMENT': 'STYLE.PREFIXES',
    'plpcheck.SAVEPOINT_ROLLBACK_USAGE': 'STYLE.PREFIXES',
    'plpcheck.STRING_AS_CLASS': 'STYLE.PREFIXES',
    'plpcheck.UPPER_CASED_VARCHAR2': 'STYLE.PREFIXES',
    'plpcheck.VALIDATE_ELSE_INFO': 'STYLE.PREFIXES',
    'plpcheck.VARIABLE_SAME_NAME': 'STYLE.PREFIXES',
    # --- STYLE.PREFIX_COMBINATION ---
    'plpcheck.PREFIX_TYPE_IN_VAR_NAME': 'STYLE.PREFIX_COMBINATION',
    # --- SQL.CHECKS (DBI.PURE_SQL) ---
    'plpcheck.PURE_SQL_CONNECTBY2WITH': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_DBLINK': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_FUNCTION_UNSUPPORTED': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_JSON_TYPES': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_MINUS_NOT_DBI': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_OUTER_JOIN': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_PSEUDOCOL_UNSUPPORTED': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_SELECTANALYTICARGUMENT': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_SELECT_FROM_ARRAY': 'SQL.CHECKS',
    'plpcheck.PURE_SQL_VIEW_IN_CONDITION': 'SQL.CHECKS',
    'plpcheck.PURE_UDF': 'SQL.CHECKS',
    'plpcheck.PURE_XMLTYPE_IN_SQL': 'SQL.CHECKS',
    # --- WEB.ADAPTATION (category WEB) ---
    'plpcheck.CONTROLS_VALIDATE_NAME': 'WEB.ADAPTATION',
    'plpcheck.EXCEL_WORD_LIBS_WEB': 'WEB.ADAPTATION',
    'plpcheck.REPORT_METHODS_WEB': 'WEB.ADAPTATION',
    'plpcheck.WEB_REPORT': 'WEB.ADAPTATION',
    'plpcheck.HOT_KEY_PROHIBITED': 'WEB.ADAPTATION',
    'plpcheck.VBS_LINKING_ERROR': 'WEB.ADAPTATION',
    'plpcheck.WEB_NOT_IMPLEMENTED': 'WEB.ADAPTATION',
    # --- DBI.ADAPTATION (category DBI, кроме DBI.PURE_SQL) ---
    'plpcheck.CROSS_DB_QUERY': 'DBI.ADAPTATION',
    'plpcheck.COND_COMPILE_COMMENT': 'DBI.ADAPTATION',
    'plpcheck.USER_IF_DEF': 'DBI.ADAPTATION',
    'plpcheck.INSERT_WITH_ID': 'DBI.ADAPTATION',
    'plpcheck.UPDATE_DELETE_BY_SUBQUERY': 'DBI.ADAPTATION',
    'plpcheck.DYNAMIC_PLP': 'DBI.ADAPTATION',
    'plpcheck.EXECUTEIMMEDIATE': 'DBI.ADAPTATION',
    'plpcheck.OBLIGATORY_UNIQUE_ALIAS': 'DBI.ADAPTATION',
    'plpcheck.NOT_HANDLED_CURSOR_EXCEPTIONS': 'DBI.ADAPTATION',
    'plpcheck.OBLIGATORY_IN_OTHERS': 'DBI.ADAPTATION',
    'plpcheck.USESQLCODE': 'DBI.ADAPTATION',
    'plpcheck.USE_LOCAL_OBJECT_IN_EXTENSION': 'DBI.ADAPTATION',
    'plpcheck.RESTRICTIONS_ON_IGNITE_FUNCTIONS': 'DBI.ADAPTATION',
    'plpcheck.SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP': 'DBI.ADAPTATION',
    'plpcheck.JSON_TYPES': 'DBI.ADAPTATION',
    'plpcheck.CONTROLTABLECOLUMNSTYPE': 'DBI.ADAPTATION',
    'plpcheck.INDEX_LENGTH': 'DBI.ADAPTATION',
    'plpcheck.ROWIDIDENTIFIEDTABLE': 'DBI.ADAPTATION',
    'plpcheck.WITHRECURSIVEMODEL': 'DBI.ADAPTATION',
    'plpcheck.ACCESS_STATIC': 'DBI.ADAPTATION',
    'plpcheck.COMPILE_MISSING_COND': 'DBI.ADAPTATION',
    'plpcheck.REFERENCED_TO_OBJECT': 'DBI.ADAPTATION',
    'plpcheck.ANALYTIC_AND_FETCH_BAD_USE': 'DBI.ADAPTATION',
    'plpcheck.CARTESIAN_JOIN': 'DBI.ADAPTATION',
    'plpcheck.CONCAT_CONTROL': 'DBI.ADAPTATION',
    'plpcheck.CONV_STREAM_CHECKS': 'DBI.ADAPTATION',
    'plpcheck.DEREFERENCE_IN_LOOP': 'DBI.ADAPTATION',
    'plpcheck.FORM_TRANSACT_CONTROL': 'DBI.ADAPTATION',
    'plpcheck.FULL_INDEX_SCAN': 'DBI.ADAPTATION',
    'plpcheck.FULL_TABLE_SCAN': 'DBI.ADAPTATION',
    'plpcheck.FUNCTION_BREAK_INDEX': 'DBI.ADAPTATION',
    'plpcheck.INDEX_CAN_USE_BETTER': 'DBI.ADAPTATION',
    'plpcheck.MANY_SUB_TRANSACTIONS': 'DBI.ADAPTATION',
    'plpcheck.MULTIPLE_MODIFIERS': 'DBI.ADAPTATION',
    'plpcheck.PARTITION_ALL': 'DBI.ADAPTATION',
    'plpcheck.SIZE_RESTRICTION': 'DBI.ADAPTATION',
    'plpcheck.SUBOPTIMAL_QUERY_WROWNUM': 'DBI.ADAPTATION',
    'plpcheck.SUBOPTIMAL_UNSELECTED_COL_USAGE': 'DBI.ADAPTATION',
    'plpcheck.UDF': 'DBI.ADAPTATION',
    'plpcheck.NOT_CLOSED_CURSOR': 'DBI.ADAPTATION',
    'plpcheck.NOT_CLOSED_FILE': 'DBI.ADAPTATION',
    'plpcheck.CALL_STACK_ANALYSIS': 'DBI.ADAPTATION',
    'plpcheck.COLUMNS_LIMIT_EXCEEDED': 'DBI.ADAPTATION',
    'plpcheck.DEREFERENCING_TO_OUT_PARAM': 'DBI.ADAPTATION',
    'plpcheck.ERROR_MESSAGE_ANALYSIS': 'DBI.ADAPTATION',
    'plpcheck.EXCEPTIONLOOP': 'DBI.ADAPTATION',
    'plpcheck.INSERT_PLSQL': 'DBI.ADAPTATION',
    'plpcheck.INVALID_INIT': 'DBI.ADAPTATION',
    'plpcheck.MACROEXECUTEPROCESS': 'DBI.ADAPTATION',
    'plpcheck.MACROEXECUTEPROCESS_COMMENT': 'DBI.ADAPTATION',
    'plpcheck.MACRO_CALL_EXECUTEPROCESS': 'DBI.ADAPTATION',
    'plpcheck.NULL_IS_NULL_TO_JAVA': 'DBI.ADAPTATION',
    'plpcheck.PARALLEL_EXECUTION': 'DBI.ADAPTATION',
    'plpcheck.REFERENCE_COMPARISON': 'DBI.ADAPTATION',
    'plpcheck.RESTRICT_REFERENCES_BAD_USE': 'DBI.ADAPTATION',
    'plpcheck.ROWID': 'DBI.ADAPTATION',
    'plpcheck.SAVEPOINT_ROLLBACK_MACRO_PARAM_LENGTH': 'DBI.ADAPTATION',
    'plpcheck.SAVEPOINT_ROLLBACK_NAME_LENGTH': 'DBI.ADAPTATION',
    'plpcheck.CONNECTBY2WITH': 'DBI.ADAPTATION',
    'plpcheck.CONSTANT_IN_ORDER_AND_GROUP_BY': 'DBI.ADAPTATION',
    'plpcheck.CONSTANT_ORDER_BY_ON_UDF': 'DBI.ADAPTATION',
    'plpcheck.DIRECT_COMPARISON_WITH_NULL': 'DBI.ADAPTATION',
    'plpcheck.DISTINCT_AND_ORDER_BY': 'DBI.ADAPTATION',
    'plpcheck.DISTINCT_UDF': 'DBI.ADAPTATION',
    'plpcheck.EMPTY_STRING_IN_CURSOR': 'DBI.ADAPTATION',
    'plpcheck.EXIST_ALL_OR_COLLECTIONS': 'DBI.ADAPTATION',
    'plpcheck.FETCH_OVER_SUBQUERY': 'DBI.ADAPTATION',
    'plpcheck.FUNC_ATTR_DEREFERENCE': 'DBI.ADAPTATION',
    'plpcheck.HINT_INDEX_ORDER_BY': 'DBI.ADAPTATION',
    'plpcheck.INTERVAL_NOT_SELECT': 'DBI.ADAPTATION',
    'plpcheck.MATCHING_TYPES': 'DBI.ADAPTATION',
    'plpcheck.NESTED_TABLE': 'DBI.ADAPTATION',
    'plpcheck.NVL_IN_SELECT': 'DBI.ADAPTATION',
    'plpcheck.OUTER_JOIN': 'DBI.ADAPTATION',
    'plpcheck.QUOTING': 'DBI.ADAPTATION',
    'plpcheck.ROWNUM': 'DBI.ADAPTATION',
    'plpcheck.SCHEMA_IN_DDL': 'DBI.ADAPTATION',
    'plpcheck.SELECTANALYTICARGUMENT': 'DBI.ADAPTATION',
    'plpcheck.SELECTLOCKWAIT': 'DBI.ADAPTATION',
    'plpcheck.SQL_FUNCTION_UNSUPPORTED': 'DBI.ADAPTATION',
    'plpcheck.SYSTEM_VIEWS': 'DBI.ADAPTATION',
    'plpcheck.VERIFY_TYPE_IN_WITH': 'DBI.ADAPTATION',
    'plpcheck.XMLTYPE_IN_SQL': 'DBI.ADAPTATION',
    'plpcheck.REGEXP_DIFF_IN_JAVA': 'DBI.ADAPTATION',
    'plpcheck.MAX_SIZE_ID': 'DBI.ADAPTATION',
    'plpcheck.NATIVE_ID_OBJ_IDENTIFIER': 'DBI.ADAPTATION',
    'plpcheck.NOT_CLASS_REF_TABLE_PARAM': 'DBI.ADAPTATION',
    'plpcheck.PLATFORM_INTEGER_MISMATCH': 'DBI.ADAPTATION',
    'plpcheck.REF_NONTABLE': 'DBI.ADAPTATION',
    'plpcheck.ROWTYPE_DECLARED_PUBLIC': 'DBI.ADAPTATION',
    'plpcheck.SIZELESS': 'DBI.ADAPTATION',
    'plpcheck.ALIAS_COLUMN_VIEW': 'DBI.ADAPTATION',
    'plpcheck.CRIT_EXT_IN_OLD_FORMAT': 'DBI.ADAPTATION',
    'plpcheck.UDF_IN_FILTER_FORMULA': 'DBI.ADAPTATION',
    # --- OTHER (category DEV, кроме DEV.NAMING/DEV.STYLE) ---
    'plpcheck.CONTINUE_EXIT_OFF_THE_LOOP': 'OTHER',
    'plpcheck.ENDLESS_CYCLE': 'OTHER',
    'plpcheck.NOT_RETURN_STATEMENT': 'OTHER',
    'plpcheck.FIXME_NOT_ALLOWED': 'OTHER',
    'plpcheck.VALIDATE_DEFAULT_TWICE': 'OTHER',
    'plpcheck.GETOBJECTINIFELSESECTION': 'OTHER',
    'plpcheck.RAISE_IN_OTHERS': 'OTHER',
    'plpcheck.TRIVIAL_EXCEPTION_HANDLER': 'OTHER',
    'plpcheck.GOTO': 'OTHER',
    'plpcheck.THIS_IN_DEFAULT': 'OTHER',
    'plpcheck.METHOD_AVAILABILITY': 'OTHER',
    'plpcheck.NATIONAL_CURRENCY': 'OTHER',
    'plpcheck.SYNTAX_ERROR': 'OTHER',
    'plpcheck.EDIT_HOTKEY': 'OTHER',
    'plpcheck.FORM_SIZE': 'OTHER',
    'plpcheck.ORDERED_CONTROLS': 'OTHER',
}

# ============================================================
# DS 037: КАТЕГОРИИ PlpCheck ДЛЯ GUI И ОТЧЁТА
# (из 2.RUBRICATOR_CATEGORIES v5.md, №31-37 + OTHER)
# ============================================================
# Структура: (код_категории, описание, CHECK-значения через запятую)
# Константа перенесена из gui_app.py (DS 036) в scanner.py (Вариант A из DS 037),
# чтобы быть доступной и сканеру, и GUI (gui_app.py импортирует её отсюда).
PLPCHECK_CATEGORIES: List[Tuple[str, str, str]] = [
    ('PLSQL.OPTIMIZATION',        'Оптимизация (2L/перевызов БД)',   ''),
    ('JAVA.OPTIMIZATION',         'Оптимизация (СП/Java)',           ''),
    ('DBI.ADAPTATION',            'Адаптация под PostgreSQL',        ''),
    ('SQL.CHECKS',                'Проверки чистого SQL',            ''),
    ('WEB.ADAPTATION',            'Адаптация под Веб-Навигатор',     ''),
    ('STYLE.PREFIXES',            'Префиксы и оформление',
        'bad_prefix, not_mentioned, wrong_method_syntax, code_in_comment'),
    ('STYLE.PREFIX_COMBINATION',  'Комбинированные префиксы',
        'prefix_type_in_var_name'),
    ('OTHER',                     'Прочие PlpCheck-правила',          ''),
]


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
    # DS 032: секция кода (PRIVATE/EXECUTE/...) для ЦФТ-формата отчёта
    section: str = ''
    
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

    # DS_056A: совместимый алиас для lexer_state.in_block_comment
    @property
    def in_block_comment(self):
        return self.lexer_state.in_block_comment

    @in_block_comment.setter
    def in_block_comment(self, val):
        self.lexer_state.in_block_comment = val

    def __init__(self, config: dict, selected_rules: List[str] = None, rubricator_prompts=None,
                 plpcheck_categories: List[str] = None, abort_callback=None, fix_flags: Dict[str, bool] = None):
        self.config = config
        self.selected_rules = selected_rules or []
        # DS 036: выбранные категории PlpCheck (7 категорий + OTHER)
        self.plpcheck_categories = plpcheck_categories or []
        # DS 038: callback прерывания — возвращает True, если пользователь нажал «Прервать»
        self.abort_callback = abort_callback
        # DS_053_Уточнение_2 (задача A): флаги детерминированного фикса для
        # отображения в заголовке всех отчётов. None — дефолт (regex+hybrid).
        self.fix_flags = fix_flags
        # DS 040: процент выполнения при прерывании
        # None — если не прервано; иначе float (0.0–100.0)
        self.abort_percent = None
        self.issues: List[Issue] = []
        self.stats: Dict[str, int] = {}
        self.lexer_state = LexerState()
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
        """
        Проверка, находится ли найденное совпадение в комментарии или строковом литерале.

        DS_056A: делегирует в единый хелпер analyzer.lexer_state.
        НЕ мутирует состояние — читает self.lexer_state (состояние НАЧАЛА строки).
        Состояние переноса обновляет advance_lexer_state (один раз на строку).
        """
        return is_in_comment_or_string(line, match_start, match_end, self.lexer_state)

    def _update_block_comment_state(self, line: str):
        """Обновление состояния лексического разбора по итогам строки."""
        advance_lexer_state(line, self.lexer_state)
    
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
                
                # DS 032/033: правила PlpCheck, не применимые к .plp файлам
                # (PLP_EXCLUDED_RULES — ложные срабатывания;
                #  PLP_MULTILINE_IMPLEMENTED_RULES — реализованы точными
                #  многострочными проверками _check_plp_*)
                if file_code.lower() == 'plpcheck' and (
                    rule_key in PLP_EXCLUDED_RULES or
                    rule_key in PLP_MULTILINE_IMPLEMENTED_RULES
                ):
                    reason = 'исключено' if rule_key in PLP_EXCLUDED_RULES else 'реализовано многострочной проверкой'
                    print(f"[DS 033] Правило {rule_key} {reason} для .plp файлов (regex пропущен)")
                    continue
                
                # DS 036: фильтрация правил PlpCheck по выбранным категориям.
                # plpcheck_categories пуст -> PlpCheck выключен в GUI, все правила проходят
                # (совместимость с прежним поведением); не пуст -> только выбранные категории.
                if file_code.lower() == 'plpcheck' and self.plpcheck_categories:
                    rule_category = PLPCHECK_RULE_TO_CATEGORY.get(rule_key, 'OTHER')
                    if rule_category not in self.plpcheck_categories:
                        print(f"[DS 036] Правило {rule_key} пропущено (категория {rule_category} не выбрана)")
                        continue
                
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
        
        DS 034: поддерживаются ОБА формата selected_rules (как в DS 024 для
        _load_patterns_from_rubricator):
        - коды файлов: ['PlpCheck', 'v53'] — сравнение по file_code;
        - коды правил: ['plpcheck.BAD_PREFIX', 'v53.SQL.OUTERJOIN.п.1.1'] —
          сравнение по полному коду правила (так передаёт GUI из
          _get_rules_for_selected_files).
        Без пункта 3 многострочные проверки отключались при запуске из GUI:
        file_code 'plpcheck' не совпадал точным вхождением с кодами правил.
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
        
        # 1) Выбран файл рубрикатора целиком (['PlpCheck', ...])
        if file_code.lower() in selected_lower:
            # DS 036: если задан фильтр категорий, многострочные проверки
            # PlpCheck выполняются только для выбранных категорий
            if rule_prefix == 'plpcheck' and self.plpcheck_categories:
                rule_category = PLPCHECK_RULE_TO_CATEGORY.get(rule_code, 'OTHER')
                return rule_category in self.plpcheck_categories
            return True
        
        # 2) DS 034: переданы коды правил — проверяем точный код этого правила
        if rule_code.lower() in selected_lower:
            # DS 036: фильтр категорий применяется и здесь
            if rule_prefix == 'plpcheck' and self.plpcheck_categories:
                rule_category = PLPCHECK_RULE_TO_CATEGORY.get(rule_code, 'OTHER')
                return rule_category in self.plpcheck_categories
            return True
        
        # 3) DS 034: переданы коды правил — совпадение файла-источника
        #    (selected_rules содержит коды того же файла, например
        #     'plpcheck.BAD_PREFIX' для rule_code 'plpcheck.NOT_MENTIONED')
        if any(s.startswith(rule_prefix + '.') for s in selected_lower):
            # DS 036: фильтр категорий применяется и здесь
            if rule_prefix == 'plpcheck' and self.plpcheck_categories:
                rule_category = PLPCHECK_RULE_TO_CATEGORY.get(rule_code, 'OTHER')
                return rule_category in self.plpcheck_categories
            return True
        
        return False
    
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
    
    # ============================================================
    # DS 032: МНОГОСТРОЧНЫЕ ПРОВЕРКИ PlpCheck (СИНХРОНИЗАЦИЯ С ЦФТ)
    # ============================================================
    
    def _plp_capitalize(self, name: str) -> str:
        """DS 032: первая буква — заглавная, остальное без изменений (dp -> Dp, fmtHMS -> FmtHMS)"""
        return name[0].upper() + name[1:] if name else name
    
    def _plp_type_letter(self, type_str: str) -> str:
        """DS 032: префиксная буква типа по соглашению ЦФТ (number->n, string->s, ref->r...)"""
        t = type_str.lower().strip()
        if t.startswith('['):
            # [STRING_1000], [BOOLEAN] и т.п. — строковые ТБП-типы
            return 's' if 'string' in t.lower() else ''
        if t.startswith('&'):
            return ''  # пользовательский тип — буква неизвестна
        return PLP_TYPE_LETTERS.get(t, '')
    
    def _plp_parse_sections(self, lines: List[str]) -> Dict[int, str]:
        """DS 032: определить секцию (PRIVATE/EXECUTE) для каждой строки файла."""
        sections = {}
        current = 'PRIVATE'
        for i, line in enumerate(lines, 1):
            stripped = line.strip().lower()
            if re.match(r'^method\s+\w+\s+is$', stripped) or re.match(r'^method\s+\w+\s+is\b', stripped):
                current = 'PRIVATE'
            elif re.match(r'^execute\s+is$', stripped) or re.match(r'^execute\s+is\b', stripped):
                current = 'EXECUTE'
            sections[i] = current
        return sections
    
    def _plp_iter_declarations(self, lines: List[str]):
        """DS 032: итератор по объявлениям переменных.
        
        Возвращает кортежи (line_num, var_name, type_str, is_execute_section).
        Распознаёт: 'x integer:=0;', 'fmt string(10):=...', 'lrBranch ref [BRANCH];',
        'lrecBrInfo &pkg.type;', 'P_FILE_XML [STRING_1000];'
        """
        sections = self._plp_parse_sections(lines)
        # тип: базовый тип | ref [CLASS] | [CLASS] | &pkg.type
        decl_re = re.compile(
            r'^\s*(\w+)\s+('
            r'integer|number|string|varchar2|date|boolean|timestamp|rowtype'
            r'|(?:ref\s*)?\[[\w\d_]+\]'
            r'|&[\w.]+'
            r')\s*(\(\s*\d+\s*\))?\s*(?::=|;)',
            re.IGNORECASE
        )
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('--') or stripped.startswith('@') \
               or stripped.lower().startswith(('class', 'method', 'execute', 'begin',
                                              'pragma', 'function', 'end', 'if', 'return')):
                continue
            m = decl_re.match(line)
            if m:
                var_name = m.group(1)
                type_str = m.group(2)
                # 'ref [CLASS]' — нормализуем к 'ref'
                if type_str.lower().startswith('ref'):
                    type_str = 'ref'
                yield i, var_name, type_str, sections.get(i, 'PRIVATE') == 'EXECUTE'
    
    def _plp_suggest_var_name(self, var_name: str, type_str: str, is_param: bool = False) -> str:
        """DS 032: предложить корректное имя по соглашению ЦФТ.
        
        Переменные: v_<буква типа><Имя> (dp integer -> v_iDp);
        для ref с префиксом 'lr' — v_r + остаток (lrBranch -> v_rBranch);
        для неизвестного типа — v_ + имя (lrecBrInfo -> v_lrecBrInfo).
        Параметры: p_<буква типа><Имя> (v1 boolean -> p_bV1).
        """
        base = 'p_' if is_param else 'v_'
        letter = self._plp_type_letter(type_str)
        
        if not letter:
            # Неизвестный тип: просто добавляем базовый префикс
            return base + var_name
        
        # Если имя в camelCase (ведущие строчные + заглавная),
        # ведущая строчная часть считается неправильным префиксом и отбрасывается:
        # fmtHMS -> HMS -> v_sHMS, lrBranch -> Branch -> v_rBranch
        if not is_param:
            m = re.match(r'^[a-z]+(?=[A-Z])', var_name)
            if m and m.end() < len(var_name):
                var_name = var_name[m.end():]
        
        return f'{base}{letter}{self._plp_capitalize(var_name)}'
    
    def _check_plp_bad_prefix(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """DS 032: bad_prefix — некорректные префиксы переменных и параметров (PRIVATE-секция).
        
        Возвращает список (line_num, message, original_line).
        """
        issues = []
        sections = self._plp_parse_sections(lines)
        func_re = re.compile(r'^\s*function\s+(\w+)\s*\((.*)\)\s*return', re.IGNORECASE)
        param_re = re.compile(
            r'(\w+)\s+(boolean|varchar2|string|number|integer|date)(\s*\(\s*\d+\s*\))?',
            re.IGNORECASE
        )
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('@'):
                continue
            if sections.get(i, 'PRIVATE') != 'PRIVATE':
                continue  # в EXECUTE работает prefix_type_in_var_name
            
            # Параметры локальных функций: function NAME(p1 type, p2 type) return ...
            fm = func_re.match(line)
            if fm:
                func_name = fm.group(1)
                params_str = fm.group(2)
                for pm in param_re.finditer(params_str):
                    p_name = pm.group(1)
                    p_type = pm.group(2)
                    if p_name.lower() == func_name.lower():
                        continue
                    expected = f'p_{self._plp_type_letter(p_type)}'
                    if not p_name.lower().startswith(expected):
                        new_name = self._plp_suggest_var_name(p_name, p_type, is_param=True)
                        msg = f'Не корректный префикс, пожалуйста переименуйте в "{new_name}"'
                        issues.append((i, msg, stripped))
                continue
        
        # Объявления переменных PRIVATE-секции
        for line_num, var_name, type_str, is_exec in self._plp_iter_declarations(lines):
            if is_exec:
                continue
            letter = self._plp_type_letter(type_str)
            if letter:
                expected = f'v_{letter}'
                ok = var_name.lower().startswith(expected)
            else:
                ok = var_name.lower().startswith('v_')
            if not ok:
                new_name = self._plp_suggest_var_name(var_name, type_str)
                msg = f'Не корректный префикс, пожалуйста переименуйте в "{new_name}"'
                issues.append((line_num, msg, lines[line_num - 1].strip()))
        
        return issues
    
    def _check_plp_prefix_type_in_var_name(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """DS 032: prefix_type_in_var_name — имя не содержит префикс типа (EXECUTE-секция).
        
        Возвращает список (line_num, message, original_line).
        """
        issues = []
        for line_num, var_name, type_str, is_exec in self._plp_iter_declarations(lines):
            if not is_exec:
                continue
            letter = self._plp_type_letter(type_str)
            if letter and not var_name.lower().startswith(letter):
                new_name = f'{letter}{self._plp_capitalize(var_name)}'
                msg = (f'Наименование переменной не содержит префикс типа, '
                       f'пожалуйста переименуйте в "{new_name}"')
                issues.append((line_num, msg, lines[line_num - 1].strip()))
        return issues
    
    def _check_plp_not_mentioned(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """DS 032: not_mentioned — неиспользуемые объявления переменных и функций.
        
        Возвращает список (line_num, message, original_line).
        """
        issues = []
        declared = {}   # name -> (line_num, kind, original_line)
        
        for line_num, var_name, type_str, is_exec in self._plp_iter_declarations(lines):
            declared[var_name] = (line_num, 'var', lines[line_num - 1].strip())
        
        # Объявленные функции
        func_re = re.compile(r'^\s*function\s+(\w+)\s*\(', re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('--'):
                continue
            fm = func_re.match(line)
            if fm:
                declared[fm.group(1)] = (i, 'func', stripped)
        
        # Поиск упоминаний вне строки объявления
        for name, (decl_line, kind, original_line) in declared.items():
            pattern = re.compile(rf'\b{re.escape(name)}\b')
            used = False
            for i, line in enumerate(lines, 1):
                if i == decl_line:
                    continue
                if pattern.search(line):
                    used = True
                    break
            if not used:
                if kind == 'func':
                    msg = f'Функция {name} нигде не вызывается. Проверьте внимательно программный код.'
                else:
                    msg = f'Переменная {name} более нигде не упоминается. Проверьте внимательно программный код.'
                issues.append((decl_line, msg, original_line))
        
        return issues
    
    def _check_plp_wrong_method_syntax(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """DS 032: wrong_method_syntax — обращение к методу без полного пути ::[CLASS].[METHOD].
        
        Возвращает список (line_num, message, original_line).
        """
        issues = []
        # Системные ТБП с кратким написанием (настройка ::[RUNTIME])
        runtime_map = {'str': '::[RUNTIME].[STR]'}
        call_re = re.compile(r'\[(\w+)\]\.(\w+)\s*\(')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('--'):
                continue
            for m in call_re.finditer(line):
                prefix = line[:m.start()]
                # Полный путь: [CLASS] является частью цепочки после ::
                # (например, ::[RUNTIME].[STR].Set_Par(...) -> prefix '::[RUNTIME].')
                prefix_stripped = prefix.rstrip()
                if '::' in prefix_stripped and prefix_stripped.endswith(('.', '::')):
                    continue  # полный путь уже указан
                class_name = m.group(1)
                full_path = runtime_map.get(
                    class_name.lower(), f'::[{class_name}].[{m.group(2).upper()}]'
                )
                msg = f'Обращение к методу должно быть в формате {full_path}'
                issues.append((i, msg, stripped))
        return issues
    
    def _plp_has_code_signs(self, text: str) -> bool:
        """DS 032: содержит ли текст признаки исполняемого кода."""
        if ';' in text:
            return True
        keywords = r'\b(if|then|else|elsif|begin|end|loop|while|for|select|from|where|' \
                   r'insert|update|delete|return|function|procedure|declare|case|when)\b'
        if re.search(keywords, text, re.IGNORECASE):
            return True
        if ':=' in text:
            return True
        return False
    
    def _check_plp_code_in_comment(self, lines: List[str]) -> List[Tuple[int, str, str]]:
        """DS 032: code_in_comment — закомментированный код.
        
        Однострочные '--' комментарии: репортится первая строка каждой группы
        подряд идущих комментариев с признаками кода.
        Блочные '/* ... */' комментарии: репортится строка открытия, если
        внутри блока есть признаки кода.
        
        Возвращает список (line_num, message, original_line).
        """
        issues = []
        
        # --- Блочные комментарии: трекинг /* ... */ ---
        in_block = False
        opener_line = None
        block_content = []
        block_issues = []  # (line_num, original_line)
        for i, line in enumerate(lines, 1):
            j = 0
            while j < len(line):
                if not in_block:
                    idx = line.find('/*', j)
                    if idx == -1:
                        break
                    in_block = True
                    opener_line = i
                    block_content = []
                    j = idx + 2
                else:
                    idx = line.find('*/', j)
                    if idx == -1:
                        block_content.append(line[j:])
                        j = len(line)
                    else:
                        block_content.append(line[j:idx])
                        j = idx + 2
                        in_block = False
                        if opener_line is not None:
                            if self._plp_has_code_signs(' '.join(block_content)):
                                block_issues.append((opener_line, 'Удалите закомментированный код',
                                                     lines[opener_line - 1].strip()))
                            opener_line = None
        
        # --- Однострочные '--' комментарии: группы подряд идущих ---
        group_first = None
        prev_had_code = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('--'):
                has_code = self._plp_has_code_signs(stripped[2:])
                if has_code and not prev_had_code:
                    group_first = i
                prev_had_code = has_code
            else:
                if prev_had_code and group_first is not None:
                    issues.append((group_first, 'Удалите закомментированный код',
                                   lines[group_first - 1].strip()))
                prev_had_code = False
                group_first = None
        if prev_had_code and group_first is not None:
            issues.append((group_first, 'Удалите закомментированный код',
                           lines[group_first - 1].strip()))
        
        issues.extend(block_issues)
        return issues
    
    def scan_file(self, file_path: Path, log_callback=None) -> List[Issue]:
        """Сканирование одного файла"""
        issues = []
        self.lexer_state = LexerState()  # DS_056A: сброс лексического состояния на новый файл
        self.file_path = file_path
        
        # DS 023: отладочный вывод
        print(f"[DEBUG] scan_file: {getattr(file_path, 'name', file_path)}, selected_rules: {self.selected_rules}")
        
        # DS 033: отладочный вывод для диагностики проверок PlpCheck
        print(f"[DEBUG-DS033] selected_rules={self.selected_rules}")
        print(f"[DEBUG-DS033] PATTERNS загружено: {len(self.PATTERNS)}")
        print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.BAD_PREFIX')={self._is_rule_selected('plpcheck.BAD_PREFIX')}")
        print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.NOT_MENTIONED')={self._is_rule_selected('plpcheck.NOT_MENTIONED')}")
        print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX')={self._is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX')}")
        print(f"[DEBUG-DS033] _is_rule_selected('plpcheck.CODE_IN_COMMENT')={self._is_rule_selected('plpcheck.CODE_IN_COMMENT')}")
        
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

                # DS_056A: лексическое состояние читается на НАЧАЛЕ строки.
                # advance_lexer_state вызывается РОВНО ОДИН РАЗ в конце итерации.

                if stripped.startswith('--'):
                    advance_lexer_state(line, self.lexer_state)
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

                # DS_056A: ровно один раз на строку — после всех is_in_comment_or_string.
                advance_lexer_state(line, self.lexer_state)

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
            
            # 4. NOT_MENTIONED: неиспользуемые переменные — DS 032: заменена точной
            #    проверкой _check_plp_not_mentioned (см. блок DS 032 ниже)
            
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
            
            # ========== DS 032: ПРОВЕРКИ PlpCheck ЦФТ-СТИЛЯ ==========
            file_section_map = self._plp_parse_sections(self.lines)
            
            # 1. bad_prefix (plpcheck.BAD_PREFIX)
            if self._is_rule_selected('plpcheck.BAD_PREFIX'):
                bp_issues = self._check_plp_bad_prefix(self.lines)
                print(f"[DEBUG-DS033] _check_plp_bad_prefix нашел: {len(bp_issues)}")
                for line_num, message, bad_code in bp_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.BAD_PREFIX',
                        description=message,
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='plpcheck.BAD_PREFIX',
                        rubricator_full_description='Проверка префиксов: v,t,gt,cur,gcur,ret,p,cn,gcn',
                        tags=['prefix', 'naming', 'style'],
                        section=file_section_map.get(line_num, 'PRIVATE')
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] bad_prefix в строке {line_num}: {message}", 'warning')
            
            # 2. not_mentioned (plpcheck.NOT_MENTIONED)
            if self._is_rule_selected('plpcheck.NOT_MENTIONED'):
                nm_issues = self._check_plp_not_mentioned(self.lines)
                print(f"[DEBUG-DS033] _check_plp_not_mentioned нашел: {len(nm_issues)}")
                for line_num, message, bad_code in nm_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.NOT_MENTIONED',
                        description=message,
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='plpcheck.NOT_MENTIONED',
                        rubricator_full_description='Непубличные сущности, объявленные в операции, должны в ней упоминаться',
                        tags=['unused', 'declaration', 'mention'],
                        section=file_section_map.get(line_num, 'PRIVATE')
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] not_mentioned в строке {line_num}: {message}", 'warning')
            
            # 3. prefix_type_in_var_name (plpcheck.PREFIX_TYPE_IN_VAR_NAME)
            if self._is_rule_selected('plpcheck.PREFIX_TYPE_IN_VAR_NAME'):
                pt_issues = self._check_plp_prefix_type_in_var_name(self.lines)
                print(f"[DEBUG-DS033] _check_plp_prefix_type_in_var_name нашел: {len(pt_issues)}")
                for line_num, message, bad_code in pt_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.PREFIX_TYPE_IN_VAR_NAME',
                        description=message,
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='plpcheck.PREFIX_TYPE_IN_VAR_NAME',
                        rubricator_full_description='Наименование переменной должно содержать префикс типа',
                        tags=['variable', 'prefix', 'type'],
                        section=file_section_map.get(line_num, 'EXECUTE')
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] prefix_type_in_var_name в строке {line_num}: {message}", 'warning')
            
            # 4. wrong_method_syntax (plpcheck.WRONG_METHOD_SYNTAX)
            if self._is_rule_selected('plpcheck.WRONG_METHOD_SYNTAX'):
                wm_issues = self._check_plp_wrong_method_syntax(self.lines)
                print(f"[DEBUG-DS033] _check_plp_wrong_method_syntax нашел: {len(wm_issues)}")
                for line_num, message, bad_code in wm_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.WRONG_METHOD_SYNTAX',
                        description=message,
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='plpcheck.WRONG_METHOD_SYNTAX',
                        rubricator_full_description='Обращение к методу в формате ::[CLASS].[METHOD]',
                        tags=['method', 'syntax', 'path'],
                        section=file_section_map.get(line_num, 'EXECUTE')
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] wrong_method_syntax в строке {line_num}: {message}", 'warning')
            
            # 5. code_in_comment (plpcheck.CODE_IN_COMMENT)
            if self._is_rule_selected('plpcheck.CODE_IN_COMMENT'):
                cc_issues = self._check_plp_code_in_comment(self.lines)
                print(f"[DEBUG-DS033] _check_plp_code_in_comment нашел: {len(cc_issues)}")
                for line_num, message, bad_code in cc_issues:
                    issue = Issue(
                        file_path=str(file_path.resolve()),
                        line_number=line_num,
                        issue_type='plpcheck.CODE_IN_COMMENT',
                        description=message,
                        original_code=bad_code[:200],
                        category='DEV',
                        rubricator_code='plpcheck.CODE_IN_COMMENT',
                        rubricator_full_description='Закомментированный код считается плохим тоном и запрещен в многих регламентах.',
                        tags=['comment', 'code', 'style'],
                        section=file_section_map.get(line_num, 'EXECUTE')
                    )
                    issues.append(issue)
                    if log_callback:
                        log_callback(f"    [PlpCheck] code_in_comment в строке {line_num}", 'warning')
            
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
        
        # DS 034: отладочный вывод списка найденных файлов (Шаги 1-2 диагностики)
        print(f"[DEBUG-DS034] scan_directory: source_dir={source_dir}, pattern={file_pattern}, recursive={recursive}")
        print(f"[DEBUG-DS034] Найдено файлов для сканирования: {len(all_files)}")
        for f in all_files[:5]:
            print(f"[DEBUG-DS034]   - {f}")
        
        if log_callback and total_files > 0:
            log_callback(f"\nВсего файлов для сканирования: {total_files}", 'info')
        
        for idx, plp_file in enumerate(all_files, 1):
            # DS 038: проверка прерывания (кнопка «Прервать» в GUI)
            if self.abort_callback and self.abort_callback():
                # DS 042: отладка переменных прерывания (обёрнуто в DEBUG_FILTER)
                if DEBUG_FILTER:
                    print(f"[DS_042-DEBUG] total_files={total_files}")
                    print(f"[DS_042-DEBUG] idx={idx}")
                    print(f"[DS_042-DEBUG] files_scanned={files_scanned}")
                    print(f"[DS_042-DEBUG] abort_percent (до)={self.abort_percent}")
                # DS 040/DS 042: процент ОБРАБОТАННЫХ файлов на момент прерывания
                if total_files > 0:
                    self.abort_percent = files_scanned / total_files * 100.0
                else:
                    self.abort_percent = 0.0
                # DS 042: отладка
                if DEBUG_FILTER:
                    print(f"[DS_042-DEBUG] abort_percent (после)={self.abort_percent}")
                if log_callback:
                    log_callback(
                        f"[ПРЕРВАНО] Сканирование остановлено пользователем. "
                        f"Обработано файлов: {files_scanned} из {total_files} "
                        f"({self.abort_percent:.2f}%)",
                        'warning'
                    )
                break
            
            # DS 034: отладочный вывод вызова scan_file (Шаг 2)
            print(f"[DEBUG-DS034] scan_directory: вызываю scan_file для {plp_file.name}")
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
        
    def _parse_class_and_method(self, file_path, line_number: int = None) -> Tuple[str, str, str]:
        """Парсинг имени класса, метода и секции из файла (DS 025).

        DS 038 (Проблема C): если передан line_number — секция определяется
        ПО СТРОКЕ проблемы (последний маркер секции до этой строки),
        а не по первому вхождению секции в файле.
        DS 044: для представлений (view VW_CRIT_*, VW_RPT_*, VW_SQL_*)
        секция = пустая строка, как в эталонном отчёте ЦФТ-PlpCheck.
        """
        class_name = "UNKNOWN"
        method_name = "UNKNOWN"
        section = "PRIVATE"
        
        try:
            content, _ = read_file_with_encoding(Path(file_path))
            lines = content.splitlines()

            # DS 044: определяем — это представление (view) или операция (class)
            is_view = bool(re.search(r'^\s*view\s+\w+', content, re.MULTILINE))

            # Ищем класс
            class_match = re.search(r'\bclass\s+(\w+)', content)
            if class_match:
                class_name = class_match.group(1)
            # Ищем метод
            method_match = re.search(r'\bmethod\s+(\w+)\s+is', content, re.IGNORECASE)
            if method_match:
                method_name = method_match.group(1)
            # DS 044: для представления имя = имя view
            if is_view and method_name == "UNKNOWN":
                view_name_match = re.search(r'^\s*view\s+(\w+)', content, re.MULTILINE)
                if view_name_match:
                    method_name = view_name_match.group(1)

            # DS 044: для представлений секция всегда пуста — как в ЦФТ
            if is_view:
                return class_name, method_name, ""

            # DS 038: карта секций по строкам — маркеры "private is",
            # "execute is", "validate is", "public is"
            section_markers = []  # [(line_num, section_name), ...]
            for i, line in enumerate(lines, 1):
                m = re.match(r'^(private|execute|validate|public)\s+is\b',
                             line.strip(), re.IGNORECASE)
                if m:
                    section_markers.append((i, m.group(1).upper()))
            
            if line_number is not None and section_markers:
                # Секция = последний маркер на строке <= line_number
                current_section = "PRIVATE"  # до первого маркера
                for marker_line, marker_section in section_markers:
                    if marker_line <= line_number:
                        current_section = marker_section
                    else:
                        break
                section = current_section
            elif section_markers:
                # line_number не указан — первая секция в файле
                section = section_markers[0][1]
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
    
    def _generate_active_rubricators_lines(self) -> List[str]:
        """DS 037: строки блока «Активные рубрикаторы и флаги» для отчёта.

        Определяет активность рубрикаторов по кодам правил в self.selected_rules
        (GUI передаёт коды правил вида 'plpcheck.BAD_PREFIX', 'v53...', либо
        коды файлов 'PlpCheck', 'v53' — поддерживаются оба варианта).
        """
        lines = ["Активные рубрикаторы и флаги:"]

        selected_lower = [s.lower() for s in (self.selected_rules or [])]

        # DS 037 (ЗАДАЧА 6): ни один рубрикатор не выбран
        if not selected_lower:
            lines.append("  (ни один рубрикатор не выбран)")
            lines.extend(self._generate_fix_flags_lines())  # DS_053_Уточнение_2 (задача A)
            return lines

        # (ключ, отображаемое имя, префиксы кодов правил)
        rubricators = [
            ('v53',            'v53',            ('v53.', 'v50.')),
            ('тдс20240828',    'тдс20240828',    ('тдс20240828.',)),
            ('тклоик20240828', 'тклоик20240828', ('тклоик20240828.',)),
            ('PlpCheck',       'PlpCheck',       ('plpcheck.',)),
        ]

        for code, name, prefixes in rubricators:
            # Активность: точное совпадение кода файла ИЛИ префикс кода правила
            is_on = any(s == code.lower() or s.startswith(prefixes) for s in selected_lower)
            lines.append(f"  {name:<18}: {'ВКЛ' if is_on else 'ВЫКЛ'}")

            # DS 037: для PlpCheck — детализация по категориям
            if code == 'PlpCheck' and is_on:
                active_lower = [c.lower() for c in (self.plpcheck_categories or [])]

                # DS 037 (ЗАДАЧА 5): PlpCheck выбран, но категории пусты
                if not active_lower:
                    lines.append("    └ (ни одна категория не выбрана — PlpCheck-правила не применялись)")
                else:
                    total = len(PLPCHECK_CATEGORIES)
                    for idx, (cat_code, _cat_descr, _cat_checks) in enumerate(PLPCHECK_CATEGORIES):
                        cat_on = cat_code.lower() in active_lower
                        cat_status = 'ВКЛ' if cat_on else 'ВЫКЛ'
                        prefix = '└' if idx == total - 1 else '├'
                        lines.append(f"    {prefix} {cat_code:<26}: {cat_status}")

        # DS_053_Уточнение_2 (задача A): 6 флагов замены в каноне — во всех отчётах.
        lines.extend(self._generate_fix_flags_lines())
        return lines

    # DS_053_Уточнение_5 (задача B): расшифровки флагов — точно как на форме GUI.
    FIX_FLAG_DESCRIPTIONS = {
        'regex': 'чистые regex-правила',
        'hybrid': 'полудетерм. с algorithmic_hint',
        'ai_fallback': 'помечать needs_ai_fix',
        'ignore': 'не автофиксить, только лог',
        'backup': 'резервные regex-правила',
        'other': 'hybrid без algorithmic_hint',
    }

    def _generate_fix_flags_lines(self) -> List[str]:
        """DS_053_Уточнение_2 (задача A): блок «Флаги замены» по канону.

        Порядок и имена — по канону DS_053 (regex, hybrid, ai_fallback,
        ignore, backup, other). Значения V/x берутся из self.fix_flags;
        если флаги не переданы — дефолт: regex+hybrid включены, остальные
        выключены (совпадает с дефолтом GUI первого запуска).

        DS_053_Уточнение_5 (задача B): каждый флаг снабжён расшифровкой
        (текст — как подписи чекбоксов на форме GUI); выравнивание по «—».
        """
        canon = ['regex', 'hybrid', 'ai_fallback', 'ignore', 'backup', 'other']
        defaults = {'regex': True, 'hybrid': True}
        flags = self.fix_flags if isinstance(self.fix_flags, dict) else {}
        # Ширина колонки «имя: V» — для выравнивания тире.
        width = max(len(f"{n}: {'V'}") for n in canon)
        lines = ["  Флаги замены:"]
        for name in canon:
            on = flags.get(name, defaults.get(name, False))
            left = f"{name}: {'V' if on else 'x'}"
            desc = self.FIX_FLAG_DESCRIPTIONS.get(name, '')
            lines.append(f"    {left:<{width}} — {desc}")
        return lines

    def _normalize_check_name(self, issue_type: str) -> str:
        """DS 044: нормализация CHECK — без префикса plpcheck., в нижнем регистре.

        Если правило есть в PLPCHECK_RULE_NAMES — берём значение оттуда
        (значения уже без префикса и в нижнем регистре).
        Иначе — снимаем префикс ``plpcheck.`` и приводим к нижнему регистру.
        """
        if issue_type in PLPCHECK_RULE_NAMES:
            return PLPCHECK_RULE_NAMES[issue_type]
        name = issue_type
        if name.startswith('plpcheck.'):
            name = name[len('plpcheck.'):]
        return name.lower()

    def generate_report(self, output_path: Path):
        """Генерация отчёта. DS 025: если расширение .html - генерируется HTML-таблица
        в формате дистрибутивного PlpCheck-отчёта.
        DS 032: Markdown-отчёт синхронизирован с эталонным логом ЦФТ-PlpCheck:
        таб-разделяемая таблица № | CLASS_ID | SHORT_NAME | SECTION | LINE | CHECK |
        LEVEL | TYPE | ERROR | PLAN.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # DS 025: HTML-отчёт в формате дистрибутивного PlpCheck
        if output_path.suffix.lower() == '.html':
            self._generate_html_report(output_path)
            return
        
        # DS 030: удаление дубликатов
        unique_issues = []
        seen = set()
        for issue in self.issues:
            key = (issue.file_path, issue.line_number, issue.issue_type, issue.description)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        if not unique_issues:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("CFT Platform IDE Version: 2.36.431 (АРМ «Адаптация под DBI»)\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                # DS 037: блок активных рубрикаторов и флагов
                f.write("\n".join(self._generate_active_rubricators_lines()))
                f.write("\n\n")
                f.write("Проблем не найдено.\n")
            print(f"Отчёт сохранён: {output_path}")
            return
        
        # DS 032: формирование строк таблицы в формате ЦФТ-PlpCheck
        meta_cache = {}
        rows = []
        for issue in unique_issues:
            fp = issue.file_path
            if fp not in meta_cache:
                meta_cache[fp] = self._parse_class_and_method(fp)
            class_name, method_name, default_section = meta_cache[fp]
            
            # CHECK: короткое имя правила PlpCheck без префикса, в нижнем регистре (DS 044)
            check_name = self._normalize_check_name(issue.issue_type)
            # LEVEL: WARNING/ERROR
            if issue.issue_type in PLPCHECK_RULE_LEVELS:
                level = PLPCHECK_RULE_LEVELS[issue.issue_type]
            else:
                level = 'ERROR' if self._get_severity_level(issue.issue_type) == 'ERROR_STYLE' else 'WARNING'
            # TYPE: STYLE/SYNTAX/SQL/... или категория правила
            issue_type_ru = PLPCHECK_RULE_TYPES.get(issue.issue_type, issue.category.upper())
            # SECTION: точная секция (DS 032) или секция из метаданных файла.
            # DS 038 (Проблема C): если issue.section пуст — секция определяется
            # ПО СТРОКЕ проблемы, а не по первому вхождению секции в файле
            if issue.section:
                section = issue.section
            else:
                _, _, section = self._parse_class_and_method(fp, line_number=issue.line_number)
            # PLAN (DS_059: формат <CHECK> — <действие>)
            plan = self._generate_plan(issue.issue_type, issue.description,
                                       check_name=check_name)
            
            # ERROR (DS_059_Уточнение_A): <описание>: "<исходный_фрагмент>"
            error_text = self._error_with_fragment(issue)
            rows.append({
                'class': class_name,
                'method': method_name,
                'section': section,
                'line': issue.line_number,
                'check': check_name,
                'level': level,
                'type': issue_type_ru,
                'error': error_text,
                'plan': plan,
                'file': fp,
            })
        
        # Сортировка: файл -> строка -> not_mentioned первым -> алфавит CHECK
        def _row_sort_key(r):
            check_order = 0 if r['check'] == 'not_mentioned' else 1
            return (r['file'], r['line'], check_order, r['check'])
        
        rows.sort(key=_row_sort_key)
        
        # Таблица в формате эталонного лога ЦФТ-PlpCheck (таб-разделяемая)
        header = "№	CLASS_ID	SHORT_NAME	SECTION	LINE	CHECK	LEVEL	TYPE	ERROR	PLAN"
        sep = "-" * 149
        table_lines = [header, sep]
        for i, r in enumerate(rows, 1):
            table_lines.append(
                f"{i}	{r['class']}	{r['method']}	{r['section']}	{r['line']}	"
                f"{r['check']}	{r['level']}	{r['type']}	{r['error']}	{r['plan']}"
            )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("CFT Platform IDE Version: 2.36.431 (АРМ «Адаптация под DBI»)\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            # DS 037: блок активных рубрикаторов и флагов
            f.write("\n".join(self._generate_active_rubricators_lines()))
            f.write("\n\n")
            f.write("\n".join(table_lines))
            f.write("\n\n")
            # DS 041: при прерывании «Всего» вводит в заблуждение — обработана
            # только часть файлов. Вариант B: при прерывании «Обработано»,
            # при завершении — привычное «Всего».
            total_word = "Обработано" if self.abort_percent is not None else "Всего"
            f.write(f"{total_word} проблем: {len(self.issues)}\n")
            # DS 033: «Уникальных» считается группировкой по (LINE, CHECK) —
            # как в эталонном логе ЦФТ-PlpCheck (два bad_prefix на строке 17
            # схлопываются в одну уникальную позицию)
            unique_line_check = len(set((r['file'], r['line'], r['check']) for r in rows))
            f.write(f"Уникальных проблем: {unique_line_check}\n")
            f.write(f"{total_word} файлов: {len(meta_cache)}\n")
            # DS 043: упрощённая строка прерывания (без HTML-тегов, без эмодзи)
            if self.abort_percent is not None:
                f.write("\n")
                f.write(f"ПРЕРВАНО НА {self.abort_percent:.2f} %\n")
        
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
            class_name, method_name, _ = parsed_cache[fp]
            # DS 038 (Проблема C): секция по строке проблемы, а не по первому вхождению
            if issue.section:
                section = issue.section
            else:
                _, _, section = self._parse_class_and_method(fp, line_number=issue.line_number)
            severity = self._get_severity_level(issue.issue_type)
            # DS 044: LEVEL — без суффикса _STYLE (WARNING / ERROR, как в ЦФТ)
            level_clean = severity.replace('_STYLE', '')
            plan_data = self._generate_issue_with_plan(issue, len(rows), parsed_cache)
            rows.append({
                'class': class_name,
                'method': method_name,
                'section': section,
                'line': issue.line_number,
                # DS 044: CHECK — без префикса plpcheck., в нижнем регистре
                'check': self._normalize_check_name(issue.issue_type),
                # DS 044: TYPE — затронутые технологии (STYLE, DBI,JAVA,PLSQL, ...)
                'type': PLPCHECK_RULE_TYPES.get(issue.issue_type, issue.category.upper()),
                'level': level_clean,
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
            css = 'error' if r['level'] == 'ERROR' else ('warning' if r['level'] == 'WARNING' else 'info')
            
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
                f'<td>{html_module.escape(str(r["check"]))}</td>'
                f'<td>{html_module.escape(r["level"])}</td>'
                f'<td>{html_module.escape(str(r["type"]))}</td>'
                f'<td>{html_module.escape(str(r["description"]))}</td>'
                f'<td>{plan_html}</td>'
                f'</tr>'
            )
        
        # DS 042: условные заголовки + блок прерывания
        is_aborted = self.abort_percent is not None
        label_issues = "Обработано проблем" if is_aborted else "Всего найдено проблем"
        label_files = "Обработано файлов" if is_aborted else "Всего файлов"
        meta_html = (
            f'<p class="meta">Дата: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} &nbsp;|&nbsp;\n'
            f'   {label_issues}: {len(rows)} &nbsp;|&nbsp;\n'
            f'   {label_files}: {len(parsed_cache)}</p>'
        )
        # DS 042: блок ⚠ ПРЕРВАНО
        if is_aborted:
            meta_html += (
                f'\n<div style="background:#FFF4CC; color:#8B6914; '
                f'font-weight:bold; padding:8px 12px; border:1px solid #FFA500; '
                f'margin-bottom:20px;">'
                f'⚠ ПРЕРВАНО НА {self.abort_percent:.2f} %'
                f'</div>'
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
        .active-rubricators {{ background: #fff; border: 1px solid #bdc3c7; padding: 10px 14px;
            font-family: 'Consolas', 'Courier New', monospace; font-size: 13px;
            white-space: pre; margin-bottom: 20px; color: #2c3e50; }}
    </style>
</head>
<body>
    <h1>PlpCheck Отчёт</h1>
    {meta_html}
    <div class="active-rubricators">{html_module.escape(chr(10).join(self._generate_active_rubricators_lines()))}</div>
    <h2>Статистика</h2>
    <table>
        <thead><tr><th>Уровень</th><th>Количество</th></tr></thead>
        <tbody>{stats_rows}</tbody>
    </table>
    <h2>Проблемы</h2>
    <table>
        <thead>
            <tr>
                <th>№</th>
                <th>CLASS_ID</th>
                <th>SHORT_NAME</th>
                <th>SECTION</th>
                <th>LINE</th>
                <th>CHECK</th>
                <th>LEVEL</th>
                <th>TYPE</th>
                <th>ERROR</th>
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
    
    # DS_059: глаголы действия (Приложение A задания)
    _ACTION_VERBS = (
        # Категория 1 — прямое действие
        'переименовать', 'переименуйте', 'удалить', 'удалите', 'добавить',
        'добавьте', 'заменить', 'замените', 'исправить', 'исправьте',
        'вынести', 'вынесите', 'преобразовать', 'преобразуйте', 'исключить',
        'исключите', 'убрать', 'уберите',
        # Категория 2 — стилевое / синтаксическое
        'привести', 'приведите', 'оформить', 'оформите', 'переписать',
        'перепишите', 'переделать', 'переделайте', 'изменить', 'измените',
        # Категория 3 — проверка / контроль
        'проверить', 'проверьте', 'проконтролировать', 'проконтролируйте',
        'убедиться', 'убедитесь',
        # Категория 4 — указание / вынесение
        'указать', 'укажите', 'выделить', 'выделите', 'объявить', 'объявите',
        # Категория 5 — удаление / обнуление
        'снять', 'снимите', 'обнулить', 'обнулите', 'очистить', 'очистите',
        # Категория 6 — отказ / замена
        'отказаться', 'откажитесь', 'заместить', 'заместите',
        # Категория 7 — улучшение / оптимизация
        'оптимизировать', 'оптимизируйте', 'упростить', 'упростите',
        'сократить', 'сократите',
    )

    # DS_059: ложные глаголы — исключения (Приложение B задания)
    _FALSE_ACTION_PREFIXES = (
        'наименование', 'имя', 'название', 'идентификатор', 'код',
        'объявление', 'описание', 'проверка', 'использование', 'обращение',
        'сравнение', 'присвоение', 'передача', 'вызов', 'определение',
        'тип', 'значение', 'ссылка', 'свойство', 'параметр',
        'не корректный', 'не корректное', 'не корректная',
        'некорректный', 'некорректное', 'некорректная',
        'отсутствует', 'отсутствие', 'не найден', 'не найдено',
        'запрещено', 'запрещён', 'запрещена', 'недопустимо', 'недопустимый',
        'ошибка', 'предупреждение', 'внимание',
    )

    def _error_is_action(self, error_text: str) -> Optional[str]:
        """DS_059: является ли ERROR действием (Приложения A/B задания).

        1. Начинается с глагола действия -> вернуть ERROR как действие.
        2. Начинается с заглавной, глагол в первых 3 словах, длина < 200,
           не из списка исключений -> действие.
        Иначе — None.
        """
        text = (error_text or '').strip()
        if not text:
            return None
        low = text.lower()
        # Приложение B: исключения имеют приоритет — не действие
        for pref in self._FALSE_ACTION_PREFIXES:
            if low.startswith(pref):
                return None
        # Приоритет 1: начинается с глагола действия
        for verb in self._ACTION_VERBS:
            if low.startswith(verb + ' ') or low == verb:
                return text
        # Приоритет 2: заглавная + глагол в первых 3 словах + длина < 200
        if text[0].isupper() and len(text) < 200:
            words = low.split()[:3]
            for w in words:
                w_clean = w.strip('.,;:!?()«»"\'')
                if w_clean in self._ACTION_VERBS:
                    return text
        return None

    def _transform_action(self, issue_type: str) -> Optional[str]:
        """DS_059 (приоритет 3): действие из PARSER_SQL —
        "Заменить <example_in> на <example_out>" (или transform)."""
        try:
            from rule_engine import get_rule_engine
            eng = get_rule_engine()
            rule = eng.get_rule(issue_type)
            if not rule:
                return None
            for pt in rule.get('patterns', []):
                ex_in = (pt.get('example_in') or '').strip()
                ex_out = (pt.get('example_out') or '').strip()
                if ex_in and ex_out:
                    return f'Заменить {ex_in} на {ex_out}'
                transform = (pt.get('transform') or '').strip()
                if transform and ex_out:
                    return f'Заменить на {transform}'
            return None
        except Exception:
            return None

    # DS_059_Уточнение_A: тип-ключевые слова PlpCheck-объявлений
    _PLP_TYPE_KEYWORDS = r'(?:boolean|varchar2|string|number|integer|date)'

    def _extract_error_fragment(self, issue) -> Optional[str]:
        """DS_059_Уточнение_A: исходный проблемный фрагмент для колонки ERROR.

        Приоритет источников: правило-специфичное извлечение из
        issue.original_code / issue.description; фолбэк — исходная строка
        (сжатые пробелы, обрезка до 50 символов). Если фрагмент недоступен —
        None (в ERROR ничего не добавляется, не выдумываем).
        """
        itl = (issue.issue_type or '').lower()
        oc = (issue.original_code or '').strip()
        desc = (issue.description or '').strip()

        def _identifiers(text):
            return re.findall(r'\b[A-Za-z_]\w*\b', text or '')

        if 'bad_prefix' in itl:
            # Имя без корректного префикса v_/p_ в объявлении/параметре
            for m in re.finditer(rf'(\w+)\s+{self._PLP_TYPE_KEYWORDS}\b',
                                 oc, re.IGNORECASE):
                name = m.group(1)
                if not name.lower().startswith(('v_', 'p_')):
                    return name
            ids = _identifiers(oc)
            if ids:
                return ids[0]
        elif 'not_mentioned' in itl:
            m = re.search(r'(?:Переменная|Функция)\s+(\w+)', desc)
            if m:
                return m.group(1)
        elif 'prefix_type_in_var_name' in itl:
            m = re.search(rf'(\w+)\s+{self._PLP_TYPE_KEYWORDS}\b', oc,
                          re.IGNORECASE)
            if m:
                return m.group(1)
            ids = _identifiers(oc)
            if ids:
                return ids[0]
        elif 'wrong_method_syntax' in itl:
            m = re.search(r'\[(\w+)\]\.(\w+)\s*\(', oc)
            if m:
                return f'[{m.group(1)}].{m.group(2)}'
        elif 'code_in_comment' in itl:
            frag = oc.lstrip('-').strip()
            if frag.startswith('/*'):
                frag = frag[2:].strip()
            if frag:
                return frag[:50] + ('…' if len(frag) > 50 else '')

        # Универсальный фолбэк: исходная строка (до 50 символов)
        if oc:
            frag = re.sub(r'\s+', ' ', oc)
            return frag[:50] + ('…' if len(frag) > 50 else '')
        return None

    def _error_with_fragment(self, issue) -> str:
        """DS_059_Уточнение_A: ERROR = '<описание>: "<исходный_фрагмент>"'.

        PLAN не меняется (остаётся действием). Если фрагмент недоступен —
        возвращается только описание.
        """
        desc = (issue.description or '').strip().rstrip(':')
        frag = self._extract_error_fragment(issue)
        if frag:
            return f'{desc}: "{frag}"'
        return desc

    def _generate_plan(self, issue_type: str, description: str = '',
                       check_name: str = None) -> str:
        """Генерация текста ПЛАНА на основе типа правила.

        DS_059: унификация — приоритеты источника действия:
        спец-ветки PlpCheck (извлечение из description) -> ERROR как действие
        (Приложения A/B) -> transform+example_out из PARSER_SQL -> фолбэк
        «Исправить по описанию». Формат: <CHECK> — <действие>.
        """
        issue_type_lower = issue_type.lower()

        # Спец-ветки PlpCheck (извлечение действия из description) — сохранены
        special = None
        if 'bad_prefix' in issue_type_lower:
            import re
            match = re.search(r'переименуйте в ["\']([^"\']+)["\']', description, re.IGNORECASE)
            if match:
                special = f'Переименовать в "{match.group(1)}"'
            else:
                special = 'Переименовать в корректный префикс'
        elif 'not_mentioned' in issue_type_lower:
            special = 'Удалить объявление'
        elif 'code_in_comment' in issue_type_lower:
            special = 'Удалить закомментированный код'
        elif 'wrong_method_syntax' in issue_type_lower:
            special = 'Исправить синтаксис'
        elif 'prefix_type_in_var_name' in issue_type_lower:
            special = 'Добавить префикс типа'
        elif 'syntax_error' in issue_type_lower:
            special = 'Исправить синтаксическую ошибку'
        elif 'pure_sql_dblink' in issue_type_lower:
            special = 'Заменить на прикладную таблицу'
        elif 'pure_udf' in issue_type_lower or 'udf' in issue_type_lower:
            special = 'Вынести UDF в процедурный код'
        elif 'outer_join' in issue_type_lower:
            special = 'Заменить на ANSI JOIN'
        elif 'rownum' in issue_type_lower:
            special = 'Заменить на FETCH'
        elif 'direct_comparison' in issue_type_lower:
            special = 'Исправить сравнение с NULL'
        elif 'update_delete_by_subquery' in issue_type_lower:
            special = 'Заменить на прикладную таблицу'
        elif 'connectby2with' in issue_type_lower:
            special = 'Заменить на CONNECT BY PRIOR'

        # Универсальные приоритеты DS_059
        action = special
        if action is None:
            action = self._error_is_action(description)
        if action is None:
            action = self._transform_action(issue_type)
        if action is None:
            action = 'Исправить по описанию'

        # Формат: <CHECK> — <действие>
        check = check_name if check_name else issue_type
        return f'{check} — {action}'
    
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