#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Маппинг между пунктами в "Приоритизация задач для адаптации прикладного кода под требования DBI"
и кодами правил рубрикатора v3.0.0

Файл: Этапы миграции ЦФТ.docx -> Приложение 1 -> Таблица приоритетов
"""


# Маппинг: "Пункт в Рекомендациях" -> список кодов правил рубрикатора
# Формат пункта: "X.Y. Название" или "X.Y.Z. Название"
RUBRICATOR_PRIORITY_MAPPING = {
    # Приоритет 1
    '1.1': ['v50.SQL.OUTERJOIN.п.1.1'],
    '1.1. Outer_join': ['v50.SQL.OUTERJOIN.п.1.1'],
    
    # Приоритет 2
    '1.2': ['v50.SQL.ROWNUM.п.1.2'],
    '1.2. Ограничение выборки': ['v50.SQL.ROWNUM.п.1.2'],
    '1.21': ['v50.SQL.SIMPLE_VIEW.п.1.21'],
    '1.21. Простые представления Oracle': ['v50.SQL.SIMPLE_VIEW.п.1.21'],
    '4.2': ['v50.INT.DBLINK.п.4.2'],
    '4.2. Использование Database Link в прикладном коде': ['v50.INT.DBLINK.п.4.2'],
    '4.3': ['v50.INT.SOAP.п.4.3'],
    '4.3. Подключение внешнего клиентского приложения к базе данных': ['v50.INT.SOAP.п.4.3'],
    '4.4.1': ['v50.INT.REST_SYNC.п.4.4.1'],
    '4.4.1. Интегратор. Синхронное взаимодействие': ['v50.INT.REST_SYNC.п.4.4.1'],
    '4.4.2': ['v50.INT.REST_DIRECT.п.4.4.2'],
    '4.4.2. Интегратор. Прямой вызов обработчиков': ['v50.INT.REST_DIRECT.п.4.4.2'],
    
    # Приоритет 3
    '1.3': ['v50.SQL.UDF.п.1.3'],
    '1.3. UDF': ['v50.SQL.UDF.п.1.3'],
    '1.8': ['v50.SQL.CONNECTBY.п.1.8'],
    '1.8. Иерархические запросы': ['v50.SQL.CONNECTBY.п.1.8'],
    '1.10': ['v50.SQL.SYSTABLES.п.1.10'],
    '1.10. Системные таблицы и представления ТЯ': ['v50.SQL.SYSTABLES.п.1.10'],
    '1.17': ['v50.SQL.DML_JOIN.п.1.17'],
    '1.17. DML on join': ['v50.SQL.DML_JOIN.п.1.17'],
    '1.20': ['v50.SQL.PSEUDO.п.1.20'],
    '1.20. Прочие псевдоколонки Oracle': ['v50.SQL.PSEUDO.п.1.20'],
    '2.1': ['v50.STOR.NESTED.п.2.1'],
    '2.1. Nested table': ['v50.STOR.NESTED.п.2.1'],
    '2.7': ['v50.STOR.OLE.п.2.7'],
    '2.7. OLE объекты Oracle': ['v50.STOR.OLE.п.2.7'],
    '3.9': ['v50.PROC.PIPELINED.п.3.9'],
    '3.9. Pipelined functions': ['v50.PROC.PIPELINED.п.3.9'],
    '3.10': ['v50.PROC.REPORTS.п.3.10'],
    '3.10. Оракловые отчеты': ['v50.PROC.REPORTS.п.3.10'],
    '3.11': ['v50.PROC.TYPING.п.3.11'],
    '3.11. Ограничения типизации': ['v50.PROC.TYPING.п.3.11'],
    
    # Приоритет 4
    '1.6.1': ['v50.SQL.DECODE.п.1.6.1'],
    '1.6.1 SQL функции': ['v50.SQL.DECODE.п.1.6.1'],
    '1.6': ['v50.SQL.ANALYTIC.п.1.6'],
    '1.6. Аналитические SQL функции': ['v50.SQL.ANALYTIC.п.1.6'],
    '1.11': ['v50.SQL.ORACLE_PKG.п.1.11'],
    '1.11. Oracle supplied PL/SQL': ['v50.SQL.ORACLE_PKG.п.1.11'],
    '1.14': ['v50.SQL.FUNC_REQ.п.1.14'],
    '1.14. Функциональные реквизиты': ['v50.SQL.FUNC_REQ.п.1.14'],
    '1.19': ['v50.SQL.VW_CRIT_RPT.п.1.19'],
    '1.19. Select from VW_CRIT, VW_RPT, VW_SQL (родительская заявка)': ['v50.SQL.VW_CRIT_RPT.п.1.19'],
    '3.1': ['v50.PROC.EXT_CALL.п.3.1'],
    '3.1. Oracle supplied PL/SQL packages': ['v50.PROC.EXT_CALL.п.3.1'],
    '3.1.1': ['v50.PROC.CRYPTO.п.3.1.2'],
    '3.1.1. Замена использования ::[RUNTIME].[LIB_EXT_CALL] ( Oracle dbms_crypto)': ['v50.PROC.CRYPTO.п.3.1.2'],
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
# (только для правил, которые существуют в рубрикаторе v3.0.0)
PRIORITY_RULES = {
    'Приоритет 1': [
        'v50.SQL.OUTERJOIN.п.1.1',
    ],
    'Приоритет 2': [
        'v50.INT.DBLINK.п.4.2',
        'v50.SQL.OUTERJOIN.п.1.1',
        'v50.SQL.ROWNUM.п.1.2',
    ],
    'Приоритет 3': [
        'v50.PROC.TYPING.п.3.11',
        'v50.SQL.CONNECTBY.п.1.8',
        'v50.SQL.DML_JOIN.п.1.17',
        'v50.SQL.PSEUDO.п.1.20',
        'v50.SQL.ROWNUM.п.1.2',
        'v50.SQL.SYSTABLES.п.1.10',
        'v50.SQL.UDF.п.1.3',
    ],
    'Приоритет 4': [
        'v50.PROC.CRYPTO.п.3.1.2',
        'v50.SQL.DECODE.п.1.6.1',
        'v50.SQL.ORACLE_PKG.п.1.11',
        'v50.SQL.VW_CRIT_RPT.п.1.19',
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
