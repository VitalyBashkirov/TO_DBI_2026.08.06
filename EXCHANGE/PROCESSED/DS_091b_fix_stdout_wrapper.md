# DS_091b — Фикс 7 тестовых файлов: обернуть `sys.stdout` в `if __name__ == '__main__':`

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация (инфраструктура)
**Приоритет:** высокий
**Зависит от:** DS_091a
**Блокирует:** DS_092 (e2e)

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

## 1. Цель

Устранить баг: 7 тестовых файлов на уровне модуля заменяют `sys.stdout` → pytest при сборе каталога `SRC\tests\` падает на `terminalwriter` с `ValueError: I/O operation on closed file`.

**Результат:** `python -m pytest -v` из корня проекта собирает **все** тесты без `ValueError`.

## 2. Причина (подтверждено разведкой)

7 файлов содержат на уровне модуля:
```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

После замены `sys.stdout` pytest теряет свой capture-буфер (terminalwriter смотрит на **старый** `sys.stdout`). При сборе каталога → `ValueError`.

`test_ds089a.py`, `test_ds089b.py` — без этой строки, работают всегда.

## 3. Что менять

В каждом из 7 файлов **заменить строку**:

```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

**на две строки:**

```python
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

**Отступ:** 4 пробела.

## 4. Файлы

| # | Файл | Строка |
|---|------|--------|
| 1 | `SRC\tests\test_ds056_is_in_comment.py` | 15 |
| 2 | `SRC\tests\test_ds077.py` | 14 |
| 3 | `SRC\tests\test_ds086_ui_hide.py` | 22 |
| 4 | `SRC\tests\test_ds087_workflow.py` | 21 |
| 5 | `SRC\tests\test_ds088a_ai_cycle.py` | 18 |
| 6 | `SRC\tests\test_ds088a_fix.py` | 11 |
| 7 | `SRC\tests\test_ds088b.py` | 14 |

## 5. Что НЕ трогать

- `test_ds089a.py`, `test_ds089b.py` — работают без фикса.
- `pytest.ini` — создан в DS_091a, **не менять**.
- `__pycache__`, `.pytest_cache` — восстановятся автоматически.
- **Существующий** `if __name__ == '__main__':` в конце файлов (155, 218, 267, 209, 242, 226) — **не трогать**, там `print`/`main()`.

## 6. Проверка

| # | Команда | Ожидание |
|---|---------|----------|
| 1 | `cd F:\TO_DBI` + `python -m pytest -v` | Все тесты, **0** `ValueError` |
| 2 | `python -m pytest SRC\tests\test_ds077.py -v` | 8/8 PASSED |
| 3 | `python -m pytest SRC\tests\test_ds089b.py -v` | 15/15 PASSED |
| 4 | `python -m pytest SRC\tests\test_ds089a.py -v` | 13/13 PASSED |
| 5 | `python SRC\tests\test_ds077.py` | Прямой запуск — 8 OK |

## 7. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). Менять **только** 7 файлов, **только** указанную строку. Логику тестов не трогать.

## 8. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + разделы:

```
## Diff по файлам
| Файл | Строка до | Строка после |
|------|-----------|--------------|

## Прогон `python -m pytest -v`
<сколько собрано, сколько PASSED, сколько FAILED>

## Регресс
- test_ds089b: N/15
- test_ds089a: N/13
- test_ds077: N/8

## Прямой запуск
python SRC\tests\test_ds077.py → 8 OK
```

## 9. Критерии успеха

- `python -m pytest -v` — **0** `ValueError`.
- Все тесты собраны (≥ 9 файлов).
- `test_ds089b` — 15/15.
- `test_ds077` — 8/8.
- Прямой запуск `python SRC\tests\test_ds077.py` — 8 OK.

## 10. Артефакты

- 7 файлов в `SRC\tests\` (изменены)
- `EXCHANGE\OUTBOX\DS_091b_report.md`