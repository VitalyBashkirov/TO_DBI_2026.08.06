# DS_140 — Отчёт: pytest-миграция legacy-тестов

**Дата:** 2026-10-11
**Автор:** DeepSeek
**Пользователь:** Vitaly
**Статус:** Закрыт

## Что сделано

Переведены два legacy-теста с самописного runner на pytest.
Legacy-файлы сохранены как `.py.txt` (референс, pytest их не собирает).

| Legacy | Pytest-версия | Тестов |
|--------|---------------|--------|
| test_ds133_buttons_state.py | test_ds133_buttons_state_pytest.py | 18 |
| test_ds086_ui_hide.py | test_ds086_ui_hide_pytest.py | 15 |

## Новые файлы

- `SRC/tests/conftest.py` — общие фикстуры.
- `SRC/tests/test_ds133_buttons_state_pytest.py` — 18 тестов.
- `SRC/tests/test_ds086_ui_hide_pytest.py` — 15 тестов.

## Переименованные (git mv)

- `SRC/tests/test_ds133_buttons_state.py` → `.py.txt`
- `SRC/tests/test_ds086_ui_hide.py` → `.py.txt`

## Фикстуры (conftest.py v4)

- `app` (scope=function): Tk + DBIMigrationApp, гарантированный destroy.
- `isolated_ai`: monkeypatch `_ai_in_request_files` / `_ai_out_files` → tmp_path.
- `settings_backup`: backup/restore `SRC/settings.json` через `.ds140bak`.
- `patched_messagebox` (autouse, session): диалоги → noop.

Monkeypatch в `app`:
- `log` → noop (не пишем в `logs_Deep`).
- `_check_log_size` → noop (вызывается в `__init__`).
- `_poll_ai_out` → noop (5-секундный таймер, страховка).

Фикс TclError:
- `_cancel_all_after(root)` — отмена pending `after` перед `destroy()`.

## Результаты

| Метрика | Значение |
|---------|----------|
| pytest полный | **110 passed** |
| exit code | 0 |
| Старых тестов | 77 |
| Новых тестов | 33 (18 + 15) |
| BOM у новых файлов | False |
| `ast.parse` | OK |
| `logs_Deep` | не выросло |
| `settings.json` | восстановлен |

## Проблемы и решения

### 1. TclError: `invalid command name "..._poll_ai_out"`

**Причина:** pending `after(5000, _poll_ai_out)` после `root.destroy()`.

**Решение (v3 conftest):**
- `_cancel_all_after(root)` — отмена всех pending `after` перед destroy.
- monkeypatch `_poll_ai_out` → noop.

### 2. `Рубрикатор v5` — кириллица в путях

PS `Test-Path` с кириллицей в имени папки может врать.
**Решение:** проверять через Python `Path.exists()`.

### 3. `settings.json` — реальный файл

DS_086 работает с `SRC/settings.json`.
**Решение:** фикстура `settings_backup` (Вариант A — backup/restore через `.ds140bak`).

### 4. `--capture=no` в pytest.ini

`print` из `_load_rubricator_prompts` виден в консоли (18/15/77 раз).
Безвредно, но шумно. Решение не требуется.

## Уроки

- **LLL:** Активный транскрипт в `PS\` блокирует N7-очистку → N7 v2 обход.
- **MMM:** Tkinter `after()` в pytest → TclError после destroy.
- **NNN:** Кириллица в PS-путях — проверять через Python.
- **OOO:** `trace_add('write', ...)` → side-effects при `.set()` в тестах.
- **PPP:** `pytest.ini --capture=no` → `print` из legacy виден.

## Артефакты

- Задание: `EXCHANGE\PROCESSED\DS_140_pytest_migration.md`
- Отчёт: `EXCHANGE\OUTBOX\DS_140_pytest_migration_report.md`
- Логи PS: `PS\DS_140_step*.log`

## Итог

Миграция завершена. Все legacy-тесты живут в pytest-стиле,
единый `pytest SRC\tests\` даёт 110 passed. Legacy сохранён для сверки.