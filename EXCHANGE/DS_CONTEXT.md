# DS_CONTEXT — Общий контекст проекта

**Назначение:** факты, которые используются в нескольких DS. Ссылаться вместо повторения в каждой задаче.

**Версия:** 2.9 от 25.09.2026 (после DS_063–DS_067 + Уточнения, DS_072a–DS_072e, DS_073, DS_075, DS_076).

---

## 1. Вендорские эталоны

### 1.1. `_is_in_comment_or_string` — эталон отсутствует

Проверенные источники:

- `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` — только коды проверок.
- `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` — 87 правил трансформации, алгоритма нет.
- `DATA\CFT Platform IDE Documentation\Программирование_PLPlus_Материалы_курса.doc` — «`--` до конца строки; `/* */` между символами».
- `DATA\CFT Platform IDE Documentation\rule-description.html` (PlpCheck 2.5.2) — требование «не анализировать код в комментариях», алгоритма нет.
- `DATA\CFT Platform IDE Documentation\Рекомендации по адаптации...v53.docx` — `&` — макрос; `"` внутри `'...'` — не терминатор.
- `DATA\CFT Platform IDE Documentation\тклоик20240828...docx` — стиль кода.
- `DATA\CFT Platform IDE Documentation\CFT Platform IDE. Приложения 2.3.docx` — грамматика `str ::= 'character_sequence'` не описывает `''` и q-quoting.

**Вывод:** алгоритм — собственный, на основе синтаксиса PL/SQL/PLPlus и поведения PlpCheck.
**Детали:** `EXCHANGE\OUTBOX\DS_056_report.md`, `DS_056A` (закрыт).

### 1.2. `&debug(...)` — макро-подстановка

- Не SQL*Plus-переменная.
- После раскрытия — обычный вызов процедуры.
- Переменные внутри `'...'` — литералы; спец-обработка только `PLPlusFixer._update_renamed_vars` (см. `DOCUMENTATION_ARM.md` 212, 246).

---

## 2. Структура рубрикатора

### 2.1. Файлы

| Файл | Назначение | Правил |
|------|-----------|--------|
| `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Правила проверок v5.3.0 **+ источник 309 regex-паттернов сканера** | 332 |
| `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Парсер (трансформации `transform`) | 85 |
| `DATA\Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил с признаками | — |
| `DATA\CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2 | — |

**Примечание (21.09.2026):**

