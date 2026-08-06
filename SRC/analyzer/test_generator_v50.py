#!/usr/bin/env python3
"""
Генератор тестового файла для всех правил v50
Источник: 3.RUBRICATOR_FIXES.md, документация v50.docx
Генерирует один файл с процедурами для каждого правила
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ========== КОНФИГУРАЦИЯ ==========
RUBRICATOR_DIR = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор'
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'DATA' / 'Тестовые файлы'
OUTPUT_FILENAME = "test_all_v50_rules.plp"
# =================================


class V50TestGenerator:
    """Генератор тестового файла для всех правил v50"""

    # Правила и их описания
    RULES = {
        'v50.SQL.OUTERJOIN.п.1.1': {
            'name': 'v50_SQL_OUTERJOIN_п_1_1',
            'description': 'Замена (+) на LEFT/RIGHT JOIN',
            'category': 'SQL',
            'bad': """
    FOR rec IN (SELECT x.*
                FROM folder.[DOCS_IN_FOLD] x, (::[MAIN_DOCUM]) md
                WHERE x%id = md%id(+)
                AND x.[DOCUMENT]%class = ::[MAIN_DOCUM]%class
                ORDER BY 2 DESC)
    LOOP
        NULL;
    END LOOP;""",
            'good': """
    FOR rec IN (SELECT x.*
                FROM folder.[DOCS_IN_FOLD] x
                LEFT JOIN (::[MAIN_DOCUM]) md ON x%id = md%id
                AND x.[DOCUMENT]%class = ::[MAIN_DOCUM]%class
                ORDER BY 2 DESC)
    LOOP
        NULL;
    END LOOP;"""
        },
        'v50.SQL.ROWNUM.п.1.2': {
            'name': 'v50_SQL_ROWNUM_п_1_2',
            'description': 'Замена rownum на FETCH FIRST',
            'category': 'SQL',
            'bad': """
    SELECT p(p) INTO v_ref
    FROM ::[PRICE_LIST] p
    WHERE p.[CODE] = UPPER('CODE')
    AND ROWNUM = 1;""",
            'good': """
    SELECT p(p) INTO v_ref
    FROM ::[PRICE_LIST] p
    WHERE p.[CODE] = UPPER('CODE')
    FETCH FIRST 1 ROWS ONLY;""",
            'declare': 'v_ref REF [PRICE_LIST];'
        },
        'v50.SQL.UDF.п.1.3': {
            'name': 'v50_SQL_UDF_п_1_3',
            'description': 'Запрет UDF в WHERE/GROUP BY/ORDER BY',
            'category': 'SQL',
            'functions': """FUNCTION my_func(p_id NUMBER) RETURN NUMBER IS
    BEGIN
        RETURN p_id * 2;
    END my_func;""",
            'bad': """
    FOR rec IN (SELECT id FROM ::[CLIENT] WHERE my_func(id) > 100)
    LOOP
        NULL;
    END LOOP;""",
            'good': """
    FOR rec IN (SELECT id, my_func(id) AS calc_val FROM ::[CLIENT] WHERE calc_val > 100)
    LOOP
        NULL;
    END LOOP;"""
        },
        'v50.SQL.DECODE.п.1.6.1': {
            'name': 'v50_SQL_DECODE_п_1_6_1',
            'description': 'Замена DECODE на CASE',
            'category': 'SQL',
            'declare': 'v_status NUMBER := 1;\n    v_result VARCHAR2(100);',
            'bad': """
    SELECT DECODE(v_status, 1, 'Активен', 2, 'Закрыт', 'Неизвестно') INTO v_result FROM DUAL;""",
            'good': """
    SELECT CASE v_status
        WHEN 1 THEN 'Активен'
        WHEN 2 THEN 'Закрыт'
        ELSE 'Неизвестно'
    END INTO v_result FROM DUAL;"""
        },
        'v50.SQL.CONNECTBY.п.1.8': {
            'name': 'v50_SQL_CONNECTBY_п_1_8',
            'description': 'Замена CONNECT BY на WITH RECURSIVE',
            'category': 'SQL',
            'declare': 'v_dep_id NUMBER := 100;\n    v_high_dep REF [DEPART];',
            'bad': """
    SELECT d(d%id) INTO v_high_dep
    FROM (SELECT d(d%id, d.[HIGH]) FROM ::[DEPART] d
          CONNECT BY d%id = PRIOR d.[HIGH]
          START WITH d%id = v_dep_id)
    WHERE d.[HIGH] IS NULL AND ROWNUM = 1;""",
            'good': """
    WITH RECURSIVE t(id, high) AS (
        SELECT d%id, d.[HIGH] FROM ::[DEPART] WHERE d%id = v_dep_id
        UNION ALL
        SELECT d.d%id, d.[HIGH]
        FROM ::[DEPART] d
        JOIN t ON t.high = d.d%id
    )
    SELECT t.id INTO v_high_dep FROM t WHERE t.high IS NULL FETCH FIRST 1 ROWS ONLY;"""
        },
        'v50.SQL.SYSVIEW.п.1.9': {
            'name': 'v50_SQL_SYSVIEW_п_1_9',
            'description': 'Замена v$session на VW_DB_SESSION',
            'category': 'SQL',
            'declare': 'v_session_info VW_DB_SESSION%ROWTYPE;',
            'bad': """
    SELECT * INTO v_session_info FROM v$session WHERE ROWNUM = 1;""",
            'good': """
    SELECT SESSION_SID, STATUS, MODULE, ACTION INTO v_session_info
    FROM VW_DB_SESSION
    FETCH FIRST 1 ROWS ONLY;"""
        },
        'v50.SQL.CONTEXT.п.1.23': {
            'name': 'v50_SQL_CONTEXT_п_1_23',
            'description': 'Замена sys_context',
            'category': 'SQL',
            'declare': 'v_dbname VARCHAR2(100);\n    v_sessionid VARCHAR2(100);\n    v_user VARCHAR2(100);',
            'bad': """
    v_dbname := SYS_CONTEXT('USERENV', 'DB_NAME');
    v_sessionid := SYS_CONTEXT('USERENV', 'SESSIONID');
    v_user := SYS_CONTEXT('USERENV', 'CURRENT_USER');""",
            'good': """
    v_dbname := ::[RUNTIME].[ENVIRONMENT].ClassStorage('ТБП').dbName;
    v_sessionid := rtl.session_id;
    v_user := rtl.usr$;"""
        },
        'v50.STOR.DATE.п.2.2': {
            'name': 'v50_STOR_DATE_п_2_2',
            'description': 'Замена DATE на DATE_TIME',
            'category': 'STOR',
            'bad': '    -- DateTimeEnd DATE;',
            'good': '    DateTimeEnd DATE_TIME;\nBEGIN\n    DateTimeEnd := SYSDATE;',
            'has_begin': True
        },
        'v50.PROC.WHENOTHERS.п.3.5': {
            'name': 'v50_PROC_WHENOTHERS_п_3_5',
            'description': 'Добавление ROLLBACK или RAISE в WHEN OTHERS',
            'category': 'PROC',
            'bad': """
    BEGIN
        SELECT 1/0 INTO v_val FROM DUAL;
    EXCEPTION
        WHEN OTHERS THEN
            NULL;
    END;""",
            'good': """
    BEGIN
        SELECT 1/0 INTO v_val FROM DUAL;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END;""",
            'declare': 'v_val NUMBER;'
        },
        'v50.PROC.EXECUTE.п.3.3': {
            'name': 'v50_PROC_EXECUTE_п_3_3',
            'description': 'Экранирование имён таблиц в execute immediate',
            'category': 'PROC',
            'bad': """
    EXECUTE IMMEDIATE 'truncate table Z#TEMP';""",
            'good': """
    EXECUTE IMMEDIATE 'truncate table "Z#TEMP"';"""
        },
        'v50.PROC.CRYPTO.п.3.1.2': {
            'name': 'v50_PROC_CRYPTO_п_3_1_2',
            'description': 'Замена dbms_crypto на INT_EXT_CALL_001',
            'category': 'PROC',
            'declare': 'v_hash VARCHAR2(100);\n    v_blob BLOB;',
            'bad': '    -- v_hash := dbms_crypto.hash(v_blob, dbms_crypto.hash_md5);',
            'good': '    v_hash := ::[PCORE_INTERFACE].[INT_EXT_CALL_001].HSH_B(v_blob, ::[PCORE_INTERFACE].[INT_EXT_CALL_001].H_2);'
        },
        'v50.PROC.BULK.п.1.28': {
            'name': 'v50_PROC_BULK_п_1_28',
            'description': 'Включение batch для bulk операций',
            'category': 'PROC',
            'declare': 'TYPE t_num_array IS TABLE OF NUMBER INDEX BY PLS_INTEGER;\n    v_arr t_num_array;',
            'bad': '    -- без batch',
            'good': """
    PRAGMA HINT('jdbc_batch(true)');

    FOR i IN 1..1000 LOOP
        v_arr(i) := i;
    END LOOP;

    FORALL i IN 1..v_arr.COUNT
        INSERT INTO Z#TEMP VALUES (v_arr(i));"""
        },
        'v50.CACHE.REF.п.6.10': {
            'name': 'v50_CACHE_REF_п_6_10',
            'description': 'Получение полей сразу в курсоре',
            'category': 'CACHE',
            'declare': 'v_value VARCHAR2(100);',
            'bad': """
    -- FOR rec IN (SELECT ref_col FROM ::[CLIENT]) LOOP
    --     v_value := rec.ref_col.[FIELD];
    -- END LOOP;""",
            'good': """
    FOR rec IN (SELECT ref_col.[FIELD] FROM ::[CLIENT]) LOOP
        v_value := rec.[FIELD];
    END LOOP;"""
        },
    }

    def __init__(self, rubricator_dir: Path = None):
        self.rubricator_dir = rubricator_dir or RUBRICATOR_DIR

    def _generate_procedure(self, rule_code: str, rule: Dict) -> str:
        """Генерирует одну процедуру для правила"""
        lines = []
        lines.append("")
        lines.append("-- ============================================================================")
        lines.append(f"-- {rule_code}")
        lines.append(f"-- Описание: {rule['description']}")
        lines.append("-- ============================================================================")
        lines.append(f"PROCEDURE {rule['name']} IS")

        # DECLARE секция
        declare_lines = []
        if 'declare' in rule:
            # Разбиваем на строки и добавляем отступы
            for decl_line in rule['declare'].split('\n'):
                if decl_line.strip():
                    declare_lines.append(f"    {decl_line.strip()}")
        
        if 'functions' in rule:
            # Функции внутри IS...BEGIN - полные функции с IS/BEGIN/END
            for func_line in rule['functions'].split('\n'):
                if func_line.strip():
                    declare_lines.append(f"    {func_line.strip()}")

        # Добавляем DECLARE секцию если есть
        if declare_lines:
            lines.extend(declare_lines)

        # Добавляем BEGIN только один раз для основной части процедуры
        lines.append("BEGIN")

        # НЕПРАВИЛЬНЫЙ код
        lines.append("    -- [-] НЕПРАВИЛЬНО")
        for bad_line in rule['bad'].split('\n'):
            if bad_line.strip():
                lines.append(f"    {bad_line.strip()}")

        # ПРАВИЛЬНЫЙ код
        lines.append("")
        lines.append("    -- [+] ПРАВИЛЬНО")
        for good_line in rule['good'].split('\n'):
            if good_line.strip():
                lines.append(f"    {good_line.strip()}")

        lines.append("END;")
        lines.append("")

        return '\n'.join(lines)

    def generate_all_tests_file(self, output_dir: Path) -> Path:
        """Генерирует один файл со всеми процедурами"""
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / OUTPUT_FILENAME

        lines = []
        lines.append("-- ============================================================================")
        lines.append("-- ТЕСТОВЫЙ ФАЙЛ: Все правила v50")
        lines.append(f"-- Источник: 3.RUBRICATOR_FIXES.md, документация v50.docx")
        lines.append(f"-- Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("-- ============================================================================")

        for rule_code, rule in self.RULES.items():
            proc = self._generate_procedure(rule_code, rule)
            lines.append(proc)

        lines.append("")
        lines.append("-- ============================================================================")
        lines.append("-- КОНЕЦ ФАЙЛА")
        lines.append("-- ============================================================================")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return file_path


# ========== ЗАПУСК ==========

def main():
    """Запуск генерации тестового файла"""
    print(f"\n[INFO] Генерация тестового файла для всех правил v50")
    print(f"[INFO] Каталог вывода: {OUTPUT_DIR}")
    print(f"[INFO] Имя файла: {OUTPUT_FILENAME}\n")

    generator = V50TestGenerator()
    file_path = generator.generate_all_tests_file(OUTPUT_DIR)

    print(f"[OK] Файл создан: {file_path}")
    print(f"[OK] Всего правил: {len(generator.RULES)}")


if __name__ == '__main__':
    main()
