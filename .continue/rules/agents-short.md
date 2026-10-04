# TO_DBI. Правило для Ai-Continue (CNT)

## Роль
CNT (Ai-Continue) — помощник в редакторе (Chat / Edit / Apply /
Autocomplete / Embed). НЕ исполнитель. Исполнитель DS — KODA.
CNT не пишет вне разрешённых каталогов, не делает git без указания.

## Контекст проекта
- Проект TO_DBI. АРМ «Адаптация под DBI».
- Перевод PL/SQL (Oracle) -> PostgreSQL (DBI).
- Репозиторий F:\TO_DBI, ветка feature/dockerization.

## Ссылки
- EXCHANGE\DS_STANDARD.md — стандарт DS.
- EXCHANGE\DS_FILES.md, DS_CONTEXT.md — файлы и контекст.
- EXCHANGE\DS_089b_report.md — шаблон отчёта.
- EXCHANGE\test_ds089b.py — шаблон unittest.
- EXCHANGE\DS_CNT_000_regulation.md — регламент ночных задач.
- AGENTS.md — инструкция KODA (справочник).

## Формат DS (Text Copy Download)
Два блока: имя файла (code-блок) + содержимое DS.
Без прогноза KODA.

## Регламент
- Логи операций АРМа — F:\TO_DBI\logs.
- Лог АРМа — F:\TO_DBI\EXCHANGE\bot.log.
- Отчёты — F:\TO_DBI\EXCHANGE\OUTBOX\.
- GIT — только по запросу.
- SRC не трогать без указания.
- LM Studio + Ollama одновременно — запрещено.
- Пакетный режим — без интерактива.

## Матрица доступа (роль АРМ)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Запреты
- Не формировать DS на правку SRC, ai_local_worker, rule_based_fixer,
  scanner, code_fixer.
- Не дублировать задачи чата 9 (DS_090).
- Не использовать внешние AI.

## MCP (когда будет включён)
- Локальные MCP: shell (allow-list), git (read-only),
  filesystem (rw: logs, PATCH_OUT; ro: DATA, EXCHANGE, PATCH_IN).
- Внешние MCP запрещены.
- CNT не пишет в DATA, EXCHANGE, PATCH_IN.
- CNT не делает git push/commit без указания.

## Ограничения ИБ (кратко)
- Локальные модели (Ollama, 11434) и локальные MCP-серверы.
- Внешние AI и облачные MCP — запрещены.
- Логи — F:\TO_DBI\logs. Лог АРМа — EXCHANGE\bot.log.
- При отказе — не обходить, эскалировать.
- Пакетный режим: EXCHANGE\DS_CNT_000_regulation.md.


## Ограничения ИБ (кратко)
- Локальные модели (Ollama, 11434) и локальные MCP-серверы.
- Внешние AI и облачные MCP — запрещены.
- MCP: shell (allow-list), git (read-only),
  filesystem (rw: logs, PATCH_OUT; ro: DATA, EXCHANGE, PATCH_IN).
- CNT не пишет в DATA, EXCHANGE, PATCH_IN.
- CNT не делает commit/push/checkout без указания.
- CNT не читает SRC, .git, секреты, системные каталоги.
- SRC, ai_local_worker, rule_based_fixer, scanner, code_fixer — не трогать.
- Логи — F:\TO_DBI\logs. Лог АРМа — EXCHANGE\bot.log.
- LM Studio + Ollama одновременно — запрещено.
- Пакетный режим — без интерактива.

Полная политика ИБ: EXCHANGE\SEC_POLICY_AI.md.


## MCP — конкретика (DS_CNT_004)
- MCP shell — только allow-list команд.
- MCP git — только read-only.
- MCP filesystem: rw — logs, PATCH_OUT; ro — DATA, EXCHANGE, PATCH_IN.
- Запись в DATA, EXCHANGE, PATCH_IN — запрещена.
- MCP-серверы запускаются под учёткой `svc_mcp`.
- При отказе MCP — не обходить, эскалировать.


## Индексация @codebase
- Индексируется: F:\TO_DBI (кроме .continueignore).
- Embed-модель: nomic-embed-text (Ollama, 11434).
- Исключено: logs/, PATCH_IN/, PATCH_OUT/, .git/,
  EXCHANGE/AI_IN|AI_OUT|OUTBOX, *.log.
- Лог: F:\TO_DBI\logs\ds_cnt_005_index.log.
- При ошибке — не обходить, эскалировать.


## @codebase — ограничения (текущая версия Continue)
- В текущей версии Continue индекс @codebase не построен.
- @codebase работает «по памяти» модели: может ссылаться
  на несуществующие файлы (галлюцинации).
- Для точных данных — читать SEC_POLICY_AI.md, agents-short.md,
  DS_STANDARD.md напрямую.
- Для пакетного поиска — свой индексатор (DS_CNT_005c,
  tools\indexer\).
- @codebase — использовать с проверкой результата.
- При ссылке на файл — проверить его существование:
  `Get-ChildItem -Recurse -Filter "<имя>"`.

- F: — NTFS. ACL применены для `svc_mcp`: rw — logs, PATCH_OUT;
  ro — DATA, EXCHANGE, PATCH_IN; нет доступа — SRC, .git.
- `svc_mcp` — вне групп.
- svc_mcp — служебная учётка для MCP-серверов.


## Пакетные скрипты (DS_CNT_006)
- Скрипты этапов: `tools\run_cnt_<NNN>_nightly.cmd`.
- Старые скрипты: `tools\_archive\`.
- Логи: `logs\ds_cnt_<NNN>.log`.

- CLI `ai-continue` отсутствует в публичной версии Continue;
- индексация -- вручную в UI Continue (Settings -> Index);
- Task Scheduler для 005b -- не применять;
- пакетный режим -- отложен (DS_CNT_005c).

- MCP-серверы: проверка -- в UI Continue (Settings -> MCP Servers);
- CLI `ai-continue` отсутствует (п. 1.12 регламента).

## Свой индексатор (DS_CNT_005c)
- Назначение: пакетный семантический поиск по F:\TO_DBI.
- Модель: nomic-embed-text (Ollama, 11434).
- Хранилище: F:\TO_DBI\logs\indexer\ (chunks.db, embeddings.npy).
- CLI: python -m tools.indexer.cli {index|query|stats}.
- Запуск: tools\run_cnt_005c_index.cmd.
- НЕ используется Continue @codebase (там - ручная индексация).
- При ошибке - не обходить, эскалировать.
- Массовый прогон: ночной режим (rate limit 1 req/sec).


## Модели Ollama (allow-list)
- Продуктив (CNT): qwen2.5-coder:7b, qwen2.5-coder:1.5b-base,
  nomic-embed-text.
- Pipeline (ночные задачи CNT):
  - qwen2.5-coder:3b — OK (check-standard, explain-log).
    Компромисс между качеством и скоростью.
- Разработка/тест: llama3.1:8b, deepseek-coder:6.7b — используются
  разработчиком АРМа, KODA, ai_local_worker на этапах разработки
  и тестирования.
- Примечание: qwen2.5-coder:1.5b удалена (устарела, слабое качество).
- В продуктивном AI-контуре CNT используются только модели продуктив.
- Разработка/тест — вне CNT, по согласованию с ИБ.