- `4.RUBRICATOR_PROMPT v5.json` — **источник** regex-паттернов **для сканера** (309 паттернов). `5.RUBRICATOR_PARSER_SQL v5.json` — **источник** трансформаций (`transform`). Правки regex **должны** вноситься **в оба** файла (DS_065).
- После `DS_059_Уточнение_D/E` в `5.RUBRICATOR_PARSER_SQL v5.json` **добавлены** паттерны: `bad_prefix_varchar2`, `bad_prefix_number`, `bad_prefix_date`, `bad_prefix_boolean`; `wrong_method_syntax_bracket`.
- После `DS_065` — regex `SPEC_CHARS` **сужен** в **обоих** файлах.
- После `DS_066` — в `5.RUBRICATOR_PARSER_SQL v5.json` добавлен паттерн `p_local_prefix` в `PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4`; в **обоих** файлах уточнены `note` для `PREFIX_TYPE_IN_VAR_NAME` и `CODE_IN_COMMENT`.
- После `DS_072a` — в `5.RUBRICATOR_PARSER_SQL v5.json` добавлены **11 правил** `PlpCheck.DBI.<NAME>.п.1` (группа A из DS_071: CALL_STACK_ANALYSIS, DIRECT_COMPARISON_WITH_NULL, DYNAMIC_PLP, FUNCTION_BREAK_INDEX, MAX_SIZE_ID, NVL_IN_SELECT, PARALLEL_EXECUTION, PLATFORM_INTEGER_MISMATCH, REF_NONTABLE, SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP, SYSTEM_VIEWS) — паттерны `regex` с `transform` + 2 AI-фолбэк-паттерна (`max_size_id_other`, `platform_integer_mismatch_other`, bucket `ignore`); в `4.RUBRICATOR_PROMPT v5.json` синхронно обновлены `fix_instruction` для 11 NAME.
- После `DS_072a_Уточнение_A` — правило `PlpCheck.DBI.DYNAMIC_PLP.п.1` **удалено** из `5.RUBRICATOR_PARSER_SQL v5.json` (обобщение `rownum < N -> fetch N-1` синтаксически ломало SQL: `where fetch 1 into`). `DYNAMIC_PLP` возвращён в **детекторы** (вариант B, категория E DS_071 §7.3). Итого группа A: **10** правил с transform.
- После `DS_072a_Уточнение_B` — AI-фолбэк для `MAX_SIZE_ID` / `PLATFORM_INTEGER_MISMATCH` зафиксирован как **`transform_type: "ignore"`** (паттерны `max_size_id_other`, `platform_integer_mismatch_other`). Причина: `rule_engine._pattern_bucket` **не поддерживает `hybrid`** без реального `transform` (паттерн без transform -> всегда `ignore`). Попадание в AI-очередь — через **`needs_ai_fix`** (DS_054, флаг `ai_fallback`, `_verify_file`). `hybrid` как отдельная корзина не реализован (перенесено в DS_073+).
- После `DS_072b` — в `5.RUBRICATOR_PARSER_SQL v5.json` добавлены **5 правил** `PlpCheck.DBI.<NAME>.п.1` (группа B из DS_071 §7.3): **3 transform** (`transform_type: "regex"`, `replace_scope: "match"`) — `INSERT_WITH_ID`, `REFERENCED_TO_OBJECT`, `SELECTLOCKWAIT`; **2 ignore-детектора** — `ALIAS_COLUMN_VIEW`, `MULTIPLE_MODIFIERS` (требуют метаданных/типа, regex не даёт однозначной замены → исправление вручную, обоснование в отчёте §8). В `4.RUBRICATOR_PROMPT v5.json` синхронно (DS_065) обновлены `fix_instruction` для 5 NAME. Итого PARSER_SQL: **90** правил.
- После `DS_072b_Уточнение_A` — исправлен **`example_out`** метаданных `PlpCheck.DBI.INSERT_WITH_ID.п.1` в `5.RUBRICATOR_PARSER_SQL v5.json`: было ошибочное `txt_job_ref := insert into ...` (присваивание `:=` + `insert` — не PL/SQL), стало `insert into ... return t into txt_job_ref;` (без `X := `). **Сам `transform` менять не потребовалось**: `replace_scope: "match"` + regex `(\w+)\s*:=\s*::\[(\w+)\]%insert\((\w+),\s*\3%id\)` матчат **всю** конструкцию `obj := ::[TBP]%insert(obj, obj%id)` и заменяют её целиком (Вариант B брифа). Движок `apply_fix_ex` не поддерживает `replace_scope: "line"` (Вариант A): `apply_transform` использует плейсхолдеры `{1}/{2}`, спец-значения `"line"` нет (любое ≠ `"match"` → подстрочная замена первого span). `fix_instruction` в `4.RUBRICATOR_PROMPT v5.json` уже корректен (цель без `:=`) — синхронизация подтверждена, не изменён.
- После `DS_072c_Реализация` — группа C закрыта (19 NAME, разведка §7.3): **4 multiline-transform** (`NOT_CLOSED_CURSOR`, `NOT_CLOSED_FILE`, `NOT_HANDLED_CURSOR_EXCEPTIONS`, `OBLIGATORY_IN_OTHERS`; `replace_scope: "multiline"`) + **1 C1-fallback** (`OUTER_JOIN` — ignore: `{object_type}` движку неоткуда взять, бриф §3.1 fallback) + **3 C2-ignore** (`SUBOPTIMAL_UNSELECTED_COL_USAGE`, `FETCH_OVER_SUBQUERY`, `CRIT_EXT_IN_OLD_FORMAT` — структурные, «не ломать SQL») + **6 C3-ignore** (AI: `ACCESS_STATIC`, `DEREFERENCE_IN_LOOP`, `MANY_SUB_TRANSACTIONS`, `NESTED_TABLE`, `SUBOPTIMAL_QUERY_WROWNUM`, `UDF` — `needs_ai_fix`, DS_054) + **5 C4-ignore** (`CONCAT_CONTROL`, `CONV_STREAM_CHECKS`, `NOT_CLASS_REF_TABLE_PARAM`, `ROWTYPE_DECLARED_PUBLIC`, `USE_LOCAL_OBJECT_IN_EXTENSION`). **Движок**: `apply_fix_multiline` в `sql_parser.py` (DOTALL+MULTILINE, transform-плейсхолдеры `{N}`) + обёртка `RuleEngine.apply_fix_multiline`; построчный `apply_fix_ex` multiline-паттерны **пропускает** (интеграция в `code_fixer.py` — вне рамок DS_072c, он не трогался). Итого PARSER_SQL: **109** правил. AGENTS.md: правило «`bot.log` — только `EXCHANGE\bot.log`» (раздел «Логирование»).
- После `DS_073` — `apply_fix_multiline` **интегрирован в прод-фиксер**: `code_fixer.py:_apply_issue_fixes` применяет multiline-правила (`replace_scope: "multiline"`) **первым проходом** (до построчного `apply_fix`, бриф §3.4), окно — Вариант C (`Issue.block_start/block_end`, DS_069; fallback — весь файл), после успешной замены правило исключается из построчного прохода (идемпотентность §3.5). Заработали 4 multiline-правила C2 (`NOT_CLOSED_CURSOR`, `NOT_CLOSED_FILE`, `NOT_HANDLED_CURSOR_EXCEPTIONS`, `OBLIGATORY_IN_OTHERS`) в GUI-фиксе. Критерий multiline-правила — `replace_scope: "multiline"` в паттернах (bucket не различает: transform → `regex`).
- После `DS_072d_Реализация` — группа D закрыта (15 NAME, разведка §7.3): **3 transform** (`MATCHING_TYPES` — varchar2-литерал→number; `SIZE_RESTRICTION` — `%size(0|null) OP 0|1` → `%size(1) OP N`; `INDEX_LENGTH` — `STRING_1000+` → `STRING_200`; все `replace_scope: "match"`) + **12 ignore** (fallback брифа «или ignore»: `CONTROLTABLECOLUMNSTYPE` — subtype семантичен; `HINT_INDEX_ORDER_BY` — колонки из хинта; `INVALID_INIT` — целевая форма неясна; D3 ×3 — модель/вендор good пуст; D4 ×6 — AI `needs_ai_fix`/детекторы). Итого PARSER_SQL: **124** правил. SRC не тронут (движок готов DS_072c/DS_073).
- После `DS_072e_Реализация` — группа E зафиксирована (24 NAME «нет замены»): все `transform_type: "ignore"`-детекторы (regex из PROMPT `for_search`), note по категориям брифа §4.2 (план запроса ×3, условная компиляция ×2, запрет DBI ×5, макросы ×3, savepoint ×2, идентификаторы ×1, SQL-функции ×2, regex ×1, UDF ×1, прочие ×4). PROMPT `fix_instruction` для 24 NAME синхронно. **PlpCheck-аудит DS_071 завершён: 74/74 NAME зафиксированы в PARSER_SQL** — 20 transform + 54 ignore/AI. Итого PARSER_SQL: **148** правил.

