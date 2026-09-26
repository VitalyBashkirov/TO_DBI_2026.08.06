# DS_FILES — Карта файлов и ключевых функций

**Назначение:** адреса файлов и функций для ссылок в DS. Заменяет повтор адресов в каждой задаче.

**Версия:** 2.1 от 25.09.2026 (после DS_063–DS_067 + Уточнения, DS_072a–DS_072e, DS_073, DS_075, DS_076).

---

## 1. `SRC\gui_app.py` — GUI

| Функция | Строки | Назначение |
|---------|--------|-----------|
| `_load_rubricator_files` | 765–791 | Чтение `1.RUBRICATOR_FILES v5.md`. `+` = вкл, `−` (U+2212) = выкл. |
| `_on_rule_click` | 838–858 | Клик по чекбоксу — только ставит `rules_changed = True`. |
| `save_settings` | 1887 | Вызов `_save_rubricator_state`. |
| `_save_rubricator_state` | 1889–1945 | Пишет в рубрикатор (баг DS_058). |
| `_populate_rules_tree` | — | Построение дерева правил, начальное состояние чекбоксов. |
| `show_sql_for_manual_fix` | — | Отображение результатов скана: счётчики «Всего issues (с дублями)» / «Всего проблем (после дедупа)». Строка «Уникальных (file,line,check)» **удалена** (DS_066). |
| `on_close` | 3845 | Закрытие окна — вызов `save_settings`. |
| `report_stats_min_files_var` | 128 | DS_075: `tk.StringVar(value="10")` — порог включения блока топ-файлов. |
| Поле ввода `report_stats_min_files` | 477 | DS_075: `ttk.Entry` в `options_frame` (row 0, column 5). |
| Загрузка из настроек | 2158 | DS_075: `settings.get('report_stats_min_files', 10)` → `report_stats_min_files_var`. |
| Сохранение в настройки | 2240 | DS_075: `'report_stats_min_files': int(...)` в `save_settings` (ключ `settings.json`). |
| Проброс в конвейер | 2663–2682 | DS_075: `_log_level` / `_min_files` передаются в `generate_report(...)` (2668) и `save_scan_only_log(...)` (2682). |

---

## 2. `SRC\analyzer\` — анализатор

