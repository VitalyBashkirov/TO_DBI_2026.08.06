# DS_072a — Реализация: transform для группы A (11 правил)

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** высокий
**Зависит от:** DS_071
**Блокирует:** DS_072b

**См.:** `DS_STANDARD.md` (раздел 5 — шаблон реализации, раздел 2 — ограничения), `DS_CONTEXT.md` (§2.1, §6, §7), `DS_FILES.md` (§6), `EXCHANGE\OUTBOX\DS_071_report.md` (§7.2, §7.3, §7.5).

---

## 1. Цель

Добавить **детерминированный `transform`** (автофикс) для 11 правил категории A (простой transform, одна строка) из DS_071 §7.3.

| # | NAME | Замена (было → стало) |
|---|------|-----------------------|
| 1 | `CALL_STACK_ANALYSIS` | `utils.call_stack` → `utils.call_stack(32000)`; `utils.error_stack` → `utils.error_stack(true, 32000)` |
| 2 | `DIRECT_COMPARISON_WITH_NULL` | `x = ''` → `x is null`; `x != ''` / `x <> ''` → `x is not null` |
| 3 | `DYNAMIC_PLP` | `rownum < 2` → `fetch 1` (в `PLP_N(...)`) |
| 4 | `FUNCTION_BREAK_INDEX` | `substr(col,1,n)='v'` → `col like 'v%'` |
| 5 | `MAX_SIZE_ID` | `idobj [NUM10] := x%id` → тип `number` |
| 6 | `NVL_IN_SELECT` | `nvl(a, f()/подзапрос)` → `coalesce(a, f()/подзапрос)` |
| 7 | `PARALLEL_EXECUTION` | `pragma hint('PARALLEL (N)')` → удалить строку |
| 8 | `PLATFORM_INTEGER_MISMATCH` | `integer` → `number` (только там, где API ТЯ: `executor.lock_open`, `rtl.userid`, `sys_context('IBS_SYSTEM','ID')` и т.п.) |
| 9 | `REF_NONTABLE` | `ref [X]` → `[X]` (только для классов без экземпляров — `[SUMMA]`, `[REQ_CLIENT]`) |
| 10 | `SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP` | `dbms_transaction.commit` → `commit`; `dbms_utility.format_error_backtrace` → `::[RUNTIME].[UTILS].error_stack(false)`; `dbms_lock.sleep` → `::[RUNTIME].[UTILS].sleep` |
| 11 | `SYSTEM_VIEWS` | `gv$session` → `VW_DB_SESSION`; `v$session_longops` — оставить (разрешено) |

**Правила 1–4, 6–7, 9, 10, 11** — regex-замены `transform_type: "replace"`.
**Правило 5 (`MAX_SIZE_ID`)** — regex + **AI-фолбэк** (тип не всегда очевиден).
**Правило 8 (`PLATFORM_INTEGER_MISMATCH`)** — regex + **AI-фолбэк** (не каждое `integer` → `number`).

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Добавить `transform` для 11 NAME (`transform_type: "replace"`) |
| 2 | `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Синхронно (DS_065): `note` для 11 NAME + при необходимости regex-паттерн |
| 3 | `EXCHANGE\DS_CONTEXT.md` | §2.1, §9 — обновить (после закрытия DS_072a) |
| 4 | `EXCHANGE\DS_FILES.md` | §6 (таблица PARSER_SQL) + §9 (история) — обновить |

**Синхронность (DS_065):** правки regex — **в оба** JSON.

---

## 3. Детали реализации

### 3.1. Формат `transform`

По образцу DS_059/DS_063/DS_066. Пример:

```json
{
  "code": "PlpCheck.DBI.ADAPTATION.CALL_STACK_ANALYSIS.п.X.Y",
  "transform_type": "replace",
  "transform": {
    "pattern": "\\butils\\.call_stack\\b(?!\\s*\\()",
    "replacement": "utils.call_stack(32000)",
    "flags": "g"
  },
  "note": "call_stack без параметра → call_stack(32000); error_stack → error_stack(true, 32000)"
}
Точный формат transform — брать по эталонам:

BAD_PREFIX (DS_063);

CODE_IN_COMMENT (DS_066);

PREFIX_TYPE_IN_VAR_NAME (DS_066);

WRONG_METHOD_SYNTAX (DS_065).

3.2. AI-фолбэк
Для правил 5 и 8 — где regex не даёт однозначной замены:

Правило	Когда AI
MAX_SIZE_ID	Если тип не NUM10/NUM*/STRING_* — AI
PLATFORM_INTEGER_MISMATCH	Если API не из фиксированного списка — AI
Механизм AI-фолбэка — существующий (SRC\ai_exchange.py, DS_054). В scan_VVxVVx_* — пометка [AI] (DS_067).

3.3. По каждому правилу
CALL_STACK_ANALYSIS