Число правил в файле — **условное** (отражает базовую версию до правок).

### 2.2. Префиксы `rule_code`

| Префикс | Источник |
|---------|----------|
| `v53.` | `4.RUBRICATOR_PROMPT v5.json` |
| `тдс20240828.` | `тдс20240828.Требования...` |
| `тклоик20240828.` | `тклоик20240828.Требования...` |
| `plpcheck.` | `rule-description.html` (PlpCheck 2.5.2) |

### 2.3. Формат `1.RUBRICATOR_FILES v5.md`

- Строки вида `|N|±|rule_code|...`.
- Признак `+` — включено, `−` (U+2212, **не** U+00B1) — выключено.
- **`1.RUBRICATOR_FILES v5.md` — read-only для GUI.** Состояние чекбоксов хранится в `settings.json`.

### 2.4. Категории PlpCheck (GUI)

| Категория | Правила | Примечание |
|-----------|---------|-----------|
| `PLSQL.OPTIMIZATION` | … | — |
| `JAVA.OPTIMIZATION` | … | — |
| `DBI.ADAPTATION` | … | — |
| `SQL.CHECKS` | … | — |
| `WEB.ADAPTATION` | … | — |
| `STYLE.PREFIXES` | `bad_prefix`, `not_mentioned` | `code_in_comment`, `wrong_method_syntax` **убраны** (DS_065) |
| `STYLE.PREFIX_COMBINATION` | `prefix_type_in_var_name` | — |
| **`STYLE.SYNTAX`** | `wrong_method_syntax` | **Новая категория (DS_065)**, «Синтаксис методов» |
| `OTHER` | `code_in_comment` + прочие | — |