| Файл | Функция | Строки | Назначение |
|------|---------|--------|-----------|
| `scanner.py` | `Issue` (dataclass) | — | Поля: `line`, `issue_type`, `description`, `match_fragment: str = ''` (DS_064_Уточнение_A), `block_start: int = 0`, `block_end: int = 0` (DS_069; 0 = не блок `/* ... */`), `original_code` (вся строка). |
| `scanner.py` | `PLPlusScanner._is_in_comment_or_string` | 489 | Фильтрация regex-совпадений. |
| `scanner.py` | `_find_code_positions` | 551 | Вызов `_is_in_comment_or_string`. |
| `scanner.py` | `scan_file` | — | Основной цикл сканирования; заполняет `match_fragment` из конкретного issue (DS_066); дедуп по ключу `(file, line, issue_type, description, match_fragment)`; `self.issues_before_dedup += len(issues)`. |
| `scanner.py` | `_check_plp_bad_prefix` | — | Возвращает 4-й элемент — имя конкретной переменной (DS_066). |
| `scanner.py` | `_check_plp_prefix_type_in_var_name` | — | Логика DS_066: `P_*` локальные → `v_<тип><CamelCase>`. |
| `scanner.py` | `_plp_suggest_execute_var_name` | — | Генерация нового имени: `P_` → `v_`, тип → префикс, CamelCase по сегментам (DS_066). |
| `scanner.py` | `_plp_type_letter` | — | Таблица `PLP_TYPE_LETTERS` (ref→r, [STRING_*]→s) — существующая. |
| `scanner.py` | `_extract_error_fragment` | — | Формирование `match_fragment`; для `code_in_comment` — маркеры (`--`, `/**/`) сохраняются (DS_066). |
| `scanner.py` | `_check_plp_code_in_comment` | — | Трекер блоков: открывает `/*`, закрывает `*/`. **DS_069:** возвращает 6-ки `(line, msg, orig, block_start, block_end)`; `block_end` = строка `*/` или EOF при незакрытом блоке (незакрытый блок репортится). Для `--` и однострочных блоков — `block_start=block_end=0`. |
| `scanner.py` | `_generate_plan` | — | Формирование PLAN. Формат `> <действие>` (DS_066). Приоритет-3 (`example_out`) **удалён** (DS_065). Исправлен `UnboundLocalError` (локальный `import re`) — DS_066. **DS_067:** ключ сортировки отчёта (`generate_report`, scanner.py:2008) используется в `save_scan_only_log` для PLAN и цепочки. |
| `scanner.py` | `_transform_action` | — | Сохранён для совместимости, **не вызывается** (DS_065). |
| `scanner.py` | `generate_report` | 1951–2078 | Строка «Уникальных проблем» **удалена** (DS_066). **Ключ сортировки:** `(line, not_mentioned первым, алфавит check)` — используется `save_scan_only_log` (DS_067_B). **DS_075:** сигнатура `generate_report(output_path, mode='scan', fixed_count=0, log_level='Минимальный', report_stats_min_files=10)`; пишет 3 счётчика (`Прогноз исправлений:` / `Исправлено:` / `В AI:`) и блок топ-файлов. **DS_076:** метрики файлов — `Всего файлов` (self.total_files; при прерывании `Обработано файлов` = self.files_scanned) / `Файлов с проблемами` / `Файлов с изменениями` (self.forecast_files_changed). |
| `scanner.py` | `_dedup_issues` | 2079–2091 | DS_075: список issues без дублей по ключу `(file, line, issue_type, description, match_fragment)` — общая основа счётчиков и топ-файлов. |
| `scanner.py` | `_forecast_and_ai_counts` | 2092–2135 | DS_075: `(forecast, ai)`. `forecast` — число dry-run детерминированных фиксов, `ai` = дедуп-issues − forecast. Консервативный фолбэк при недоступности движка: `(0, len(dedup))`. **DS_076:** попутно фиксирует `self.forecast_files_changed` — файлов с ≥ 1 change (метрика «Файлов с изменениями»). |
| `scanner.py` | `_top_files_lines` | 2136–2189 | DS_075: строки блока топ-файлов. Пусто, если `log_level != "Подробный"` или файлов < `min_files`. Лидер по числу issues + лидер по числу видов; при совпадении — один блок. Формат: `Статистика по файлу: <имя> (N issues, M видов)` + `  <issue_type>: K`. |
| `scanner.py` | `scan_directory` | — | Итоговая статистика: строка «Всего issues (с дублями)» при `before != after` (DS_064_Уточнение_A). |
| `scanner.py` | `PLPCHECK_RULE_TO_CATEGORY` | — | Маппинг: `plpcheck.CODE_IN_COMMENT` → `OTHER`; `plpcheck.WRONG_METHOD_SYNTAX` → `STYLE.SYNTAX` (DS_065). |
| `scanner.py` | `PLPCHECK_CATEGORIES` | — | Категории GUI. Из `STYLE.PREFIXES` убраны `wrong_method_syntax`, `code_in_comment`; добавлена `STYLE.SYNTAX`; `code_in_comment` → `OTHER` (DS_065). |
| `lexer_state.py` | `LexerState` | — | Состояние (DS_056A). |
| `lexer_state.py` | `is_in_comment_or_string` | — | Чистая, не мутирует state. |
| `lexer_state.py` | `advance_lexer_state` | — | Единственная точка мутации. |
| `lexer_state.py` | `is_line_fully_in_comment_or_string` | — | Обёртка для VariableParser. |
| `sql_parser.py` | — | — | Глобальный `re.IGNORECASE`; поддержка маркеров `(?-i)` и `(?i:...)` (DS_059_Уточнение_E). |
| `sql_parser.py` | `apply_fix_multiline` | — | Многострочные transform (`replace_scope: "multiline"`, DS_072c): re.DOTALL+re.MULTILINE, плейсхолдеры `{N}` через `apply_transform`, count=1. Построчный `apply_fix_ex` multiline-паттерны пропускает (не ломать построчный путь). |
| `rule_engine.py` | `RuleEngine.apply_fix_multiline` | — | Обёртка над `sql_parser.apply_fix_multiline` с маппингом `plpcheck.<NAME>` (DS_059) и фильтром флагов. |
| `code_fixer.py` | `PLPlusFixer._apply_issue_fixes` | ~1210 | DS_073: первым проходом — multiline-правила (`replace_scope: "multiline"`, окно `Issue.block_start/block_end` / весь файл, Вариант C), затем построчный `apply_fix` (multiline-issues исключены — идемпотентность §3.5). |

