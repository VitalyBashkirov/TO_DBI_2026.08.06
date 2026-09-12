-- ============================================================================
-- Скрипт поиска проблемных мест в PLPlus коде по правилам рубрикатора v5.0.0
-- Назначение: найти строки кода, требующие исправления для DBI
-- Версия: 2.1
-- Дата: 2026-08-18
-- Совместимость: Oracle (использует REGEXP_LIKE вместо REGEXP)
-- ============================================================================

-- ============================================================================
-- 1. SQL/DML правила (v50.SQL.*)
-- ============================================================================

-- 1.1 Поиск устаревших OUTER JOIN (v50.SQL.OUTERJOIN.п.1.1)
SELECT 
    'v50.SQL.OUTERJOIN.п.1.1' as rule_code,
    'Замена (+) на LEFT/RIGHT JOIN' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%(+)%'
   OR UPPER(line_text) LIKE '%&COLLECTION(TRUE)%'
   OR UPPER(line_text) LIKE '%(TRUE)%'
   OR REGEXP_LIKE(UPPER(line_text), '\]\(TRUE\)|\(TRUE\)'))
  AND UPPER(line_text) NOT LIKE '%LEFT JOIN%'
  AND UPPER(line_text) NOT LIKE '%RIGHT JOIN%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.2 Поиск ROWNUM (v50.SQL.ROWNUM.п.1.2)
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

-- 1.3 Поиск UDF в WHERE/GROUP BY/ORDER BY (v50.SQL.UDF.п.1.3)
SELECT 
    'v50.SQL.UDF.п.1.3' as rule_code,
    'UDF в WHERE/GROUP BY/ORDER BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'WHERE.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'GROUP BY.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'ORDER BY.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'HAVING.*[A-Z_]+\('))
  AND NOT REGEXP_LIKE(UPPER(line_text), '(NVL|DECODE|CASE|COALESCE|TO_CHAR|TO_DATE|TO_NUMBER|SUBSTR|INSTR|LENGTH|TRIM|UPPER|LOWER|COUNT|SUM|AVG|MIN|MAX|SYSDATE)\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.4 Поиск неявного приведения типов (v50.SQL.CAST.п.1.5)
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

-- 1.5 Поиск DECODE (v50.SQL.DECODE.п.1.6.1)
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

-- 1.6 Поиск CONNECT BY (v50.SQL.CONNECTBY.п.1.8)
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

-- 1.7 Поиск V$SESSION и системных представлений (v50.SQL.SYSVIEW.п.1.9)
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

-- 1.8 Поиск обращений к системным таблицам ТЯ (v50.SQL.SYSTABLES.п.1.10)
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

-- 1.9 Поиск Oracle пакетов (v50.SQL.ORACLE_PKG.п.1.11)
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

-- 1.10 Поиск SELECT FROM TABLE() (v50.SQL.TABLE_SELECT.п.1.13)
SELECT 
    'v50.SQL.TABLE_SELECT.п.1.13' as rule_code,
    'SELECT FROM TABLE()' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'SELECT.*FROM\s+TABLE\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.11 Поиск DML с JOIN (v50.SQL.DML_JOIN.п.1.17)
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

-- 1.12 Поиск подсказок оптимизатора (v50.SQL.HINTS.п.1.18)
SELECT 
    'v50.SQL.HINTS.п.1.18' as rule_code,
    'Подсказки оптимизатора /*+ ... */' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '/\*\+.*?\*/')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.13 Поиск SELECT из VW_CRIT/VW_RPT/VW_SQL (v50.SQL.VW_CRIT_RPT.п.1.19)
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

-- 1.14 Поиск псевдоколонок Oracle (v50.SQL.PSEUDO.п.1.20)
SELECT 
    'v50.SQL.PSEUDO.п.1.20' as rule_code,
    'Псевдоколонки Oracle (ROWID, ORA_ROWSCN и др.)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(ROWID|ORA_ROWSCN|OBJECT_ID|OBJECT_VALUE|XMLDATA)\b')
  AND UPPER(line_text) NOT LIKE '%ROWNUM%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.15 Поиск SYS_CONTEXT с USERENV (v50.SQL.CONTEXT.п.1.23)
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

