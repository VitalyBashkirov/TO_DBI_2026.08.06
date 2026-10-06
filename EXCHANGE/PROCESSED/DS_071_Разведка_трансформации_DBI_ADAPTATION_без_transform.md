# DS_071 — Разведка: трансформации DBI.ADAPTATION без transform

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** разведка
**Приоритет:** высокий
**Зависит от:** DS_070
**Блокирует:** DS_072+

**См.:** `DS_STANDARD.md` (раздел 4 — шаблон разведки, раздел 2 — ограничения), `DS_CONTEXT.md` (§2.2, §6), `DS_FILES.md` (§2, §5, §6), `EXCHANGE\OUTBOX\DS_070_report.md` (§7.2, §7.3, §7.5).

---

## 1. Цель

По итогам DS_070 §7.5: **74 правила** в `DBI.ADAPTATION` не имеют детерминированного `transform` в `5.RUBRICATOR_PARSER_SQL v5.json` (сканируются, но не автофиксятся).

Определить по каждому NAME:

1. Возможен ли **детерминированный** `transform` (regex-замена / структурная замена).
2. Что мешает, если невозможен (многострочность, семантика, контекст, отсутствие однозначной замены).
3. Предлагаемый подход: `transform` / `ignore` / AI-фикс / ручной фикс.
4. Подгруппа для реализации (DS_072a, DS_072b, …).

Разведка — **без правок исходников и рубрикаторов**.

---

## 2. Что искать

### 2.1. Источник списка — 74 NAME

Из `EXCHANGE\OUTBOX\DS_070_report.md` §7.2 — фильтр:

- колонка `RULE_TO_CAT` = `DBI.ADAPTATION`,
- колонка `TRANSFORM` = `НЕТ`.

Ожидаемый список (сверить с отчётом DS_070):

