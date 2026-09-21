# DS_CONTEXT — Общий контекст проекта

**Назначение:** факты, которые используются в нескольких DS. Ссылаться вместо повторения в каждой задаче.

**Версия:** 2.0 от 21.09.2026 (после DS_063, DS_064_Уточнение_A, DS_065, DS_066).

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
| `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Парсер (трансформации `transform`) | 75 |
| `DATA\Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил с признаками | — |
| `DATA\CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2 | — |

**Примечание (21.09.2026):**
- `4.RUBRICATOR_PROMPT v5.json` — **источник** regex-паттернов **для сканера** (309 паттернов). `5.RUBRICATOR_PARSER_SQL v5.json` — **источник** трансформаций (`transform`). Правки regex **должны** вноситься **в оба** файла (DS_065).
- После `DS_059_Уточнение_D/E` в `5.RUBRICATOR_PARSER_SQL v5.json` **добавлены** паттерны: `bad_prefix_varchar2`, `bad_prefix_number`, `bad_prefix_date`, `bad_prefix_boolean`; `wrong_method_syntax_bracket`.
- После `DS_065` — regex `SPEC_CHARS` **сужен** в **обоих** файлах.
- После `DS_066` — в `5.RUBRICATOR_PARSER_SQL v5.json` добавлен паттерн `p_local_prefix` в `PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4`; в **обоих** файлах уточнены `note` для `PREFIX_TYPE_IN_VAR_NAME` и `CODE_IN_COMMENT`.

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

### 3.2. Схема `settings.json` (согласовано)

```json
{
  "rubricator_selected_rules": {
    "v53.rule_code_1": true,
    "тдс20240828.DML_JOIN.стр.1": true,
    "plpcheck.CODE_IN_COMMENT": false
  }
}
```

- Формат: словарь `{"<rule_code>": true|false}`.
- Идемпотентен.
- Начальное состояние (нет ключа): прочитать `1.RUBRICATOR_FILES v5.md`, сохранить в `settings.json` (вариант C).
- Новые правила: дополнять со значением `false`, сохраняя существующие.

---

## 4. Соглашения по коду

- Python — UTF-8 без BOM.
- OUTBOX — CRLF.
- `bot.log` — UTF-8 без BOM, формат `[ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <итог>`.
- Стиль логов и отчётов — русский, формальный.

---

## 5. История ключевых решений

| Дата | Решение | Обоснование |
|------|---------|-------------|
| 19.09.2026 | DS_056B отменён | Вендорского эталона нет, все источники проверены |
| 19.09.2026 | DS_056A — разделение `is_in_comment_or_string` / `advance_lexer_state` | Многократный вызов для одной строки требует чистоты функции |
| 19.09.2026 | DS_058+DS_057 объединены | Одна область кода (`gui_app.py`) |
| 19.09.2026 | `1.RUBRICATOR_FILES v5.md` — read-only для GUI | Баг `−`→`+`; состояние в `settings.json` |
| 19.09.2026 | Бот `exchange_bot.py` отключён. Перенос файлов — вручную (DS_049). | Бот не запущен (нет процесса, автозапуска). KODA работает без него. Раздел DS_048 удалён из `AGENTS.md`. |
| 20.09.2026 | DS_059 — маппинг кодов PlpCheck (`rule_engine.py:_resolve_code`) | Сканер: `plpcheck.<NAME>`; PARSER_SQL: `PlpCheck.<CAT>.<NAME>.п.<N>`; 33/33 NAME уникальны |
| 20.09.2026 | DS_059_Уточнение_A — формат `ERROR` в `scan_report_*` | `<описание>: "<исходный_фрагмент>"`, обрезка 50 символов + `…` |
| 20.09.2026 | DS_059_Уточнение_B — заголовок `scan_VVxVVx_*` | Переиспользование `_generate_active_rubricators_lines()` из сканера |
| 20.09.2026 | DS_059_Уточнение_D — восстановление формата `scan_VVxVVx_*` | `Режим: сканирование (...)`, PLAN, блок «Прогноз:», статистика, блок «Правил в ignore» |
| 20.09.2026 | DS_059_Уточнение_E — безопасные правки | `code_in_comment` → `ignore`; `bad_prefix_*` разделены; `vDateRep` — не автофиксится; lookahead `(?i)` + исключение параметров `in/out` |
| 20.09.2026 | DS_054_Уточнение_C — кнопка «От AI» disabled при пустом `AI_OUT` | Таймер 5 сек; тултип динамический |
| 20.09.2026 | DS_059_Уточнение_F — `PREFIX_TYPE_IN_VAR_NAME` → `ignore` | Multi-line rename риск; параметры не автофиксятся |
| 20.09.2026 | DS_062 (разведка) — 89.6% дублей даёт `SPEC_CHARS` | regex `[^A-Z0-9_#]` матчит каждый спецсимвол |
| 21.09.2026 | DS_063 — `bad_prefix_*` → `ignore` | Multi-line rename риск; `missing_prefix_*` уже `ignore` с DS_059_F |
| 21.09.2026 | DS_064 — дедупликация issues в `scanner.py` | 634 → 67 уникальных (SPEC_CHARS 89.6%) |
| 21.09.2026 | DS_064_Уточнение_A — ключ дедупа: `(file, line, issue_type, description, match_fragment)` | `original_code` = вся строка, не ERROR-фрагмент; поле `match_fragment` |
| 21.09.2026 | DS_065 — PLAN без `example_out`, `SPEC_CHARS` сужен, категории PlpCheck | SPEC: 350 → 2, ложных 207 → 0; `STYLE.SYNTAX` — новая категория; `code_in_comment` → `OTHER` |
| 21.09.2026 | DS_066 — PLAN `> <действие>`, соответствие PLAN между отчётами (вариант A), маркеры комментариев в ERROR, `P_*` локальные → `v_<тип><CamelCase>`, счётчик «Уникальных» удалён | Унификация отчётов, корректность `match_fragment`, семантика `P_` |

---

## 6. Маппинг кодов PlpCheck

### 6.1. Проблема

Сканер выдаёт **краткие** коды (`plpcheck.BAD_PREFIX`).
PARSER_SQL хранит **полные** коды (`PlpCheck.STYLE.BAD_PREFIX.п.4.3`).
**Несовпадение** → `has_rule()` = False → фикс не срабатывает → PLAN пуст.

### 6.2. Решение

`SRC\rule_engine.py:_resolve_code` — маппинг:

```
plpcheck.<NAME>  →  PlpCheck.<CAT>.<NAME>.п.<N>
```

Применён в: `has_rule`, `get_rule`, `rule_buckets`, `apply_fix`.
33/33 NAME уникальны.

### 6.3. Фолбэк `BAD_PREFIX → PREFIX_TYPE`

Сканер выдаёт **один** код `bad_prefix` — покрывает **и** «плохой префикс», **и** «отсутствие префикса».
PARSER_SQL — **два** правила: `bad_prefix_*` и `missing_prefix_*`.

**Фолбэк:** если `bad_prefix` не найден в `bad_prefix_*` — искать в `missing_prefix_*` / `PREFIX_TYPE_*`.

### 6.4. Категория `ignore` в PlpCheck

**20 из 33** PlpCheck-правил в PARSER_SQL — `transform_type: "ignore"`.
Правила `ignore` **не автофиксятся** → **не попадают** в `scan_VVxVVx_*` (в блок PLAN).
Это **норма** (по семантике DS_053).

**После DS_066:** блок PLAN в `scan_VVxVVx_*` содержит **все** issues (вариант A), с пометкой `[auto]` / `[ignore]`.

---

## 7. Особенности регулярных выражений

### 7.1. Глобальный `IGNORECASE` в `sql_parser.py`

`SRC\analyzer\sql_parser.py` использует `re.IGNORECASE` **глобально** для всех паттернов.

### 7.2. Маркер `(?-i)` — локальное отключение

Для **регистрозависимых** паттернов (например, camelCase-lookahead `(?!v[A-Z]|...)` — для `vDateRep`) — используется маркер **`(?-i)`**.
**Поддержка** — в `sql_parser.py` (DS_059_Уточнение_E).

### 7.3. Регистронезависимый lookahead

Для **исключений** (`(?!v_|p_|n_|...)`) — используется **`(?i:...)`** — регистронезависимая группа.
Позволяет `P_PARAM`, `V_Date` **не матчить** префиксы `v_`/`p_`.

### 7.4. Два источника паттернов

- `4.RUBRICATOR_PROMPT v5.json` — **источник** regex-паттернов **для сканера** (309 паттернов).
- `5.RUBRICATOR_PARSER_SQL v5.json` — **источник** трансформаций (`transform`).

**При правке regex** — **оба** файла **должны** быть **синхронизированы** (DS_065).

---

## 8. Форматы логов

### 8.1. `scan_report_*` — табличный

Колонки: `№ CLASS_ID SHORT_NAME SECTION LINE CHECK LEVEL TYPE ERROR PLAN`.

**Формат `ERROR`:** `<описание проблемы>: "<исходный_фрагмент>"` — **исходный** фрагмент в кавычках, обрезка до **50 символов** + `…`.

**Маркеры комментариев** сохраняются в `match_fragment` для `code_in_comment` (`--`, `/*`, `*/`, `/**/`) — DS_066.

**Формат `PLAN`:** `> <действие>` (стрелка, без `CHECK`). `example_out` **не используется** (DS_065).

**Пример (после DS_066):**
```
23  code_in_comment  WARNING  STYLE  Удалите закомментированный код: "--if lrecBrInfo.f_BIC ..."  > Удалить закомментированный код
```

**Строка «Уникальных проблем» удалена** из `scan_report_*` (DS_066). Остаётся «Всего проблем: N».

### 8.2. `scan_VVxVVx_*` — прогноз исправлений

Формат — **эталон** из `DS_053_Уточнение_4`, обновлён в DS_066:

```
Режим: сканирование (прогноз исправлений, без записи)

PLAN:
  [auto]   > <действие-1>
  [ignore] > <действие-2>
  ...

Правил в PLAN: N

Прогноз:
Строка 32:
..........................> <было>
<КР-код-1>   <стало>
Строка 33:
...

Статистика по файлу:
  <КР-код-1>: N
  <КР-код-2>: M

Правил в ignore (не автофиксятся): N
  <КР-код-3>
  ...
```

**Ключевое (DS_066):** PLAN = **все** issues (вариант A), с пометкой `[auto]` / `[ignore]`. Ранее PLAN содержал только автофиксимые.

### 8.3. `plpcheck_report_*.html`

HTML-отчёт PlpCheck 2.5.2.

---

## 9. Открытые замечания

_На 21.09.2026 — **открытых замечаний нет**._

### 9.1. Multi-line rename — **ЗАКРЫТО**
- `PREFIX_TYPE_IN_VAR_NAME` → `ignore` (DS_059_Уточнение_F).
- `bad_prefix_*` → `ignore` (DS_063).
- `missing_prefix_*` → `ignore` (DS_059_Уточнение_F).

### 9.2. Различение «параметр / переменная» — **ЗАКРЫТО**
- Частично решено в E (lookahead `in/out`).
- Полностью — в F (параметры не автофиксятся).
- **Уточнение DS_066:** `P_` в локальных переменных — ошибка программиста; `prefix_type_in_var_name` заменяет `P_` на `v_<тип><CamelCase>`.

### 9.3. `SPEC_CHARS` — **ЗАКРЫТО** (DS_065)
- Regex сужен до имён: `\b(class|view|method|library|interface|enum)\s+...` и `@(name|tag)\s*\(...`.
- SPEC: 350 → 2 на `REPS_EXP_115_1.plp`; ложных 207 → 0.

### 9.4. Формат PLAN и соответствие отчётов — **ЗАКРЫТО** (DS_066)
- `scan_report_*`: `> <действие>`.
- `scan_VVxVVx_*`: PLAN = все issues с `[auto]`/`[ignore]`.
- Счётчик «Уникальных» удалён.

---

## 10. `prefix_type_in_var_name` — алгоритм (DS_066)

### 10.1. Правило

`PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4` — `transform_type: "ignore"` (DS_059_Уточнение_F). Автофикс отключён, issue попадает в `scan_report_*`.

### 10.2. Формат переименования

`v_<тип><CamelCase>` (разделитель `_`).

| Исходный префикс | Судьба | Пример |
|-----------------|--------|--------|
| `P_` (в локальной переменной) | **Заменяется** на `v_` (признак параметра в локальной — ошибка) | `P_PARAM ref [REPS_PARAMS]` → `v_rParam` |
| `v`, `lv`, `dp`, `fmt`, `lr`, `lrec` | **Сохраняется** как часть имени | `vDateRep varchar2(10)` → `v_vDateRep` |

### 10.3. Таблица соответствия (тип → префикс)

| Тип PL/SQL | Префикс | Пример |
|-----------|---------|--------|
| `ref` | `r` | `P_PARAM ref [REPS_PARAMS]` → `v_rParam` |
| `varchar2` / `varchar` | `v` | `vDateRep varchar2(10)` → `v_vDateRep` |
| `[STRING_*]` | `s` | `P_FILE_XML [STRING_1000]` → `v_sFile_Xml` |

### 10.4. Отличие от `bad_prefix`

`bad_prefix` (DS_063) — формат **без `_`**: `v_iDp`, `v_sFmt`, `v_rBranch`.
`prefix_type_in_var_name` — формат **с `_`**: `v_rParam`, `v_sFile_Xml`.

**Решение DS_066:** форматы не унифицируются — это **разные правила** с разной семантикой.