Паттерн: \butils\.(call_stack|error_stack)\b(?!\s*\()

Замена:

utils.call_stack → utils.call_stack(32000)

utils.error_stack → utils.error_stack(true, 32000)

Исключение: если уже есть (...) — не трогать.

DIRECT_COMPARISON_WITH_NULL

Паттерн: (=|!=|<>)\s*'' и ''\s*(=|!=|<>)

Замена:

= '' → is null

!= '' → is not null

<> '' → is not null

Исключение: литералы 'x' — не трогать.

DYNAMIC_PLP

Паттерн: внутри ::[RUNTIME].[PLP].PLP_N('...') — rownum\s*<\s*\d+

Замена: rownum < N → fetch N

Только в строковом литерале PLP_N.

FUNCTION_BREAK_INDEX

Паттерн: substr\((\w+),\s*1,\s*(\d+)\)\s*=\s*'([^']*)'

Замена: col like 'v%' (первый символ + %)

Ограничение: только = и один символ.

MAX_SIZE_ID (+AI-фолбэк)

Паттерн: (\w+)\s+\[NUM(\d+)\]\s*:=\s*\w+%id

Замена: [NUM10] → number (если %id)

AI: если тип [STRING_*] или [NUM*] не мал.

NVL_IN_SELECT (+AI-нет, только regex)

Паттерн: nvl\(([^,]+),\s*(\w+\s*\(|[^(]+\(SELECT)

Замена: nvl( → coalesce(

Только если второй параметр — функция или подзапрос.

PARALLEL_EXECUTION

Паттерн: pragma\s+hint\s*\(\s*'PARALLEL\s*\(\d+\)'\s*\)\s*;?

Замена: удалить строку (оставить пустую).

PLATFORM_INTEGER_MISMATCH (+AI-фолбэк)

Паттерн: (\w+)\s+integer\b перед := с executor.lock_open, rtl.userid, sys_context('IBS_SYSTEM','ID')

Замена: integer → number

AI: если API не из списка.

REF_NONTABLE

Паттерн: ref\s+\[(SUMMA|REQ_CLIENT|R2_LOAN_REF|...)\]

Замена: ref [X] → [X]

Список классов — из PLPCHECK_RULE_TO_CATEGORY / настроек.

SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP

Паттерны:

dbms_transaction\.commit → commit

dbms_utility\.format_error_backtrace → ::[RUNTIME].[UTILS].error_stack(false)

dbms_lock\.sleep → ::[RUNTIME].[UTILS].sleep

Остальные dbms_*/utl_* — AI (DS_071 §7.2).

SYSTEM_VIEWS

Паттерн: \bgv\$session\b

Замена: VW_DB_SESSION

Исключение: v$session_longops — разрешено (не трогать).

4. Тесты
Файл: temp\test_ds072a.py. По кейсу на каждое правило:

#	NAME	Вход	Выход
1	CALL_STACK_ANALYSIS	instr(utils.call_stack, 'X')	instr(utils.call_stack(32000), 'X')
2	DIRECT_COMPARISON_WITH_NULL	if s = '' then	if s is null then
3	DYNAMIC_PLP	PLP_N('... rownum < 2 ...')	PLP_N('... fetch 1 ...')
4	FUNCTION_BREAK_INDEX	substr(col,1,5)='40817'	col like '40817%'
5	MAX_SIZE_ID	idobj [NUM10] := ref%id	idobj number := ref%id
6	NVL_IN_SELECT	nvl(a, f())	coalesce(a, f())
7	PARALLEL_EXECUTION	pragma hint('PARALLEL (8)');	(удалено)
8	PLATFORM_INTEGER_MISMATCH	sl integer; sl := executor.lock_open;	sl number; sl := executor.lock_open;
9	REF_NONTABLE	vSumma ref [SUMMA];	vSumma [SUMMA];
10	SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP	dbms_transaction.commit;	commit;
11	SYSTEM_VIEWS	in gv$session%rowtype	in VW_DB_SESSION%rowtype
Регресс: DS_032–DS_071.

5. Прогнать регресс
Все тесты DS_032–DS_071 PASSED.

6. Отчёт
Стандартный (DS_STANDARD.md → раздел 3). Дополнительно:

§6. До/после — примеры для 11 правил.

§7. Актуализация тестов — если регресс-тесты DS_070/DS_071 требуют правок.

7. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

KODA не создаёт в EXCHANGE\ новых каталогов, кроме регламентированных (INBOX, OUTBOX, PROCESSED, bot.log). Логирование — только в EXCHANGE\bot.log по DS_050 ([ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <итог>.).

Запись в temp\ — разрешена (артефакты, тесты, скрипты).

DATA\ — строго read-only (кроме случаев явного разрешения в DS). В DS_072a — разрешено править 5.RUBRICATOR_PARSER_SQL v5.json и 4.RUBRICATOR_PROMPT v5.json.

Синхронизация regex — в оба JSON (DS_065).

Не трогать scanner.py, code_fixer.py, gui_app.py (это уровень рубрикаторов, не кода).

Если при реализации выявится расхождение с DS_071 §7.2 — остановиться, доложить автору DS.

8. Артефакты
EXCHANGE\OUTBOX\DS_072a_report.md

temp\test_ds072a.py

temp\ds072a_run.py

DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json (обновлён)

DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json (обновлён)

EXCHANGE\DS_CONTEXT.md (v2.2)

EXCHANGE\DS_FILES.md (v1.4)