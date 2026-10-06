# DS_CNT_005b. Ручная индексация @codebase в UI Continue

## Цель
Закрыть этап 005a (индексация `@codebase`) **без CLI** — ручной
индексацией в UI Continue. CLI `ai-continue` отсутствует в публичной
версии Continue; пакетный режим индексации отложен до DS_CNT_005c.

**Важно:** индексация в UI Continue — **только вручную**, днём.
Для ночного (пакетного) режима — DS_CNT_005c. Task Scheduler для
DS_CNT_005b **не применять**.

## Предусловия
- DS_CNT_000, DS_CNT_000a выполнены.
- DS_CNT_005 выполнен частично: `embeddingsProvider`, `.continueignore`,
  блок в `agents-short.md` — есть; индексация — нет.
- DS_CNT_004a выполнен частично (шаг 4 отложен; закрывается в DS_CNT_004b).
- Ai-Continue установлен в VS Code (GUI).
- Ollama на порту 11434, модель `nomic-embed-text` доступна.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7,
  включая п. 1.11 про exFAT, п. 1.12 про отсутствие CLI).

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- CLI `ai-continue` — отсутствует в публичной версии Continue.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Проверить Ollama и embed-модель
```
ollama list
```
Ожидаемо: `nomic-embed-text`. Иначе — код 3.

### Шаг 2. Проверить `config.yaml`
Путь: `~/.continue/config.yaml` (фактический путь зафиксировать в отчёте).

- `embeddingsProvider` присутствует (ollama / nomic-embed-text).
- Порядок блоков: models → slashCommands → embeddingsProvider → mcpServers.
- YAML валиден.

### Шаг 3. Проверить `.continueignore`
- Исключает `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `.git/`, `*.log`,
  `EXCHANGE/AI_IN|AI_OUT|OUTBOX`.
- `DATA/` и `EXCHANGE/` (кроме исключённых) — индексируются.

### Шаг 4. Открыть VS Code и Continue
- Открыть VS Code.
- Открыть воркспейс `F:\TO_DBI`.
- Открыть панель Continue.

### Шаг 5. Запустить индексацию в UI Continue
- Continue → Settings → Index (или иконка «Index» в панели).
- Нажать «Index workspace» / «Build index» (зависит от версии).
- Дождаться завершения. Прогресс — в UI.
- Если кнопки нет — в чате набрать `@codebase` и следовать подсказке
  Continue («Index your workspace»).

**Примечание:** индексация — только вручную, днём. Task Scheduler
не применять (UI не работает в фоне).

### Шаг 6. Проверить результат
- Continue → Settings → Index — статус «Indexed», число файлов > 0.
- Или: `dir ~/.continue\index` (или `F:\TO_DBI\.continue\index`) —
  размер > 0.
- Фактический путь индекса зафиксировать в отчёте.

Проверить, что в индексе нет исключённых каталогов:
- Continue → Settings → Index → «Files» (если показывает список) —
  убедиться, что `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `*.log`
  не в списке.
- Дополнительно: `@codebase`-запрос «Что в logs?» — ответ не должен
  ссылаться на содержимое `logs/`.

### Шаг 7. Контрольные запросы `@codebase` (в чате Continue)
```
@codebase Где описана матрица доступа TO_DBI?
@codebase Что такое CNT в TO_DBI?
@codebase Чем logs отличается от EXCHANGE\bot.log?
@codebase Какие MCP-серверы разрешены?
```
Ожидаемо:
- матрица доступа → `SEC_POLICY_AI.md`, раздел 3;
- CNT → Ai-Continue;
- logs vs bot.log → разграничены;
- allow-list MCP → shell, git, filesystem.

### Шаг 8. Обновить отчёт `DS_CNT_005a_report.md`
Дописать:
- CLI `ai-continue` отсутствует в публичной версии Continue
  (это факт, не ошибка);
- индексация выполнена **вручную** в UI Continue;
- индекс создан (путь, число файлов);
- контрольные запросы `@codebase` — результаты.

Изменить статус:
- было «Не выполнено (код 3, зависимость)»;
- стало «Выполнено вручную (UI Continue); пакетный режим отложен
  до DS_CNT_005c».

### Шаг 9. Зафиксировать в `agents-short.md`
В блоке «Индексация @codebase» дополнить:
- CLI `ai-continue` отсутствует в публичной версии Continue;
- индексация — вручную в UI Continue (Settings → Index);
- Task Scheduler для 005b — не применять;
- пакетный режим — отложен (DS_CNT_005c).

### Шаг 10. Обновить регламент
В `DS_CNT_000_regulation.md` добавить п. 1.12:

```markdown
1.12. **CLI Continue.** В публичной версии Continue CLI `ai-continue`
отсутствует. Индексация `@codebase` выполняется вручную в UI Continue
(Settings → Index). Task Scheduler для этой индексации не применять.
Пакетный режим индексации — через свой скрипт (DS_CNT_005c).
Проверка MCP-серверов — в UI Continue (Settings → MCP).
```

**Примечание:** если DS_CNT_005c уже выполнен и добавил п. 1.13 —
не дублировать. Пункт 1.12 добавляется **до** 1.13.

### Шаг 11. Закрыть шаг 4 DS_CNT_004a
После индексации — по возможности закрыть шаг 4 DS_CNT_004a
(проверка MCP под `svc_mcp`). Если отдельным DS — см. DS_CNT_004b.
Если в рамках 005b — зафиксировать в отчёте.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Не индексировать `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `.git/`, `*.log`.
- Task Scheduler для 005b — не применять.

## Артефакты
- Индекс создан (путь зафиксировать).
- `EXCHANGE\OUTBOX\DS_CNT_005a_report.md` — обновлён.
- `.continue/rules/agents-short.md` — дополнен.
- `EXCHANGE\DS_CNT_000_regulation.md` — дополнен (п. 1.12).
- `F:\TO_DBI\logs\ds_cnt_005b.log`, `ds_cnt_005b.exit`,
  `ds_cnt_005b.err`, `ds_cnt_005b.lock`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_005b_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. Индексация `@codebase` выполнена в UI Continue.
2. Индекс создан, число файлов > 0 (путь зафиксирован).
3. В индексе нет исключённых каталогов.
4. Контрольные запросы `@codebase` дают корректные ответы.
5. `DS_CNT_005a_report.md` обновлён (статус — «выполнено вручную»).
6. `agents-short.md` дополнен.
7. `DS_CNT_000_regulation.md` дополнен (п. 1.12).
8. Шаг 4 DS_CNT_004a — закрыт (или зафиксировано, что закрывается
   в DS_CNT_004b).
9. Отчёт `DS_CNT_005b_report.md` в OUTBOX.