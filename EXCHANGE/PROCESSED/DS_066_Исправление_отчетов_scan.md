# DS_066

**Дата:** 21.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** высокий
**Зависит от:** DS_064_Уточнение_A, DS_065
**Блокирует:** —

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

---

## 1. Цель

Устранить 7 дефектов, выявленных при тестировании `REPS_EXP_115_1` (см. §3). Все — в одном задании.

**Решения автора DS (приняты):**

| # | Вопрос | Решение |
|---|--------|---------|
| 1 | `not_mentioned`: формат ERROR | Оставить `код.: "фрагмент"` |
| 2 | `vDateRep` / `lvRepPeriod` | Переименовывать: `v_vDateRep` / `v_lvRepPeriod` |
| 3 | `P_*` локальные в `prefix_type_in_var_name` | Переименовывать (`P_` → `v_`) |
| 4 | Формат PLAN в `scan_report_*` | `> <действие>` (со стрелкой) |
| 5 | PLAN в `scan_VVxVVx_*` | Все issues + `[auto]`/`[ignore]` |
| 6 | Счётчик «Уникальных» | Удалить из вывода |
| 7 | `bad_prefix` vs `prefix_type_in_var_name` | Форматы разные — оставить как есть |

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `SRC\analyzer\scanner.py` | `_generate_plan`: PLAN → `> <действие>`, без `<CHECK> — ` |
| 2 | `SRC\analyzer\scanner.py` | `scan_file`: `match_fragment` — брать фрагмент конкретного issue, не первое совпадение в строке |
| 3 | `SRC\analyzer\scanner.py` | `match_fragment` для `code_in_comment` — включать маркеры (`--`, `/*`, `*/`) |
| 4 | `SRC\analyzer\scanner.py` | `_generate_plan` + `save_scan_only_log`: PLAN в `scan_VVxVVx_*` = все issues, с пометкой `[auto]`/`[ignore]` |
| 5 | `SRC\gui_app.py` | Убрать строку «Уникальных проблем» из вывода статистики |
| 6 | `SRC\analyzer\scanner.py` (regex/lookahead) | `prefix_type_in_var_name`: `P_*` локальные → `P_` заменять на `v_` |
| 7 | `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` + `5.RUBRICATOR_PARSER_SQL v5.json` | Синхронная правка regex `prefix_type_in_var_name` / `code_in_comment` |

---

## 3. Дефекты (детали)

### Дефект 1 — PLAN: дублирование `CHECK`

**Было:**
bad_prefix — Переименовать в "v_iDp"

text

**Стало:**
Переименовать в "v_iDp"

text

Применить ко всем PLAN в `scan_report_*` (`_generate_plan`).

---

### Дефект 2 — `match_fragment` для `bad_prefix` на строке 17

**Исходник (строка 17):**
function iif(v1 boolean, v2 varchar2(32767), v3 varchar2(32767)) return varchar2(32767) is

text

**Было:** три issue, все с `match_fragment = "v1"`:
9 ... переименуйте в "p_bV1": "v1"
10 ... переименуйте в "p_sV2": "v1"
11 ... переименуйте в "p_sV3": "v1"

text

**Стало:** `match_fragment` = `v1`, `v2`, `v3` соответственно:
9 ... переименуйте в "p_bV1": "v1"
10 ... переименуйте в "p_sV2": "v2"
11 ... переименуйте в "p_sV3": "v3"

text

**Причина:** в `scan_file` `match_fragment` берётся из первого совпадения regex в строке. Нужно — из совпадения, соответствующего конкретному issue.

**Разведка:** как формируется список issues (по каждому regex-матчу) и где теряется привязка `match_fragment` ↔ `description`.

---

### Дефект 3 — `match_fragment` для `code_in_comment`