---

## 3. `SRC\fixer\` — фиксер

| Файл | Функция | Строки | Назначение |
|------|---------|--------|-----------|
| `variable_parser.py` | `DeterministicFixer._is_in_comment_or_string` | 330 | Упрощённая (баг DS_056 №1). |
| `variable_parser.py` | `_rename_variable` | 322 | Вызов `_is_in_comment_or_string`. |
| `variable_parser.py` | `_is_variable_used` | 376 | Вызов `_is_in_comment_or_string`. |
| `code_fixer.py` | `PLPlusFixer._is_in_comment_or_string` | 990 | Основная реализация. |
| `code_fixer.py` | `_find_code_positions` | 1114 | Вызов `_is_in_comment_or_string`. |
| `code_fixer.py` | `_update_renamed_vars` | 755–762 | Спец-обработка `&debug`. |
| `code_fixer.py` | `PLPlusFixer._verify_file` | ~1291 | Верификация повторным сканом (DS_053): остаток issue + флаг `ai_fallback` -> `needs_ai_fix` (DS_054). AI-фолбэк `MAX_SIZE_ID` / `PLATFORM_INTEGER_MISMATCH` работает через неё; корзина `ignore` (не `hybrid` — `_pattern_bucket` без `transform` -> `ignore`, DS_072a_Уточнение_B). |
| `code_fixer.py` | `_apply_issue_fixes` | — | Основной цикл фиксера. Сухой прогон даёт `changes` `{line_number, rule_code, before, after}` (DS_067 §7). |
| `code_fixer.py` | `_validate_fix` | 876–879 | Спец-обработка `&debug`. |
| `code_fixer.py` | `_is_delete` | — | Хелпер: issue с действием удаления (`not_mentioned` / `code_in_comment` / действие «удалить» из `_generate_plan`) — DS_067_A. |
| `code_fixer.py` | `save_scan_only_log` | 2255 | Лог `scan_VVxVVx_*`. **DS_066:** PLAN = все issues (вариант A) с `[auto]`/`[ignore]`; заголовок через `_generate_active_rubricators_lines` (DS_059_Уточнение_B/D). **DS_067:** PLAN с колонкой `LINE` (заголовок `LINE AUTO ДЕЙСТВИЕ`); «Прогноз» — все строки-мишени, цепочка правил, единая позиция `>`, МКР = `max(len(код_правила)) + 1` по всем issues файла; итоговый текст: `not_mentioned` → `(удалить объявление)`, `code_in_comment` → `(удалить строку)`. **DS_067_A:** приоритет удаления (`_is_delete`), обрыв цепочки удалён как отдельный механизм. **DS_067_B:** сортировка PLAN и цепочки внутри LINE по ключу `scan_report_*`. **DS_075:** параметры `log_level='Минимальный'`, `report_stats_min_files=10`; после блока «Правил в ignore» пишет 3 счётчика (`Прогноз исправлений:` / `Исправлено: 0` / `В AI:`) и блок топ-файлов через `scanner._top_files_lines(...)`. |

---

## 4. `SRC\tests\` — тесты

| Файл | Назначение |
|------|-----------|
| `test_ds056_is_in_comment.py` | Тесты хелпера (DS_056A). |
| `test_ds032.py` … `test_ds055.py` | Регресс (не ломать). |

---

## 5. `SRC\` — прочее

| Файл | Назначение |
|------|-----------|
| `ai_exchange.py` | AI-fallback (DS_054, DS_054_Уточнение_C). |
| `koda_prompts.py` | Правила AI (`&debug`). |
| `rule_engine.py` | RuleEngine. `_resolve_code` — маппинг `plpcheck.<NAME>` → `PlpCheck.<CAT>.<NAME>.п.<N>`; фолбэк `BAD_PREFIX` → `PREFIX_TYPE` (DS_059). |
| `rule_engine.py` | `has_rule`, `get_rule`, `rule_buckets`, `apply_fix` — используют `_resolve_code`. |

---

## 6. `DATA\` — данные

