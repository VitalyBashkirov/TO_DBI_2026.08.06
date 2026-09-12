-- ============================================================================
-- Скрипт поиска проблемных мест в PLPlus коде по правилам рубрикатора v5.3.0
-- Назначение: найти строки кода, требующие исправления для DBI
-- Версия: 3.0
-- Дата: 2026-08-20
-- Совместимость: Oracle (использует REGEXP_LIKE вместо REGEXP)
-- Всего правил: 345
-- ============================================================================

-- ============================================================================
-- 1. SQL/DML правила из v53 (27 правил)
-- ============================================================================

-- 1.1 Поиск устаревших OUTER JOIN (v53.SQL.OUTERJOIN.п.1.1)
SELECT 
    'v53.SQL.OUTERJOIN.п.1.1' as rule_code,
    'HIGH' as priority,
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

-- 1.2 Поиск ROWNUM (v53.SQL.ROWNUM.п.1.2)
SELECT 
    'v53.SQL.ROWNUM.п.1.2' as rule_code,
    'HIGH' as priority,
    'Замена rownum на FETCH FIRST' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%ROWNUM%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.3 Поиск UDF в WHERE/GROUP BY/ORDER BY (v53.SQL.UDF.п.1.3)
SELECT 
    'v53.SQL.UDF.п.1.3' as rule_code,
    'HIGH' as priority,
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

-- 1.4 Поиск неявного приведения типов (v53.SQL.CAST.п.1.5)
SELECT 
    'v53.SQL.CAST.п.1.5' as rule_code,
    'HIGH' as priority,
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

-- 1.5 Поиск DECODE (v53.SQL.DECODE.п.1.6.1)
SELECT 
    'v53.SQL.DECODE.п.1.6.1' as rule_code,
    'HIGH' as priority,
    'Использование DECODE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DECODE(%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.6 Поиск CONNECT BY (v53.SQL.CONNECTBY.п.1.8)
SELECT 
    'v53.SQL.CONNECTBY.п.1.8' as rule_code,
    'HIGH' as priority,
    'Использование CONNECT BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CONNECT BY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.7 Поиск V$SESSION и системных представлений (v53.SQL.SYSVIEW.п.1.9)
SELECT 
    'v53.SQL.SYSVIEW.п.1.9' as rule_code,
    'HIGH' as priority,
    'Обращение к системным представлениям Oracle' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(V\$|GV\$|USER_|ALL_|DBA_)[A-Z0-9_]+')
  AND UPPER(line_text) NOT LIKE '%VW_DB_SESSION%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.8 Поиск обращений к системным таблицам ТЯ (v53.SQL.SYSTABLES.п.1.10)
SELECT 
    'v53.SQL.SYSTABLES.п.1.10' as rule_code,
    'HIGH' as priority,
    'SELECT из системных таблиц ТЯ' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(FROM|INTO|JOIN)\s+(CLASSES|CLASS_ATTRIBUTES|METHODS|CRITERIA|RTL_ENTRIES|SOURCES|DEPENDENCIES|ERRORS|HOST2PLP|CURSORS|CURSORS_BIND|CURSORS_VIEW|DEPLOYMENT_SUPPLY|HOST_SOURCES|HOST_ERRORS)')
  AND UPPER(line_text) NOT LIKE '%::\[METACLASS\]%'
  AND UPPER(line_text) NOT LIKE '%::\[STATES\]%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.9 Поиск Oracle пакетов (v53.SQL.ORACLE_PKG.п.1.11)
SELECT 
    'v53.SQL.ORACLE_PKG.п.1.11' as rule_code,
    'HIGH' as priority,
    'Использование Oracle пакетов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UTL_FILE|DBMS_OUTPUT|DBMS_ALERT|DBMS_PIPE|DBMS_LOB|DBMS_RANDOM|UTL_RAW|UTL_COMPRESS|DBMS_XMLGEN|DBMS_CRYPTO|UTL_SMTP|UTL_URL|UTL_HTTP|UTL_TCP|DBMS_SQL)\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.10 Поиск SELECT FROM TABLE() (v53.SQL.TABLE_SELECT.п.1.13)
SELECT 
    'v53.SQL.TABLE_SELECT.п.1.13' as rule_code,
    'HIGH' as priority,
    'SELECT FROM TABLE()' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'SELECT.*FROM\s+TABLE\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.11 Поиск функциональных реквизитов (v53.SQL.FUNC_REQ.п.1.14)
SELECT 
    'v53.SQL.FUNC_REQ.п.1.14' as rule_code,
    'MEDIUM' as priority,
    'Функциональные реквизиты в SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.12 Поиск XMLType в SQL (v53.SQL.XMLTYPE.п.1.15)
SELECT 
    'v53.SQL.XMLTYPE.п.1.15' as rule_code,
    'MEDIUM' as priority,
    'XMLType в SQL запросах' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'XMLTYPE\(|XMLTYPE\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.13 Поиск XMLQuery (v53.SQL.XMLQUERY.п.1.16)
SELECT 
    'v53.SQL.XMLQUERY.п.1.16' as rule_code,
    'MEDIUM' as priority,
    'Использование XMLQuery' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%XMLQUERY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.14 Поиск DML с JOIN (v53.SQL.DML_JOIN.п.1.17)
SELECT 
    'v53.SQL.DML_JOIN.п.1.17' as rule_code,
    'HIGH' as priority,
    'UPDATE/DELETE с JOIN' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UPDATE|DELETE)\s+.*FROM.*JOIN')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.15 Поиск подсказок оптимизатора (v53.SQL.HINTS.п.1.18)
SELECT 
    'v53.SQL.HINTS.п.1.18' as rule_code,
    'HIGH' as priority,
    'Подсказки оптимизатора /*+ ... */' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '/\*\+.*?\*/')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.16 Поиск SELECT из VW_CRIT/VW_RPT/VW_SQL (v53.SQL.VW_CRIT_RPT.п.1.19)
SELECT 
    'v53.SQL.VW_CRIT_RPT.п.1.19' as rule_code,
    'HIGH' as priority,
    'SELECT из VW_CRIT/VW_RPT/VW_SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(VW_CRIT|VW_RPT|VW_SQL)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.17 Поиск псевдоколонок Oracle (v53.SQL.PSEUDO.п.1.20)
SELECT 
    'v53.SQL.PSEUDO.п.1.20' as rule_code,
    'HIGH' as priority,
    'Псевдоколонки Oracle (ROWID, ORA_ROWSCN и др.)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(ROWID|ORA_ROWSCN|OBJECT_ID|OBJECT_VALUE|XMLDATA)\b')
  AND UPPER(line_text) NOT LIKE '%ROWNUM%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.18 Поиск простых представлений (v53.SQL.SIMPLE_VIEW.п.1.21)
SELECT 
    'v53.SQL.SIMPLE_VIEW.п.1.21' as rule_code,
    'MEDIUM' as priority,
    'Простые представления' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'CREATE\s+VIEW\s+[A-Z_]+\s+AS\s+SELECT')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.19 Поиск SYS_CONTEXT с USERENV (v53.SQL.CONTEXT.п.1.23)
SELECT 
    'v53.SQL.CONTEXT.п.1.23' as rule_code,
    'HIGH' as priority,
    'Использование SYS_CONTEXT(USERENV)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%SYS_CONTEXT(%USERENV%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.20 Поиск DDL без схемы (v53.SQL.DDL.п.1.24)
SELECT 
    'v53.SQL.DDL.п.1.24' as rule_code,
    'HIGH' as priority,
    'DDL команды без указания схемы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(CREATE|ALTER|DROP|TRUNCATE)\s+(TABLE|INDEX|VIEW|SEQUENCE)\s+[A-Z#]+\b')
  AND UPPER(line_text) NOT LIKE '%APP\.%'
  AND UPPER(line_text) NOT LIKE '%IBS\.%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.21 Поиск EXCEPTIONLOOP (v53.SQL.EXCEPTIONLOOP.п.1.25)
SELECT 
    'v53.SQL.EXCEPTIONLOOP.п.1.25' as rule_code,
    'HIGH' as priority,
    'Использование EXCEPTIONLOOP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXCEPTIONLOOP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.22 Поиск bind переменных в GROUP BY/ORDER BY (v53.SQL.BIND_GROUP.п.1.26)
SELECT 
    'v53.SQL.BIND_GROUP.п.1.26' as rule_code,
    'HIGH' as priority,
    'Bind переменная в GROUP BY/ORDER BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(GROUP BY|ORDER BY|DISTINCT).*:[a-z_]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.23 Поиск SELECT из REF переменной (v53.SQL.REF_SELECT.п.1.27)
SELECT 
    'v53.SQL.REF_SELECT.п.1.27' as rule_code,
    'HIGH' as priority,
    'SELECT из REF переменной' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%SELECT%REF%'
   OR UPPER(line_text) LIKE '%IN%REF%')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.24 Поиск BULK операций без batch (v53.SQL.BULK.п.1.28)
SELECT 
    'v53.SQL.BULK.п.1.28' as rule_code,
    'HIGH' as priority,
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

-- 1.25 Поиск пустой строки в курсоре (v53.SQL.EMPTY_CURSOR.п.1.29)
SELECT 
    'v53.SQL.EMPTY_CURSOR.п.1.29' as rule_code,
    'MEDIUM' as priority,
    'Пустая строка в курсоре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select\s+y\s*\(\s*''\s*:')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.26 Поиск CREATE VIEW для неплатформенных таблиц (v53.SQL.CREATE_VIEW.п.1.30)
SELECT 
    'v53.SQL.CREATE_VIEW.п.1.30' as rule_code,
    'MEDIUM' as priority,
    'Создание представлений для данных неплатформенных таблиц' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'report\s+view\s+[A-Z_]+\s*\{')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 1.27 Поиск COMPILE$TARGET (v53.PROC.COMPILE_TARGET.п.3.25)
SELECT 
    'v53.PROC.COMPILE_TARGET.п.3.25' as rule_code,
    'LOW' as priority,
    'Использование COMPILE$TARGET' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'COMPILE\$TARGET')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 2. Хранение (STOR) правила из v53 (12 правил)
-- ============================================================================

-- 2.1 Поиск NESTED TABLE (v53.STOR.NESTED.п.2.1)
SELECT 
    'v53.STOR.NESTED.п.2.1' as rule_code,
    'MEDIUM' as priority,
    'Использование NESTED TABLE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'NESTED\s+TABLE')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.2 Поиск типа DATE (v53.STOR.DATE.п.2.2)
