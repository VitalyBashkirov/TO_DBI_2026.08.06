# DS_FILES — Карта файлов и ключевых функций

**Назначение:** адреса файлов и функций для ссылок в DS. Заменяет повтор адресов в каждой задаче.

**Версия:** 1.3 от 21.09.2026 (после DS_063, DS_064_Уточнение_A, DS_065, DS_066, DS_067 + Уточнения_A/B).

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
| `scanner.py` | `generate_report` | 2008 | Строка «Уникальных проблем» **удалена** (DS_066). **Ключ сортировки:** `(line, not_mentioned первым, алфавит check)` — используется `save_scan_only_log` (DS_067_B). |
| `scanner.py` | `scan_directory` | — | Итоговая статистика: строка «Всего issues (с дублями)» при `before != after` (DS_064_Уточнение_A). |
| `scanner.py` | `PLPCHECK_RULE_TO_CATEGORY` | — | Маппинг: `plpcheck.CODE_IN_COMMENT` → `OTHER`; `plpcheck.WRONG_METHOD_SYNTAX` → `STYLE.SYNTAX` (DS_065). |
| `scanner.py` | `PLPCHECK_CATEGORIES` | — | Категории GUI. Из `STYLE.PREFIXES` убраны `wrong_method_syntax`, `code_in_comment`; добавлена `STYLE.SYNTAX`; `code_in_comment` → `OTHER` (DS_065). |
| `lexer_state.py` | `LexerState` | — | Состояние (DS_056A). |
| `lexer_state.py` | `is_in_comment_or_string` | — | Чистая, не мутирует state. |
| `lexer_state.py` | `advance_lexer_state` | — | Единственная точка мутации. |
| `lexer_state.py` | `is_line_fully_in_comment_or_string` | — | Обёртка для VariableParser. |
| `sql_parser.py` | — | — | Глобальный `re.IGNORECASE`; поддержка маркеров `(?-i)` и `(?i:...)` (DS_059_Уточнение_E). |

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
| `code_fixer.py` | `_apply_issue_fixes` | — | Основной цикл фиксера. Сухой прогон даёт `changes` `{line_number, rule_code, before, after}` (DS_067 §7). |
| `code_fixer.py` | `_validate_fix` | 876–879 | Спец-обработка `&debug`. |
| `code_fixer.py` | `_is_delete` | — | Хелпер: issue с действием удаления (`not_mentioned` / `code_in_comment` / действие «удалить» из `_generate_plan`) — DS_067_A. |
| `code_fixer.py` | `save_scan_only_log` | ~2193 | Лог `scan_VVxVVx_*`. **DS_066:** PLAN = все issues (вариант A) с `[auto]`/`[ignore]`; заголовок через `_generate_active_rubricators_lines` (DS_059_Уточнение_B/D). **DS_067:** PLAN с колонкой `LINE` (заголовок `LINE AUTO ДЕЙСТВИЕ`); «Прогноз» — все строки-мишени, цепочка правил, единая позиция `>`, МКР = `max(len(код_правила)) + 1` по всем issues файла; итоговый текст: `not_mentioned` → `(удалить объявление)`, `code_in_comment` → `(удалить строку)`. **DS_067_A:** приоритет удаления (`_is_delete`), обрыв цепочки удалён как отдельный механизм. **DS_067_B:** сортировка PLAN и цепочки внутри LINE по ключу `scan_report_*`. |

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
| `Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | 75 правил парсера; **источник трансформаций (`transform`)**. Правки regex — синхронно с `4.RUBRICATOR_PROMPT v5.json` (DS_065). DS_066: добавлен паттерн `p_local_prefix` в `PREFIX_TYPE_IN_VAR_NAME`. |
| `Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил (read-only для GUI). |
| `CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2. |

### Ключевые правила PARSER_SQL

| Правило | Состояние | Источник |
|---------|-----------|----------|
| `PlpCheck.STYLE.BAD_PREFIX.п.4.3` (`bad_prefix_varchar2`, `bad_prefix_number`, `bad_prefix_date`, `bad_prefix_boolean`) | `transform_type: "ignore"` | DS_063 |
| `PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4` (`missing_prefix_*`, `p_local_prefix`) | `transform_type: "ignore"` | DS_059_Уточнение_F, DS_066 |
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