| Файл | Назначение |
|------|-----------|
| `Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | 332 правила; **источник regex-паттернов сканера** (309 паттернов). Правки regex — синхронно с `5.RUBRICATOR_PARSER_SQL v5.json` (DS_065). Описания `PREFIX_TYPE_IN_VAR_NAME` и `CODE_IN_COMMENT` дополнены (DS_066). |
| `Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | 148 правил парсера; **источник трансформаций (`transform`)**. Правки regex — синхронно с `4.RUBRICATOR_PROMPT v5.json` (DS_065). DS_066: добавлен паттерн `p_local_prefix` в `PREFIX_TYPE_IN_VAR_NAME`. DS_072a: добавлены 11 правил `PlpCheck.DBI.<NAME>.п.1` (группа A из DS_071). DS_072a_Уточнение_A: `DYNAMIC_PLP.п.1` удалён (детектор, вариант B) → 10 правил группы A. DS_072b: добавлены 5 правил группы B — 3 transform (`INSERT_WITH_ID`, `REFERENCED_TO_OBJECT`, `SELECTLOCKWAIT`, `replace_scope: "match"`) + 2 ignore (`ALIAS_COLUMN_VIEW`, `MULTIPLE_MODIFIERS`). DS_072b_Уточнение_A: `example_out` `INSERT_WITH_ID` исправлен на `insert into ... return t into obj_ref;` (без `X := `); transform не менялся (Вариант B: regex матчит всю конструкцию). DS_072c_Реализация: +19 правил группы C — 4 multiline-transform (`NOT_CLOSED_CURSOR`, `NOT_CLOSED_FILE`, `NOT_HANDLED_CURSOR_EXCEPTIONS`, `OBLIGATORY_IN_OTHERS`, `replace_scope: "multiline"`) + 15 ignore (C1-fallback `OUTER_JOIN`, C2-структурные ×3, C3-AI ×6, C4 ×5). |
| `Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил (read-only для GUI). |
| `CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2. |

### Ключевые правила PARSER_SQL

| Правило | Состояние | Источник |
|---------|-----------|----------|
| `PlpCheck.STYLE.BAD_PREFIX.п.4.3` (`bad_prefix_varchar2`, `bad_prefix_number`, `bad_prefix_date`, `bad_prefix_boolean`) | `transform_type: "ignore"` | DS_063 |
| `PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4` (`missing_prefix_*`, `p_local_prefix`) | `transform_type: "ignore"` | DS_059_Уточнение_F, DS_066 |
| `PlpCheck.DBI.<NAME>.п.1` × 10 (группа A: CALL_STACK_ANALYSIS, DIRECT_COMPARISON_WITH_NULL, FUNCTION_BREAK_INDEX, MAX_SIZE_ID, NVL_IN_SELECT, PARALLEL_EXECUTION, PLATFORM_INTEGER_MISMATCH, REF_NONTABLE, SUBOPTIMAL_EXPLICIT_DB_ROUNDRTIP, SYSTEM_VIEWS) | `transform_type: "regex"`; AI-фолбэк-паттерны `max_size_id_other` / `platform_integer_mismatch_other` — `"ignore"` (DS_072a_Уточнение_B) | DS_072a, DS_072a_Уточнение_B |
| `PlpCheck.DBI.DYNAMIC_PLP.п.1` | **удалён** из PARSER_SQL (обобщение ломало SQL) — детектор | DS_072a_Уточнение_A |
| `v53.STOR.SPEC_CHARS.п.2.10` | regex сужен до имён (`\b(class\|view\|...)\s+...`, `@(name\|tag)\s*\(...`) | DS_065 (в **обоих** JSON) |

---

## 7. `EXCHANGE\` — обмен