SELECT 
    'v53.STOR.DATE.п.2.2' as rule_code,
    'HIGH' as priority,
    'Использование типа DATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '[^_`]date\>')
  AND line_text NOT LIKE '--%'
  AND UPPER(line_text) NOT LIKE '%TO_DATE%'
UNION ALL

-- 2.3 Поиск идентификации по rowid (v53.STOR.ROWID.п.2.3)
SELECT 
    'v53.STOR.ROWID.п.2.3' as rule_code,
    'MEDIUM' as priority,
    'Идентификация ТБП по rowid' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'identified\s+by\s+rowid', 'i')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.4 Поиск секционирования (v53.STOR.PARTITION.п.2.4)
SELECT 
    'v53.STOR.PARTITION.п.2.4' as rule_code,
    'MEDIUM' as priority,
    'Секционирование PARTITIONING' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'PARTITION\s+BY')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.5 Поиск секционирования по профилю (v53.STOR.PARTITION_PROF.п.2.5)
SELECT 
    'v53.STOR.PARTITION_PROF.п.2.5' as rule_code,
    'MEDIUM' as priority,
    'Секционирование по профилю' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'PARTITIONING\s+PROFILE')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.6 Поиск глобальных индексов (v53.STOR.GLOBAL_IDX.п.2.6.1)
SELECT 
    'v53.STOR.GLOBAL_IDX.п.2.6.1' as rule_code,
    'MEDIUM' as priority,
    'Глобальные индексы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'GLOBAL\s+INDEX')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.7 Поиск уникальных индексов с NULL (v53.STOR.UNIQUE_IDX.п.2.6.2)
SELECT 
    'v53.STOR.UNIQUE_IDX.п.2.6.2' as rule_code,
    'HIGH' as priority,
    'Уникальный индекс с NULL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'CREATE\s+UNIQUE\s+INDEX.*ON.*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.8 Поиск индексов на текстовых полях (v53.STOR.INDEX.п.2.6.3)
SELECT 
    'v53.STOR.INDEX.п.2.6.3' as rule_code,
    'HIGH' as priority,
    'Индекс на текстовом поле (возможно > 2704 байт)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'CREATE\s+INDEX.*ON.*\(.*VARCHAR2.*\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.9 Поиск OLE объектов (v53.STOR.OLE.п.2.7)
SELECT 
    'v53.STOR.OLE.п.2.7' as rule_code,
    'MEDIUM' as priority,
    'OLE объекты' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'OLE|LONG\s+RAW')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.10 Поиск временных таблиц (v53.STOR.TEMP.п.2.8)
SELECT 
    'v53.STOR.TEMP.п.2.8' as rule_code,
    'HIGH' as priority,
    'Временные таблицы (TEMP TABLE)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%GLOBAL TEMPORARY TABLE%'
   OR UPPER(line_text) LIKE '%TEMP TABLE%')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.11 Поиск количества колонок > 1664 (v53.STOR.COLUMNS_LIMIT.п.2.9)
SELECT 
    'v53.STOR.COLUMNS_LIMIT.п.2.9' as rule_code,
    'MEDIUM' as priority,
    'Количество колонок в запросе > 1664' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select.*::\[.*\].*where.*\[.*\]\s*=\s*::\[.*\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 2.12 Поиск спецсимволов в коротких именах (v53.STOR.SPEC_CHARS.п.2.10)
SELECT 
    'v53.STOR.SPEC_CHARS.п.2.10' as rule_code,
    'MEDIUM' as priority,
    'Спецсимволы в коротких именах' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'class\s+[A-Z0-9_]*[^A-Z0-9_#][A-Z0-9_#]*|@name\s*\([^)]*[^а-яА-Яa-zA-Z0-9_\s#\.\(\)\-][^)]*\)')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 3. Процедурный код (PROC) правила из v53 (29 правил)
-- ============================================================================

-- 3.1 Поиск утилитных функций ТЯ (v53.PROC.UTILS.п.3.1.1)
SELECT 
    'v53.PROC.UTILS.п.3.1.1' as rule_code,
    'HIGH' as priority,
    'Утилитные функции ТЯ' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UTILS\.SESSION_ID|METHOD_MGR\.CLEAR_OBJECT_REFCING|STDIO\.ZIP)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.2 Поиск DBMS_CRYPTO (v53.PROC.CRYPTO.п.3.1.2)
SELECT 
    'v53.PROC.CRYPTO.п.3.1.2' as rule_code,
    'HIGH' as priority,
    'Использование DBMS_CRYPTO' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_CRYPTO%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.3 Поиск UTL_SMTP (v53.PROC.SMTP.п.3.1.3)
SELECT 
    'v53.PROC.SMTP.п.3.1.3' as rule_code,
    'HIGH' as priority,
    'Использование UTL_SMTP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%UTL_SMTP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.4 Поиск JSON_Object_T и др. (v53.PROC.JSON.п.3.1.4)
SELECT 
    'v53.PROC.JSON.п.3.1.4' as rule_code,
    'HIGH' as priority,
    'Использование Oracle JSON типов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'JSON_(OBJECT|ARRAY|ELEMENT|SCALAR)_T')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.5 Поиск UTL_URL (v53.PROC.UTL_URL.п.3.1.5)
SELECT 
    'v53.PROC.UTL_URL.п.3.1.5' as rule_code,
    'MEDIUM' as priority,
    'Использование UTL_URL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%UTL_URL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.6 Поиск UTL_HTTP (v53.PROC.HTTP.п.3.1.6)
SELECT 
    'v53.PROC.HTTP.п.3.1.6' as rule_code,
    'HIGH' as priority,
    'Использование UTL_HTTP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%UTL_HTTP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.7 Поиск UTL_TCP (v53.PROC.UTL_TCP.п.3.1.7)
SELECT 
    'v53.PROC.UTL_TCP.п.3.1.7' as rule_code,
    'MEDIUM' as priority,
    'Использование UTL_TCP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%UTL_TCP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.8 Поиск utils.hash_value (v53.PROC.HASH_VALUE.п.3.1.8)
SELECT 
    'v53.PROC.HASH_VALUE.п.3.1.8' as rule_code,
    'MEDIUM' as priority,
    'Использование utils.hash_value' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'UTILS\.HASH_VALUE(2)?')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.9 Поиск пустой строки (v53.PROC.EMPTY_STRING.п.3.2)
SELECT 
    'v53.PROC.EMPTY_STRING.п.3.2' as rule_code,
    'HIGH' as priority,
    'Сравнение/присваивание пустой строки' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '=\s*''''|\s*:=\s*''')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.10 Поиск EXECUTE IMMEDIATE без кавычек (v53.PROC.EXECUTE.п.3.3)
SELECT 
    'v53.PROC.EXECUTE.п.3.3' as rule_code,
    'HIGH' as priority,
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

-- 3.11 Поиск DBMS_SQL (v53.PROC.DYNAMIC_SQL.п.3.3)
SELECT 
    'v53.PROC.DYNAMIC_SQL.п.3.3' as rule_code,
    'HIGH' as priority,
    'Использование DBMS_SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_SQL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.12 Поиск макросов execute/process (v53.PROC.MACROS.п.3.4)
SELECT 
    'v53.PROC.MACROS.п.3.4' as rule_code,
    'HIGH' as priority,
    'Макросы execute/process' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'PRAGMA\s+MACRO\([^,]+,[^,]+,(EXECUTE|PROCESS)\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.13 Поиск WHEN OTHERS без ROLLBACK/RAISE (v53.PROC.WHENOTHERS.п.3.5)
SELECT 
    'v53.PROC.WHENOTHERS.п.3.5' as rule_code,
    'HIGH' as priority,
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

-- 3.14 Поиск запрещенных XML пакетов (v53.PROC.XML.п.3.6)
SELECT 
    'v53.PROC.XML.п.3.6' as rule_code,
    'HIGH' as priority,
    'Использование dbms_xmldom/dbms_xmlparser' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(DBMS_XMLDOM|DBMS_XMLPARSER|XRC_XMLDOM|XRC_XMLPARSER)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.15 Поиск SQLCODE/SQLSTATE (v53.PROC.SQLCODE.п.3.7)
SELECT 
    'v53.PROC.SQLCODE.п.3.7' as rule_code,
    'MEDIUM' as priority,
    'Использование SQLCODE/SQLSTATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(SQLCODE|SQLSTATE)\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.16 Поиск CREATE TRIGGER (v53.PROC.TRIGGER.п.3.8)
SELECT 
    'v53.PROC.TRIGGER.п.3.8' as rule_code,
    'HIGH' as priority,
    'CREATE TRIGGER в БД' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CREATE TRIGGER%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.17 Поиск операций типа Отчет (v53.PROC.REPORT.п.3.10)
SELECT 
    'v53.PROC.REPORT.п.3.10' as rule_code,
    'MEDIUM' as priority,
    'Операции типа Отчет' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\<Report\>|\<MethodPresentation.*Report')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.18 Поиск %rowtype (v53.PROC.TYPING.п.3.11)
SELECT 
    'v53.PROC.TYPING.п.3.11' as rule_code,
    'HIGH' as priority,
    'Ограничения типизации (%rowtype)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+%rowtype')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.19 Поиск регулярных выражений (v53.PROC.REGEXP.п.3.12)
SELECT 
    'v53.PROC.REGEXP.п.3.12' as rule_code,
    'MEDIUM' as priority,
    'Регулярные выражения' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'regexp_(replace|substr|instr|count|like)\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.20 Поиск LOB объектов (v53.PROC.LOB.п.3.13)
SELECT 
    'v53.PROC.LOB.п.3.13' as rule_code,
    'MEDIUM' as priority,
    'Использование LOB объектов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(CLOB|BLOB|NCLOB)\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.21 Поиск недостижимого кода (v53.PROC.UNREACHABLE.п.3.14.1)
SELECT 
    'v53.PROC.UNREACHABLE.п.3.14.1' as rule_code,
    'LOW' as priority,
    'Unreachable code' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'return.*pragma\s+IF_DEF|exception.*pragma\s+IF_DEF')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.22 Поиск больших методов (v53.PROC.METHOD_SIZE.п.3.14.2)
SELECT 
    'v53.PROC.METHOD_SIZE.п.3.14.2' as rule_code,
    'LOW' as priority,
    'Превышение 65535 bytes limit' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'method\s+\w+\s+is\s+.*?(?:begin|end)', 's')
  AND length(line_text) > 60000
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.23 Поиск кодогенерации (v53.PROC.CODEGEN.п.3.15)
SELECT 
    'v53.PROC.CODEGEN.п.3.15' as rule_code,
    'HIGH' as priority,
    'Кодогенерация операций/представлений' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(CREATE|ALTER|DROP)\s+(OPERATION|VIEW)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.24 Поиск NLS_* функций (v53.PROC.CHARSET.п.3.16)
SELECT 
    'v53.PROC.CHARSET.п.3.16' as rule_code,
    'HIGH' as priority,
    'Использование NLS_* функций' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(NLS_INITCAP|NLS_LOWER|NLS_UPPER|NCHR|ASCIISTR|COMPOSE|DECOMPOSE|DUMP|UNISTR|LENGTHC|LENGTH2|LENGTH4|SUBSTRC|SUBSTR2|SUBSTR4|NLSSORT)\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.25 Поиск прерванных транзакций (v53.PROC.TRANS_ABORTED.п.3.18.1)
SELECT 
    'v53.PROC.TRANS_ABORTED.п.3.18.1' as rule_code,
    'HIGH' as priority,
    'WHEN OTHERS без rollback/raise' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%WHEN OTHERS%'
  AND UPPER(line_text) NOT LIKE '%ROLLBACK%'
  AND UPPER(line_text) NOT LIKE '%RAISE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.26 Поиск SAVEPOINT в цикле (v53.PROC.SAVEPOINT_LIMIT.п.3.18.2)
SELECT 
    'v53.PROC.SAVEPOINT_LIMIT.п.3.18.2' as rule_code,
    'MEDIUM' as priority,
    'SAVEPOINT в цикле без commit' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\w+\s+IN\s+[0-9]+\s*\.\.\s*[0-9]+\s+LOOP.*savepoint')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.27 Поиск ControlTransaction (v53.PROC.TRANSACT_CONTROL.п.3.18.3)
SELECT 
    'v53.PROC.TRANSACT_CONTROL.п.3.18.3' as rule_code,
    'MEDIUM' as priority,
    'Признак Операция контролирует транзакцию' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<ControlTransaction>true</ControlTransaction>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.28 Поиск длинных имен SAVEPOINT (v53.PROC.SAVEPOINT_LENGTH.п.3.18.4)
SELECT 
    'v53.PROC.SAVEPOINT_LENGTH.п.3.18.4' as rule_code,
    'MEDIUM' as priority,
    'Длинное имя SAVEPOINT (>28 символов)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '&sp\(''[^'']{29,}''\)|&rb\(''[^'']{29,}''\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.29 Поиск SUBMIT_JOB (v53.PROC.JOBS.п.3.19)
SELECT 
    'v53.PROC.JOBS.п.3.19' as rule_code,
    'LOW' as priority,
    'Задания по расписанию' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%SUBMIT_JOB%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.30 Поиск set_this (v53.PROC.SET_THIS.п.3.20)
SELECT 
    'v53.PROC.SET_THIS.п.3.20' as rule_code,
    'MEDIUM' as priority,
    'Конструкция set_this' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'set_this\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.31 Поиск условной компиляции (v53.PROC.COND_COMPILE.п.3.21)
SELECT 
    'v53.PROC.COND_COMPILE.п.3.21' as rule_code,
    'HIGH' as priority,
    'Условная компиляция (#IF, IF_DEF)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '--#IF|--#ELSE|--#ENDIF')
   OR REGEXP_LIKE(UPPER(line_text), 'IF_DEF\s*\(|PRAGMA\s+DEFINE'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.32 Поиск родительского класса по ссылке (v53.PROC.PARENT_REF.п.3.22)
SELECT 
    'v53.PROC.PARENT_REF.п.3.22' as rule_code,
    'MEDIUM' as priority,
    'Обращение к реквизитам родительского класса по ссылке' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'ref\s+\[[A-Z_]+\]\s*:=\s*\w+%id.*\w+\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.33 Поиск конкатенации CLOB/BLOB (v53.PROC.CONCAT_LIB.п.3.23)
SELECT 
    'v53.PROC.CONCAT_LIB.п.3.23' as rule_code,
    'LOW' as priority,
    'Многократная конкатенация CLOB/BLOB' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'dbms_lob\.(write|writeappend|append)\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.34 Поиск обобщенных ссылок (v53.PROC.GENERIC_REF.п.3.24)
SELECT 
    'v53.PROC.GENERIC_REF.п.3.24' as rule_code,
    'MEDIUM' as priority,
    'Обобщенные ссылки в представлении' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select.*\[REFERENCE\].*in.*::\[.*\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.35 Поиск NativeID в NUMBER (v53.PROC.NATIVEID.п.3.26)
SELECT 
    'v53.PROC.NATIVEID.п.3.26' as rule_code,
    'HIGH' as priority,
    'NativeID в NUMBER переменной' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(\w+)\s+NUMBER\s*;.*\1\s*:=\s*\w+%id')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.36 Поиск ID с малым размером (v53.PROC.ID_SIZE.п.3.27)
SELECT 
    'v53.PROC.ID_SIZE.п.3.27' as rule_code,
    'HIGH' as priority,
    'ID в VARCHAR2(10) или меньше' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(\w+)\s+(VARCHAR2|STRING|NUMBER)\s*\(([0-9]|1[0-9])\)\s*;')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.37 Поиск динамического PL+ (v53.PROC.DYNAMIC_PL.п.3.28)
SELECT 
    'v53.PROC.DYNAMIC_PL.п.3.28' as rule_code,
    'HIGH' as priority,
    'Динамический PL+' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '::\[RUNTIME\]\.\[PLP\]\.|::\[RUNTIME\]\.\[PLP2\]\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 3.38 Поиск сортировки по ID (v53.PROC.SORT_BY_ID.п.3.29)
SELECT 
    'v53.PROC.SORT_BY_ID.п.3.29' as rule_code,
    'MEDIUM' as priority,
    'Сортировка по ID' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'ORDER\s+BY.*%id')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 4. Интеграции (INT) правила из v53 (5 правил)
-- ============================================================================

-- 4.1 Поиск UTL_HTTP (v53.INT.UTL_HTTP.п.4.1)
SELECT 
    'v53.INT.UTL_HTTP.п.4.1' as rule_code,
    'HIGH' as priority,
    'Использование UTL_HTTP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%UTL_HTTP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 4.2 Поиск Database Link (v53.INT.DBLINK.п.4.2)
SELECT 
    'v53.INT.DBLINK.п.4.2' as rule_code,
    'HIGH' as priority,
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

-- 4.3 Поиск внешних подключений (v53.INT.CLIENT.п.4.3)
SELECT 
    'v53.INT.CLIENT.п.4.3' as rule_code,
    'MEDIUM' as priority,
    'Подключение внешнего клиентского приложения' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'jdbc:|odbc:')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 4.4 Поиск DBMS_AQ (v53.INT.QUEUE.п.4.4)
SELECT 
    'v53.INT.QUEUE.п.4.4' as rule_code,
    'HIGH' as priority,
    'Использование DBMS_AQ' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_AQ%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 4.5 Поиск синхронного взаимодействия (v53.INT.SYNC.п.4.4.1)
SELECT 
    'v53.INT.SYNC.п.4.4.1' as rule_code,
    'MEDIUM' as priority,
    'Синхронное взаимодействие Интегратора' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'синхрон|sync')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 5. Кэширование (CACHE) правила из v53 (14 правил)
-- ============================================================================

-- 5.1 Поиск разыменования ссылок в цикле (v53.CACHE.REF.п.6.10)
SELECT 
    'v53.CACHE.REF.п.6.10' as rule_code,
    'HIGH' as priority,
    'Разыменование ссылок в цикле' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\w+\s+IN\s+.*?\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 5.2 Поиск cache_mgr функций (v53.CACHE.FUNCTIONS.п.6.4)
SELECT 
    'v53.CACHE.FUNCTIONS.п.6.4' as rule_code,
    'LOW' as priority,
    'Функции управления кэшем' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'cache_mgr\.cache_(clear|refresh|flush)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 5.3 Поиск %insert (v53.CACHE.INSERT.п.6.12)
SELECT 
    'v53.CACHE.INSERT.п.6.12' as rule_code,
    'MEDIUM' as priority,
    'Использование %insert' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '%insert')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 6. Регламенты разработчика из тклоик20240828 (43 правила)
-- ============================================================================

-- 6.1 Поиск объектов без префикса FTC_ (тклоик20240828.PREFIX_FTC.стр.1)
SELECT 
    'тклоик20240828.PREFIX_FTC.стр.1' as rule_code,
    'LOW' as priority,
    'Объект без префикса FTC_' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'class\s+[A-Z][A-Z0-9_]+|view\s+VW_[A-Z][A-Z0-9_]+')
  AND UPPER(line_text) NOT LIKE '%FTC_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.2 Поиск локальных объектов без префикса (тклоик20240828.LOCAL_OBJECTS.стр.1)
SELECT 
    'тклоик20240828.LOCAL_OBJECTS.стр.1' as rule_code,
    'MEDIUM' as priority,
    'Локальный объект без префикса' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'class\s+[A-Z][A-Z0-9_]+|view\s+VW_[A-Z][A-Z0-9_]+')
  AND UPPER(line_text) NOT LIKE '%VND_%'
  AND UPPER(line_text) NOT LIKE '%FTC_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.3 Поиск OOXML отчетов (тклоик20240828.OOXML.стр.1)
SELECT 
    'тклоик20240828.OOXML.стр.1' as rule_code,
    'LOW' as priority,
    'Отчеты не в формате OOXML' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\<Report\>')
  AND line_text NOT LIKE '%OOXML%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.4 Поиск кириллицы в вычисляемых кодах (тклоик20240828.CYRILLIC.стр.1)
SELECT 
    'тклоик20240828.CYRILLIC.стр.1' as rule_code,
    'MEDIUM' as priority,
    'Кириллица в вычисляемых кодах' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '[а-яА-Я]')
  AND line_text NOT LIKE '@name%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.5 Поиск расширений без флага Объединенный пакет (тклоик20240828.EXTENSION_UNITED.стр.1)
SELECT 
    'тклоик20240828.EXTENSION_UNITED.стр.1' as rule_code,
    'MEDIUM' as priority,
    'Расширение без флага Объединенный пакет' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'instead\s+of')
  AND UPPER(line_text) NOT LIKE '%UNITED:=TRUE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.6 Поиск отсутствия VW_CRIT_ИМЯ_КЛАССА (тклоик20240828.VIEW_DEFAULT.стр.2)
SELECT 
    'тклоик20240828.VIEW_DEFAULT.стр.2' as rule_code,
    'LOW' as priority,
    'Отсутствует умолчательное представление' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'view\s+VW_')
  AND UPPER(line_text) NOT LIKE '%VW_CRIT_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.7 Поиск USER вместо STDLIB.userid (тклоик20240828.VIEW_USER.стр.2)
SELECT 
    'тклоик20240828.VIEW_USER.стр.2' as rule_code,
    'MEDIUM' as priority,
    'Использование USER вместо STDLIB.userid' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\bUSER\b')
  AND line_text NOT LIKE '%STDLIB%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.8 Поиск идентификаторов без подчеркивания (тклоик20240828.NAMING_UNDERSCORE.стр.2)
SELECT 
    'тклоик20240828.NAMING_UNDERSCORE.стр.2' as rule_code,
    'LOW' as priority,
    'Идентификатор без подчеркивания' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b[A-Z]+[A-Z][a-z]|\b[a-z]+[A-Z]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.9 Поиск неполного пути к объекту (тклоик20240828.REFERENCE_SYNTAX.стр.2)
SELECT 
    'тклоик20240828.REFERENCE_SYNTAX.стр.2' as rule_code,
    'LOW' as priority,
    'Неполный путь к объекту' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\[\w+\]\.\w+\(')
  AND line_text NOT LIKE '%::%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.10 Поиск THIS в инициализации (тклоик20240828.THIS_FORBIDDEN.стр.3)
SELECT 
    'тклоик20240828.THIS_FORBIDDEN.стр.3' as rule_code,
    'MEDIUM' as priority,
    'THIS в инициализации переменных' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'var\s+\w+\s+\w+\s*:=\s*THIS\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.11 Поиск дублирования функций (тклоик20240828.REUSE_LIBRARIES.стр.3)
SELECT 
    'тклоик20240828.REUSE_LIBRARIES.стр.3' as rule_code,
    'LOW' as priority,
    'Дублирование существующих функций' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'function\s+\w+\s+return')
  AND line_text NOT LIKE '%RUNTIME%'
  AND line_text NOT LIKE '%STDLIB%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.12 Поиск запросов к OBJECTS/COL2OBJ/REFS (тклоик20240828.NO_OBJECTS_VIEW.стр.3)
SELECT 
    'тклоик20240828.NO_OBJECTS_VIEW.стр.3' as rule_code,
    'MEDIUM' as priority,
    'Запрос к OBJECTS/COL2OBJ/REFS' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(OBJECTS|COL2OBJ|REFS)\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.13 Поиск нескольких модификаторов % подряд (тклоик20240828.NO_MULTI_MODIFIER.стр.3)
SELECT 
    'тклоик20240828.NO_MULTI_MODIFIER.стр.3' as rule_code,
    'MEDIUM' as priority,
    'Несколько модификаторов % подряд' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+%\w+%\w+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.14 Поиск VARCHAR2/STRING без размера (тклоик20240828.VARCHAR_SIZE.стр.4)
SELECT 
    'тклоик20240828.VARCHAR_SIZE.стр.4' as rule_code,
    'MEDIUM' as priority,
    'VARCHAR2/STRING без размера' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+(VARCHAR2|STRING)\s*[;(]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 6.15 Поиск INTEGER для ID (тклоик20240828.NO_INTEGER_FOR_ID.стр.4)
SELECT 
    'тклоик20240828.NO_INTEGER_FOR_ID.стр.4' as rule_code,
    'HIGH' as priority,
    'INTEGER для ID экземпляров' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+INTEGER\s*[;(]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.16 Поиск GOTO (тклоик20240828.NO_GOTO.стр.5)
SELECT 
    'тклоик20240828.NO_GOTO.стр.5' as rule_code,
    'HIGH' as priority,
    'Использование GOTO' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\bGOTO\s+\w+\b|<<\w+>>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.17 Поиск прямых SAVEPOINT/ROLLBACK (тклоик20240828.NO_SAVEPOINT_DIRECT.стр.5)
SELECT 
    'тклоик20240828.NO_SAVEPOINT_DIRECT.стр.5' as rule_code,
    'MEDIUM' as priority,
    'Прямой SAVEPOINT/ROLLBACK' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), '\bSAVEPOINT\s+\w+\b')
   OR REGEXP_LIKE(UPPER(line_text), '\bROLLBACK\s+TO\s+SAVEPOINT\s+\w+\b'))
  AND UPPER(line_text) NOT LIKE '%&SP(%'
  AND UPPER(line_text) NOT LIKE '%&RB(%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.18 Поиск переменных без префикса v_ (тклоик20240828.VARIABLE_PREFIX.стр.6)
SELECT 
    'тклоик20240828.VARIABLE_PREFIX.стр.6' as rule_code,
    'LOW' as priority,
    'Переменная без префикса v_' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+(VARCHAR2|STRING|NUMBER|DATE|BOOLEAN|REF|ROWTYPE)\s*[;(]')
  AND UPPER(line_text) NOT LIKE 'V_%'
  AND UPPER(line_text) NOT LIKE 'P_%'
  AND UPPER(line_text) NOT LIKE 'CN_%'
  AND UPPER(line_text) NOT LIKE 'CUR_%'
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 6.19 Поиск констант без префикса cn_ (тклоик20240828.CONSTANT_PREFIX.стр.6-7)
SELECT 
    'тклоик20240828.CONSTANT_PREFIX.стр.6-7' as rule_code,
    'LOW' as priority,
    'Константа без префикса cn_/gcn_' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'CONST\s+\w+')
  AND UPPER(line_text) NOT LIKE 'CN_%'
  AND UPPER(line_text) NOT LIKE 'GCN_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.20 Поиск параметров без префикса p_ (тклоик20240828.PARAM_PREFIX.стр.7)
SELECT 
    'тклоик20240828.PARAM_PREFIX.стр.7' as rule_code,
    'LOW' as priority,
    'Параметр без префикса p_' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\(\s*[^)]*,\s*\w+\s+(VARCHAR2|STRING|NUMBER|DATE|BOOLEAN|REF)')
  AND UPPER(line_text) NOT LIKE 'P_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.21 Поиск курсоров без префикса cur_ (тклоик20240828.CURSOR_PREFIX.стр.7)
SELECT 
    'тклоик20240828.CURSOR_PREFIX.стр.7' as rule_code,
    'LOW' as priority,
    'Курсор без префикса cur_/gcur_' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'TYPE\s+\w+\s+CURSOR|REF\s+CURSOR\s+\w+')
  AND UPPER(line_text) NOT LIKE 'CUR_%'
  AND UPPER(line_text) NOT LIKE 'GCUR_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.22 Поиск глобальных переменных (тклоик20240828.GLOBAL_VAR.стр.7)
SELECT 
    'тклоик20240828.GLOBAL_VAR.стр.7' as rule_code,
    'MEDIUM' as priority,
    'Глобальная переменная' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '^\s*PUBLIC\s+\w+\s+(VARCHAR2|STRING|NUMBER|DATE|BOOLEAN|REF)\s*;')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.23 Поиск служебных слов в верхнем регистре (тклоик20240828.CASE.стр.8)
SELECT 
    'тклоик20240828.CASE.стр.8' as rule_code,
    'LOW' as priority,
    'Служебные слова в верхнем регистре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(BEGIN|END|DECLARE|SELECT|FROM|WHERE|LOOP|IF|THEN|ELSE|WHILE|FOR)\b')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 6.24 Поиск PL/SQL вставок (тклоик20240828.NO_PLSQL_INSERT.стр.8)
SELECT 
    'тклоик20240828.NO_PLSQL_INSERT.стр.8' as rule_code,
    'HIGH' as priority,
    'PL/SQL вставка' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '--\s*begin\s+pl/sql|--\s*begin\s+sql')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.25 Поиск функций в EXECUTE/VALIDATE (тклоик20240828.FUNCTIONS_BODY.стр.8)
SELECT 
    'тклоик20240828.FUNCTIONS_BODY.стр.8' as rule_code,
    'MEDIUM' as priority,
    'Функция/процедура в EXECUTE/VALIDATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'EXECUTE\s+' || CHR(10) || '\s*(FUNCTION|PROCEDURE)')
   OR REGEXP_LIKE(UPPER(line_text), 'VALIDATE\s+' || CHR(10) || '\s*(FUNCTION|PROCEDURE)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.26 Поиск злоупотребления макросами (тклоик20240828.MACROS_LIMIT.стр.8)
SELECT 
    'тклоик20240828.MACROS_LIMIT.стр.8' as rule_code,
    'LOW' as priority,
    'Злоупотребление макросами' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'PRAGMA\s+MACRO')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.27 Поиск SUBMIT_JOB с P_QUEUE (тклоик20240828.SUBMIT_JOB.стр.8)
SELECT 
    'тклоик20240828.SUBMIT_JOB.стр.8' as rule_code,
    'MEDIUM' as priority,
    'SUBMIT_JOB с P_QUEUE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SUBMIT_JOB\s*\([^)]*P_QUEUE')
  AND line_text NOT LIKE '%JOB_LIB.QUEUE_SCHEDULER%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.28 Поиск внешних ключей на CIT_IN/OUT_REQUEST (тклоик20240828.CIT_REF.стр.8)
SELECT 
    'тклоик20240828.CIT_REF.стр.8' as rule_code,
    'MEDIUM' as priority,
    'Внешние ключи на CIT_IN/OUT_REQUEST' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'references\s+(CIT_IN_REQUEST|CIT_OUT_REQUEST)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.29 Поиск отладки без поднятия монитора (тклоик20240828.DEBUG.стр.8)
SELECT 
    'тклоик20240828.DEBUG.стр.8' as rule_code,
    'MEDIUM' as priority,
    'Отладка без поднятия монитора' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'debug_pipe|stdio\.put_line_pipe')
  AND line_text NOT LIKE '%PRAGMA HINT%MONITOR%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.30 Поиск неиспользуемых комментариев (тклоик20240828.COMMENTS.стр.9)
SELECT 
    'тклоик20240828.COMMENTS.стр.9' as rule_code,
    'LOW' as priority,
    'Отсутствие комментариев к сложным блокам' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'function\s+\w+\s+return|procedure\s+\w+')
  AND line_text NOT LIKE '/\*%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.31 Поиск размера формы > 1024x768 (тклоик20240828.FORM_SIZE.стр.10)
SELECT 
    'тклоик20240828.FORM_SIZE.стр.10' as rule_code,
    'LOW' as priority,
    'Размер формы > 1024x768' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<Width>[0-9]{4,}|<Height>[0-9]{4,}')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.32 Поиск нарушения порядка элементов формы (тклоик20240828.FORM_ORDER.стр.10)
SELECT 
    'тклоик20240828.FORM_ORDER.стр.10' as rule_code,
    'LOW' as priority,
    'Нарушение порядка обхода элементов формы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<TabIndex>\d+</TabIndex>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.33 Поиск сложных конструкторов (тклоик20240828.CONSTRUCTOR.стр.10)
SELECT 
    'тклоик20240828.CONSTRUCTOR.стр.10' as rule_code,
    'MEDIUM' as priority,
    'Простой конструктор (не сложный)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'Простой конструктор')
  AND line_text NOT LIKE '%false%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.34 Поиск операции Изменить без F3 (тклоик20240828.EDIT_HOTKEY.стр.10)
SELECT 
    'тклоик20240828.EDIT_HOTKEY.стр.10' as rule_code,
    'LOW' as priority,
    'Операция Изменить без F3' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'EDIT#AUTO|EDIT_AUTO')
  AND line_text NOT LIKE '%F3%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.35 Поиск добавления параметра не последним (тклоик20240828.PARAM_ORDER.стр.10)
SELECT 
    'тклоик20240828.PARAM_ORDER.стр.10' as rule_code,
    'LOW' as priority,
    'Параметр добавлен не последним' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\s+in\s+\w+')
  AND line_text NOT LIKE '%DEFAULT NULL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 6.36 Поиск отсутствия проверки уникальности (тклоик20240828.VALIDATE_UNIQUE.стр.10)
SELECT 
    'тклоик20240828.VALIDATE_UNIQUE.стр.10' as rule_code,
    'MEDIUM' as priority,
    'Отсутствие проверки уникальности кода' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'ADD|EDIT|Добавить|Изменить')
  AND line_text NOT LIKE '%COUNT%'
  AND line_text NOT LIKE '%UNIQUE%'
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 7. Дополнительные требования из тдс20240828 (39 правил)
-- ============================================================================

-- 7.1 Поиск DML с JOIN (тдс20240828.DML_JOIN.стр.1)
SELECT 
    'тдс20240828.DML_JOIN.стр.1' as rule_code,
    'HIGH' as priority,
    'DML с присоединением немодифицируемых таблиц' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UPDATE|DELETE)\s+.*WHERE.*\w+\.\[\w+\]\s*=\s*\w+\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.2 Поиск SELECT из системных таблиц (тдс20240828.SYSTEM_TABLES.стр.2)
SELECT 
    'тдс20240828.SYSTEM_TABLES.стр.2' as rule_code,
    'HIGH' as priority,
    'SELECT из системных таблиц ТЯ' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(FROM|INTO|JOIN)\s+(RTL_ENTRIES|RTL_PARAMETERS|DEPENDENCIES|ERRORS|HOST2PLP|CURSORS|CURSORS_BIND|CURSORS_VIEW|SOURCES|DEPLOYMENT_SUPPLY|HOST_SOURCES|HOST_ERRORS)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.3 Поиск псевдоколонок Oracle (тдс20240828.PSEUDOCOLUMNS.стр.3)
SELECT 
    'тдс20240828.PSEUDOCOLUMNS.стр.3' as rule_code,
    'HIGH' as priority,
    'Псевдоколонки Oracle' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(ROWID|ORA_ROWSCN|OBJECT_ID|OBJECT_VALUE|XMLDATA)\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.4 Поиск операций-отчетов с Oracle Reports (тдс20240828.REPORTS.стр.4)
SELECT 
    'тдс20240828.REPORTS.стр.4' as rule_code,
    'MEDIUM' as priority,
    'Операции-отчеты с Oracle Reports' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\<Report\>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.5 Поиск простых представлений (тдс20240828.SIMPLE_VIEWS.стр.5)
SELECT 
    'тдс20240828.SIMPLE_VIEWS.стр.5' as rule_code,
    'MEDIUM' as priority,
    'Простые представления' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'CREATE\s+VIEW\s+[A-Z_]+\s+AS\s+SELECT')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.6 Поиск внешних соединений старого вида (тдс20240828.ANSI_JOIN.стр.6)
SELECT 
    'тдс20240828.ANSI_JOIN.стр.6' as rule_code,
    'MEDIUM' as priority,
    'Внешние соединения старым способом' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '\(\+\)')
   OR REGEXP_LIKE(line_text, '&collection\(true\)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.7 Поиск FETCH в EXISTS (тдс20240828.FETCH_ROWNUM.стр.7)
SELECT 
    'тдс20240828.FETCH_ROWNUM.стр.7' as rule_code,
    'HIGH' as priority,
    'FETCH в подзапросе EXISTS' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'EXISTS\s*\(.*FETCH\s+FIRST')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.8 Поиск UDF в SQL-запросах (тдс20240828.UDF_LIMITS.стр.8)
SELECT 
    'тдс20240828.UDF_LIMITS.стр.8' as rule_code,
    'HIGH' as priority,
    'UDF в SQL-запросах (кроме SELECT LIST)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'WHERE.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'GROUP BY.*[A-Z_]+\(')
   OR REGEXP_LIKE(UPPER(line_text), 'ORDER BY.*[A-Z_]+\('))
  AND NOT REGEXP_LIKE(UPPER(line_text), '(NVL|DECODE|CASE|COALESCE|TO_CHAR|TO_DATE|TO_NUMBER|SUBSTR|INSTR|LENGTH|TRIM|UPPER|LOWER|COUNT|SUM|AVG|MIN|MAX|SYSDATE)\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.9 Поиск XMLType в SQL (тдс20240828.XMLTYPE.стр.9)
SELECT 
    'тдс20240828.XMLTYPE.стр.9' as rule_code,
    'HIGH' as priority,
    'XMLType в SQL запросах' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'XMLTYPE\(|XMLTYPE\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.10 Поиск VW_SQL (тдс20240828.VW_CRIT_RPT.стр.10)
SELECT 
    'тдс20240828.VW_CRIT_RPT.стр.10' as rule_code,
    'HIGH' as priority,
    'Обращение к VW_SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%VW_SQL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.11 Поиск макросов execute/process (тдс20240828.MACROS_EXECUTE.стр.11)
SELECT 
    'тдс20240828.MACROS_EXECUTE.стр.11' as rule_code,
    'HIGH' as priority,
    'Макросы execute/process' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'PRAGMA\s+MACRO\([^,]+,[^,]+,(EXECUTE|PROCESS)\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.12 Поиск DBMS_SQL (тдс20240828.DYNAMIC_SQL.стр.12)
SELECT 
    'тдс20240828.DYNAMIC_SQL.стр.12' as rule_code,
    'HIGH' as priority,
    'Использование DBMS_SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DBMS_SQL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.13 Поиск DECODE (тдс20240828.DECODE_CASE.стр.13)
SELECT 
    'тдс20240828.DECODE_CASE.стр.13' as rule_code,
    'HIGH' as priority,
    'Использование DECODE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%DECODE(%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.14 Поиск вычитания дат без to_number (тдс20240828.DATE_ARITHMETIC.стр.14)
SELECT 
    'тдс20240828.DATE_ARITHMETIC.стр.14' as rule_code,
    'MEDIUM' as priority,
    'Вычитание дат без to_number' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'TO_DATE.*-.*TO_DATE')
  AND line_text NOT LIKE '%TO_NUMBER%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.15 Поиск временных таблиц (тдс20240828.TEMP_TABLES.стр.15)
SELECT 
    'тдс20240828.TEMP_TABLES.стр.15' as rule_code,
    'HIGH' as priority,
    'Временные таблицы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (UPPER(line_text) LIKE '%GLOBAL TEMPORARY TABLE%'
   OR UPPER(line_text) LIKE '%TEMP TABLE%')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.16 Поиск CREATE TRIGGER (тдс20240828.TRIGGERS.стр.16)
SELECT 
    'тдс20240828.TRIGGERS.стр.16' as rule_code,
    'HIGH' as priority,
    'CREATE TRIGGER в БД' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CREATE TRIGGER%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.17 Поиск CONNECT BY (тдс20240828.CONNECT_BY.стр.18)
SELECT 
    'тдс20240828.CONNECT_BY.стр.18' as rule_code,
    'HIGH' as priority,
    'Использование CONNECT BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CONNECT BY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.18 Поиск SYS_CONTEXT (тдс20240828.CONTEXTS.стр.22)
SELECT 
    'тдс20240828.CONTEXTS.стр.22' as rule_code,
    'HIGH' as priority,
    'Использование SYS_CONTEXT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%SYS_CONTEXT%'
  AND UPPER(line_text) NOT LIKE '%user_context%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.19 Поиск системных представлений Oracle (тдс20240828.SYS_VIEWS.стр.23)
SELECT 
    'тдс20240828.SYS_VIEWS.стр.23' as rule_code,
    'HIGH' as priority,
    'Системные представления Oracle' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(VW_USER_SESSIONS_[12]|V\$|GV\$|AQ\$|DBA_|USER_|ALL_|NLS_|MGW_)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.20 Поиск XMLQuery (тдс20240828.XMLQUERY.стр.24)
SELECT 
    'тдс20240828.XMLQUERY.стр.24' as rule_code,
    'MEDIUM' as priority,
    'Использование XMLQuery' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%XMLQUERY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.21 Поиск varray от record (тдс20240828.VARRAY_NESTED.стр.25)
SELECT 
    'тдс20240828.VARRAY_NESTED.стр.25' as rule_code,
    'HIGH' as priority,
    'VArray от record' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'varray\s*\([^)]*\)\s+of\s+\w+%rowtype|varray\s*\([^)]*\)\s+of\s+record')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.22 Поиск идентификации по rowid (тдс20240828.ROWID_TABLE.стр.26)
SELECT 
    'тдс20240828.ROWID_TABLE.стр.26' as rule_code,
    'MEDIUM' as priority,
    'Идентификация ТБП по rowid' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'identified\s+by\s+rowid', 'i')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.23 Поиск Oracle пакетов (тдс20240828.ORACLE_PACKAGES.стр.27)
SELECT 
    'тдс20240828.ORACLE_PACKAGES.стр.27' as rule_code,
    'HIGH' as priority,
    'Oracle пакеты' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(UTILS\.SESSION_ID|METHOD_MGR\.CLEAR_OBJECT_REFCING|UTL_HTTP|DBMS_XMLDOM|DBMS_XMLPARSER|ASCII|CHR|UTL_URL\.ESCAPE|UTL_URL\.UNESCAPE)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.24 Поиск кодогенерации (тдс20240828.CODEGEN.стр.28)
SELECT 
    'тдс20240828.CODEGEN.стр.28' as rule_code,
    'HIGH' as priority,
    'Кодогенерация операций/представлений' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(CREATE|ALTER|DROP)\s+(OPERATION|VIEW)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.25 Поиск прерванных транзакций (тдс20240828.TRANS_ABORTED.стр.29)
SELECT 
    'тдс20240828.TRANS_ABORTED.стр.29' as rule_code,
    'HIGH' as priority,
    'WHEN OTHERS без rollback/raise' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%WHEN OTHERS%'
  AND UPPER(line_text) NOT LIKE '%ROLLBACK%'
  AND UPPER(line_text) NOT LIKE '%RAISE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.26 Поиск Oracle JSON (тдс20240828.JSON_ORACLE.стр.30)
SELECT 
    'тдс20240828.JSON_ORACLE.стр.30' as rule_code,
    'HIGH' as priority,
    'Oracle JSON типы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'JSON_(OBJECT|ARRAY|ELEMENT|SCALAR)_T')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.27 Поиск CONVERT (тдс20240828.CHARSET.стр.31)
SELECT 
    'тдс20240828.CHARSET.стр.31' as rule_code,
    'HIGH' as priority,
    'Использование CONVERT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'CONVERT\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.28 Поиск set_this (тдс20240828.SET_THIS.стр.32)
SELECT 
    'тдс20240828.SET_THIS.стр.32' as rule_code,
    'MEDIUM' as priority,
    'Конструкция set_this' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'set_this\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.29 Поиск EXECUTE IMMEDIATE (тдс20240828.EXECUTE_IMMEDIATE.стр.33)
SELECT 
    'тдс20240828.EXECUTE_IMMEDIATE.стр.33' as rule_code,
    'HIGH' as priority,
    'EXECUTE IMMEDIATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXECUTE IMMEDIATE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.30 Поиск пустой строки (тдс20240828.EMPTY_STRING_NULL.стр.34)
SELECT 
    'тдс20240828.EMPTY_STRING_NULL.стр.34' as rule_code,
    'HIGH' as priority,
    'Сравнение/присваивание пустой строки' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '=\s*''''|\s*:=\s*''')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.31 Поиск условной компиляции (тдс20240828.COND_COMPILE.стр.35)
SELECT 
    'тдс20240828.COND_COMPILE.стр.35' as rule_code,
    'HIGH' as priority,
    'Условная компиляция' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '--#IF|--#ELSE|--#ENDIF')
   OR REGEXP_LIKE(UPPER(line_text), 'IF_DEF\s*\(|PRAGMA\s+DEFINE'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.32 Поиск Database Link (тдс20240828.DB_LINK.стр.36)
SELECT 
    'тдс20240828.DB_LINK.стр.36' as rule_code,
    'HIGH' as priority,
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

-- 7.33 Поиск синхронного взаимодействия (тдс20240828.INTEGRATOR_SYNC.стр.37)
SELECT 
    'тдс20240828.INTEGRATOR_SYNC.стр.37' as rule_code,
    'MEDIUM' as priority,
    'Синхронное взаимодействие Интегратора' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'синхрон|sync')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 7.34 Поиск FP_TUNE (тдс20240828.FP_TUNE.стр.39)
SELECT 
    'тдс20240828.FP_TUNE.стр.39' as rule_code,
    'MEDIUM' as priority,
    'Прямое обращение к FP_TUNE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '::\[FP_TUNE\]\[^L\]')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- 8. PlpCheck правила (165 правил) — ПОЛНАЯ ВЕРСИЯ
-- ============================================================================

-- 8.1 Поиск статического экземпляра (PlpCheck.JAVA_PLSQL.ACCESS_STATIC.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.ACCESS_STATIC.п.1' as rule_code,
    'MEDIUM' as priority,
    'Обращение к статическому экземпляру' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '::\[SYSTEM\]\.[A-Z_]+\]|::\[MAIN_DOCUM\]\.[A-Z_]+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.2 Поиск отсутствия алиаса в представлении (PlpCheck.STYLE.ALIAS_COLUMN_VIEW.п.1)
SELECT 
    'PlpCheck.STYLE.ALIAS_COLUMN_VIEW.п.1' as rule_code,
    'MEDIUM' as priority,
    'Отсутствие алиаса к колонке в представлении' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select\s+[^,]+,\s*[^:]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.3 Поиск аналитических функций с fetch (PlpCheck.JAVA_PLSQL.ANALYTIC_AND_FETCH_BAD_USE.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.ANALYTIC_AND_FETCH_BAD_USE.п.1' as rule_code,
    'HIGH' as priority,
    'Аналитические функции с fetch/exists' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'FETCH\s+FIRST')
   OR REGEXP_LIKE(UPPER(line_text), 'EXISTS\s*\(.*FETCH'))
  AND REGEXP_LIKE(UPPER(line_text), '(ROW_NUMBER|COUNT|SUM|MIN|MAX|AVG|LISTAGG)\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.4 Поиск некорректных префиксов (PlpCheck.STYLE.BAD_PREFIX.п.4.3)
SELECT 
    'PlpCheck.STYLE.BAD_PREFIX.п.4.3' as rule_code,
    'HIGH' as priority,
    'Некорректный префикс переменной' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(BAD|BADPREFIX|TMP|TEMP|VAR|DATA|INFO|Z_|X_|TEST|DUMMY|DP|DBG|DEBUG)\w+\s+(NUMBER|VARCHAR2|STRING|DATE|BOOLEAN|REF)\s*[;(]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 8.5 Поиск call_stack без размера (PlpCheck.JAVA.CALL_STACK_ANALYSIS.п.1)
SELECT 
    'PlpCheck.JAVA.CALL_STACK_ANALYSIS.п.1' as rule_code,
    'HIGH' as priority,
    'call_stack/error_stack без размера 32000' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'utils\.call_stack(?!\s*\()|utils\.error_stack(?!\s*\()')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.6 Поиск Cartesian Join (PlpCheck.JAVA_PLSQL.CARTESIAN_JOIN.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.CARTESIAN_JOIN.п.1' as rule_code,
    'HIGH' as priority,
    'Cartesian Join в плане запроса' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CARTESIAN JOIN%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.7 Поиск закомментированного кода (PlpCheck.STYLE.CODE_IN_COMMENT.п.4.6)
SELECT 
    'PlpCheck.STYLE.CODE_IN_COMMENT.п.4.6' as rule_code,
    'MEDIUM' as priority,
    'Закомментированный код' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '/\*.*(BEGIN|IF|LOOP|CASE|SELECT|UPDATE|DELETE).*\*/')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.8 Поиск количества колонок > 1664 (PlpCheck.JAVA.COLUMNS_LIMIT_EXCEEDED.п.1)
SELECT 
    'PlpCheck.JAVA.COLUMNS_LIMIT_EXCEEDED.п.1' as rule_code,
    'HIGH' as priority,
    'Количество колонок в запросе > 1664' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select.*::\[.*\].*where.*\[.*\]\s*=\s*::\[.*\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.9 Поиск неполных условий поиска (PlpCheck.JAVA_PLSQL.COMPILE_MISSING_COND.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.COMPILE_MISSING_COND.п.1' as rule_code,
    'HIGH' as priority,
    'Неполное условие поиска экземпляра' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '::\[[A-Z_]+\]\([^)]*\)')
  AND UPPER(line_text) NOT LIKE '%AND%[UD_CODE]%'
  AND UPPER(line_text) NOT LIKE '%AND%[CODE]%'
  AND UPPER(line_text) NOT LIKE '%AND%[%ID]%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.10 Поиск конкатенации без CONCAT_LIB (PlpCheck.DBI.CONCAT_CONTROL.п.1)
SELECT 
    'PlpCheck.DBI.CONCAT_CONTROL.п.1' as rule_code,
    'MEDIUM' as priority,
    'Многократная конкатенация без CONCAT_LIB' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'dbms_lob\.(write|writeappend|append)\s*\(')
  AND line_text NOT LIKE '%CONCAT_LIB%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.11 Поиск условной компиляции в комментариях (PlpCheck.DBI.COND_COMPILE_COMMENT.п.1)
SELECT 
    'PlpCheck.DBI.COND_COMPILE_COMMENT.п.1' as rule_code,
    'HIGH' as priority,
    'Условная компиляция в комментариях' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '--#if|--#elsif|--#endif')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.12 Поиск CONNECT BY (PlpCheck.DBI.CONNECTBY2WITH.п.1)
SELECT 
    'PlpCheck.DBI.CONNECTBY2WITH.п.1' as rule_code,
    'HIGH' as priority,
    'Использование CONNECT BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%CONNECT BY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.13 Поиск констант в ORDER/GROUP BY (PlpCheck.DBI.CONSTANT_IN_ORDER_AND_GROUP_BY.п.1)
SELECT 
    'PlpCheck.DBI.CONSTANT_IN_ORDER_AND_GROUP_BY.п.1' as rule_code,
    'HIGH' as priority,
    'Константы в ORDER/GROUP BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'ORDER\s+BY\s+''[^'']+''|GROUP\s+BY\s+''[^'']+''')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.14 Поиск номера колонки в ORDER BY с UDF (PlpCheck.DBI.CONSTANT_ORDER_BY_ON_UDF.п.1)
SELECT 
    'PlpCheck.DBI.CONSTANT_ORDER_BY_ON_UDF.п.1' as rule_code,
    'HIGH' as priority,
    'Номер колонки в ORDER BY с UDF' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*[A-Z_]+\s*\(.*\)')
  AND REGEXP_LIKE(line_text, 'ORDER\s+BY\s+\d+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.15 Поиск continue/exit вне цикла (PlpCheck.STYLE.CONTINUE_EXIT_OFF_THE_LOOP.п.1)
SELECT 
    'PlpCheck.STYLE.CONTINUE_EXIT_OFF_THE_LOOP.п.1' as rule_code,
    'MEDIUM' as priority,
    'continue/exit вне цикла' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\bcontinue\b|\bexit\b')
  AND line_text NOT LIKE '%loop%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.16 Поиск контролов без validate_name (PlpCheck.WEB.CONTROLS_VALIDATE_NAME.п.1)
SELECT 
    'PlpCheck.WEB.CONTROLS_VALIDATE_NAME.п.1' as rule_code,
    'LOW' as priority,
    'Контрол без validate_name' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<ValidateName></ValidateName>|<ValidateName>\s*</ValidateName>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.17 Поиск запрещенных типов реквизитов (PlpCheck.DBI.CONTROLTABLECOLUMNSTYPE.п.1)
SELECT 
    'PlpCheck.DBI.CONTROLTABLECOLUMNSTYPE.п.1' as rule_code,
    'MEDIUM' as priority,
    'Запрещенный тип реквизита' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\[(CALC_TUN_NESTED|METHOD|INTERVAL|METACLASS|STATES|OBJECT|CLASS_ATTRIBUTES|METHOD_CONTROLS)\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.18 Поиск конвертаций без потоков (PlpCheck.JAVA.CONV_STREAM_CHECKS.п.1)
SELECT 
    'PlpCheck.JAVA.CONV_STREAM_CHECKS.п.1' as rule_code,
    'MEDIUM' as priority,
    'Конвертации без параметров потоков' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'A[0-9]+_')
  AND line_text NOT LIKE '%P#STREAM#COUNT%'
  AND line_text NOT LIKE '%P#STREAM#NUM%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.19 Поиск старого формата расширения (PlpCheck.STYLE.CRIT_EXT_IN_OLD_FORMAT.п.1)
SELECT 
    'PlpCheck.STYLE.CRIT_EXT_IN_OLD_FORMAT.п.1' as rule_code,
    'MEDIUM' as priority,
    'Старый формат расширения представления' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'view\s+VW_CRIT.*EXT.*instead\s+of.*\{.*select.*in\s+::\[.*\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.20 Поиск обращения к разным DAO (PlpCheck.DBI.CROSS_DB_QUERY.п.1)
SELECT 
    'PlpCheck.DBI.CROSS_DB_QUERY.п.1' as rule_code,
    'HIGH' as priority,
    'Обращение к данным из разных DAO' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'FROM\s+::\[[A-Z_]+\].*JOIN\s+::\[[A-Z_]+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.21 Поиск разыменования ссылки в цикле (PlpCheck.PLSQL.DEREFERENCE_IN_LOOP.п.1)
SELECT 
    'PlpCheck.PLSQL.DEREFERENCE_IN_LOOP.п.1' as rule_code,
    'MEDIUM' as priority,
    'Разыменование ссылки в цикле' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\w+\s+IN\s+.*?\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.22 Поиск разыменования в out параметр (PlpCheck.STYLE.DEREFERENCING_TO_OUT_PARAM.п.1)
SELECT 
    'PlpCheck.STYLE.DEREFERENCING_TO_OUT_PARAM.п.1' as rule_code,
    'HIGH' as priority,
    'Разыменованное поле в out параметре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.\[\w+\]\s*,\s*\w+\s+OUT')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.23 Поиск прямого сравнения с NULL (PlpCheck.PLSQL.DIRECT_COMPARISON_WITH_NULL.п.1)
SELECT 
    'PlpCheck.PLSQL.DIRECT_COMPARISON_WITH_NULL.п.1' as rule_code,
    'HIGH' as priority,
    'Прямое сравнение с NULL или пустой строкой' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '=\s*NULL|NULL\s*=|=\s*''''|''''\s*=')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.24 Поиск DISTINCT и ORDER BY (PlpCheck.DBI.DISTINCT_AND_ORDER_BY.п.1)
SELECT 
    'PlpCheck.DBI.DISTINCT_AND_ORDER_BY.п.1' as rule_code,
    'HIGH' as priority,
    'DISTINCT и ORDER BY с разными выражениями' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT\s+DISTINCT.*ORDER\s+BY')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.25 Поиск DISTINCT с UDF (PlpCheck.DBI.DISTINCT_UDF.п.1)
SELECT 
    'PlpCheck.DBI.DISTINCT_UDF.п.1' as rule_code,
    'HIGH' as priority,
    'DISTINCT с UDF' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT\s+DISTINCT.*[A-Z_]+\s*\(')
  AND line_text NOT LIKE '%STATENAME%'
  AND line_text NOT LIKE '%CLASSNAME%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.26 Поиск динамического PLP (PlpCheck.JAVA_PLSQL.DYNAMIC_PLP.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.DYNAMIC_PLP.п.1' as rule_code,
    'MEDIUM' as priority,
    'Динамический PLP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '::\[RUNTIME\]\.\[PLP\]\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.27 Поиск операции Изменить без F3 (PlpCheck.STYLE.EDIT_HOTKEY.п.1)
SELECT 
    'PlpCheck.STYLE.EDIT_HOTKEY.п.1' as rule_code,
    'LOW' as priority,
    'Операция Изменить без F3' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'EDIT#AUTO|EDIT_AUTO')
  AND line_text NOT LIKE '%F3%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.28 Поиск пустой строки в курсоре (PlpCheck.DBI_PLSQL.EMPTY_STRING_IN_CURSOR.п.1)
SELECT 
    'PlpCheck.DBI_PLSQL.EMPTY_STRING_IN_CURSOR.п.1' as rule_code,
    'MEDIUM' as priority,
    'Пустая строка в курсоре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select\s+y\s*\(\s*''\s*:')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.29 Поиск бесконечного цикла (PlpCheck.JAVA_PLSQL.ENDLESS_CYCLE.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.ENDLESS_CYCLE.п.1' as rule_code,
    'HIGH' as priority,
    'Бесконечный цикл' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'LOOP\s+(?!.*EXIT)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.30 Поиск анализа sqlerrm (PlpCheck.DBI_JAVA.ERROR_MESSAGE_ANALYSIS.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.ERROR_MESSAGE_ANALYSIS.п.1' as rule_code,
    'HIGH' as priority,
    'Анализ текста sqlerrm/error_stack' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'sqlerrm\s+(like|instr|regexp_like)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.31 Поиск Word/Excel библиотек (PlpCheck.WEB.EXCEL_WORD_LIBS_WEB.п.1)
SELECT 
    'PlpCheck.WEB.EXCEL_WORD_LIBS_WEB.п.1' as rule_code,
    'LOW' as priority,
    'Библиотеки Word/Excel' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(EXCEL|WORD)\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.32 Поиск EXCEPTIONLOOP (PlpCheck.DBI.EXCEPTIONLOOP.п.1)
SELECT 
    'PlpCheck.DBI.EXCEPTIONLOOP.п.1' as rule_code,
    'HIGH' as priority,
    'Использование EXCEPTIONLOOP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXCEPTIONLOOP%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.33 Поиск EXECUTE IMMEDIATE (PlpCheck.DBI.EXECUTEIMMEDIATE.п.1)
SELECT 
    'PlpCheck.DBI.EXECUTEIMMEDIATE.п.1' as rule_code,
    'HIGH' as priority,
    'EXECUTE IMMEDIATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%EXECUTE IMMEDIATE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.34 Поиск ТБП без all/collection (PlpCheck.STYLE.EXIST_ALL_OR_COLLECTIONS.п.4.7)
SELECT 
    'PlpCheck.STYLE.EXIST_ALL_OR_COLLECTIONS.п.4.7' as rule_code,
    'HIGH' as priority,
    'ТБП без all/collection' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'FROM\s+\[[A-Z][A-Z0-9_#]+\](?!\s+ALL\s*:)')
   OR REGEXP_LIKE(UPPER(line_text), 'FROM\s+\[[A-Z][A-Z0-9_#]+\]\s+\w+(?!\s+COLLECTION)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.35 Поиск FETCH над подзапросом (PlpCheck.JAVA_PLSQL.FETCH_OVER_SUBQUERY.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.FETCH_OVER_SUBQUERY.п.1' as rule_code,
    'MEDIUM' as priority,
    'FETCH над подзапросом' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*IN\s*\(.*FETCH\s+FIRST')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.36 Поиск FIXME в комментариях (PlpCheck.STYLE.FIXME_NOT_ALLOWED.п.1)
SELECT 
    'PlpCheck.STYLE.FIXME_NOT_ALLOWED.п.1' as rule_code,
    'LOW' as priority,
    'Пометка FIXME в комментариях' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FIXME')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.37 Поиск размера формы (PlpCheck.STYLE.FORM_SIZE.п.1)
SELECT 
    'PlpCheck.STYLE.FORM_SIZE.п.1' as rule_code,
    'LOW' as priority,
    'Размер формы > 1024x768' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<Width>[0-9]{4,}|<Height>[0-9]{4,}')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.38 Поиск ControlTransaction (PlpCheck.DBI.FORM_TRANSACT_CONTROL.п.1)
SELECT 
    'PlpCheck.DBI.FORM_TRANSACT_CONTROL.п.1' as rule_code,
    'HIGH' as priority,
    'Признак ControlTransaction' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<ControlTransaction>true</ControlTransaction>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.39 Поиск FULL INDEX SCAN (PlpCheck.JAVA_PLSQL.FULL_INDEX_SCAN.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.FULL_INDEX_SCAN.п.1' as rule_code,
    'HIGH' as priority,
    'FULL INDEX SCAN в плане' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%FULL INDEX SCAN%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.40 Поиск FULL TABLE SCAN (PlpCheck.JAVA_PLSQL.FULL_TABLE_SCAN.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.FULL_TABLE_SCAN.п.1' as rule_code,
    'HIGH' as priority,
    'FULL TABLE SCAN в плане' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%FULL TABLE SCAN%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.41 Поиск returning в функции (PlpCheck.STYLE.FUNCRETURNKEYWORD.п.1)
SELECT 
    'PlpCheck.STYLE.FUNCRETURNKEYWORD.п.1' as rule_code,
    'LOW' as priority,
    'Использование returning в функции' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'function\s+\w+\s+returning')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.42 Поиск функций в EXECUTE/VALIDATE (PlpCheck.STYLE.FUNCTIONS_IN_BODY_OR_VALIDATE.п.4.18)
SELECT 
    'PlpCheck.STYLE.FUNCTIONS_IN_BODY_OR_VALIDATE.п.4.18' as rule_code,
    'MEDIUM' as priority,
    'Функция/процедура в EXECUTE/VALIDATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), 'EXECUTE\s+' || CHR(10) || '\s*(FUNCTION|PROCEDURE)')
   OR REGEXP_LIKE(UPPER(line_text), 'VALIDATE\s+' || CHR(10) || '\s*(FUNCTION|PROCEDURE)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.43 Поиск преобразований над индексами (PlpCheck.JAVA_PLSQL.FUNCTION_BREAK_INDEX.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.FUNCTION_BREAK_INDEX.п.1' as rule_code,
    'HIGH' as priority,
    'Преобразования над индексированными полями' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'WHERE\s+\w+\s*\([^)]*\)\s*=' )
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.44 Поиск разыменования функциональных атрибутов (PlpCheck.DBI.FUNC_ATTR_DEREFERENCE.п.1)
SELECT 
    'PlpCheck.DBI.FUNC_ATTR_DEREFERENCE.п.1' as rule_code,
    'MEDIUM' as priority,
    'Разыменование функциональных атрибутов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.45 Поиск получения объекта в if (PlpCheck.PLSQL.GETOBJECTINIFELSESECTION.п.1)
SELECT 
    'PlpCheck.PLSQL.GETOBJECTINIFELSESECTION.п.1' as rule_code,
    'MEDIUM' as priority,
    'Получение реквизитов объекта в if/elsif' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'if\s+::\[.*\]\(.*\)\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.46 Поиск глобальных переменных (PlpCheck.STYLE.GLOBAL_VAR.п.4.10)
SELECT 
    'PlpCheck.STYLE.GLOBAL_VAR.п.4.10' as rule_code,
    'LOW' as priority,
    'Глобальная переменная' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '^\s*PUBLIC\s+\w+\s+(VARCHAR2|STRING|NUMBER|DATE|BOOLEAN|REF)\s*;')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.47 Поиск GOTO (PlpCheck.JAVA.GOTO.п.1)
SELECT 
    'PlpCheck.JAVA.GOTO.п.1' as rule_code,
    'HIGH' as priority,
    'Использование GOTO' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\bGOTO\s+\w+\b|<<\w+>>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.48 Поиск хинта на индекс без ORDER BY (PlpCheck.DBI.HINT_INDEX_ORDER_BY.п.1)
SELECT 
    'PlpCheck.DBI.HINT_INDEX_ORDER_BY.п.1' as rule_code,
    'HIGH' as priority,
    'Хинт на индекс без ORDER BY' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'pragma hint.*index')
  AND line_text NOT LIKE '%ORDER BY%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.49 Поиск запрещенных горячих клавиш (PlpCheck.WEB.HOT_KEY_PROHIBITED.п.1)
SELECT 
    'PlpCheck.WEB.HOT_KEY_PROHIBITED.п.1' as rule_code,
    'LOW' as priority,
    'Запрещенные горячие клавиши' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'Ctrl\+[TNW]|Ctrl\+F4|Ctrl\+Shift\+[NTWQ]|Alt\+[TF]|Alt\+F[124]|Ctrl\+Page(Up|Down)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.50 Поиск if exit вместо exit when (PlpCheck.STYLE.IF_EXIT_TO_EXIT_WHEN.п.1)
SELECT 
    'PlpCheck.STYLE.IF_EXIT_TO_EXIT_WHEN.п.1' as rule_code,
    'LOW' as priority,
    'if exit вместо exit when' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'if\s+.*\s+then\s+exit\s*;')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.51 Поиск части составного индекса (PlpCheck.JAVA_PLSQL.INDEX_CAN_USE_BETTER.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.INDEX_CAN_USE_BETTER.п.1' as rule_code,
    'HIGH' as priority,
    'Использование части составного индекса' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'INDEX\s+SCAN.*IDX_.*WHERE')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.52 Поиск индексов с большим размером (PlpCheck.DBI.INDEX_LENGTH.п.1)
SELECT 
    'PlpCheck.DBI.INDEX_LENGTH.п.1' as rule_code,
    'HIGH' as priority,
    'Индекс с большим текстовым полем' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'index\s+[A-Z_]+.*STRING_[0-9]{4,}')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.53 Поиск PL/SQL вставок (PlpCheck.JAVA.INSERT_PLSQL.п.1)
SELECT 
    'PlpCheck.JAVA.INSERT_PLSQL.п.1' as rule_code,
    'HIGH' as priority,
    'PL/SQL вставка' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '--\s*begin\s+pl/sql|--\s*begin\s+sql')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.54 Поиск вставки с ID (PlpCheck.JAVA.INSERT_WITH_ID.п.1)
SELECT 
    'PlpCheck.JAVA.INSERT_WITH_ID.п.1' as rule_code,
    'MEDIUM' as priority,
    'Вставка с предопределенным ID' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '%insert\s*\([^,]+,\s*[^)]+%id\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.55 Поиск interval вне SELECT (PlpCheck.DBI.INTERVAL_NOT_SELECT.п.1)
SELECT 
    'PlpCheck.DBI.INTERVAL_NOT_SELECT.п.1' as rule_code,
    'LOW' as priority,
    'Interval вне SELECT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'interval\s*\(')
  AND line_text NOT LIKE '%SELECT%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.56 Поиск %init с неподдерживаемыми параметрами (PlpCheck.DBI_JAVA.INVALID_INIT.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.INVALID_INIT.п.1' as rule_code,
    'MEDIUM' as priority,
    'Неподдерживаемый %init' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '%init\s*\([^)]*\)')
  AND line_text NOT LIKE '%init()%'
  AND line_text NOT LIKE '%init(true, true)%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.57 Поиск Oracle JSON (PlpCheck.DBI_JAVA.JSON_TYPES.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.JSON_TYPES.п.1' as rule_code,
    'HIGH' as priority,
    'Oracle JSON типы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'JSON_(OBJECT|ARRAY|ELEMENT|SCALAR)_T')
  AND line_text NOT LIKE '%LIB_JSON%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.58 Поиск макросов EXECUTE/PROCESS (PlpCheck.DBI.MACROEXECUTEPROCESS.п.1)
SELECT 
    'PlpCheck.DBI.MACROEXECUTEPROCESS.п.1' as rule_code,
    'HIGH' as priority,
    'Макросы EXECUTE/PROCESS' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), 'PRAGMA\s+MACRO\([^,]+,[^,]+,(EXECUTE|PROCESS)\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.59 Поиск макросов EXECUTE/PROCESS в комментариях (PlpCheck.DBI.MACROEXECUTEPROCESS_COMMENT.п.1)
SELECT 
    'PlpCheck.DBI.MACROEXECUTEPROCESS_COMMENT.п.1' as rule_code,
    'HIGH' as priority,
    'Макросы EXECUTE/PROCESS в комментариях' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '#define\s+\w+\s+(process|execute)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.60 Поиск вызова макросов execute/process (PlpCheck.DBI.MACRO_CALL_EXECUTEPROCESS.п.1)
SELECT 
    'PlpCheck.DBI.MACRO_CALL_EXECUTEPROCESS.п.1' as rule_code,
    'HIGH' as priority,
    'Вызов макросов execute/process' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '&[A-Z_]+')
  AND line_text NOT LIKE '%sp%'
  AND line_text NOT LIKE '%rb%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.61 Поиск SAVEPOINT в цикле без commit (PlpCheck.DBI.MANY_SUB_TRANSACTIONS.п.1)
SELECT 
    'PlpCheck.DBI.MANY_SUB_TRANSACTIONS.п.1' as rule_code,
    'MEDIUM' as priority,
    'SAVEPOINT в цикле без commit' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\w+\s+IN\s+[0-9]+\s*\.\.\s*[0-9]+\s+LOOP.*savepoint')
  AND line_text NOT LIKE '%COMMIT%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.62 Поиск несоответствия типов (PlpCheck.DBI.MATCHING_TYPES.п.1)
SELECT 
    'PlpCheck.DBI.MATCHING_TYPES.п.1' as rule_code,
    'HIGH' as priority,
    'Несоответствие типов' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\s*[-+]\s*\w+')
  AND line_text NOT LIKE '%TO_NUMBER%'
  AND line_text NOT LIKE '%TO_CHAR%'
  AND line_text NOT LIKE '%CAST%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.63 Поиск размера ID меньше 20 (PlpCheck.DBI.MAX_SIZE_ID.п.1)
SELECT 
    'PlpCheck.DBI.MAX_SIZE_ID.п.1' as rule_code,
    'HIGH' as priority,
    'Размер ID меньше 20' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(\w+)\s+(NUMBER|VARCHAR2|STRING)\s*\(([0-9]|1[0-9])\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.64 Поиск присваивания ссылок methods/criteria (PlpCheck.DBI.NATIVE_ID_OBJ_IDENTIFIER.п.1)
SELECT 
    'PlpCheck.DBI.NATIVE_ID_OBJ_IDENTIFIER.п.1' as rule_code,
    'MEDIUM' as priority,
    'Присваивание ссылок methods/criteria' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(ref\s+\[METHOD\]|ref\s+\[CRITERIA\])\s*:=\s*\w+%id')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.65 Поиск вложенных таблиц в SQL (PlpCheck.DBI.NESTED_TABLE.п.1)
SELECT 
    'PlpCheck.DBI.NESTED_TABLE.п.1' as rule_code,
    'HIGH' as priority,
    'Вложенные таблицы в SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*IN\s+[A-Z_]+\s+WHERE.*varray')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.66 Поиск массива чисел в параметрах (PlpCheck.DBI_JAVA.NOT_CLASS_REF_TABLE_PARAM.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.NOT_CLASS_REF_TABLE_PARAM.п.1' as rule_code,
    'MEDIUM' as priority,
    'Массив чисел в параметрах' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'procedure\s+\w+\s*\([^)]*table\s+of\s+number[^)]*\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.67 Поиск незакрытых курсоров (PlpCheck.JAVA_PLSQL.NOT_CLOSED_CURSOR.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.NOT_CLOSED_CURSOR.п.1' as rule_code,
    'HIGH' as priority,
    'Незакрытый курсор' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.open\s*\(')
  AND line_text NOT LIKE '%close%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.68 Поиск незакрытых файлов (PlpCheck.JAVA_PLSQL.NOT_CLOSED_FILE.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.NOT_CLOSED_FILE.п.1' as rule_code,
    'HIGH' as priority,
    'Незакрытый файл' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'stdio\.(f_open|fopen|f_dopen)\s*\(')
  AND line_text NOT LIKE '%close%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.69 Поиск неиспользуемых сущностей (PlpCheck.STYLE.NOT_MENTIONED.п.4.8)
SELECT 
    'PlpCheck.STYLE.NOT_MENTIONED.п.4.8' as rule_code,
    'LOW' as priority,
    'Неиспользуемая сущность' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+(NUMBER|VARCHAR2|STRING|DATE|BOOLEAN|REF|ROWTYPE)\s*[;(]')
  AND line_text NOT LIKE '--%'
  AND NOT EXISTS (
      SELECT 1 FROM plplus_code_source t2
      WHERE t2.file_name = t.file_name
        AND t2.line_number != t.line_number
        AND t2.line_text NOT LIKE '--%'
        AND REGEXP_LIKE(UPPER(t2.line_text), UPPER(REGEXP_SUBSTR(t.line_text, '\b\w+\b')))
  )
UNION ALL

-- 8.70 Поиск функций без RETURN (PlpCheck.JAVA_PLSQL.NOT_RETURN_STATEMENT.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.NOT_RETURN_STATEMENT.п.1' as rule_code,
    'HIGH' as priority,
    'Функция без RETURN' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'function\s+\w+\s+return\s+\w+\s+is')
  AND line_text NOT LIKE '%return%'
  AND line_text NOT LIKE '%pragma error%'
  AND line_text NOT LIKE '%raise%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.71 Поиск рекурсии без комментария (PlpCheck.DBI_JAVA_PLSQL.NO_RECURSION_COMMENT.п.1)
SELECT 
    'PlpCheck.DBI_JAVA_PLSQL.NO_RECURSION_COMMENT.п.1' as rule_code,
    'MEDIUM' as priority,
    'Рекурсия без комментария' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'function\s+\w+.*\s+\w+\s*\(')
  AND line_text NOT LIKE '%Рекурсия%'
  AND line_text NOT LIKE '%Recursion%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.72 Поиск null is [not] null (PlpCheck.DBI_JAVA.NULL_IS_NULL_TO_JAVA.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.NULL_IS_NULL_TO_JAVA.п.1' as rule_code,
    'HIGH' as priority,
    'null is [not] null в Java' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'null\s+is\s+(not\s+)?null')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.73 Поиск NVL с функцией/select (PlpCheck.JAVA_PLSQL.NVL_IN_SELECT.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.NVL_IN_SELECT.п.1' as rule_code,
    'MEDIUM' as priority,
    'NVL с функцией/select во втором параметре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'nvl\s*\([^,]+,\s*(select|\w+\()')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.74 Поиск WHEN OTHERS без rollback/raise (PlpCheck.DBI.OBLIGATORY_IN_OTHERS.п.1)
SELECT 
    'PlpCheck.DBI.OBLIGATORY_IN_OTHERS.п.1' as rule_code,
    'HIGH' as priority,
    'WHEN OTHERS без rollback/raise' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%WHEN OTHERS%'
  AND UPPER(line_text) NOT LIKE '%ROLLBACK%'
  AND UPPER(line_text) NOT LIKE '%RAISE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.75 Поиск отсутствия уникальных алиасов (PlpCheck.DBI_SQL.OBLIGATORY_UNIQUE_ALIAS.п.1)
SELECT 
    'PlpCheck.DBI_SQL.OBLIGATORY_UNIQUE_ALIAS.п.1' as rule_code,
    'HIGH' as priority,
    'Отсутствие уникальных алиасов в SELECT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT\s+[^,]+,\s*[^:]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.76 Поиск нарушения порядка элементов формы (PlpCheck.STYLE.ORDERED_CONTROLS.п.1)
SELECT 
    'PlpCheck.STYLE.ORDERED_CONTROLS.п.1' as rule_code,
    'LOW' as priority,
    'Нарушение порядка элементов формы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '<TabIndex>\d+</TabIndex>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.77 Поиск внешних соединений через (true) (PlpCheck.DBI.OUTER_JOIN.п.1)
SELECT 
    'PlpCheck.DBI.OUTER_JOIN.п.1' as rule_code,
    'HIGH' as priority,
    'Внешние соединения через (true)' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\[\w+\]\(true\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.78 Поиск хинта parallel (PlpCheck.JAVA_PLSQL.PARALLEL_EXECUTION.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.PARALLEL_EXECUTION.п.1' as rule_code,
    'HIGH' as priority,
    'Хинт parallel' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'pragma\s+hint.*parallel')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.79 Поиск PARTITION ALL (PlpCheck.JAVA_PLSQL.PARTITION_ALL.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.PARTITION_ALL.п.1' as rule_code,
    'HIGH' as priority,
    'PARTITION ALL в плане' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%PARTITION ALL%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.80 Поиск несоответствия типов Integer (PlpCheck.PLSQL.PLATFORM_INTEGER_MISMATCH.п.1)
SELECT 
    'PlpCheck.PLSQL.PLATFORM_INTEGER_MISMATCH.п.1' as rule_code,
    'HIGH' as priority,
    'Несоответствие типов Integer' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+integer\s*[;(]')
  AND REGEXP_LIKE(line_text, 'rtl\.USERID|executor\.lock_open|rtl\.session_id')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.81 Поиск переменной без префикса типа (PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4)
SELECT 
    'PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4' as rule_code,
    'HIGH' as priority,
    'Переменная без префикса типа' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(?!v_|n_|d_|b_|r_|s_|t_|o_|i_|p_|cn_|cur_|g_)(\w+)\s+(NUMBER|INTEGER|BOOLEAN|REF|STRING|TABLE|VARRAY|RECORD)\s*[;(]')
  AND line_text NOT LIKE '--%'
  AND line_text NOT LIKE '%PRAGMA%'
UNION ALL

-- 8.82 Поиск чистого SQL CONNECT BY (PlpCheck.DBI_SQL.PURE_SQL_CONNECTBY2WITH.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_CONNECTBY2WITH.п.1' as rule_code,
    'HIGH' as priority,
    'CONNECT BY в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'CONNECT\s+BY')
  AND line_text NOT LIKE '%FOR%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.83 Поиск DBLink в чистом SQL (PlpCheck.DBI_SQL.PURE_SQL_DBLINK.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_DBLINK.п.1' as rule_code,
    'HIGH' as priority,
    'DBLink в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select.*@[a-z_]+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.84 Поиск не реализованных SQL функций (PlpCheck.DBI_SQL.PURE_SQL_FUNCTION_UNSUPPORTED.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_FUNCTION_UNSUPPORTED.п.1' as rule_code,
    'HIGH' as priority,
    'Не реализованные SQL функции' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'regexp_replace\s*\(|regexp_substr\s*\(|sys_guid')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.85 Поиск JSON в чистом SQL (PlpCheck.DBI_SQL.PURE_SQL_JSON_TYPES.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_JSON_TYPES.п.1' as rule_code,
    'HIGH' as priority,
    'JSON в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'JSON_(OBJECT|ARRAY|ELEMENT|SCALAR)_T')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.86 Поиск MINUS в SQL (PlpCheck.DBI_SQL.PURE_SQL_MINUS_NOT_DBI.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_MINUS_NOT_DBI.п.1' as rule_code,
    'HIGH' as priority,
    'MINUS в SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%MINUS%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.87 Поиск (+) в чистом SQL (PlpCheck.DBI_SQL.PURE_SQL_OUTER_JOIN.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_OUTER_JOIN.п.1' as rule_code,
    'HIGH' as priority,
    '(+) в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\(\+\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.88 Поиск псевдоколонок в чистом SQL (PlpCheck.DBI_SQL.PURE_SQL_PSEUDOCOL_UNSUPPORTED.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_PSEUDOCOL_UNSUPPORTED.п.1' as rule_code,
    'HIGH' as priority,
    'Псевдоколонки в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(ROWID|ORA_ROWSCN|OBJECT_ID|OBJECT_VALUE|XMLDATA)\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.89 Поиск оконных функций Oracle в чистом SQL (PlpCheck.DBI_SQL.PURE_SQL_SELECTANALYTICARGUMENT.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_SELECTANALYTICARGUMENT.п.1' as rule_code,
    'HIGH' as priority,
    'Оконные функции Oracle в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'KEEP\s+DENSE_RANK|WITHIN\s+GROUP|IGNORE\s+NULLS|RESPECT\s+NULLS|FROM\s+FIRST|FROM\s+LAST')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.90 Поиск SELECT FROM TABLE() в чистом SQL (PlpCheck.DBI_SQL.PURE_SQL_SELECT_FROM_ARRAY.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_SELECT_FROM_ARRAY.п.1' as rule_code,
    'HIGH' as priority,
    'SELECT FROM TABLE() в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*FROM\s+TABLE\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.91 Поиск запрещенных таблиц в SQL (PlpCheck.DBI_SQL.PURE_SQL_VIEW_IN_CONDITION.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_SQL_VIEW_IN_CONDITION.п.1' as rule_code,
    'HIGH' as priority,
    'Запрещенные таблицы в SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'VW_CRIT|VW_RPT|VW_SQL')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.92 Поиск UDF в чистом SQL (PlpCheck.DBI_SQL.PURE_UDF.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_UDF.п.1' as rule_code,
    'HIGH' as priority,
    'UDF в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*\w+\.\w+\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.93 Поиск XMLType в чистом SQL (PlpCheck.DBI_SQL.PURE_XMLTYPE_IN_SQL.п.1)
SELECT 
    'PlpCheck.DBI_SQL.PURE_XMLTYPE_IN_SQL.п.1' as rule_code,
    'HIGH' as priority,
    'XMLType в чистом SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'XMLTYPE\s*\(|XMLTYPE\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.94 Поиск кавычек в SQL (PlpCheck.DBI_SQL.QUOTING.п.1)
SELECT 
    'PlpCheck.DBI_SQL.QUOTING.п.1' as rule_code,
    'HIGH' as priority,
    'Имена таблиц без кавычек' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'Z#[A-Z_]+')
  AND line_text NOT LIKE '%"%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.95 Поиск WHEN OTHERS без raise (PlpCheck.STYLE.RAISE_IN_OTHERS.п.1)
SELECT 
    'PlpCheck.STYLE.RAISE_IN_OTHERS.п.1' as rule_code,
    'HIGH' as priority,
    'WHEN OTHERS без raise' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE UPPER(line_text) LIKE '%WHEN OTHERS%'
  AND UPPER(line_text) NOT LIKE '%RAISE%'
  AND UPPER(line_text) NOT LIKE '%ROLLBACK%'
  AND UPPER(line_text) NOT LIKE '%RETURN%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.96 Поиск перехода в OBJECT (PlpCheck.DBI.REFERENCED_TO_OBJECT.п.1)
SELECT 
    'PlpCheck.DBI.REFERENCED_TO_OBJECT.п.1' as rule_code,
    'MEDIUM' as priority,
    'Переход в OBJECT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'select.*\[REFERENCE\].*in.*::\[.*\]')
  AND line_text NOT LIKE '%cast_to%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.97 Поиск сравнения ссылок (PlpCheck.DBI.REFERENCE_COMPARISON.п.1)
SELECT 
    'PlpCheck.DBI.REFERENCE_COMPARISON.п.1' as rule_code,
    'HIGH' as priority,
    'Сравнение ссылок > или <' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+%id\s*[><]=?\s*\w+%id|\w+%id\s*[><]=?\s*\d+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.98 Поиск ссылки на класс без экземпляров (PlpCheck.JAVA_PLSQL.REF_NONTABLE.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.REF_NONTABLE.п.1' as rule_code,
    'MEDIUM' as priority,
    'Ссылка на класс без экземпляров' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'ref\s+\[(SUMMA|REQ_CLIENT|REFERENCE)\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.99 Поиск различий в регулярных выражениях (PlpCheck.DBI_JAVA.REGEXP_DIFF_IN_JAVA.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.REGEXP_DIFF_IN_JAVA.п.1' as rule_code,
    'MEDIUM' as priority,
    'Различия в регулярных выражениях' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'regexp_(replace|substr|instr|count|like)\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.100 Поиск отчетов в Веб-Навигаторе (PlpCheck.WEB.REPORT_METHODS_WEB.п.1)
SELECT 
    'PlpCheck.WEB.REPORT_METHODS_WEB.п.1' as rule_code,
    'LOW' as priority,
    'Операции типа Отчет' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\<Report\>')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.101 Поиск зарезервированного префикса (PlpCheck.STYLE.RESERVED_PREFIX.п.4.5)
SELECT 
    'PlpCheck.STYLE.RESERVED_PREFIX.п.4.5' as rule_code,
    'HIGH' as priority,
    'Зарезервированный префикс' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(v_|gv_|t_|gt|cur_|gcur_|ret_|p_|cn_|gcn_)\w+\s+\w+\s*[;(]')
  AND line_text NOT LIKE '%PRAGMA%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.102 Поиск ignite функций (PlpCheck.DBI.RESTRICTIONS_ON_IGNITE_FUNCTIONS.п.1)
SELECT 
    'PlpCheck.DBI.RESTRICTIONS_ON_IGNITE_FUNCTIONS.п.1' as rule_code,
    'HIGH' as priority,
    'Server-side функции в Ignite' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'to_number|convert|initcap|months_between|last_day|ratio_to_report|regexp_count|regexp_instr|regexp_substr|analytic')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.103 Поиск restrict_references (PlpCheck.JAVA_PLSQL.RESTRICT_REFERENCES_BAD_USE.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.RESTRICT_REFERENCES_BAD_USE.п.1' as rule_code,
    'MEDIUM' as priority,
    'restrict_references с обращениями к БД' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'PRAGMA\s+RESTRICT_REFERENCES.*WNDS.*RNDS')
  AND REGEXP_LIKE(line_text, 'SELECT|UPDATE|DELETE|INSERT')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.104 Поиск %rowid и %orascn (PlpCheck.DBI.ROWID.п.1)
SELECT 
    'PlpCheck.DBI.ROWID.п.1' as rule_code,
    'HIGH' as priority,
    'Использование %rowid/%orascn' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '%rowid|%orascn')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.105 Поиск идентификации по rowid (PlpCheck.DBI.ROWIDIDENTIFIEDTABLE.п.1)
SELECT 
    'PlpCheck.DBI.ROWIDIDENTIFIEDTABLE.п.1' as rule_code,
    'MEDIUM' as priority,
    'Идентификация ТБП по rowid' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'identified\s+by\s+rowid', 'i')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.106 Поиск rownum (PlpCheck.DBI.ROWNUM.п.1)
SELECT 
    'PlpCheck.DBI.ROWNUM.п.1' as rule_code,
    'HIGH' as priority,
    'Использование rownum' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\bROWNUM\b')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.107 Поиск %rowtype в глобальных переменных (PlpCheck.DBI_JAVA.ROWTYPE_DECLARED_PUBLIC.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.ROWTYPE_DECLARED_PUBLIC.п.1' as rule_code,
    'MEDIUM' as priority,
    '%rowtype в глобальных переменных' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'PUBLIC\s+\w+\s+\w+%rowtype')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.108 Поиск длины макроса &sp/&rb (PlpCheck.DBI_JAVA_PLSQL.SAVEPOINT_ROLLBACK_MACRO_PARAM_LENGTH.п.1)
SELECT 
    'PlpCheck.DBI_JAVA_PLSQL.SAVEPOINT_ROLLBACK_MACRO_PARAM_LENGTH.п.1' as rule_code,
    'MEDIUM' as priority,
    'Длина параметра &sp/&rb > 28' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '&sp\(''[^'']{29,}''\)|&rb\(''[^'']{29,}''\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.109 Поиск длины имени savepoint (PlpCheck.DBI_SQL.SAVEPOINT_ROLLBACK_NAME_LENGTH.п.1)
SELECT 
    'PlpCheck.DBI_SQL.SAVEPOINT_ROLLBACK_NAME_LENGTH.п.1' as rule_code,
    'MEDIUM' as priority,
    'Длина имени savepoint > 63' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'savepoint\s+\w{64,}|rollback\s+to\s+\w{64,}')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.110 Поиск прямых SAVEPOINT/ROLLBACK (PlpCheck.PLSQL_STYLE.SAVEPOINT_ROLLBACK_USAGE.п.1)
SELECT 
    'PlpCheck.PLSQL_STYLE.SAVEPOINT_ROLLBACK_USAGE.п.1' as rule_code,
    'HIGH' as priority,
    'Прямой SAVEPOINT/ROLLBACK' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(UPPER(line_text), '\bSAVEPOINT\s+\w+\b')
   OR REGEXP_LIKE(UPPER(line_text), '\bROLLBACK\s+TO\s+SAVEPOINT\s+\w+\b'))
  AND UPPER(line_text) NOT LIKE '%&SP(%'
  AND UPPER(line_text) NOT LIKE '%&RB(%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.111 Поиск DDL без схемы (PlpCheck.DBI.SCHEMA_IN_DDL.п.1)
SELECT 
    'PlpCheck.DBI.SCHEMA_IN_DDL.п.1' as rule_code,
    'HIGH' as priority,
    'DDL без схемы' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '\b(CREATE|ALTER|DROP|TRUNCATE)\s+(TABLE|INDEX|VIEW|SEQUENCE)\s+[A-Z#]+\b')
  AND UPPER(line_text) NOT LIKE '%APP\.%'
  AND UPPER(line_text) NOT LIKE '%IBS\.%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.112 Поиск оконных функций Oracle (PlpCheck.DBI.SELECTANALYTICARGUMENT.п.1)
SELECT 
    'PlpCheck.DBI.SELECTANALYTICARGUMENT.п.1' as rule_code,
    'HIGH' as priority,
    'Оконные функции Oracle' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'KEEP\s+DENSE_RANK|WITHIN\s+GROUP|IGNORE\s+NULLS|RESPECT\s+NULLS|FROM\s+FIRST|FROM\s+LAST')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.113 Поиск wait в SELECT FOR UPDATE (PlpCheck.DBI.SELECTLOCKWAIT.п.1)
SELECT 
    'PlpCheck.DBI.SELECTLOCKWAIT.п.1' as rule_code,
    'MEDIUM' as priority,
    'wait в SELECT FOR UPDATE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*FOR\s+UPDATE.*WAIT\s+\d+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.114 Поиск строк без размера (PlpCheck.JAVA_PLSQL.SIZELESS.п.4.17)
SELECT 
    'PlpCheck.JAVA_PLSQL.SIZELESS.п.4.17' as rule_code,
    'MEDIUM' as priority,
    'VARCHAR2/STRING без размера' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b\w+\s+(VARCHAR2|STRING|CHAR|RAW|BYTE)\s*[;(]')
  AND line_text NOT LIKE '%(%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.115 Поиск %size с 0 или null (PlpCheck.JAVA_PLSQL.SIZE_RESTRICTION.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.SIZE_RESTRICTION.п.1' as rule_code,
    'MEDIUM' as priority,
    '%size с 0 или null' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '%size\s*\(\s*(0|null)\s*\)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.116 Поиск не реализованных SQL функций (PlpCheck.DBI.SQL_FUNCTION_UNSUPPORTED.п.1)
SELECT 
    'PlpCheck.DBI.SQL_FUNCTION_UNSUPPORTED.п.1' as rule_code,
    'HIGH' as priority,
    'Не реализованные SQL функции' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'regexp_replace|next_day|sys_guid')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.117 Поиск строки как идентификатора ТБП (PlpCheck.STYLE.STRING_AS_CLASS.п.4.15)
SELECT 
    'PlpCheck.STYLE.STRING_AS_CLASS.п.4.15' as rule_code,
    'HIGH' as priority,
    'Строка как идентификатор ТБП' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '''[A-Z][A-Z0-9_#]+''\s*(%class|%id|%statename)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.118 Поиск функций без Java реализации (PlpCheck.DBI_JAVA.SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP.п.1' as rule_code,
    'HIGH' as priority,
    'Функции без Java реализации' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'dbms_|utl_|utils\.regexp_|stdio\.zip|stdio\.run')
  AND line_text NOT LIKE '%RUNTIME%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.119 Поиск exit в цикле без fetch (PlpCheck.DBI.SUBOPTIMAL_QUERY_WROWNUM.п.1)
SELECT 
    'PlpCheck.DBI.SUBOPTIMAL_QUERY_WROWNUM.п.1' as rule_code,
    'HIGH' as priority,
    'exit в цикле без fetch' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\(.*SELECT.*\)\s+LOOP.*EXIT')
  AND line_text NOT LIKE '%FETCH%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.120 Поиск разыменования в курсорах (PlpCheck.PLSQL.SUBOPTIMAL_UNSELECTED_COL_USAGE.п.1)
SELECT 
    'PlpCheck.PLSQL.SUBOPTIMAL_UNSELECTED_COL_USAGE.п.1' as rule_code,
    'HIGH' as priority,
    'Разыменование в курсорах' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FOR\s+\w+\s+IN\s+.*?\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.121 Поиск синтаксических ошибок (PlpCheck.DBI_JAVA_PLSQL.SYNTAX_ERROR.п.1)
SELECT 
    'PlpCheck.DBI_JAVA_PLSQL.SYNTAX_ERROR.п.1' as rule_code,
    'HIGH' as priority,
    'Синтаксические ошибки' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'ERROR|invalid|unexpected|missing')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.122 Поиск системных представлений (PlpCheck.DBI.SYSTEM_VIEWS.п.1)
SELECT 
    'PlpCheck.DBI.SYSTEM_VIEWS.п.1' as rule_code,
    'HIGH' as priority,
    'Запрещенные системные представления' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(UPPER(line_text), '(V\$|GV\$|AQ\$|DBA_|USER_|ALL_|NLS_|MGW_)')
  AND line_text NOT LIKE '%VW_DB_SESSION%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.123 Поиск THIS в DEFAULT (PlpCheck.JAVA_PLSQL.THIS_IN_DEFAULT.п.1)
SELECT 
    'PlpCheck.JAVA_PLSQL.THIS_IN_DEFAULT.п.1' as rule_code,
    'MEDIUM' as priority,
    'THIS в DEFAULT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'var\s+\w+\s+\w+\s*:=\s*THIS\.')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.124 Поиск тривиальных обработчиков (PlpCheck.STYLE.TRIVIAL_EXCEPTION_HANDLER.п.1)
SELECT 
    'PlpCheck.STYLE.TRIVIAL_EXCEPTION_HANDLER.п.1' as rule_code,
    'MEDIUM' as priority,
    'Тривиальный обработчик исключений' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'WHEN\s+OTHERS\s+THEN\s+(debug_pipe|stdio\.put_line_buf|stdio\.put_line_pipe)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.125 Поиск UDF в SELECT (PlpCheck.DBI_JAVA_PLSQL.UDF.п.1)
SELECT 
    'PlpCheck.DBI_JAVA_PLSQL.UDF.п.1' as rule_code,
    'HIGH' as priority,
    'UDF в SELECT' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SELECT.*\w+\.\w+\s*\(')
  AND line_text NOT LIKE '%NVL%'
  AND line_text NOT LIKE '%DECODE%'
  AND line_text NOT LIKE '%CASE%'
  AND line_text NOT LIKE '%COALESCE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.126 Поиск UDF в формулах фильтров (PlpCheck.DBI.UDF_IN_FILTER_FORMULA.п.1)
SELECT 
    'PlpCheck.DBI.UDF_IN_FILTER_FORMULA.п.1' as rule_code,
    'HIGH' as priority,
    'UDF в формулах фильтров' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'FILTER.*\w+\.\w+\s*\(')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.127 Поиск UPDATE/DELETE по подзапросу (PlpCheck.DBI.UPDATE_DELETE_BY_SUBQUERY.п.1)
SELECT 
    'PlpCheck.DBI.UPDATE_DELETE_BY_SUBQUERY.п.1' as rule_code,
    'HIGH' as priority,
    'UPDATE/DELETE по подзапросу' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(UPDATE|DELETE)\s+\w+\s+IN\s+::\[.*\]\s+WHERE.*\w+\.\[\w+\]\.\[\w+\]')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.128 Поиск VARCHAR2 в верхнем регистре (PlpCheck.STYLE.UPPER_CASED_VARCHAR2.п.1)
SELECT 
    'PlpCheck.STYLE.UPPER_CASED_VARCHAR2.п.1' as rule_code,
    'LOW' as priority,
    'VARCHAR2/STRING в верхнем регистре' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\b(VARCHAR2|STRING)\b')
  AND line_text NOT LIKE '%PRAGMA%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.129 Поиск условных компиляций (PlpCheck.DBI.USER_IF_DEF.п.1)
SELECT 
    'PlpCheck.DBI.USER_IF_DEF.п.1' as rule_code,
    'MEDIUM' as priority,
    'Условные компиляции' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '--#IF|--#ELSE|--#ENDIF')
   OR REGEXP_LIKE(UPPER(line_text), 'IF_DEF\s*\(|PRAGMA\s+DEFINE'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.130 Поиск SQLCODE (PlpCheck.DBI.USESQLCODE.п.1)
SELECT 
    'PlpCheck.DBI.USESQLCODE.п.1' as rule_code,
    'HIGH' as priority,
    'Использование SQLCODE' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'SQLCODE')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.131 Поиск RIP объектов (PlpCheck.STYLE.USES_RIP_OBJECT.п.1)
SELECT 
    'PlpCheck.STYLE.USES_RIP_OBJECT.п.1' as rule_code,
    'LOW' as priority,
    'Объекты с RIP' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'RIP\.|RIP_')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.132 Поиск локальных объектов в расширении (PlpCheck.DBI_JAVA.USE_LOCAL_OBJECT_IN_EXTENSION.п.1)
SELECT 
    'PlpCheck.DBI_JAVA.USE_LOCAL_OBJECT_IN_EXTENSION.п.1' as rule_code,
    'MEDIUM' as priority,
    'Локальные объекты в расширении' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'instead\s+of')
  AND line_text NOT LIKE '%united:=true%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.133 Поиск дублирующихся DEFAULT блоков (PlpCheck.STYLE.VALIDATE_DEFAULT_TWICE.п.1)
SELECT 
    'PlpCheck.STYLE.VALIDATE_DEFAULT_TWICE.п.1' as rule_code,
    'LOW' as priority,
    'Дублирующиеся DEFAULT блоки' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'if\s+p_message\s*=\s*''DEFAULT''')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.134 Поиск else для p_message (PlpCheck.STYLE.VALIDATE_ELSE_INFO.п.1)
SELECT 
    'PlpCheck.STYLE.VALIDATE_ELSE_INFO.п.1' as rule_code,
    'LOW' as priority,
    'else для p_message/p_info' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'if\s+(p_message|p_info)\s*=\s*.*?else\s+')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.135 Поиск дублирования имен (PlpCheck.STYLE.VARIABLE_SAME_NAME.п.1)
SELECT 
    'PlpCheck.STYLE.VARIABLE_SAME_NAME.п.1' as rule_code,
    'MEDIUM' as priority,
    'Дублирование имен' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '(declare|type|function|procedure|var|for)\s+(\w+)')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.136 Поиск ошибок линкинга VBS (PlpCheck.WEB.VBS_LINKING_ERROR.п.1)
SELECT 
    'PlpCheck.WEB.VBS_LINKING_ERROR.п.1' as rule_code,
    'MEDIUM' as priority,
    'Ошибки линкинга VBS' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'VBScript|VBS')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.137 Поиск переопределения размерности в WITH (PlpCheck.DBI.VERIFY_TYPE_IN_WITH.п.1)
SELECT 
    'PlpCheck.DBI.VERIFY_TYPE_IN_WITH.п.1' as rule_code,
    'HIGH' as priority,
    'Переопределение размерности в WITH' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'WITH\s+RECURSIVE.*UNION\s+ALL')
  AND line_text NOT LIKE '%COALESCE%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.138 Поиск не реализованных конструкций VBS (PlpCheck.WEB.WEB_NOT_IMPLEMENTED.п.1)
SELECT 
    'PlpCheck.WEB.WEB_NOT_IMPLEMENTED.п.1' as rule_code,
    'MEDIUM' as priority,
    'Не реализованные конструкции VBS' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'CreateObject')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.139 Поиск DownloadReport (PlpCheck.WEB.WEB_REPORT.п.1)
SELECT 
    'PlpCheck.WEB.WEB_REPORT.п.1' as rule_code,
    'LOW' as priority,
    'DownloadReport в Веб-Навигаторе' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'DownloadReport')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.140 Поиск WITH RECURSIVE по модели данных (PlpCheck.DBI.WITHRECURSIVEMODEL.п.1)
SELECT 
    'PlpCheck.DBI.WITHRECURSIVEMODEL.п.1' as rule_code,
    'HIGH' as priority,
    'WITH RECURSIVE по модели данных' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'WITH\s+RECURSIVE.*CLASSES|WITH\s+RECURSIVE.*CLASS_ATTRIBUTES|WITH\s+RECURSIVE.*METHODS')
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.141 Поиск обращения к реквизиту без [] (PlpCheck.STYLE.WRONG_ATTR_SYNTAX.п.4.13)
SELECT 
    'PlpCheck.STYLE.WRONG_ATTR_SYNTAX.п.4.13' as rule_code,
    'HIGH' as priority,
    'Обращение к реквизиту без []' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '\w+\.([A-Z][A-Z0-9_#]+)')
  AND line_text NOT LIKE '%.[%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.142 Поиск обращения к классу без ::[] (PlpCheck.STYLE.WRONG_CLASS_SYNTAX.п.4.12)
SELECT 
    'PlpCheck.STYLE.WRONG_CLASS_SYNTAX.п.4.12' as rule_code,
    'HIGH' as priority,
    'Обращение к классу без ::[]' as description,
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

-- 8.143 Поиск локального объекта без префикса (PlpCheck.STYLE.WRONG_LOCAL_PREFIX.п.1)
SELECT 
    'PlpCheck.STYLE.WRONG_LOCAL_PREFIX.п.1' as rule_code,
    'MEDIUM' as priority,
    'Локальный объект без префикса' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'class\s+[A-Z][A-Z0-9_]+|view\s+VW_[A-Z][A-Z0-9_]+')
  AND UPPER(line_text) NOT LIKE '%VND_%'
  AND UPPER(line_text) NOT LIKE '%FTC_%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.144 Поиск обращения к методу без ::[] (PlpCheck.STYLE.WRONG_METHOD_SYNTAX.п.4.14)
SELECT 
    'PlpCheck.STYLE.WRONG_METHOD_SYNTAX.п.4.14' as rule_code,
    'HIGH' as priority,
    'Обращение к методу без ::[]' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, '[A-Z][A-Z0-9_#]+\.([a-z][a-zA-Z0-9_#]+)\s*\(')
  AND line_text NOT LIKE '%::%'
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.145 Поиск ссылки без ref [] (PlpCheck.STYLE.WRONG_REF_SYNTAX.п.1)
SELECT 
    'PlpCheck.STYLE.WRONG_REF_SYNTAX.п.1' as rule_code,
    'MEDIUM' as priority,
    'Ссылка без ref []' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE (REGEXP_LIKE(line_text, '::\[[A-Z][A-Z0-9_#]+\]\s+\w+\s*;')
   OR REGEXP_LIKE(line_text, 'ref\s+([A-Z][A-Z0-9_#]+)'))
  AND line_text NOT LIKE '--%'
UNION ALL

-- 8.146 Поиск XMLType в SQL (PlpCheck.DBI.XMLTYPE_IN_SQL.п.1)
SELECT 
    'PlpCheck.DBI.XMLTYPE_IN_SQL.п.1' as rule_code,
    'HIGH' as priority,
    'XMLType в SQL' as description,
    file_name,
    line_number,
    line_text
FROM plplus_code_source
WHERE REGEXP_LIKE(line_text, 'XMLTYPE\s*\(|XMLTYPE\.')
  AND line_text NOT LIKE '--%'
UNION ALL


-- ============================================================================
-- Сортировка результатов
-- ============================================================================
ORDER BY priority, rule_code, file_name, line_number;