-- 1.16 Поиск DDL без схемы (v50.SQL.DDL.п.1.24)
SELECT 
    'v50.SQL.DDL.п.1.24' as rule_code,
    'DDL команды без указания схемы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(CREATE|ALTER|DROP|TRUNCATE)\s+(TABLE|INDEX|VIEW|SEQUENCE)\s+[A-Z#]+\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.17 Поиск EXCEPTIONLOOP (v50.SQL.EXCEPTIONLOOP.п.1.25)
SELECT 
    'v50.SQL.EXCEPTIONLOOP.п.1.25' as rule_code,
    'Использование EXCEPTIONLOOP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXCEPTIONLOOP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.18 Поиск bind переменных в GROUP BY/ORDER BY (v50.SQL.BIND_GROUP.п.1.26)
SELECT 
    'v50.SQL.BIND_GROUP.п.1.26' as rule_code,
    'Bind переменная в GROUP BY/ORDER BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(GROUP BY|ORDER BY|DISTINCT).*:[a-z_]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.19 Поиск SELECT из REF переменной (v50.SQL.REF_SELECT.п.1.27)
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

-- 1.20 Поиск BULK операций без batch (v50.SQL.BULK.п.1.28)
SELECT 
    'v50.SQL.BULK.п.1.28' as rule_code,
    'BULK операции без batch' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%FORALL%'
   OR UPPER(line_text) LIKE '%BULK COLLECT%')
  AND UPPER(line_text) NOT LIKE '%JDBC_BATCH%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.21 Поиск FETCH в EXISTS (v50.SQL.FETCH_EXISTS.тдс20240828.стр.5)
SELECT 
    'v50.SQL.FETCH_EXISTS.тдс20240828.стр.5' as rule_code,
    'FETCH в подзапросе EXISTS' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'EXISTS\s*\(.*FETCH\s+FIRST')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 2. Хранение (STOR) правила (v50.STOR.*)
-- ============================================================================

-- 2.1 Поиск типа DATE (v50.STOR.DATE.п.2.2)
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

-- 2.2 Поиск GLOBAL TEMPORARY TABLE (v50.STOR.TEMP.п.2.8)
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

-- 2.3 Поиск уникальных индексов с NULL (v50.STOR.UNIQUE_IDX.п.2.6.2)
SELECT 
    'v50.STOR.UNIQUE_IDX.п.2.6.2' as rule_code,
    'Уникальный индекс с NULL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'CREATE\s+UNIQUE\s+INDEX.*ON.*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.4 Поиск индексов на текстовых полях (v50.STOR.INDEX.п.2.6.3)
SELECT 
    'v50.STOR.INDEX.п.2.6.3' as rule_code,
    'Индекс на текстовом поле (возможно > 2704 байт)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'CREATE\s+INDEX.*ON.*\(.*VARCHAR2.*\)')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 3. Процедурный код (PROC) правила (v50.PROC.*)
-- ============================================================================

-- 3.1 Поиск DBMS_CRYPTO (v50.PROC.CRYPTO.п.3.1.2)
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

-- 3.2 Поиск UTL_SMTP (v50.PROC.SMTP.п.3.1.3)
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

-- 3.3 Поиск JSON_Object_T и др. (v50.PROC.JSON.п.3.1.4)
SELECT 
    'v50.PROC.JSON.п.3.1.4' as rule_code,
    'Использование Oracle JSON типов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'JSON_(OBJECT|ARRAY|ELEMENT|SCALAR)_T')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.4 Поиск UTL_HTTP/UTL_URL (v50.PROC.HTTP.п.3.1.6)
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