| Файл/каталог | Назначение |
|--------------|-----------|
| `INBOX\` | Входящие задачи. |
| `OUTBOX\` | Отчёты. |
| `PROCESSED\` | Обработанные задачи. |
| `bot.log` | Протокольный лог. |
| `DS_STANDARD.md` | Стандарт оформления DS. |
| `DS_CONTEXT.md` | Общий контекст. |
| `DS_FILES.md` | Эта карта. |

---

## 8. Как использовать

В задаче:

- вместо перечисления файлов → `См. DS_FILES.md → SRC\gui_app.py`.
- вместо описания функций → `_save_rubricator_state` (см. DS_FILES.md).
- вместо повторов адресов → ссылки.

Если в проекте появились новые файлы — обновить этот документ.

---

## 9. Изменения 21.09.2026

| Дата | Изменение | Источник |
|------|-----------|----------|
| 21.09.2026 | `Issue.match_fragment`, дедуп по `(file,line,issue_type,description,match_fragment)`, `issues_before_dedup` | DS_064_Уточнение_A |
| 21.09.2026 | `_generate_plan`: удалён `example_out`; `_transform_action` не вызывается | DS_065 |
| 21.09.2026 | `PLPCHECK_RULE_TO_CATEGORY`, `PLPCHECK_CATEGORIES`: `STYLE.SYNTAX`, `code_in_comment`→`OTHER` | DS_065 |
| 21.09.2026 | SPEC_CHARS regex сужен в **обоих** JSON (`4.RUBRICATOR_PROMPT`, `5.RUBRICATOR_PARSER_SQL`) | DS_065 |
| 21.09.2026 | `bad_prefix_*` → `ignore` | DS_063 |
| 21.09.2026 | `scan_report_*`: PLAN `> <действие>`; «Уникальных проблем» удалено | DS_066 |
| 21.09.2026 | `scan_VVxVVx_*`: PLAN = все issues с `[auto]`/`[ignore]` | DS_066 |
| 21.09.2026 | `_check_plp_bad_prefix`, `_check_plp_prefix_type_in_var_name` — 4-й элемент (имя переменной) | DS_066 |
| 21.09.2026 | `_plp_suggest_execute_var_name` — новая функция (`P_`→`v_`, тип→префикс, CamelCase) | DS_066 |
| 21.09.2026 | `_extract_error_fragment`: маркеры `code_in_comment` сохраняются | DS_066 |
| 21.09.2026 | `PREFIX_TYPE_IN_VAR_NAME`: паттерн `p_local_prefix` в PARSER_SQL | DS_066 |
| 21.09.2026 | `save_scan_only_log`: PLAN с колонкой `LINE` (заголовок `LINE AUTO ДЕЙСТВИЕ`) | DS_067 |
| 21.09.2026 | `save_scan_only_log`: «Прогноз» — все строки-мишени, цепочка, единая позиция `>`, МКР = max(len)+1 | DS_067 |
| 21.09.2026 | `save_scan_only_log`: приоритет удаления, `_is_delete`, `not_mentioned` → `(удалить объявление)`, обрыв цепочки удалён | DS_067_A |
| 21.09.2026 | `save_scan_only_log`: сортировка PLAN и цепочки по ключу `scan_report_*` | DS_067_B |
| 21.09.2026 | `generate_report` (`scanner.py:2008`): ключ сортировки используется `save_scan_only_log` | DS_067_B |
| 22.09.2026 | `Issue.block_start/block_end`; `_check_plp_code_in_comment` — 6-ки, незакрытый блок репортится (block_end=EOF); `save_scan_only_log` — `(удалить диапазон строк N–M)` | DS_069 |
| 23.09.2026 | PARSER_SQL: +11 правил `PlpCheck.DBI.<NAME>.п.1` (группа A DS_071, transform `regex`); PROMPT: `fix_instruction` для 11 NAME синхронно | DS_072a |
| 23.09.2026 | PARSER_SQL: `PlpCheck.DBI.DYNAMIC_PLP.п.1` удалён (86→85), PROMPT: `fix_instruction` DYNAMIC_PLP = детектор (структурный перенос fetch, вручную) | DS_072a_Уточнение_A |
| 23.09.2026 | PARSER_SQL: AI-фолбэк-паттерны `max_size_id_other` / `platform_integer_mismatch_other` — `transform_type: "ignore"` (вместо `hybrid`); PROMPT: `fix_instruction` = `needs_ai_fix`; `rule_engine.py` не тронут | DS_072a_Уточнение_B |
| 23.09.2026 | PARSER_SQL: +5 правил группы B — 3 transform (`INSERT_WITH_ID`, `REFERENCED_TO_OBJECT`, `SELECTLOCKWAIT`, `replace_scope: "match"`) + 2 ignore (`ALIAS_COLUMN_VIEW`, `MULTIPLE_MODIFIERS`) (86→90); PROMPT: `fix_instruction` для 5 NAME синхронно | DS_072b |
| 23.09.2026 | PARSER_SQL: `example_out` `INSERT_WITH_ID` исправлен (`txt_job_ref := insert into ...` → `insert into ... return t into txt_job_ref;`); transform не менялся (Вариант B: `replace_scope: "match"` матчит всю конструкцию); PROMPT `fix_instruction` уже корректен — проверен, не изменён | DS_072b_Уточнение_A |
| 23.09.2026 | `sql_parser.py`: `apply_fix_multiline` (replace_scope "multiline", DOTALL+MULTILINE, плейсхолдеры {N}); `apply_fix_ex` пропускает multiline построчно; `rule_engine.py`: обёртка `RuleEngine.apply_fix_multiline` | DS_072c_Реализация |
| 23.09.2026 | PARSER_SQL: +19 правил группы C (90→109): 4 multiline-transform + 15 ignore (C1-fallback `OUTER_JOIN` — `{object_type}` неизвестен; C2-структурные ×3; C3-AI ×6 — needs_ai_fix DS_054; C4 ×5); PROMPT: `fix_instruction` для 19 NAME синхронно | DS_072c_Реализация |
| 23.09.2026 | `AGENTS.md` раздел «Логирование»: правило — `bot.log` только `EXCHANGE\bot.log`, создание в других каталогах (`SRC\bot.log` и пр.) запрещено | DS_072c_Реализация |
| 23.09.2026 | `code_fixer.py:_apply_issue_fixes`: интеграция `apply_fix_multiline` — первым проходом (до построчного `apply_fix`), окно Вариант C (`block_start/block_end` / весь файл), идемпотентность (правило исключается из построчного прохода). Заработали 4 multiline-правила C2 в прод-фиксе | DS_073 |
| 23.09.2026 | PARSER_SQL: +15 правил группы D (109→124): 3 transform (`MATCHING_TYPES`, `SIZE_RESTRICTION`, `INDEX_LENGTH`, `replace_scope: "match"`) + 12 ignore (fallback брифа: `CONTROLTABLECOLUMNSTYPE`, `HINT_INDEX_ORDER_BY`, `INVALID_INIT`, D3 ×3, D4 ×6); PROMPT: `fix_instruction` для 15 NAME синхронно; SRC не тронут | DS_072d_Реализация |
| 23.09.2026 | PARSER_SQL: +24 правила группы E (124→148) — все `transform_type: "ignore"`-детекторы (regex из PROMPT `for_search`), note по категориям брифа §4.2; PROMPT: `fix_instruction` для 24 NAME синхронно. PlpCheck-аудит DS_071 завершён: 74/74 NAME — 20 transform + 54 ignore/AI | DS_072e_Реализация |
| 25.09.2026 | `scanner.py`: `generate_report` — параметры `mode`/`fixed_count`/`log_level`/`report_stats_min_files`; 3 счётчика `Прогноз исправлений` / `Исправлено` / `В AI` | DS_075 |
| 25.09.2026 | `scanner.py`: новые хелперы `_dedup_issues` (2079), `_forecast_and_ai_counts` (2092), `_top_files_lines` (2136) | DS_075 |
| 25.09.2026 | `code_fixer.py:save_scan_only_log` — параметры `log_level`/`report_stats_min_files`, те же 3 счётчика + блок топ-файлов | DS_075 |
| 25.09.2026 | `gui_app.py`: `report_stats_min_files_var` (128), поле ввода (477), загрузка/сохранение ключа (2158/2240), проброс в отчёт и лог (2663–2682) | DS_075 |
| 25.09.2026 | `settings.json`: новый ключ `report_stats_min_files` (по умолчанию 10) | DS_075 |
| 25.09.2026 | `scanner.py`: `__init__` — атрибуты `total_files`/`files_scanned`/`forecast_files_changed`; `scan_directory` фиксирует `total_files`/`files_scanned`; `_forecast_and_ai_counts` — `forecast_files_changed`; `generate_report` — 3 метрики файлов («Всего»/«с проблемами»/«с изменениями»; при прерывании «Обработано файлов») | DS_076 |
| 25.09.2026 | `code_fixer.py:save_scan_only_log` — те же 3 метрики файлов (источник: `scanner.total_files`/`dedup_by_file`/`sim_files[changes]`) | DS_076 |
| 25.09.2026 | `gui_app.py` (2505, 2970), `code_fixer.py` (2082): из `exclude_patterns` удалён мёртвый паттерн `.v????` | DS_076 |