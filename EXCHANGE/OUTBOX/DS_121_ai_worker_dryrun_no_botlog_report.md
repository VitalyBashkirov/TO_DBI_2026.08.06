# DS_121 — отчёт: ai_local_worker dry-run не пишет в bot.log

**Статус:** Выполнено вручную PowerShell (KODA не запускалась).
**Дата:** 09.10.2026 01:24:55

## Что сделано

- Найдена причина засорения bot.log (145 записей "DS 082b: AI_REQUEST_test.md: dry-run...").
- Источник: pytest test_ds094_resume.py (t4, t7) -> run_request(..., dry_run=True) -> log(..., bot=True).
- Правка: tools/ai_local_worker.py L757: bot=True -> bot=False.

## Изменённые файлы

- tools/ai_local_worker.py (1 строка, L757)

## Проверка (§5)

1. bot=True (вызовы): L844, L847 — 2 совпадения (ожидалось 2).
   L109 — docstring, не считается.
2. bot=False (вызовы): L757 — 1 совпадение (ожидалось 1).
   L108 — сигнатура функции, не считается.
3. BOM: False.
4. pytest test_ds094_resume.py: 8 passed, exit code 0.
5. git status ДО теста: M tools/ai_local_worker.py.
   git status ПОСЛЕ теста: M tools/ai_local_worker.py (bot.log НЕ тронут).
6. git diff: одна строка (bot=True -> bot=False).

## Ожидаемый результат

- bot.log больше не растёт при прогоне test_ds094_resume.py.
- Реальные прогоны (L844, L847) — по-прежнему пишут в bot.log.

## Задание

EXCHANGE\PROCESSED\DS_121_ai_worker_dryrun_no_botlog.md