-- 3.5 Поиск utils.session_id и др. (v50.PROC.UTILS.п.3.1.1)
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

-- 3.6 Поиск пустой строки (v50.PROC.EMPTY_STRING.п.3.2)
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

-- 3.7 Поиск EXECUTE IMMEDIATE без кавычек (v50.PROC.EXECUTE.п.3.3)
SELECT 
    'v50.PROC.EXECUTE.п.3.3' as rule_code,
    'EXECUTE IMMEDIATE без кавычек у таблиц' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXECUTE IMMEDIATE%'
  AND REGEXP_LIKE(line_text, 'Z#[A-Z_]+')
  AND line_text NOT LIKE '%"%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.8 Поиск DBMS_SQL (v50.PROC.DYNAMIC_SQL.п.3.3)
SELECT 
    'v50.PROC.DYNAMIC_SQL.п.3.3' as rule_code,
    'Использование DBMS_SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_SQL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.9 Поиск макросов execute/process (v50.PROC.MACROS.п.3.4)
SELECT 
    'v50.PROC.MACROS.п.3.4' as rule_code,
    'Макросы execute/process' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'PRAGMA\s+MACRO\([^,]+,[^,]+,(EXECUTE|PROCESS)\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.10 Поиск WHEN OTHERS без ROLLBACK/RAISE (v50.PROC.WHENOTHERS.п.3.5)
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

-- 3.11 Поиск XMLType и DBMS_XMLDOM (v50.PROC.XML.п.3.6)
SELECT 
    'v50.PROC.XML.п.3.6' as rule_code,
    'Использование XMLType/DBMS_XMLDOM' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(XMLTYPE|DBMS_XMLDOM|DBMS_XMLPARSER)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.12 Поиск триггеров БД (v50.PROC.TRIGGER.п.3.8)
SELECT 
    'v50.PROC.TRIGGER.п.3.8' as rule_code,
    'CREATE TRIGGER в БД' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CREATE TRIGGER%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.13 Поиск проблем типизации (v50.PROC.TYPING.п.3.11)
SELECT 
    'v50.PROC.TYPING.п.3.11' as rule_code,
    'Проблемы типизации (%rowtype, ref)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '\w+%rowtype')
   OR REGEXP_LIKE(line_text, 'ref\s+\[[A-Z]+\]'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.14 Поиск кодогенерации (v50.PROC.CODEGEN.п.3.15)
SELECT 
    'v50.PROC.CODEGEN.п.3.15' as rule_code,
    'Кодогенерация операций/представлений' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(CREATE|ALTER|DROP)\s+(OPERATION|VIEW)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.15 Поиск NLS_* функций (v50.PROC.CHARSET.п.3.16)
SELECT 
    'v50.PROC.CHARSET.п.3.16' as rule_code,
    'Использование NLS_* функций' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(NLS_INITCAP|NLS_LOWER|NLS_UPPER|NCHR|ASCIISTR|COMPOSE|DECOMPOSE|DUMP|UNISTR|LENGTHC|LENGTH2|LENGTH4|SUBSTRC|SUBSTR2|SUBSTR4)\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.16 Поиск условной компиляции (v50.PROC.COND_COMPILE.п.3.21)
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

-- 3.17 Поиск NativeID в NUMBER (v50.PROC.NATIVEID.п.3.26)
SELECT 
    'v50.PROC.NATIVEID.п.3.26' as rule_code,
    'NativeID в NUMBER переменной' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(\w+)\s+NUMBER\s*;.*\1\s*:=\s*\w+%id')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.18 Поиск ID с малым размером (v50.PROC.ID_SIZE.п.3.27)
SELECT 
    'v50.PROC.ID_SIZE.п.3.27' as rule_code,
    'ID в VARCHAR2(10) или меньше' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(\w+)\s+(VARCHAR2|STRING)\s*\(([0-9]|1[0-9])\)\s*;')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 4. Интеграции (INT) правила (v50.INT.*)
-- ============================================================================

-- 4.1 Поиск Database Link (v50.INT.DBLINK.п.4.2)
SELECT 
    'v50.INT.DBLINK.п.4.2' as rule_code,
    'Database Link (@dblink)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+@\w+')
  AND line_text NOT LIKE '@import_plsql%'
  AND line_text NOT LIKE '@this%'
  AND line_text NOT LIKE '@name%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 4.2 Поиск DBMS_AQ (v50.INT.QUEUE.п.4.4)
