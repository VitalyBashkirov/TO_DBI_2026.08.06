# DS_FILES — Карта файлов и ключевых функций

**Назначение:** адреса файлов и функций для ссылок в DS. Заменяет повтор адресов в каждой задаче.

---

## 1. `SRC\gui_app.py` — GUI

| Функция | Строки | Назначение |
|---------|--------|-----------|
| `_load_rubricator_files` | 765–791 | Чтение `1.RUBRICATOR_FILES v5.md`. `+` = вкл, `−` (U+2212) = выкл. |
| `_on_rule_click` | 838–858 | Клик по чекбоксу — только ставит `rules_changed = True`. |
| `save_settings` | 1887 | Вызов `_save_rubricator_state`. |
| `_save_rubricator_state` | 1889–1945 | Пишет в рубрикатор (баг DS_058). |
| `_populate_rules_tree` | — | Построение дерева правил, начальное состояние чекбоксов. |
| `on_close` | 3845 | Закрытие окна — вызов `save_settings`. |

---

## 2. `SRC\analyzer\` — анализатор

| Файл | Функция | Строки | Назначение |
|------|---------|--------|-----------|
| `scanner.py` | `PLPlusScanner._is_in_comment_or_string` | 489 | Фильтрация regex-совпадений |
| `scanner.py` | `_find_code_positions` | 551 | Вызов `_is_in_comment_or_string` |
| `scanner.py` | `scan_file` | — | Основной цикл сканирования |
| `lexer_state.py` | `LexerState` | — | Состояние (создан в DS_056A) |
| `lexer_state.py` | `is_in_comment_or_string` | — | Чистая, не мутирует state |
| `lexer_state.py` | `advance_lexer_state` | — | Единственная точка мутации |
| `lexer_state.py` | `is_line_fully_in_comment_or_string` | — | Обёртка для VariableParser |

---

## 3. `SRC\fixer\` — фиксер

| Файл | Функция | Строки | Назначение |
|------|---------|--------|-----------|
| `variable_parser.py` | `DeterministicFixer._is_in_comment_or_string` | 330 | Упрощённая (баг DS_056 №1) |
| `variable_parser.py` | `_rename_variable` | 322 | Вызов `_is_in_comment_or_string` |
| `variable_parser.py` | `_is_variable_used` | 376 | Вызов `_is_in_comment_or_string` |
| `code_fixer.py` | `PLPlusFixer._is_in_comment_or_string` | 990 | Основная реализация |
| `code_fixer.py` | `_find_code_positions` | 1114 | Вызов `_is_in_comment_or_string` |
| `code_fixer.py` | `_update_renamed_vars` | 755–762 | Спец-обработка `&debug` |
| `code_fixer.py` | `_apply_issue_fixes` | — | Основной цикл фиксера |
| `code_fixer.py` | `_validate_fix` | 876–879 | Спец-обработка `&debug` |

---

## 4. `SRC\tests\` — тесты

| Файл | Назначение |
|------|-----------|
| `test_ds056_is_in_comment.py` | Тесты хелпера (DS_056A) |
| `test_ds032.py` … `test_ds055.py` | Регресс (не ломать) |

---

## 5. `SRC\` — прочее

| Файл | Назначение |
|------|-----------|
| `ai_exchange.py` | AI-fallback (DS_054) |
| `koda_prompts.py` | Правила AI (`&debug`) |
| `rule_engine.py` | RuleEngine (расширяется в DS_060) |

---

## 6. `DATA\` — данные

| Файл | Назначение |
|------|-----------|
| `Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | 332 правила |
| `Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | 75 правил парсера |
| `Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил (read-only для GUI) |
| `CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2 |

---

## 7. `EXCHANGE\` — обмен

| Файл/каталог | Назначение |
|--------------|-----------|
| `INBOX\` | Входящие задачи |
| `OUTBOX\` | Отчёты |
| `PROCESSED\` | Обработанные задачи |
| `bot.log` | Протокольный лог |
| `DS_STANDARD.md` | Стандарт оформления DS |
| `DS_CONTEXT.md` | Общий контекст |
| `DS_FILES.md` | Эта карта |

---

## 8. Как использовать

В задаче:

- вместо перечисления файлов → `См. DS_FILES.md → SRC\gui_app.py`.
- вместо описания функций → `_save_rubricator_state` (см. DS_FILES.md).
- вместо повторов адресов → ссылки.

Если в проекте появились новые файлы — обновить этот документ.