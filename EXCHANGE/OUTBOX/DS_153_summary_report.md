# DS_153 Summary Report: покрытие К2 («Исправить код») тестами

**Чат:** 44
**Ветка:** feature/dockerization
**Коммиты:** fe4deaa (DS_153a), c9b5c1d (DS_153b), 9d1772f (DS_153c), fbb9415 (DS_153d)
**Регресс:** 293 -> **314 passed** (+21)
**Статус:** чат 44 закрыт, ahead 0

---

## 1. Обзор

Тема чата 44 — покрытие тестами кнопки К2 («Исправить код»):
`start_fix` -> `_run_fix` -> `PLPlusFixer.fix_directory` -> `_verify_file` -> `scan_results.remaining_by_rule`.

| Подшаг | Тестов | Регресс | Коммит |
|--------|--------|---------|--------|
| DS_153-a | +5 AST | 293 -> 298 | fe4deaa |
| DS_153-b | +5 AST | 298 -> 303 | c9b5c1d |
| DS_153-c | +5 AST | 303 -> 308 | 9d1772f |
| DS_153-d | +6 (4 функц. + 1 AST + 1 баг) | 308 -> **314** | fbb9415 |

---

## 2. Матрица «пункт чек-листа × тест × DS»

| Пункт | Тест | DS | Тип |
|-------|------|----|-----|
| п.0 (порядок проверок до потока) | test_start_fix_checks_before_thread | DS_153-a | AST |
| п.1 (нет scan_results) | test_run_fix_no_scan_results_dialog | DS_153-a | AST |
| п.1b (total_issues == 0) | test_run_fix_zero_issues_message | DS_153-a | AST |
| п.2 (нет selected_rules) | test_start_fix_no_selected_rules_message | DS_153-a | AST |
| п.2b (нет source_dir) | test_start_fix_no_source_dir_message | DS_153-a | AST |
| п.3 (_get_rules_for_selected_files) | test_run_fix_uses_get_rules_for_selected_files | DS_153-b | AST |
| п.3b (fix_directory(scanner)) | test_run_fix_calls_fix_directory_with_scanner | DS_153-b | AST |
| п.3b (fixer.flags) | test_run_fix_assigns_fixer_flags | DS_153-b | AST |
| п.3c (_current_fix_flags defaults) | test_current_fix_flags_defaults | DS_153-b | AST |
| п.9 (ai_only не в К2) | test_ai_only_not_in_run_fix_but_in_send_to_ai | DS_153-b | AST |
| п.5 (remaining_by_rule) | test_verify_file_has_remaining_keys | DS_153-c | AST |
| п.5 (fixed = max(0, b-a)) | test_verify_file_uses_max_zero | DS_153-c | AST |
| п.5 (ai_on -> needs_ai_fix/manual) | test_verify_file_ai_on_branch | DS_153-c | AST |
| п.6 (бэкапы _preai/_YYYYMMDD) | test_rescan_ai_files_backup_regex | DS_153-c | AST |
| п.7 (save_log + _bot_log) | test_run_fix_save_log_and_bot_log | DS_153-c | AST |
| п.4* (scanner fallback) | test_scanner_returns_issues_when_empty | DS_153-d | функц. |
| п.4* (scanner с selected_rule) | test_scanner_returns_issues_with_selected_rule | DS_153-d | функц. |
| п.4* (multiline не фильтруются) | test_multiline_not_filtered_by_selected_rules | DS_153-d | функц. |
| п.4* (get_issues_by_file) | test_get_issues_by_file_returns_dict | DS_153-d | функц. |
| п.4* (_is_rule_selected в scan_file) | test_is_rule_selected_called_in_scan_file | DS_153-d | AST |
| п.4* (известное ограничение) | test_selected_rule_does_not_narrow_plpcheck | DS_153-d | функц. (баг) |

---

## 3. Известное ограничение (п.4*)

`_is_rule_selected` (SRC/analyzer/scanner.py:728) фильтрует **загрузку PATTERNS** (regex) по `selected_rules`,
но **multiline-правила** (`plpcheck.BAD_PREFIX`, `plpcheck.NOT_MENTIONED`, `plpcheck.WRONG_METHOD_SYNTAX`,
`plpcheck.CODE_IN_COMMENT`) выполняются **всегда** для `.plp`.

Кроме того, `selected_rules=[`plpcheck.X`]` **не сужает** набор `plpcheck.*` — сравнение идёт по
**префиксу** (`plpcheck`), а не по **полному коду** правила (`plpcheck.X`).

**Зафиксировано:** `SRC/tests/test_ds153d_scanner_selected_rules.py::test_selected_rule_does_not_narrow_plpcheck`.

---

## 4. Открытый вопрос для чата 45 (OQ-1)

**Доработка `_is_rule_selected`:** сравнение по **полному коду** правила, а не по префиксу `plpcheck`.
Плюс — фильтрация **multiline**-правил по `selected_rules` (сейчас выполняются всегда).

**Влияние:** `selected_rules=[`plpcheck.BAD_PREFIX`]` реально не сужает набор — К2/К1 работают «шире»,
чем ожидает пользователь. Это **не блокер** (текущее поведение зафиксировано тестом), но **задача на доработку**.

---

## 5. Метрики

| Метрика | Значение |
|---------|----------|
| Тестов добавлено | +21 (16 AST + 5 функц./баг) |
| Регресс | 293 -> **314 passed** |
| Коммитов | 4 (fe4deaa, c9b5c1d, 9d1772f, fbb9415) |
| Push | все запушены, ahead 0 |
| Время регресса | ~47-52s |

---

*Отчёт создан в чате 44 (DS_153 summary).*
