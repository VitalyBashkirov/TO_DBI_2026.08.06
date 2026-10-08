# DS_121 — ai_local_worker: dry-run не пишет в bot.log

## Контекст

EXCHANGE\bot.log засорён 145 записями "DS 082b: AI_REQUEST_test.md: dry-run..."
(период 28.09–08.10.2026). Источник — pytest test_ds094_resume.py (t4, t7),
который вызывает run_request(..., dry_run=True).

При --dry-run реальной работы нет (Ollama не запрошена, AI_RESPONSE не создан),
но воркер всё равно пишет итоговую строку в bot.log через log(..., bot=True).

## Файл

F:\TO_DBI\tools\ai_local_worker.py

## Правка

Найти (L756–757):

        log(f'{request_path.name}: dry-run — {len(batches)} батч(ов), '
            f'Ollama не запрошена, AI_RESPONSE не создан', bot=True)

Заменить на:

        log(f'{request_path.name}: dry-run — {len(batches)} батч(ов), '
            f'Ollama не запрошена, AI_RESPONSE не создан', bot=False)

Изменение: bot=True → bot=False (строка L757).

## Что НЕ менять

- L125 (fh.write(f'[{stamp}] DS 082b: {text}\r\n')) — НЕ трогать.
  Это метка для реальных прогонов (L844, L847), работает корректно.
- L844, L847 (bot=True) — НЕ трогать.
- Комментарии, docstrings — НЕ трогать.

## Ограничения

- Сохранить кодировку UTF-8 без BOM.
- Не менять другие файлы.
- Одна замена — ровно bot=True → bot=False на L757.

## Проверка (§5 обязателен)

1. Select-String -LiteralPath F:\TO_DBI\tools\ai_local_worker.py -Pattern "bot=True" -SimpleMatch
   → должно быть 2 совпадения (L844, L847), не 3.
2. Select-String -LiteralPath F:\TO_DBI\tools\ai_local_worker.py -Pattern "bot=False" -SimpleMatch
   → должно быть 1 совпадение (L757).
3. BOM-check tools\ai_local_worker.py → BOM = False.
4. Тест на засорение:
   - git status -sb → clean.
   - python -m pytest SRC\tests\test_ds094_resume.py -q → OK.
   - git status -sb → clean (bot.log НЕ изменился). ← ключевая проверка
5. git diff -- tools/ai_local_worker.py → одна строка (bot=True → bot=False).

## Ожидаемый результат

- bot.log больше не растёт при прогоне test_ds094_resume.py.
- Реальные прогоны (L844, L847) — по-прежнему пишут в bot.log.