SELECT 
    'v50.INT.QUEUE.п.4.4' as rule_code,
    'Использование DBMS_AQ' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_AQ%'
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 5. Кэширование (CACHE) правила (v50.CACHE.*)
-- ============================================================================

-- 5.1 Поиск разыменования ссылок в цикле (v50.CACHE.REF.п.6.10)
SELECT 
    'v50.CACHE.REF.п.6.10' as rule_code,
    'Разыменование ссылок в цикле' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\w+\s+IN\s+.*?\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 6. PlpCheck правила (PlpCheck.STYLE.*)
-- ============================================================================

-- 6.1 Поиск обращения к классу без ::[] (PlpCheck.STYLE.WRONG_CLASS.п.4.12)
SELECT 
    'PlpCheck.STYLE.WRONG_CLASS.п.4.12' as rule_code,
    'Обращение к классу без ::[CLASS]' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(FROM|INTO|JOIN)\s+[A-Z][A-Z0-9_#]+\b')
  AND UPPER(line_text) NOT LIKE '%::%'
  AND UPPER(line_text) NOT LIKE '%FROM DUAL%'
  AND UPPER(line_text) NOT LIKE '%VW_%'
  AND UPPER(line_text) NOT LIKE '%V$%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.2 Поиск обращения к реквизиту без скобок (PlpCheck.STYLE.WRONG_ATTR.п.4.13)
SELECT 
    'PlpCheck.STYLE.WRONG_ATTR.п.4.13' as rule_code,
    'Обращение к реквизиту без [ATTR]' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.([A-Z][A-Z0-9_#]+)')
  AND line_text NOT LIKE '%.[%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.3 Поиск обращения к методу через точку (PlpCheck.STYLE.WRONG_METHOD.п.4.14)
SELECT 
    'PlpCheck.STYLE.WRONG_METHOD.п.4.14' as rule_code,
    'Обращение к методу без ::[CLASS].[METHOD]' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '[A-Z][A-Z0-9_#]+\.([a-z][a-zA-Z0-9_#]+)\s*\(')
  AND line_text NOT LIKE '%::%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.4 Поиск строки вместо ::[CLASS]%class (PlpCheck.STYLE.STRING_AS_CLASS.п.4.15)
SELECT 
    'PlpCheck.STYLE.STRING_AS_CLASS.п.4.15' as rule_code,
    'Строка вместо ::[CLASS]%class' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '''[A-Z][A-Z0-9_#]+''\s*(%class|%id|%statename)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.5 Поиск VARCHAR2 без размера (PlpCheck.STYLE.SIZELESS.п.4.17)
SELECT 
    'PlpCheck.STYLE.SIZELESS.п.4.17' as rule_code,
    'VARCHAR2/STRING без размера' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+(VARCHAR2|STRING)\s*;')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.6 Поиск обращения к ТБП без all/collection (PlpCheck.STYLE.EXIST_ALL.п.4.7)
SELECT 
    'PlpCheck.STYLE.EXIST_ALL.п.4.7' as rule_code,
    'ТБП без all/collection' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'FROM\s+\[[A-Z][A-Z0-9_#]+\](?!\s+ALL\s*:)')
   OR REGEXP_LIKE(UPPER(line_text), 'FROM\s+\[[A-Z][A-Z0-9_#]+\]\s+\w+(?!\s+COLLECTION)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.7 Поиск прямых SAVEPOINT/ROLLBACK (PlpCheck.STYLE.SAVEPOINT_ROLLBACK.п.4.11)
SELECT 
    'PlpCheck.STYLE.SAVEPOINT_ROLLBACK.п.4.11' as rule_code,
    'Прямой SAVEPOINT/ROLLBACK (нужны &sp/&rb)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), '\bSAVEPOINT\s+\w+\b')
   OR REGEXP_LIKE(UPPER(line_text), '\bROLLBACK\s+TO\s+SAVEPOINT\s+\w+\b'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.8 Поиск переменных без префикса типа (PlpCheck.STYLE.PREFIX_TYPE.п.4.4)
SELECT 
    'PlpCheck.STYLE.PREFIX_TYPE.п.4.4' as rule_code,
    'Переменная без префикса типа (v_, n_, d_)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(?!v_|n_|d_|b_|lr_|lrec_|tb_)(\w+)\s+(NUMBER|VARCHAR2|STRING|DATE|DATE_TIME)\s*[;(]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 6.9 Поиск некорректных префиксов (PlpCheck.STYLE.BAD_PREFIX.п.4.3)
SELECT 
    'PlpCheck.STYLE.BAD_PREFIX.п.4.3' as rule_code,
    'Некорректный префикс переменной' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(BAD|BADPREFIX|TMP|TEMP|VAR|DATA|INFO|Z_|X_)\w+\s+(NUMBER|VARCHAR2|STRING|DATE)\s*[;(]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.10 Поиск зарезервированных префиксов (PlpCheck.STYLE.RESERVED_PREFIX.п.4.5)
SELECT 
    'PlpCheck.STYLE.RESERVED_PREFIX.п.4.5' as rule_code,
    'Зарезервированный префикс (sys_, dba_, pg_)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(SYS_|DBA_|PG_)\w+\s+(NUMBER|VARCHAR2|STRING|DATE)\s*[;(]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.11 Поиск закомментированного кода (PlpCheck.STYLE.CODE_IN_COMMENT.п.4.6)
SELECT 
    'PlpCheck.STYLE.CODE_IN_COMMENT.п.4.6' as rule_code,
    'Закомментированный код (более 3 строк)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '/\*.*(BEGIN|IF|LOOP|CASE|SELECT|UPDATE|DELETE).*\*/')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.12 Поиск функций в EXECUTE/VALIDATE (PlpCheck.STYLE.FUNCTIONS_IN_BODY.п.4.18)
SELECT 
    'PlpCheck.STYLE.FUNCTIONS_IN_BODY.п.4.18' as rule_code,
    'Функция/процедура в EXECUTE/VALIDATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'EXECUTE\s*' || CHR(10) || '\s*(FUNCTION|PROCEDURE)')
   OR REGEXP_LIKE(UPPER(line_text), 'VALIDATE\s*' || CHR(10) || '\s*(FUNCTION|PROCEDURE)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.13 Поиск глобальных переменных (PlpCheck.STYLE.GLOBAL_VAR.п.4.10)
SELECT 
    'PlpCheck.STYLE.GLOBAL_VAR.п.4.10' as rule_code,
    'Глобальная переменная вне метода' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '^\s*\w+\s+(NUMBER|VARCHAR2|STRING|DATE)\s*;')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
  AND (SELECT COUNT(*) FROM plplus_code_source t2 
       WHERE t2.file_name = t.file_name 
         AND t2.line_number > t.line_number 
         AND t2.line_text NOT LIKE '--%'
         AND REGEXP_LIKE(UPPER(t2.line_text), UPPER(REGEXP_SUBSTR(t.line_text, '\w+'))) > 0) > 0
UNION ALL

-- 6.14 Поиск разыменованного поля в out параметре (PlpCheck.STYLE.DEREFERENCE_OUT.п.4.16)
SELECT 
    'PlpCheck.STYLE.DEREFERENCE_OUT.п.4.16' as rule_code,
    'Разыменованное поле в out параметре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.\[\w+\]\s*,\s*\w+\s+OUT')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.15 Поиск повторяющихся DEFAULT валидаций (PlpCheck.STYLE.VALIDATE_DEFAULT.п.4.9)
SELECT 
    'PlpCheck.STYLE.VALIDATE_DEFAULT.п.4.9' as rule_code,
    'Повторяющийся DEFAULT валидация' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'IF\s+\w+\s+IS\s+NULL\s+THEN\s+\w+\s*:=\s*DEFAULT\w+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.16 Поиск неиспользуемых переменных (PlpCheck.STYLE.NOT_MENTIONED.п.4.8)
SELECT 
    'PlpCheck.STYLE.NOT_MENTIONED.п.4.8' as rule_code,
    'Переменная/параметр/алиас не используется' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+(NUMBER|VARCHAR2|STRING|DATE)\s*[;(]')
  AND line_text NOT LIKE '--%'
  AND NOT EXISTS (
      SELECT 1 FROM plplus_code_source t2
      WHERE t2.file_name = t.file_name
        AND t2.line_number != t.line_number
        AND t2.line_text NOT LIKE '--%'
        AND REGEXP_LIKE(UPPER(t2.line_text), UPPER(REGEXP_SUBSTR(t.line_text, '\b\w+\b')))
  )
UNION ALL


-- ============================================================================
-- 7. PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19 - Комбинированные префиксы
-- ============================================================================

-- 7.1 Поиск переменных без префикса назначения (v_, p_, cn_, cur_)
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'Переменная без префикса назначения (v_/p_/cn_/cur_)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(?!v_|p_|cn_|cur_|g_)(\w+)\s+(integer|number|varchar2|string|date|date_time|boolean|ref|rowtype|record)\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.2 Поиск integer без префикса типа i
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'integer без префикса типа i (должно быть v_i или p_i)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!i)(\w+)\s+integer\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.3 Поиск number без префикса типа n
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'number без префикса типа n (должно быть v_n или p_n)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!n)(\w+)\s+number\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.4 Поиск varchar2/string без префикса типа v
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'varchar2/string без префикса типа v (должно быть v_v или p_v)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!v)(\w+)\s+(varchar2|string)\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.5 Поиск date/date_time без префикса типа d
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'date/date_time без префикса типа d (должно быть v_d или p_d)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!d)(\w+)\s+(date|date_time)\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.6 Поиск boolean без префикса типа b
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'boolean без префикса типа b (должно быть v_b или p_b)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!b)(\w+)\s+boolean\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.7 Поиск ref без префикса типа r
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'ref без префикса типа r (должно быть v_r или p_r)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!r)(\w+)\s+ref\s*\[')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.8 Поиск rowtype без префикса типа rt
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'rowtype без префикса типа rt (должно быть v_rt или p_rt)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!rt)(\w+)\s+\w+%rowtype\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.9 Поиск record без префикса типа rec
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'record без префикса типа rec (должно быть v_rec или p_rec)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!rec)(\w+)\s+record\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.10 Поиск table без префикса типа tb
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'table без префикса типа tb (должно быть v_tb или p_tb)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|p_|cn_|cur_|g_)(?!tb)(\w+)\s+\w+_table\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 7.11 Поиск переменных с некорректным префиксом (dp, tmp, var, и т.д.)
SELECT 
    'PlpCheck.STYLE.PREFIX_COMBINATION.п.4.19' as rule_code,
    'Некорректный префикс переменной (dp/tmp/var/data и т.д.)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(dp|dbg|debug|tmp|temp|var|data|info|z_|x_)\w*\s+(integer|number|varchar2|string|date|date_time|boolean|ref|rowtype|record)\s*[;(:=]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'


-- ============================================================================
-- Сортировка результатов
-- ============================================================================
ORDER BY rule_code, file_name, line_number;