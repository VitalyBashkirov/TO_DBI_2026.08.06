# DS_100a — Graceful `KeyboardInterrupt` в `tools\indexer\cli.py`

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация (fix)
**Приоритет:** высокий
**Зависит от:** DS_100 (разведка). Task Scheduler уже изменён (Vitaly, от админа).
**Блокирует:** следующий ночной прогон CNT (06.10.2026 01:00) — для защиты от редких прерываний

**См.:** `DS_STANDARD.md`, `CNT_REFERENCE.md` (§7).

## 1. Цель

Добавить в `tools\indexer\cli.py` обработку `KeyboardInterrupt` — graceful завершение при Ctrl+C. Даже если задача прервётся (shutdown, сигнал ОС, случайное закрытие дочернего окна), индексатор **завершится корректно** и `ds_cnt_005c.exit` **будет записан**.

## 2. Контекст (уже сделано)

**Vitaly, от админа, применил Task Scheduler:**
- `LogonType = S4U` (окно cmd больше не создаётся).
- `DisallowStartIfOnBatteries = False`.
- `StopIfGoingOnBatteries = False`.
- `StartWhenAvailable = True`.
- `WakeToRun = True`.
- `ExecutionTimeLimit = PT4H`.

**Подтверждено:** `Get-ScheduledTask` показывает `S4U` и все флаги.

**Остаётся `cli.py`** — защита от **редких** случаев Ctrl+C (shutdown системы, сигнал от ОС, ручное вмешательство).

## 3. Что менять

**Файл:** `F:\TO_DBI\tools\indexer\cli.py`

**Точка входа** (определить точно при реализации):
- найти `if __name__ == '__main__':`
- найти `def main()` / `def dispatch()`

**Что добавить:**

```python
def main():
    try:
        # существующая логика (argparse + вызов index/query/stats)
        return 0
    except KeyboardInterrupt:
        # DS_100a: graceful exit при Ctrl+C (аналог SIGINT — 130)
        print("\n[DS_100a] Interrupted by user (Ctrl+C / window close)", flush=True)
        return 130
```

**Что НЕ делать:**
- Не менять логику `index`, `query`, `stats`.
- Не трогать `argparse`-конфигурацию.
- Только обернуть в `try/except`.

**Если в `cli.py` уже есть `try/except`** — добавить ветку `except KeyboardInterrupt` в существующий блок.

## 4. Проверка

| # | Что | Как |
|---|-----|-----|
| t1 | Syntax check | `python -m py_compile tools\indexer\cli.py` |
| t2 | Ctrl+C | `python -m tools.indexer.cli index --path F:\TO_DBI` → Ctrl+C → exit 130 |
| t3 | `.exit` записан | После Ctrl+C — проверить `logs\ds_cnt_005c.exit` |
| t4 | Норма | `python -m tools.indexer.cli stats` — работает |
| t5 | Регресс `pytest` | 57 PASSED (не сломан) |

## 5. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). Менять **только** `tools\indexer\cli.py`. Task Scheduler **не трогать** (уже изменён). SRC не трогать.

## 6. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + разделы:

```
## Diff cli.py
- Добавлен try/except KeyboardInterrupt в main
- Строки: <N–M>

## Проверка
- py_compile: OK
- Ctrl+C: exit 130
- .exit записан
- stats: работает
- pytest: 57 PASSED
```

## 7. Критерии успеха

- `py_compile` — без ошибок.
- Ctrl+C → exit 130, `ds_cnt_005c.exit` записан.
- `stats` работает.
- `pytest -v` — 57 PASSED.

## 8. Артефакты

- `tools\indexer\cli.py` (изменён)
- `EXCHANGE\OUTBOX\DS_100a_report.md`