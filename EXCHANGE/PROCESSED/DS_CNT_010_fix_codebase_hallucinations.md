# DS_CNT_010. Фиксация @codebase-галлюцинаций и оговорка в agents-short.md

## Цель
Зафиксировать факт: `@codebase` в текущей версии Continue **не индексирован**
и **галлюцинирует** (ссылается на несуществующие файлы). Добавить оговорку
в `agents-short.md` и обновить `DS_CNT_005b_report.md`.

## Предусловия
- DS_CNT_009 выполнен (модели Ollama, правки отчётов, rate limit).
- DS_CNT_005b выполнен частично (UI-шаги).
- Проверено: `@codebase` возвращает ссылку на `EXCHANGE/DS_CNT_004.md`
  — файла не существует.
- `Get-ChildItem -Recurse -Filter "*DS_CNT*"` показал: в `EXCHANGE\` —
  только `DS_CNT_000_regulation.md`; остальные — в `INBOX\`, `OUTBOX\`,
  `PROCESSED\`.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md`.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- `@codebase` — семантический поиск в Continue.
- Галлюцинация — ответ модели со ссылкой на несуществующий объект.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Обновить `DS_CNT_005b_report.md`
Добавить раздел «Состояние @codebase»:

```markdown
## Состояние @codebase (03.10.2026)

### Проверка
- `@codebase` доступен в чате Continue (Agent mode, tool use).
- Раздел Index в Settings отсутствует.
- Запрос «Где описана матрица доступа TO_DBI?» → ответ:
  `EXCHANGE/DS_CNT_004.md`.
- Файл `DS_CNT_004.md` не существует.
- `Get-ChildItem -Recurse -Filter "*DS_CNT*"`:
  - `EXCHANGE\` — только `DS_CNT_000_regulation.md`;
  - `EXCHANGE\INBOX\` — `DS_CNT_009_*.md`;
  - `EXCHANGE\OUTBOX\` — 15 отчётов;
  - `EXCHANGE\PROCESSED\` — 11 заданий.

### Вывод
- `@codebase` **не индексирован** (или индексирован неполно).
- Continue работает «по памяти» модели, не по индексу.
- Модель **галлюцинирует** — ссылается на несуществующие файлы.
- Отдельная кнопка «Index» в Settings отсутствует (норма для версии).

### Рекомендация
- Для точных данных — читать `SEC_POLICY_AI.md`, `agents-short.md`,
  `DS_STANDARD.md` напрямую.
- Для пакетного семантического поиска — свой индексатор
  (`tools\indexer\`, DS_CNT_005c).
- `@codebase` — только как вспомогательный инструмент,
  с проверкой результата.

### Статус
- DS_CNT_005b: **выполнено частично** (с оговоркой).
```

### Шаг 2. Обновить `agents-short.md`
Добавить в блок «Ограничения ИБ (кратко)» (или отдельным блоком
«@codebase — ограничения»):

```markdown
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
```

Если блок «Ограничения ИБ (кратко)» отсутствует — создать его.

### Шаг 3. Обновить `DS_CNT_000_report.md`
В сводной таблице уточнить статус 005b:

| DS | Статус | Код | Отчёт |
|---|---|---|---|
| 005b | Выполнено частично | 0 | DS_CNT_005b_report.md |

Примечание: `@codebase` галлюцинирует; индекс не построен.
Для точных данных — читать файлы напрямую; для пакетного поиска —
свой индексатор (005c).

### Шаг 4. Проверить консистентность
- `agents-short.md` — блок «@codebase — ограничения» присутствует.
- `DS_CNT_005b_report.md` — раздел «Состояние @codebase» присутствует.
- `DS_CNT_000_report.md` — статус 005b уточнён.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Не пытаться «починить» `@codebase` (в текущей версии Continue
  индекса нет).

## Артефакты
- `.continue/rules/agents-short.md` — дополнен.
- `EXCHANGE\OUTBOX\DS_CNT_005b_report.md` — обновлён.
- `EXCHANGE\OUTBOX\DS_CNT_000_report.md` — обновлён.
- `F:\TO_DBI\logs\ds_cnt_010.log`, `ds_cnt_010.exit`,
  `ds_cnt_010.err`, `ds_cnt_010.lock`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_010_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `agents-short.md` — блок «@codebase — ограничения».
2. `DS_CNT_005b_report.md` — раздел «Состояние @codebase».
3. `DS_CNT_000_report.md` — статус 005b «выполнено частично».
4. Консистентность проверена.
5. Отчёт `DS_CNT_010_report.md` в OUTBOX.