-- ============================================================================
-- Скрипт поиска проблемных мест в PLPlus коде по правилам рубрикатора v3.0.0
-- Назначение: найти строки кода, требующие исправления для DBI
-- Версия: 1.0
-- Дата: 2026-05-05
-- Совместимость: Oracle (использует REGEXP_LIKE вместо REGEXP)
-- ============================================================================

-- 1. Поиск устаревших OUTER JOIN (v50.SQL.OUTERJOIN.п.1.1)
SELECT 
    'v50.SQL.OUTERJOIN.п.1.1' as rule_code,
    'Замена (+) на LEFT/RIGHT JOIN' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%(+)%'
   OR UPPER(line_text) LIKE '%&COLLECTION(TRUE)%'
   OR UPPER(line_text) LIKE '%(TRUE)%')
  AND UPPER(line_text) NOT LIKE '%LEFT JOIN%'
  AND UPPER(line_text) NOT LIKE '%RIGHT JOIN%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2. Поиск ROWNUM (v50.SQL.ROWNUM.п.1.2)
SELECT 
    'v50.SQL.ROWNUM.п.1.2' as rule_code,
    'Замена rownum на FETCH FIRST' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%ROWNUM%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3. Поиск UDF в WHERE/GROUP BY/ORDER BY (v50.SQL.UDF.п.1.3)
SELECT 
    'v50.SQL.UDF.п.1.3' as rule_code,
    'UDF в WHERE/GROUP BY/ORDER BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'WHERE.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'GROUP BY.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'ORDER BY.*[A-Z_]+\('))
  AND NOT REGEXP_LIKE(UPPER(line_text), '(NVL|DECODE|CASE|COALESCE|TO_CHAR|TO_DATE|TO_NUMBER|SUBSTR|INSTR|LENGTH|TRIM|UPPER|LOWER|COUNT|SUM|AVG|MIN|MAX)\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 4. Поиск неявного приведения типов (v50.SQL.CAST.п.1.5)
SELECT 
    'v50.SQL.CAST.п.1.5' as rule_code,
    'Неявное приведение типов (строка + число)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '[a-zA-Z_][a-zA-Z0-9_]*\s*\+\s*[0-9]+')
   OR REGEXP_LIKE(line_text, '[0-9]+\s*\+\s*[a-zA-Z_][a-zA-Z0-9_]*'))
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%''%''%'
UNION ALL

-- 5. Поиск обращений к системным таблицам ТЯ (v50.SQL.SYSTABLES.п.1.10)
SELECT 
    'v50.SQL.SYSTABLES.п.1.10' as rule_code,
    'SELECT из системных таблиц ТЯ' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(FROM|INTO|JOIN)\s+(CLASSES|CLASS_ATTRIBUTES|METHODS|CRITERIA|RTL_ENTRIES|SOURCES|DEPENDENCIES|ERRORS)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6. Поиск Oracle пакетов (v50.SQL.ORACLE_PKG.п.1.11)
SELECT 
    'v50.SQL.ORACLE_PKG.п.1.11' as rule_code,
    'Использование Oracle пакетов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UTL_FILE|DBMS_OUTPUT|DBMS_ALERT|DBMS_PIPE|DBMS_LOB|DBMS_RANDOM|UTL_RAW|UTL_COMPRESS|DBMS_XMLGEN)\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7. Поиск DECODE (v50.SQL.DECODE.п.1.6.1)
SELECT 
    'v50.SQL.DECODE.п.1.6.1' as rule_code,
    'Использование DECODE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DECODE(%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8. Поиск CONNECT BY (v50.SQL.CONNECTBY.п.1.8)
SELECT 
    'v50.SQL.CONNECTBY.п.1.8' as rule_code,
    'Использование CONNECT BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CONNECT BY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 9. Поиск V$SESSION и системных представлений (v50.SQL.SYSVIEW.п.1.9)
SELECT 
    'v50.SQL.SYSVIEW.п.1.9' as rule_code,
    'Обращение к системным представлениям Oracle' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(V\$|GV\$|USER_|ALL_|DBA_)[A-Z0-9_]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 10. Поиск SYS_CONTEXT с USERENV (v50.SQL.CONTEXT.п.1.23)
SELECT 
    'v50.SQL.CONTEXT.п.1.23' as rule_code,
    'Использование SYS_CONTEXT(USERENV)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%SYS_CONTEXT(%USERENV%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 11. Поиск DML с JOIN (v50.SQL.DML_JOIN.п.1.17)
SELECT 
    'v50.SQL.DML_JOIN.п.1.17' as rule_code,
    'UPDATE/DELETE с JOIN' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UPDATE|DELETE)\s+.*FROM.*JOIN')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 12. Поиск SELECT из VW_CRIT/VW_RPT/VW_SQL (v50.SQL.VW_CRIT_RPT.п.1.19)