**Исходник (строка 68):**
--if lrecBrInfo.f_BIC is not null then null; &debug(TB$||'БИК ...

text

**Было:**
Удалите закомментированный код: "if lrecBrInfo.f_BIC ..."

text

**Стало:**
Удалите закомментированный код: "--if lrecBrInfo.f_BIC ..."

text

`match_fragment` **должен включать** маркеры комментария (`--`, `/*`, `*/`, `/**/`).

**Строки:** 68, 75, 124. Особый случай — строка 99 (`/** /`): разведка — что именно матчит regex `code_in_comment` в этом случае.

---

### Дефект 4 — Соответствие PLAN между отчётами

**Вариант A (принят):** PLAN = все issues.

`scan_VVxVVx_*` — PLAN = все issues из `scan_report_*`, с пометкой `[auto]`/`[ignore]` перед действием:
PLAN:
[ignore] > Переименовать в "v_iDp"
[ignore] > Удалить объявление
[auto] > Исправить синтаксис
...

Правил в PLAN: 26
Правил в ignore (не автофиксятся): N
plpcheck.BAD_PREFIX
plpcheck.CODE_IN_COMMENT
plpcheck.NOT_MENTIONED
plpcheck.PREFIX_TYPE_IN_VAR_NAME

text

Точное выравнивание — на усмотрение KODA.

---

### Дефект 5 — Удалить счётчик «Уникальных»

**Было:**
Всего проблем: 26
Уникальных проблем: 24

text

**Стало:**
Всего проблем: 26

text

Убрать строку «Уникальных проблем» из `scan_report_*` (и из GUI-статистики, если есть).

---

### Дефект 6 — `prefix_type_in_var_name`: `P_*` локальные

**Исходник (строки 31, 34, 35):**
execute is
P_PARAM ref [REPS_PARAMS]; -- ссылка на реализацию филиала
...
P_FILE_XML [STRING_1000];
P_FILE_ZIP [STRING_1000];

text

**Правило:** `P_` — признак параметра. Если локальная переменная начинается с `P_` — ошибка программиста. Правило **заменяет** `P_` на `v_`.

**Формат:** `v_<тип><CamelCase>`.

| Было | Стало | Логика |
|------|-------|--------|
| `P_PARAM ref [REPS_PARAMS];` | `v_rParam ref [REPS_PARAMS];` | `P_`→`v_`, `ref`→`r` |
| `P_FILE_XML [STRING_1000];` | `v_sFile_Xml [STRING_1000];` | `P_`→`v_`, `string`→`s` |
| `P_FILE_ZIP [STRING_1000];` | `v_sFile_Zip [STRING_1000];` | `P_`→`v_`, `string`→`s` |

**Правило замены префиксов:**

| Исходный префикс | Судьба |
|-----------------|--------|
| `P_` (в локальной переменной) | **Заменяется** на `v_` |
| `v`, `lv`, `dp`, `fmt`, `lr`, `lrec` | **Сохраняется** как часть имени |

**Итоговая таблица (все локальные из `execute is`):**

| Было | Стало |
|------|-------|
| `P_PARAM ref [REPS_PARAMS];` | `v_rParam ref [REPS_PARAMS];` |
| `vDateRep varchar2(10);` | `v_vDateRep varchar2(10);` |
| `lvRepPeriod varchar2(5);` | `v_lvRepPeriod varchar2(5);` |
| `P_FILE_XML [STRING_1000];` | `v_sFile_Xml [STRING_1000];` |
| `P_FILE_ZIP [STRING_1000];` | `v_sFile_Zip [STRING_1000];` |

**Разделитель** между префиксом типа и именем — `_`.

---

### Дефект 7 — Форматы `bad_prefix` / `prefix_type_in_var_name` — оставить разными

`bad_prefix` использует формат **без `_`**: `v_iDp`, `v_sFmt`, `v_rBranch`.

`prefix_type_in_var_name` — **с `_`**: `v_rParam`, `v_sFile_Xml`.

**Решение:** оставить как есть. Унификация — вне рамок DS_066.

---

## 4. Разведка (обязательные пункты)

| # | Что найти | Где |
|---|-----------|-----|
| 1 | Формирование `match_fragment` в `scan_file` | `scanner.py` |
| 2 | Логика `_generate_plan` (PLAN) | `scanner.py` |
| 3 | Формирование `scan_VVxVVx_*` | `code_fixer.py:save_scan_only_log` |
| 4 | Счётчик «Уникальных» | `gui_app.py` |
| 5 | Regex `code_in_comment` (с маркерами) | `4.RUBRICATOR_PROMPT v5.json`, `5.RUBRICATOR_PARSER_SQL v5.json` |
| 6 | Regex/lookahead `prefix_type_in_var_name` | там же |
| 7 | Как определить тип переменной для `prefix_type_in_var_name` (для `P_PARAM`→`r`, `P_FILE_XML`→`s`) | там же |

**При обнаружении расхождений** с предположениями задачи — остановиться, доложить автору DS.

---

## 5. Тесты

| # | Кейс | Ожидание |
|---|------|----------|
| 1 | PLAN в `scan_report_*` | `> <действие>`, без `CHECK` |
| 2 | `bad_prefix` строка 17 | `match_fragment` = `v1`, `v2`, `v3` |
| 3 | `code_in_comment` строки 68, 75, 124 | `match_fragment` начинается с `--` |
| 4 | `code_in_comment` строка 99 | разведка + решение |
| 5 | PLAN `scan_report_*` vs `scan_VVxVVx_*` | Все issues в обоих (вариант A) |
| 6 | Пометка `[auto]` / `[ignore]` | В `scan_VVxVVx_*` |
| 7 | «Уникальных проблем» | Отсутствует в `scan_report_*` |
| 8 | `P_PARAM ref [REPS_PARAMS];` | → `v_rParam ref [REPS_PARAMS];` |
| 9 | `vDateRep varchar2(10);` | → `v_vDateRep varchar2(10);` |
| 10 | `lvRepPeriod varchar2(5);` | → `v_lvRepPeriod varchar2(5);` |
| 11 | `P_FILE_XML [STRING_1000];` | → `v_sFile_Xml [STRING_1000];` |
| 12 | `P_FILE_ZIP [STRING_1000];` | → `v_sFile_Zip [STRING_1000];` |
| 13 | Регресс DS_056, DS_064_A, DS_065 | PASSED |

---

## 6. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + дополнительные разделы:

- **§6. До/после** — таблица по каждому дефекту (было/стало).
- **§7. Разведка** — выводы по каждому пункту §4.
- **§8. Вопросы к автору** — если разведка выявила неоднозначность.

---

## 7. Ограничения

См. `DS_STANDARD.md` → раздел 2.

Дополнительно:

- Правка regex — **синхронно** в `4.RUBRICATOR_PROMPT v5.json` и `5.RUBRICATOR_PARSER_SQL v5.json` (DS_065).
- Не ломать существующие тесты DS_032–DS_065.