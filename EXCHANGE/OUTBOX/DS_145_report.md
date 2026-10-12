# DS_145 — deep_scanner: фильтр временных + расширение is_temporary_filename

**Дата:** 2026-10-12
**Ветка:** feature/dockerization
**Автор DS:** DeepSeek
**Пользователь:** Vitaly
**Тип:** Реализация + regression

## Задача

Расширить фильтр временных/служебных файлов:
1. `is_temporary_filename` (scanner.py) — добавить расширения, префиксы, точные имена.
2. `deep_scanner.py` — применить фильтр, считать `skipped_temporary`, вернуть в dict.
3. `exclude_patterns` deep_scanner — добавить каталоги `.git`, `__pycache__`, `node_modules`.
4. Задокументировать: `deep_mode` в GUI не используется (DS_146 в очередь).

## Разведка (recon 1–7)

| # | Что проверено | Результат |
|---|---------------|-----------|
| 1 | Ollama, git, INBOX, pytest | OK, 145 passed, INBOX пуст |
| 2 | scanner.py, deep_scanner.py, gui_app.py — структура | Точки вставки найдены |
| 3 | `__init__`, `run()` финал, `_run_scan` тело | Картина ясна |
| 4 | DeepScanner в SRC/tools | **Не вызывается из GUI вообще** |
| 5 | Тесты с temp-расширениями | **Пусто** — расширение безопасно |
| 6 | test_ds135 + gui_app + fixer | Инвариант DS_135: backup без `_` — не временный |
| 7 | К3/К4 (кнопки «В AI»/«Из AI») | **Не зависят** от `is_temporary_filename` |

## Правки

### scanner.py (~строки 15–45)

- Добавлены константы: `_TEMP_SUFFIXES`, `_TEMP_PREFIXES`, `_TEMP_EXACT`.
- Расширена `is_temporary_filename`:
  - DS_135 (timestamp `_YYYYMMDD_HHMMSS_`) — сохранён.
  - DS_145: суффиксы `.bak`, `.tmp`, `.temp`, `.swp`, `.swo`, `.plp~`, `.~plp` (регистронезависимо).
  - DS_145: префикс `~$`.
  - DS_145: точные имена `.DS_Store`, `Thumbs.db`, `desktop.ini`.

### deep_scanner.py

- Строка ~471: `exclude_patterns` расширен: `['.v????', '.bak', '.tmp', '\\__pycache__\\', '\\.git\\', '\\node_modules\\']`.
- Строка ~491: добавлен локальный импорт `from analyzer.scanner import is_temporary_filename`.
- Строка ~523: `skipped_temporary = 0`.
- Строки ~533–536: в цикле `for plp_file` — пропуск временных.
- Строка ~554+: логирование `Пропущено временных/служебных файлов: N`.
- Строка ~601: `return {..., 'skipped_temporary': skipped_temporary}`.

### gui_app.py

- Docstring `_run_scan` расширен комментарием про DS_146.

## Тесты

`SRC/tests/test_ds145_temporary_filter_pytest.py` — 22 теста:
- DS_135 регресс (timestamp) — 4 теста.
- DS_145 суффиксы — 7 тестов.
- DS_145 префикс `~$` — 2 теста.
- DS_145 точные имена — 3 теста.
- DS_145 регистронезависимость — 2 теста.
- Границы — 3 теста.
- DeepScanner возвращает `skipped_temporary` — 2 теста.

## Регресс

- `test_ds135_temporary.py` — 12 тестов, все зелёные (не сломаны).
- Полный pytest — см. лог `PS\ds145_impl_b.log`.

## Что НЕ сделано (вне scope)

- **DS_146** (в очередь): интеграция `DeepScanner` в GUI. Факт: `start_deep_scan` (gui_app.py:4017) вызывает `_run_scan(True)`, где `deep_mode` не используется. Требуется разведка и решение (подключить / переименовать кнопку / удалить).
- DS_144d (.mcs, .mp, .pck) — без изменений.
- DS_119 (CLI-сканер) — без изменений.

## Изменённые файлы

- `SRC/analyzer/scanner.py` — расширение `is_temporary_filename`.
- `SRC/analyzer/deep_scanner.py` — фильтр + `skipped_temporary`.
- `SRC/gui_app.py` — docstring `_run_scan` (комментарий про DS_146).
- `SRC/tests/test_ds145_temporary_filter_pytest.py` — новый.
- `EXCHANGE/DS_STANDARD.md` — §6.6.24.
- `EXCHANGE/bot.log` — запись о DS_145.