**Маппинг** — в `SRC\analyzer\scanner.py`: `PLPCHECK_RULE_TO_CATEGORY`, `PLPCHECK_CATEGORIES`.

---

## 3. GUI

### 3.1. Ключевые факты (из DS_058-разведки)

- Пишет в рубрикатор: `_save_rubricator_state` (`SRC\gui_app.py:1889–1945`), вызывается из `save_settings()` (1887) по `on_close` (3845) или Ctrl+S.
- Клик по чекбоксу (`_on_rule_click`, 838–858) — только `rules_changed = True`.
- Чтение: `_load_rubricator_files` (765–791), используется в `_populate_rules_tree`.
- `settings.json` — ключ `rubricator_selected_rules` добавлен (DS_058+DS_057).
- `settings.json` — ключ `report_stats_min_files` (число, по умолчанию 10) — порог включения блока топ-файлов в отчёте/логе (DS_075). Парная настройка GUI — `report_stats_min_files_var`; в скан/фикс-конвейер передаётся в `generate_report()` и `save_scan_only_log()` вместе с `log_level`.

### 3.2. Схема `settings.json` (согласовано)

```json
{
  "rubricator_selected_rules": {
    "v53.rule_code_1": true,
    "тдс20240828.DML_JOIN.стр.1": true,
    "plpcheck.CODE_IN_COMMENT": false
  }
}
Формат: словарь {"<rule_code>": true|false}.

Идемпотентен.

Начальное состояние (нет ключа): прочитать 1.RUBRICATOR_FILES v5.md, сохранить в settings.json (вариант C).

Новые правила: дополнять со значением false, сохраняя существующие.

4. Соглашения по коду
Python — UTF-8 без BOM.

OUTBOX — CRLF.

bot.log — UTF-8 без BOM, формат [ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <итог>.

Стиль логов и отчётов — русский, формальный.

5. История ключевых решений
Дата	Решение	Обоснование
19.09.2026	DS_056B отменён	Вендорского эталона нет, все источники проверены
19.09.2026	DS_056A — разделение is_in_comment_or_string / advance_lexer_state	Многократный вызов для одной строки требует чистоты функции
19.09.2026	DS_058+DS_057 объединены	Одна область кода (gui_app.py)
19.09.2026	1.RUBRICATOR_FILES v5.md — read-only для GUI	Баг −→+; состояние в settings.json
19.09.2026	Бот exchange_bot.py отключён. Перенос файлов — вручную (DS_049).	Бот не запущен (нет процесса, автозапуска). KODA работает без него. Раздел DS_048 удалён из AGENTS.md.
20.09.2026	DS_059 — маппинг кодов PlpCheck (rule_engine.py:_resolve_code)	Сканер: plpcheck.<NAME>; PARSER_SQL: PlpCheck.<CAT>.<NAME>.п.<N>; 33/33 NAME уникальны
20.09.2026	DS_059_Уточнение_A — формат ERROR в scan_report_*	<описание>: "<исходный_фрагмент>", обрезка 50 символов + …
20.09.2026	DS_059_Уточнение_B — заголовок scan_VVxVVx_*	Переиспользование _generate_active_rubricators_lines() из сканера
20.09.2026	DS_059_Уточнение_D — восстановление формата scan_VVxVVx_*	Режим: сканирование (...), PLAN, блок «Прогноз:», статистика, блок «Правил в ignore»
20.09.2026	DS_059_Уточнение_E — безопасные правки	code_in_comment → ignore; bad_prefix_* разделены; vDateRep — не автофиксится; lookahead (?i) + исключение параметров in/out
20.09.2026	DS_054_Уточнение_C — кнопка «От AI» disabled при пустом AI_OUT	Таймер 5 сек; тултип динамический
20.09.2026	DS_059_Уточнение_F — PREFIX_TYPE_IN_VAR_NAME → ignore	Multi-line rename риск; параметры не автофиксятся
20.09.2026	DS_062 (разведка) — 89.6% дублей даёт SPEC_CHARS	regex [^A-Z0-9_#] матчит каждый спецсимвол
21.09.2026	DS_063 — bad_prefix_* → ignore	Multi-line rename риск; missing_prefix_* уже ignore с DS_059_F
21.09.2026	DS_064 — дедупликация issues в scanner.py	634 → 67 уникальных (SPEC_CHARS 89.6%)
21.09.2026	DS_064_Уточнение_A — ключ дедупа: (file, line, issue_type, description, match_fragment)	original_code = вся строка, не ERROR-фрагмент; поле match_fragment
21.09.2026	DS_065 — PLAN без example_out, SPEC_CHARS сужен, категории PlpCheck	SPEC: 350 → 2, ложных 207 → 0; STYLE.SYNTAX — новая категория; code_in_comment → OTHER
21.09.2026	DS_066 — PLAN > <действие>, соответствие PLAN между отчётами (вариант A), маркеры комментариев в ERROR, P_* локальные → v_<тип><CamelCase>, счётчик «Уникальных» удалён	Унификация отчётов, корректность match_fragment, семантика P_
21.09.2026	DS_067 — формат scan_VVxVVx_*: PLAN с колонкой LINE, «Прогноз» по всем строкам-мишеням, цепочка правил, единая позиция >, МКР = max(len(код_правила)) + 1	Унификация формата, читаемость, соответствие scan_report_*
21.09.2026	DS_067_Уточнение_A — приоритет удаления (одна delete-issue на строку), not_mentioned → (удалить объявление), обрыв цепочки удалён как отдельный механизм	Устранение дублей, согласование с scan_report_*
21.09.2026	DS_067_Уточнение_B — сортировка PLAN и цепочки внутри LINE по ключу scan_report_*: (line, not_mentioned первым, алфавит check)	Симметрия PLAN ↔ Прогноз ↔ scan_report_*
25.09.2026	DS_075 — счётчики «Прогноз исправлений / Исправлено / В AI» в scan_report_* и scan_VVxVVx_*; топ-2 файла при Подробном	Видна доля автофикса vs AI-очереди; статистика только на репрезентативной выборке (≥ report_stats_min_files)
25.09.2026	DS_075 — новый ключ settings.json `report_stats_min_files` (по умолчанию 10) + поле в GUI	Порог включения топ-файлов настраивается пользователем
25.09.2026	DS_076 — три унифицированные метрики файлов (Всего / с проблемами / с изменениями) в scan_report_* и scan_VVxVVx_*; при прерывании — «Обработано файлов»	Одна метка «Всего файлов» означала разные величины (166 vs 71); побочный фикс — удалён мёртвый паттерн .v???? из exclude_patterns
6. Маппинг кодов PlpCheck
6.1. Проблема
Сканер выдаёт краткие коды (plpcheck.BAD_PREFIX).
PARSER_SQL хранит полные коды (PlpCheck.STYLE.BAD_PREFIX.п.4.3).
Несовпадение → has_rule() = False → фикс не срабатывает → PLAN пуст.

6.2. Решение
SRC\rule_engine.py:_resolve_code — маппинг:

text
plpcheck.<NAME>  →  PlpCheck.<CAT>.<NAME>.п.<N>
Применён в: has_rule, get_rule, rule_buckets, apply_fix.
33/33 NAME уникальны.

6.3. Фолбэк BAD_PREFIX → PREFIX_TYPE
Сканер выдаёт один код bad_prefix — покрывает и «плохой префикс», и «отсутствие префикса».
PARSER_SQL — два правила: bad_prefix_* и missing_prefix_*.

Фолбэк: если bad_prefix не найден в bad_prefix_* — искать в missing_prefix_* / PREFIX_TYPE_*.

6.4. Категория ignore в PlpCheck
20 из 33 PlpCheck-правил в PARSER_SQL — transform_type: "ignore".
Правила ignore не автофиксятся → не попадают в scan_VVxVVx_* (в блок PLAN).
Это норма (по семантике DS_053).

После DS_066: блок PLAN в scan_VVxVVx_* содержит все issues (вариант A), с пометкой [auto] / [ignore].

После DS_067: PLAN с колонкой LINE; сортировка внутри LINE — по ключу scan_report_* (not_mentioned первым, алфавит check); в «Прогнозе» — все строки-мишени с цепочкой правил и единой позицией >.

7. Особенности регулярных выражений
7.1. Глобальный IGNORECASE в sql_parser.py
SRC\analyzer\sql_parser.py использует re.IGNORECASE глобально для всех паттернов.

7.2. Маркер (?-i) — локальное отключение
Для регистрозависимых паттернов (например, camelCase-lookahead (?!v[A-Z]|...) — для vDateRep) — используется маркер (?-i).
Поддержка — в sql_parser.py (DS_059_Уточнение_E).

7.3. Регистронезависимый lookahead
Для исключений ((?!v_|p_|n_|...)) — используется (?i:...) — регистронезависимая группа.
Позволяет P_PARAM, V_Date не матчить префиксы v_/p_.

7.4. Два источника паттернов
4.RUBRICATOR_PROMPT v5.json — источник regex-паттернов для сканера (309 паттернов).

5.RUBRICATOR_PARSER_SQL v5.json — источник трансформаций (transform).

При правке regex — оба файла должны быть синхронизированы (DS_065).

8. Форматы логов
8.1. scan_report_* — табличный
Колонки: № CLASS_ID SHORT_NAME SECTION LINE CHECK LEVEL TYPE ERROR PLAN.

Формат ERROR: <описание проблемы>: "<исходный_фрагмент>" — исходный фрагмент в кавычках, обрезка до 50 символов + ….

Маркеры комментариев сохраняются в match_fragment для code_in_comment (--, /*, */, /**/) — DS_066.

Формат PLAN: > <действие> (стрелка, без CHECK). example_out не используется (DS_065).

Пример (после DS_066):

text
23  code_in_comment  WARNING  STYLE  Удалите закомментированный код: "--if lrecBrInfo.f_BIC ..."  > Удалить закомментированный код
Строка «Уникальных проблем» удалена из scan_report_* (DS_066). Итоговая строка: «Всего проблем: N»; при наличии дублей (`issues_before_dedup != len(issues)`) перед ней — «Всего проблем (с дублями): N» (DS_077).

Ключ сортировки (scanner.generate_report, scanner.py:2008): (line, not_mentioned первым, алфавит check). Используется в save_scan_only_log для PLAN и цепочки (DS_067_B).

Счётчики режимов (DS_075): сразу после итоговой строки «Всего проблем» выводятся три строки:

text
Прогноз исправлений: X
Исправлено: Y
В AI: Z

X — dry-run детерминированных фиксов (`_forecast_and_ai_counts`), Y — число реально исправленных (`fixed_count`, в режиме «Сканировать» = 0), Z = дедуп-issues − X (кандидаты в AI-очередь).

Метрики файлов (DS_076): после «В AI» — три унифицированные метрики (одинаковые в scan_report_* и scan_VVxVVx_*):

```text
Всего файлов: T          # найдено .plp после _should_exclude (scanner.total_files)
Файлов с проблемами: P   # уникальные file_path в issues (в scan_VVxVVx_* — dedup_by_file)
Файлов с изменениями: C  # файлов, где dry-run дал >= 1 change
```

При прерывании (DS_041) `Всего файлов` → `Обработано файлов: scanner.files_scanned`. Фолбэк (scan_directory не вызывался): T = P. Источник C для scan_report_* — `scanner.forecast_files_changed` (фиксируется в `_forecast_and_ai_counts`), для scan_VVxVVx_* — `len([sf for sf in sim_files if sf['changes']])`.

Топ-файлы (DS_075): блок по двум лидерам (по числу issues и по числу видов issues) — только при `log_level == "Подробный"` **и** числе файлов ≥ `report_stats_min_files` (по умолчанию 10). При совпадении лидеров — один блок.

### 8.1.1. Формат блока топ-файлов (DS_075)

text
Статистика по файлу: <имя_файла> (N issues, M видов)
  <issue_type>: K
  ...

Заголовок — `Статистика по файлу:` + имя файла и скобочная сводка; далее отступ 2 пробела, полный `issue_type` и число.

8.2. scan_VVxVVx_* — прогноз исправлений
Формат — эталон из DS_053_Уточнение_4, обновлён в DS_066 и DS_067:

text
Режим: сканирование (прогноз исправлений, без записи)

PLAN:
LINE AUTO ДЕЙСТВИЕ
3 [ignore] > Удалить объявление
3 [ignore] > Переименовать в "v_dp"
4 [ignore] > Переименовать в "v_fmt24"
...

Правил в PLAN: N

Прогноз:
Строка 7:
.................................> P_PARAM ref [REPS_PARAMS];
<plpcheck.PREFIX_TYPE_IN_VAR_NAME> v_rParam ref [REPS_PARAMS];

Строка 11:
.................................> P_PARAM := [str].get_str_par(P_ADDS, 'P_PARAM');
<plpcheck.WRONG_METHOD_SYNTAX    > P_PARAM := ::[str].[get_str_par](P_ADDS, 'P_PARAM');

Строка 12:
.................................> --if lrecBrInfo.f_BIC is not null then null;
<plpcheck.CODE_IN_COMMENT        > (удалить строку)

Статистика по файлу:
  <КР-код-1>: N
  <КР-код-2>: M

Правил в ignore (не автофиксятся): N
  <КР-код-3>
  ...

Всего проблем (с дублями): N  # при issues_before_dedup != len(dedup_issues) (DS_077)
Всего проблем: N
Всего файлов: M
Ключевое (DS_066): PLAN = все issues (вариант A), с пометкой [auto] / [ignore].

Ключевое (DS_067):

PLAN: заголовок LINE AUTO ДЕЙСТВИЕ, каждая строка {line} {[auto]|[ignore]} > <действие>; сортировка по ключу scan_report_*.

«Прогноз»: все строки-мишени (не только dry-run changes); цепочка по всем issues строки; единая позиция >; МКР = max(len(код_правила)) + 1 по кодам всех issues файла (формат B — полный plpcheck.NAME).

Приоритет удаления (DS_067_A): при наличии delete-issue (not_mentioned / code_in_comment / действие «удалить» из _generate_plan) на строке выводится только она (первая по №); остальные issues строки скрыты.

Отсечение цепочки после (удалить строку) — как отдельный механизм удалён (заменён приоритетом удаления).

Итоговый текст: not_mentioned → (удалить объявление); code_in_comment → (удалить строку).

Сортировка внутри LINE: (line, not_mentioned первым, алфавит check) — ключ scanner.generate_report.

Дополнение DS_075: в `save_scan_only_log` после блока «Правил в ignore» идёт итоговая группа: `Всего проблем: N`, затем те же три счётчика — `Прогноз исправлений: X`, `Исправлено: 0`, `В AI: Z` (тот же порядок, что в `scan_report_*`, п. 8.2), затем метрики файлов DS_076 (см. §8.1): `Всего файлов: T` / `Файлов с проблемами: P` / `Файлов с изменениями: C`; при прерывании — `Обработано файлов: scanner.files_scanned`. Строка `Спрогнозировано исправлений:` (DS_053_Уточнение_4/5) выводится **не** была — актуальная метка `Прогноз исправлений:`. Топ-файлы — по тем же условиям (`log_level == "Подробный"` и файлов ≥ `report_stats_min_files`).

8.3. plpcheck_report_*.html
HTML-отчёт PlpCheck 2.5.2.

9. Открытые замечания
9.1. Multi-line rename — ЗАКРЫТО
PREFIX_TYPE_IN_VAR_NAME → ignore (DS_059_Уточнение_F).

bad_prefix_* → ignore (DS_063).

missing_prefix_* → ignore (DS_059_Уточнение_F).

9.2. Различение «параметр / переменная» — ЗАКРЫТО
Частично решено в E (lookahead in/out).

Полностью — в F (параметры не автофиксятся).

Уточнение DS_066: P_ в локальных переменных — ошибка программиста; prefix_type_in_var_name заменяет P_ на v_<тип><CamelCase>.

9.3. SPEC_CHARS — ЗАКРЫТО (DS_065)
Regex сужен до имён: \b(class|view|method|library|interface|enum)\s+... и @(name|tag)\s*\(....

SPEC: 350 → 2 на REPS_EXP_115_1.plp; ложных 207 → 0.

9.4. Формат PLAN и соответствие отчётов — ЗАКРЫТО (DS_066, DS_067)
scan_report_*: > <действие>.

scan_VVxVVx_*: PLAN = все issues с [auto]/[ignore]; колонка LINE; сортировка по ключу scan_report_*.

Счётчик «Уникальных» удалён.

9.5. Заглушки DS_067 — ЧАСТИЧНО ЗАКРЫТО (DS_068, DS_069)

AI-пометка: needs_ai_fix в Issue отсутствует → выводится заглушка [AI] Требуется AI-анализ: <не реализовано> для правил без детерминированного итогового текста (пример: GLOBAL_VAR). Решение DS_068 §6.3: оставить как есть (needs_ai_fix — агрегат _verify_file, не атрибут проблемы).

Диапазон удаления — ЗАКРЫТО (DS_069): поля block_start/block_end добавлены в Issue (0 = не блок). _check_plp_code_in_comment возвращает 6-ки; block_end = строка закрывающего */ или EOF при незакрытом блоке (DS_069 §3.4 — незакрытый блок теперь репортится). В save_scan_only_log: block_end > block_start → (удалить диапазон строк N–M), иначе (удалить строку). Для -- и однострочных блоков — block_start=block_end=0 → (удалить строку).

10. prefix_type_in_var_name — алгоритм (DS_066)
10.1. Правило
PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4 — transform_type: "ignore" (DS_059_Уточнение_F). Автофикс отключён, issue попадает в scan_report_*.

10.2. Формат переименования
v_<тип><CamelCase> (разделитель _).

Исходный префикс	Судьба	Пример
P_ (в локальной переменной)	Заменяется на v_ (признак параметра в локальной — ошибка)	P_PARAM ref [REPS_PARAMS] → v_rParam
v, lv, dp, fmt, lr, lrec	Сохраняется как часть имени	vDateRep varchar2(10) → v_vDateRep
10.3. Таблица соответствия (тип → префикс)
Тип PL/SQL	Префикс	Пример
ref	r	P_PARAM ref [REPS_PARAMS] → v_rParam
varchar2 / varchar	v	vDateRep varchar2(10) → v_vDateRep
[STRING_*]	s	P_FILE_XML [STRING_1000] → v_sFile_Xml
10.4. Отличие от bad_prefix
bad_prefix (DS_063) — формат без _: v_iDp, v_sFmt, v_rBranch.
prefix_type_in_var_name — формат с _: v_rParam, v_sFile_Xml.

Решение DS_066: форматы не унифицируются — это разные правила с разной семантикой.

text

---