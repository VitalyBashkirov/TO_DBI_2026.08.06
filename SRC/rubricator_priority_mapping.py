#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Маппинг между пунктами в "Приоритизация задач для адаптации прикладного кода под требования DBI"
и кодами правил рубрикатора v5.3.0

Файл: Этапы миграции ЦФТ.docx -> Приложение 1 -> Таблица приоритетов
"""


# Маппинг: "Пункт в Рекомендациях" -> список кодов правил рубрикатора
# Формат пункта: "X.Y. Название" или "X.Y.Z. Название"
RUBRICATOR_PRIORITY_MAPPING = {
    # Приоритет 1
    '1.1': ['v53.SQL.OUTERJOIN.п.1.1'],
    '1.1. Outer_join': ['v53.SQL.OUTERJOIN.п.1.1'],
    
    # Приоритет 2
    '1.2': ['v53.SQL.ROWNUM.п.1.2'],
    '1.2. Ограничение выборки': ['v53.SQL.ROWNUM.п.1.2'],
    '1.21': ['v53.SQL.SIMPLE_VIEW.п.1.21'],
    '1.21. Простые представления Oracle': ['v53.SQL.SIMPLE_VIEW.п.1.21'],
    '4.2': ['v53.INT.DBLINK.п.4.2'],
    '4.2. Использование Database Link в прикладном коде': ['v53.INT.DBLINK.п.4.2'],
    '4.3': ['v53.INT.CLIENT.п.4.3'],
    '4.3. Подключение внешнего клиентского приложения к базе данных': ['v53.INT.CLIENT.п.4.3'],
    '4.4.1': ['v53.INT.SYNC.п.4.4.1'],
    '4.4.1. Интегратор. Синхронное взаимодействие': ['v53.INT.SYNC.п.4.4.1'],
    '4.4.2': ['v53.INT.QUEUE.п.4.4'],
    '4.4.2. Интегратор. Прямой вызов обработчиков': ['v53.INT.QUEUE.п.4.4'],
    
    # Приоритет 3
    '1.3': ['v53.SQL.UDF.п.1.3'],
    '1.3. UDF': ['v53.SQL.UDF.п.1.3'],
    '1.8': ['v53.SQL.CONNECTBY.п.1.8'],
    '1.8. Иерархические запросы': ['v53.SQL.CONNECTBY.п.1.8'],
    '1.10': ['v53.SQL.SYSTABLES.п.1.10'],
    '1.10. Системные таблицы и представления ТЯ': ['v53.SQL.SYSTABLES.п.1.10'],
    '1.17': ['v53.SQL.DML_JOIN.п.1.17'],
    '1.17. DML on join': ['v53.SQL.DML_JOIN.п.1.17'],
    '1.20': ['v53.SQL.PSEUDO.п.1.20'],
    '1.20. Прочие псевдоколонки Oracle': ['v53.SQL.PSEUDO.п.1.20'],
    '2.1': ['v53.STOR.NESTED.п.2.1'],
    '2.1. Nested table': ['v53.STOR.NESTED.п.2.1'],
    '2.7': ['v53.STOR.OLE.п.2.7'],
    '2.7. OLE объекты Oracle': ['v53.STOR.OLE.п.2.7'],
    '3.9': ['v53.PROC.PIPELINED.п.3.9'],
    '3.9. Pipelined functions': ['v53.PROC.PIPELINED.п.3.9'],
    '3.10': ['v53.PROC.REPORT.п.3.10'],
    '3.10. Оракловые отчеты': ['v53.PROC.REPORT.п.3.10'],
    '3.11': ['v53.PROC.TYPING.п.3.11'],
    '3.11. Ограничения типизации': ['v53.PROC.TYPING.п.3.11'],
    
    # Приоритет 4
    '1.6.1': ['v53.SQL.DECODE.п.1.6.1'],
    '1.6.1 SQL функции': ['v53.SQL.DECODE.п.1.6.1'],
    '1.6': ['v53.SQL.ANALYTIC.п.1.6'],
    '1.6. Аналитические SQL функции': ['v53.SQL.ANALYTIC.п.1.6'],
    '1.11': ['v53.SQL.ORACLE_PKG.п.1.11'],
    '1.11. Oracle supplied PL/SQL': ['v53.SQL.ORACLE_PKG.п.1.11'],
    '1.14': ['v53.SQL.FUNC_REQ.п.1.14'],
    '1.14. Функциональные реквизиты': ['v53.SQL.FUNC_REQ.п.1.14'],
    '1.19': ['v53.SQL.VW_CRIT_RPT.п.1.19'],
    '1.19. Select from VW_CRIT, VW_RPT, VW_SQL (родительская заявка)': ['v53.SQL.VW_CRIT_RPT.п.1.19'],
    '3.1': ['v53.PROC.UTILS.п.3.1.1'],
    '3.1. Oracle supplied PL/SQL packages': ['v53.PROC.UTILS.п.3.1.1'],
    '3.1.1': ['v53.PROC.CRYPTO.п.3.1.2'],
    '3.1.1. Замена использования ::[RUNTIME].[LIB_EXT_CALL] ( Oracle dbms_crypto)': ['v53.PROC.CRYPTO.п.3.1.2'],
}


def get_rules_for_priority(priority_name: str) -> list:
    """
    Получить список кодов правил для выбранного приоритета.
    
    Args:
        priority_name: Название приоритета (например, 'Приоритет 1')
    
    Returns:
        Список кодов правил рубрикатора
    """
    if priority_name not in PRIORITY_RULES:
        return []
    
    return list(PRIORITY_RULES[priority_name])


# Обратный маппинг: Приоритет -> список кодов правил
# (только для правил, которые существуют в рубрикаторе v5.3.0)
PRIORITY_RULES = {
    'Приоритет 1': [
        'v53.SQL.OUTERJOIN.п.1.1',
        'v53.SQL.ROWNUM.п.1.2',
        'v53.SQL.UDF.п.1.3',
        'v53.SQL.CAST.п.1.5',
        'v53.SQL.DECODE.п.1.6.1',
        'v53.SQL.CONNECTBY.п.1.8',
        'v53.SQL.SYSVIEW.п.1.9',
        'v53.SQL.SYSTABLES.п.1.10',
        'v53.SQL.ORACLE_PKG.п.1.11',
        'v53.SQL.TABLE_SELECT.п.1.13',
        'v53.SQL.FUNC_REQ.п.1.14',
        'v53.SQL.XMLTYPE.п.1.15',
        'v53.SQL.XMLQUERY.п.1.16',
        'v53.SQL.DML_JOIN.п.1.17',
        'v53.SQL.HINTS.п.1.18',
        'v53.SQL.VW_CRIT_RPT.п.1.19',
        'v53.SQL.PSEUDO.п.1.20',
        'v53.SQL.SIMPLE_VIEW.п.1.21',
        'v53.SQL.CONTEXT.п.1.23',
        'v53.SQL.DDL.п.1.24',
        'v53.SQL.EXCEPTIONLOOP.п.1.25',
        'v53.SQL.BIND_GROUP.п.1.26',
        'v53.SQL.REF_SELECT.п.1.27',
        'v53.SQL.BULK.п.1.28',
        'v53.SQL.EMPTY_CURSOR.п.1.29',
        'v53.SQL.CREATE_VIEW.п.1.30',
        'v53.STOR.DATE.п.2.2',
        'v53.STOR.UNIQUE_IDX.п.2.6.2',
        'v53.STOR.INDEX.п.2.6.3',
        'v53.STOR.TEMP.п.2.8',
        'v53.PROC.UTILS.п.3.1.1',
        'v53.PROC.CRYPTO.п.3.1.2',
        'v53.PROC.SMTP.п.3.1.3',
        'v53.PROC.JSON.п.3.1.4',
        'v53.PROC.HTTP.п.3.1.6',
        'v53.PROC.EMPTY_STRING.п.3.2',
        'v53.PROC.DYNAMIC_SQL.п.3.3',
        'v53.PROC.MACROS.п.3.4',
        'v53.PROC.WHENOTHERS.п.3.5',
        'v53.PROC.XML.п.3.6',
        'v53.PROC.TRIGGER.п.3.8',
        'v53.PROC.CODEGEN.п.3.15',
        'v53.PROC.CHARSET.п.3.16',
        'v53.PROC.NATIVEID.п.3.26',
        'v53.PROC.ID_SIZE.п.3.27',
        'v53.PROC.DYNAMIC_PL.п.3.28',
        'v53.INT.UTL_HTTP.п.4.1',
        'v53.INT.DBLINK.п.4.2',
        'v53.INT.QUEUE.п.4.4',
        'тдс20240828.DML_JOIN.стр.1',
        'тдс20240828.SYSTEM_TABLES.стр.2',
        'тдс20240828.PSEUDOCOLUMNS.стр.3',
        'тдс20240828.FETCH_ROWNUM.стр.7',
        'тдс20240828.UDF_LIMITS.стр.8',
        'тдс20240828.XMLTYPE.стр.9',
        'тдс20240828.VW_CRIT_RPT.стр.10',
        'тдс20240828.MACROS_EXECUTE.стр.11',
        'тдс20240828.DYNAMIC_SQL.стр.12',
        'тдс20240828.DECODE_CASE.стр.13',
        'тдс20240828.TEMP_TABLES.стр.15',
        'тдс20240828.TRIGGERS.стр.16',
        'тдс20240828.CONNECT_BY.стр.18',
        'тдс20240828.TYPE_CAST.стр.19',
        'тдс20240828.EXCEPTIONLOOP.стр.20',
        'тдс20240828.BIND_GROUP.стр.21',
        'тдс20240828.CONTEXTS.стр.22',
        'тдс20240828.SYS_VIEWS.стр.23',
        'тдс20240828.VARRAY_NESTED.стр.25',
        'тдс20240828.ORACLE_PACKAGES.стр.27',
        'тдс20240828.CODEGEN.стр.28',
        'тдс20240828.TRANS_ABORTED.стр.29',
        'тдс20240828.JSON_ORACLE.стр.30',
        'тдс20240828.CHARSET.стр.31',
        'тдс20240828.EMPTY_STRING_NULL.стр.34',
        'тдс20240828.COND_COMPILE.стр.35',
        'тдс20240828.DB_LINK.стр.36',
        'тдс20240828.EXECUTE_IMMEDIATE.стр.33',
        'тклоик20240828.NO_INTEGER_FOR_ID.стр.4',
        'тклоик20240828.NO_GOTO.стр.5',
        'тклоик20240828.NO_PLSQL_INSERT.стр.8',
        'PlpCheck.DBI.ANALYTIC_AND_FETCH_BAD_USE.п.1',
        'PlpCheck.DBI.EXCEPTIONLOOP.п.1',
        'PlpCheck.DBI.CONNECTBY2WITH.п.1',
        'PlpCheck.DBI.DIRECT_COMPARISON_WITH_NULL.п.1',
        'PlpCheck.DBI.EMPTY_STRING_IN_CURSOR.п.1',
        'PlpCheck.DBI.ROWNUM.п.1',
        'PlpCheck.DBI.NESTED_TABLE.п.1',
        'PlpCheck.DBI.REFERENCE_COMPARISON.п.1',
        'PlpCheck.DBI.SCHEMA_IN_DDL.п.1',
        'PlpCheck.DBI.UPDATE_DELETE_BY_SUBQUERY.п.1',
        'PlpCheck.DBI.PURE_SQL_OUTER_JOIN.п.1',
        'PlpCheck.DBI.PURE_SQL_PSEUDOCOL_UNSUPPORTED.п.1',
        'PlpCheck.DBI.PURE_SQL_FUNCTION_UNSUPPORTED.п.1',
        'PlpCheck.DBI.OBLIGATORY_IN_OTHERS.п.1',
        'PlpCheck.DBI.OUTER_JOIN.п.1',
        'PlpCheck.DBI.SELECTANALYTICARGUMENT.п.1',
    ],
    'Приоритет 2': [
        'v53.INT.DBLINK.п.4.2',
        'v53.SQL.OUTERJOIN.п.1.1',
        'v53.SQL.ROWNUM.п.1.2',
        'v53.SQL.ANALYTIC.п.1.6',
        'v53.SQL.SIMPLE_VIEW.п.1.21',
        'v53.SQL.FUNC_REQ.п.1.14',
        'v53.PROC.CRYPTO.п.3.1.2',
        'v53.PROC.PARENT_REF.п.3.22',
        'v53.PROC.SAVEPOINT_LIMIT.п.3.18.2',
        'v53.PROC.TRANSACT_CONTROL.п.3.18.3',
        'v53.PROC.SAVEPOINT_LENGTH.п.3.18.4',
        'v53.INT.SYNC.п.4.4.1',
        'v53.INT.CLIENT.п.4.3',
        'тдс20240828.REPORTS.стр.4',
        'тдс20240828.SIMPLE_VIEWS.стр.5',
        'тдс20240828.ANSI_JOIN.стр.6',
        'тдс20240828.DATE_ARITHMETIC.стр.14',
        'тдс20240828.ROWID_TABLE.стр.26',
        'тдс20240828.XMLQUERY.стр.24',
        'тдс20240828.SET_THIS.стр.32',
        'тдс20240828.FP_TUNE.стр.39',
        'тклоик20240828.THIS_FORBIDDEN.стр.3',
        'тклоик20240828.NO_SAVEPOINT_DIRECT.стр.5',
        'тклоик20240828.VARCHAR_SIZE.стр.4',
        'тклоик20240828.NO_OBJECTS_VIEW.стр.3',
        'тклоик20240828.NO_MULTI_MODIFIER.стр.3',
        'PlpCheck.DBI.MULTIPLE_MODIFIERS.п.1',
        'PlpCheck.DBI.FETCH_OVER_SUBQUERY.п.1',
        'PlpCheck.DBI.CROSS_DB_QUERY.п.1',
        'PlpCheck.DBI.CONSTANT_ORDER_BY_ON_UDF.п.1',
        'PlpCheck.DBI.INTERVAL_NOT_SELECT.п.1',
        'PlpCheck.DBI.THIS_IN_DEFAULT.п.1',
        'PlpCheck.DBI.OBLIGATORY_UNIQUE_ALIAS.п.1',
        'PlpCheck.DBI.FULL_INDEX_SCAN.п.1',
        'PlpCheck.DBI.FULL_TABLE_SCAN.п.1',
        'PlpCheck.DBI.PARTITION_ALL.п.1',
        'PlpCheck.DBI.JOBS.п.1',
    ],
    'Приоритет 3': [
        'v53.PROC.TYPING.п.3.11',
        'v53.SQL.CONNECTBY.п.1.8',
        'v53.SQL.DML_JOIN.п.1.17',
        'v53.SQL.PSEUDO.п.1.20',
        'v53.SQL.ROWNUM.п.1.2',
        'v53.SQL.SYSTABLES.п.1.10',
        'v53.SQL.UDF.п.1.3',
        'v53.STOR.NESTED.п.2.1',
        'v53.STOR.OLE.п.2.7',
        'v53.PROC.PIPELINED.п.3.9',
        'v53.PROC.REPORT.п.3.10',
        'v53.PROC.SQLCODE.п.3.7',
        'v53.PROC.UTL_URL.п.3.1.5',
        'v53.PROC.UTL_TCP.п.3.1.7',
        'v53.PROC.LOB.п.3.13',
        'v53.PROC.UNREACHABLE.п.3.14.1',
        'v53.PROC.SORT_BY_ID.п.3.29',
        'v53.PROC.COMPILE_TARGET.п.3.25',
        'v53.PROC.DYNAMIC_PL.п.3.28',
        'тдс20240828.JOBS_SCHEDULE.стр.38',
        'тклоик20240828.PREFIX_FTC.стр.1',
        'тклоик20240828.PREFIX_BANK.стр.1',
        'тклоик20240828.LOCAL_OBJECTS.стр.1',
        'тклоик20240828.OOXML.стр.1',
        'тклоик20240828.VIEW_DEFAULT.стр.2',
        'тклоик20240828.VIEW_COLUMNS.стр.2',
        'тклоик20240828.VIEW_FETCH.стр.2',
        'тклоик20240828.NAMING_UNDERSCORE.стр.2',
        'тклоик20240828.REFERENCE_SYNTAX.стр.2',
        'тклоик20240828.REUSE_LIBRARIES.стр.3',
        'тклоик20240828.CYRILLIC.стр.1',
        'тклоик20240828.CASE.стр.8',
        'тклоик20240828.MACROS_LIMIT.стр.8',
        'тклоик20240828.DEBUG.стр.8',
        'тклоик20240828.FORM_SIZE.стр.10',
        'тклоик20240828.FORM_ORDER.стр.10',
        'тклоик20240828.EDIT_HOTKEY.стр.10',
        'тклоик20240828.PARAM_ORDER.стр.10',
        'PlpCheck.STYLE.BAD_PREFIX.п.4.3',
        'PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4',
        'PlpCheck.STYLE.PREFIX_TYPE.п.4.4',
        'PlpCheck.STYLE.NOT_MENTIONED.п.4.8',
        'PlpCheck.STYLE.RESERVED_PREFIX.п.4.5',
        'PlpCheck.STYLE.SIZELESS.п.4.17',
    ],
    'Приоритет 4': [
        'v53.PROC.CRYPTO.п.3.1.2',
        'v53.SQL.DECODE.п.1.6.1',
        'v53.SQL.ORACLE_PKG.п.1.11',
        'v53.SQL.VW_CRIT_RPT.п.1.19',
        'v53.SQL.FUNC_REQ.п.1.14',
        'v53.SQL.XMLTYPE.п.1.15',
        'v53.SQL.XMLQUERY.п.1.16',
        'v53.STOR.SPEC_CHARS.п.2.10',
        'v53.PROC.LOB.п.3.13',
        'v53.PROC.REGEXP.п.3.12',
        'v53.PROC.CONCAT_LIB.п.3.23',
        'v53.PROC.GENERIC_REF.п.3.24',
        'v53.INT.CLIENT.п.4.3',
        'тдс20240828.COND_COMPILE.стр.35',
        'тдс20240828.INTEGRATOR_SYNC.стр.37',
        'тклоик20240828.VARIABLE_PREFIX.стр.6',
        'тклоик20240828.CONSTANT_PREFIX.стр.6-7',
        'тклоик20240828.PARAM_PREFIX.стр.7',
        'тклоик20240828.CURSOR_PREFIX.стр.7',
        'тклоик20240828.GLOBAL_VAR.стр.7',
        'тклоик20240828.VALIDATE_UNIQUE.стр.10',
        'PlpCheck.DBI.OBLIGATORY_UNIQUE_ALIAS.п.1',
        'PlpCheck.DBI.PURE_SQL_JSON_TYPES.п.1',
        'PlpCheck.DBI.PURE_SQL_MINUS_NOT_DBI.п.1',
        'PlpCheck.DBI.WRONG_ATTR_SYNTAX.п.1',
        'PlpCheck.DBI.WRONG_CLASS_SYNTAX.п.1',
        'PlpCheck.DBI.WRONG_METHOD_SYNTAX.п.1',
        'PlpCheck.DBI.WRONG_REF_SYNTAX.п.1',
        'PlpCheck.DBI.STRING_AS_CLASS.п.1',
        'PlpCheck.DBI.UDF.п.1',
        'PlpCheck.DBI.UDF_IN_FILTER_FORMULA.п.1',
        'PlpCheck.DBI.DISTINCT_AND_ORDER_BY.п.1',
        'PlpCheck.DBI.DISTINCT_UDF.п.1',
        'PlpCheck.DBI.DEREFERENCE_IN_LOOP.п.1',
        'PlpCheck.DBI.DEREFERENCING_TO_OUT_PARAM.п.1',
    ],
}


def get_matching_rules(rule_code: str, selected_priorities: list) -> bool:
    """
    Проверить, принадлежит ли правило хотя бы одному из выбранных приоритетов.
    
    Args:
        rule_code: Код правила рубрикатора
        selected_priorities: Список выбранных приоритетов
    
    Returns:
        True если правило входит хотя бы в один выбранный приоритет
    """
    if not selected_priorities:
        return True  # Если приоритеты не выбраны — показываем все
    
    for priority in selected_priorities:
        if rule_code in PRIORITY_RULES.get(priority, set()):
            return True
    
    return False


def print_priority_summary():
    """Печать сводки по приоритетам"""
    print('Сводка по приоритетам:')
    print('=' * 60)
    for priority, rules in sorted(PRIORITY_RULES.items()):
        print(f'{priority}: {len(rules)} правил')
        for r in rules:
            print(f'  - {r}')
        print()


if __name__ == '__main__':
    print_priority_summary()