SELECT 
    'v50.SQL.VW_CRIT_RPT.п.1.19' as rule_code,
    'SELECT из VW_CRIT/VW_RPT/VW_SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(VW_CRIT|VW_RPT|VW_SQL)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 13. Поиск bind переменных в GROUP BY/ORDER BY (v50.SQL.BIND_GROUP.п.1.26)
SELECT 
    'v50.SQL.BIND_GROUP.п.1.26' as rule_code,
    'Bind переменная в GROUP BY/ORDER BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(GROUP BY|ORDER BY).*:[a-z_]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 14. Поиск SELECT из REF переменной (v50.SQL.REF_SELECT.п.1.27)
SELECT 
    'v50.SQL.REF_SELECT.п.1.27' as rule_code,
    'SELECT из REF переменной' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%SELECT%REF%'
   OR UPPER(line_text) LIKE '%IN%REF%')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 15. Поиск типа DATE (v50.STOR.DATE.п.2.2)
SELECT 
    'v50.STOR.DATE.п.2.2' as rule_code,
    'Использование типа DATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '[^_`]date\>')
  AND line_text NOT LIKE '--%'
  AND UPPER(line_text) NOT LIKE '%TO_DATE%'
UNION ALL

-- 16. Поиск GLOBAL TEMPORARY TABLE (v50.STOR.TEMP.п.2.8)
SELECT 
    'v50.STOR.TEMP.п.2.8' as rule_code,
    'Использование временных таблиц' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%GLOBAL TEMPORARY TABLE%'
   OR UPPER(line_text) LIKE '%TEMP TABLE%')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 17. Поиск DBMS_CRYPTO (v50.PROC.CRYPTO.п.3.1.2)
SELECT 
    'v50.PROC.CRYPTO.п.3.1.2' as rule_code,
    'Использование DBMS_CRYPTO' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_CRYPTO%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 18. Поиск UTL_SMTP (v50.PROC.SMTP.п.3.1.3)
SELECT 
    'v50.PROC.SMTP.п.3.1.3' as rule_code,
    'Использование UTL_SMTP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%UTL_SMTP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 19. Поиск UTL_HTTP/UTL_URL (v50.PROC.HTTP.п.3.1.6)
SELECT 
    'v50.PROC.HTTP.п.3.1.6' as rule_code,
    'Использование UTL_HTTP/UTL_URL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UTL_HTTP|UTL_URL)\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 20. Поиск utils.session_id и др. (v50.PROC.UTILS.п.3.1.1)
SELECT 
    'v50.PROC.UTILS.п.3.1.1' as rule_code,
    'Использование утилитных функций' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UTILS\.SESSION_ID|METHOD_MGR\.CLEAR_OBJECT_REFCING|STDIO\.ZIP)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 21. Поиск пустой строки (v50.PROC.EMPTY_STRING.п.3.2)
SELECT 
    'v50.PROC.EMPTY_STRING.п.3.2' as rule_code,
    'Сравнение/присваивание пустой строки' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '=\s*''''|\s*:=\s*''')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 22. Поиск EXCEPTIONLOOP (v50.PROC.EXCEPTIONLOOP.п.1.25)
SELECT 
    'v50.PROC.EXCEPTIONLOOP.п.1.25' as rule_code,
    'Использование EXCEPTIONLOOP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXCEPTIONLOOP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 23. Поиск WHEN OTHERS без ROLLBACK/RAISE (v50.PROC.WHENOTHERS.п.3.5)
SELECT 
    'v50.PROC.WHENOTHERS.п.3.5' as rule_code,
    'WHEN OTHERS без ROLLBACK/RAISE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%WHEN OTHERS%'
  AND UPPER(line_text) NOT LIKE '%ROLLBACK%'
  AND UPPER(line_text) NOT LIKE '%RAISE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 24. Поиск условной компиляции (v50.PROC.COND_COMPILE.п.3.21)
SELECT 
    'v50.PROC.COND_COMPILE.п.3.21' as rule_code,
    'Условная компиляция (#IF, IF_DEF)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '--#IF|--#ELSE|--#ENDIF')
   OR REGEXP_LIKE(UPPER(line_text), 'IF_DEF\s*\(|PRAGMA\s+DEFINE'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 25. Поиск NLS_* функций (v50.PROC.CHARSET.п.3.16)
SELECT 
    'v50.PROC.CHARSET.п.3.16' as rule_code,
    'Использование NLS_* функций' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(NLS_INITCAP|NLS_LOWER|NLS_UPPER|NCHR|ASCIISTR|COMPOSE|DECOMPOSE|DUMP|UNISTR|LENGTHC|LENGTH2|LENGTH4|SUBSTRC|SUBSTR2|SUBSTR4)\(')
  AND line_text NOT LIKE '--%'

ORDER BY rule_code, file_name, line_number;