```text
ACCESS_STATIC, ANALYTIC_AND_FETCH_BAD_USE, CALL_STACK_ANALYSIS, CARTESIAN_JOIN,
COLUMNS_LIMIT_EXCEEDED, COMPILE_MISSING_COND, CONCAT_CONTROL, COND_COMPILE_COMMENT,
CONTROLTABLECOLUMNSTYPE, CONV_STREAM_CHECKS, DEREFERENCE_IN_LOOP,
DIRECT_COMPARISON_WITH_NULL, DYNAMIC_PLP, EMPTY_STRING_IN_CURSOR,
FETCH_OVER_SUBQUERY, FORM_TRANSACT_CONTROL, FULL_INDEX_SCAN, FULL_TABLE_SCAN,
FUNCTION_BREAK_INDEX, FUNC_ATTR_DEREFERENCE, HINT_INDEX_ORDER_BY, INDEX_CAN_USE_BETTER,
INDEX_LENGTH, INSERT_PLSQL, INSERT_WITH_ID, INTERVAL_NOT_SELECT, INVALID_INIT,
MACROEXECUTEPROCESS, MACROEXECUTEPROCESS_COMMENT, MACRO_CALL_EXECUTEPROCESS,
MANY_SUB_TRANSACTIONS, MATCHING_TYPES, MAX_SIZE_ID, MULTIPLE_MODIFIERS,
NATIVE_ID_OBJ_IDENTIFIER, NESTED_TABLE, NOT_CLASS_REF_TABLE_PARAM, NOT_CLOSED_CURSOR,
NOT_CLOSED_FILE, NOT_HANDLED_CURSOR_EXCEPTIONS, NVL_IN_SELECT, OBLIGATORY_IN_OTHERS,
OUTER_JOIN, PARALLEL_EXECUTION, PARTITION_ALL, PLATFORM_INTEGER_MISMATCH,
REFERENCED_TO_OBJECT, REF_NONTABLE, REGEXP_DIFF_IN_JAVA, RESTRICTIONS_ON_IGNITE_FUNCTIONS,
RESTRICT_REFERENCES_BAD_USE, ROWID, ROWIDIDENTIFIEDTABLE, ROWTYPE_DECLARED_PUBLIC,
SAVEPOINT_ROLLBACK_MACRO_PARAM_LENGTH, SAVEPOINT_ROLLBACK_NAME_LENGTH,
SELECTANALYTICARGUMENT, SELECTLOCKWAIT, SIZE_RESTRICTION, SQL_FUNCTION_UNSUPPORTED,
SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP, SUBOPTIMAL_QUERY_WROWNUM,
SUBOPTIMAL_UNSELECTED_COL_USAGE, SYSTEM_VIEWS, UDF, UDF_IN_FILTER_FORMULA,
USE_LOCAL_OBJECT_IN_EXTENSION, USESQLCODE, VERIFY_TYPE_IN_WITH, WITHRECURSIVEMODEL
Точный список брать из DS_070 §7.2 — здесь ориентир.

2.2. Источники для анализа
Что	Где
Семантика правила	DATA\CFT Platform IDE Documentation\ide_dbi_project\20260922\rule-description-11310065634873899272.html (PlpCheck 2.5.2)
Метод проверки	html → <div class="method-block">
Пример ошибки / исправления	html → <div class="code-comparison">
Текущий паттерн (regex)	DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json
Текущий note	там же
transform (если есть)	DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json
Примеры transform (эталоны)	BAD_PREFIX, CODE_IN_COMMENT, PREFIX_TYPE_IN_VAR_NAME, WRONG_METHOD_SYNTAX — имеют transform
Логика сканера	SRC\analyzer\scanner.py — как паттерн попадает в Issue
Логика фиксера	SRC\fixer\code_fixer.py — _apply_issue_fixes, _generate_plan
AI-обмен	SRC\ai_exchange.py
2.3. Что собрать по каждому NAME
#	Поле	Как получить
1	NAME	из DS_070 §7.2
2	Метод проверки (кратко)	html → method-block
3	Пример ошибки → исправления	html → code-comparison
4	Текущий паттерн (regex)	4.RUBRICATOR_PROMPT
5	Возможен ли transform	анализ: однозначна ли замена
6	Что мешает	многострочность / семантика / контекст / нет
7	Подход	transform / ignore / AI / ручной
8	Подгруппа	A / B / C / … (по типу)
9	Приоритет	высокий / средний / низкий
3. Воспроизвести
#	Что	Как
1	Взять список 74 NAME	DS_070 §7.2, фильтр RULE_TO_CAT = DBI.ADAPTATION и TRANSFORM = НЕТ
2	Для каждого NAME — html	парсить 20260922\rule-description-11310065634873899272.html, извлечь method-block + code-comparison
3	Текущий паттерн	grep_search по plpcheck.<NAME> в 4.RUBRICATOR_PROMPT v5.json
4	Примеры transform	из 5.RUBRICATOR_PARSER_SQL v5.json — эталоны (BAD_PREFIX, CODE_IN_COMMENT, PREFIX_TYPE_IN_VAR_NAME, WRONG_METHOD_SYNTAX)
5	Классификация	по критериям §4
6	Сводная таблица	temp\ds071_dbi_adaptation_audit.csv + .json
Чтение html — только:

powershell
Get-Content -Raw -Encoding UTF8 "<путь>"
# или
[System.IO.File]::ReadAllText("<путь>", [System.Text.Encoding]::UTF8)
Запись — только в temp\.

4. Критерии классификации
4.1. Возможен ли transform
Категория	Признак
A. Простой transform	Однозначная regex-замена, одна строка, без контекста. Пример: P_PARAM ref → v_rParam.
B. Структурный transform	Замена в пределах строки, но с контекстом (regex + lookahead/lookbehind, замена фрагмента). Пример: WRONG_METHOD_SYNTAX — [str].[get](...) → ::[str].[get](...).
C. Многострочный transform	Требует анализа нескольких строк (курсор, begin/end, цикл). Пример: ACCESS_STATIC.
D. Семантический	Требует понимания модели/типов (например, MATCHING_TYPES, COLUMNS_LIMIT_EXCEEDED).
E. Нет замены	Правило-детектор (запрет): INSERT_PLSQL, PARALLEL_EXECUTION, ROWNUM — только пометить, заменить нечем.
F. ignore	Уже ignore по семантике (multi-line rename risk, DS_059_F/DS_063) — оставить.
4.2. Приоритет
Приоритет	Критерий
Высокий	Категория A или B — можно сделать transform быстро, DBI-критично
Средний	Категория C или D — transform возможен, но сложнее
Низкий	Категория E или F — оставить ignore / AI
5. Зафиксировать
Факты — для каждого NAME: путь, строки, html-фрагмент, паттерн, note.

Diff — если что-то менялось (не должно).

MD5 — html-источника, 4.RUBRICATOR_PROMPT, 5.RUBRICATOR_PARSER_SQL (сверить с DS_070 §7.1).

Артефакты — temp\ds071_dbi_adaptation_audit.csv, temp\ds071_dbi_adaptation_audit.json.

6. Восстановить
Разведка read-only. Если что-то менялось — восстановить.

7. Отчёт
Стандартный (DS_STANDARD.md → раздел 3) + дополнительные разделы:

7.1. Источник и сводка
Источник html: <путь> MD5: <md5>
4.RUBRICATOR_PROMPT: MD5 <md5> 5.RUBRICATOR_PARSER_SQL: MD5 <md5>

Метрика	Значение
Всего NAME в списке (DS_070 §7.2)	74
Категория A (простой transform)	N
Категория B (структурный transform)	N
Категория C (многострочный)	N
Категория D (семантический)	N
Категория E (нет замены)	N
Категория F (ignore)	N
7.2. Таблица по каждому NAME
NAME	Метод (кратко)	Пример ошибки → исправления	Паттерн (текущий)	Возможен transform	Что мешает	Категория	Подгруппа	Приоритет
…	…	…	…	да/нет	…	A/B/C/D/E/F	…	…
7.3. Группы по категории
A (простой transform) — список NAME.
B (структурный) — список NAME.
C (многострочный) — список NAME.
D (семантический) — список NAME.
E (нет замены) — список NAME.
F (ignore) — список NAME.

7.4. Группы по приоритету
Высокий — список NAME (A + B).

Средний — список NAME (C + D).

Низкий — список NAME (E + F).

7.5. Предлагаемые DS_072+
DS	Содержание	NAME
DS_072a	Реализация transform: группа A	…
DS_072b	Реализация transform: группа B	…
DS_072c	Реализация transform: группа C	…
DS_072d	Реализация transform: группа D	…
7.6. Рекомендация
Один абзац: с чего начать (какая подгруппа), что оставить ignore/AI.

7.7. Прочее
Если источник html — 152 правила (не 284) — зафиксировать.

Сверить MD5 рубрикаторов с DS_070 §7.1 — расхождений быть не должно.

8. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

DATA\ — строго read-only. Любая запись — только в temp\.
Запрещено по путям DATA\*: Set-Content, Out-File, Remove-Item,
Move-Item, New-Item, Copy-Item (в DATA\).

Исходный html читать только через Get-Content -Raw -Encoding UTF8
или [System.IO.File]::ReadAllText(...).

Рубрикаторы (4.RUBRICATOR_PROMPT v5.json, 5.RUBRICATOR_PARSER_SQL v5.json) не менять.

Временные файлы — только в temp\.

Если при разведке выявится расхождение с DS_CONTEXT.md §2.2 / §6 или с DS_070 §7.2 — доложить автору DS.

Не выдумывать transform — только фиксировать возможность/невозможность (реализация — в DS_072+).

9. Артефакты
EXCHANGE\OUTBOX\DS_071_report.md

temp\ds071_dbi_adaptation_audit.csv

temp\ds071_dbi_adaptation_audit.json

temp\ds071_run.py