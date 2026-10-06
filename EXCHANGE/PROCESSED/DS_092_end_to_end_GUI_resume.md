# DS_092 — End-to-end проверка GUI resume (скан / фикс)

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация (тест)
**Приоритет:** высокий
**Зависит от:** DS_091, DS_091b
**Блокирует:** DS_095

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

## 1. Цель

End-to-end проверка resume в GUI: полный цикл `_run_scan` → abort → resume, `_run_fix` → abort → resume. **Только то, чего нет в `test_ds089b.py`.**

## 2. Контекст

`test_ds089b.py` (15/15 PASSED) уже покрывает:
- `_ds089b_issue_key`, `_ds089b_processed_keys`, `_ds089b_filter_processed`;
- `_abort_state` (scan + fix);
- `skip_files`, `processed_files`;
- логи resume.

DS_092 **не дублирует** эти тесты. Только новое:
- `iteration` в `_run_fix`;
- `_stop_event` set/clear;
- интеграционные сценарии A и B (2 .plp, abort, resume);
- `[T]`-строки в файлы.

## 3. Файл

`SRC\tests\test_ds092_e2e.py` — новый. По шаблону `test_ds089b.py`.

**Важно:** в новом файле **не использовать** `sys.stdout = io.TextIOWrapper(...)` на уровне модуля (см. DS_091b).

## 4. Имена (подтверждены DS_091)

| Сущность | Имя | Файл:строки |
|----------|-----|-------------|
| Метод скана | `_run_scan(deep_mode=False)` | `gui_app.py:3188` |
| Метод фикса | `_run_fix()` | `gui_app.py:3721` |
| Abort-состояние | `self._abort_state` | `gui_app.py:295` |
| Graceful stop | `self._stop_event` (threading.Event) | `gui_app.py:298` |
| Fixer iteration | `self.iteration` | `code_fixer.py:533` |

## 5. Тесты

| # | Что | Как |
|---|-----|-----|
| t1 | `_stop_event` set/clear | `set()` → `is_set()==True`; `clear()` → `False` |
| t2 | `iteration` в `_run_fix` | `fixer.iteration` не пуст, формат `YYYYMMDD_HHMMSS` |
| t3 | `iteration` в `_run_scan` | `scanner.iteration` (если есть) или `scanner` не падает |
| t4 | Сценарий A: scan + abort + resume | 2 .plp, abort после 1, resume, проверить 2-й файл |
| t5 | Сценарий B: fix + abort + resume | 2 .plp, abort после 1, resume, проверить `processed_files` |

## 6. Сценарий A (детально)

1. Создать 2 `.plp` в `SRC\tests\OUTBOX\tmp_ds092\`.
2. `DBIMigrationApp.__new__(DBIMigrationApp)` + ручная установка атрибутов (как в `test_ds089b.py`).
3. `_stop_event.set()` после 1-го файла (mock scan).
4. Проверить `_abort_state['operation'] == 'scan'`.
5. `_stop_event.clear()`, повторный `_run_scan()`.
6. Проверить `_ds089b_filter_processed` — 2-й файл не дублируется.
7. Записать `[T]`-строки в `EXCHANGE\OUTBOX\DS_092_e2e_scan.log`.

## 7. Сценарий B (детально)

1. Аналогично для `_run_fix()`.
2. Проверить `_abort_state['operation'] == 'fix'`.
3. Проверить `skip_files` → `processed_files`.
4. Записать `[T]`-строки в `EXCHANGE\OUTBOX\DS_092_e2e_fix.log`.

## 8. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). SRC **трогать можно** — только новый файл `tests\test_ds092_e2e.py`. Существующие тесты не менять. `pytest.ini` не менять.

## 9. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + разделы:

```
## Результаты тестов
- t1..t5: N/N PASSED
- Сценарий A: OK/FAIL
- Сценарий B: OK/FAIL

## Регресс
- test_ds089b.py: 15/15 PASSED (не сломан)
- test_ds089a.py: 13/13 PASSED
- test_ds077.py: 8/8 PASSED

## [T]-строки (образец)
- ...

## Расхождения с DS_091
- ...
```

## 10. Критерии успеха

- t1..t5 PASSED.
- Сценарии A и B — OK.
- `[T]`-строки записаны.
- Регресс: `test_ds089b` 15/15, `test_ds089a` 13/13, `test_ds077` 8/8.
- **`python -m pytest -v`** — 0 `ValueError` (проверка DS_091b).

## 11. Артефакты

- `SRC\tests\test_ds092_e2e.py`
- `EXCHANGE\OUTBOX\DS_092_report.md`
- `EXCHANGE\OUTBOX\DS_092_e2e_scan.log`
- `EXCHANGE\OUTBOX\DS_092_e2e_fix.log`