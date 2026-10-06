# DS_CNT_005a. Завершение этапа 005: установка CLI + индексация @codebase

## Цель
Завершить этап 005 (`@codebase`-индексация), который в DS_CNT_005_report
зафиксирован как «выполнено (код 0, индексация отложена)»:
- `embeddingsProvider`, `.continueignore`, `agents-short.md` — сделано;
- индексация не выполнена (CLI `ai-continue` не в PATH) — не сделано.

Этап 005a: установить/добавить в PATH CLI `ai-continue`, выполнить
индексацию, проверить `@codebase`, обновить отчёт DS_CNT_005.

## Предусловия
- DS_CNT_000 выполнен.
- DS_CNT_005 выполнен частично: `embeddingsProvider`, `.continueignore`,
  блок в `agents-short.md` — есть; индексация — нет.
- DS_CNT_004a — желательно выполнен, но не обязателен для 005a.
  Если 004a не выполнен — зафиксировать в отчёте, продолжить 005a,
  эскалировать.
- Ai-Continue установлен (GUI). CLI может быть не установлен
  или не в PATH — устанавливается/добавляется на шаге 1.
- Ollama на порту 11434, модель `nomic-embed-text` доступна.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7,
  включая п. 1.11 про exFAT).

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Проверить доступность CLI `ai-continue`
```
where ai-continue
ai-continue --version
```
Ожидаемо: путь и версия ≥ 0.9.x.

Если CLI не найден:
- найти исполняемый файл Ai-Continue CLI в каталоге установки;
- добавить в PATH (системный или пользовательский);
- повторить `where ai-continue`.

Источник CLI — внутренний реестр ПО банка (или дистрибутив
Ai-Continue). Внешние источники (npm, PyPI, GitHub) — только после
ревью ИБ. Если CLI отсутствует физически — установить (по согласованию
с Администратором АРМа).

Если CLI установить невозможно — код 3 (зависимость), останов, отчёт,
эскалация.

### Шаг 2. Проверить Ollama и embed-модель
```
ollama list
```
Ожидаемо: `nomic-embed-text`. Иначе — код 3.

### Шаг 3. Проверить `config.yaml`
Фактический путь может быть:
- `~/.continue/config.yaml` (стандартный);
- `F:\TO_DBI\.continue\config.yaml` (если Ai-Continue использует
  воркспейсный конфиг).

Зафиксировать фактический путь в отчёте. Если оба существуют —
какой используется Ai-Continue.

- `embeddingsProvider` присутствует (из DS_CNT_005).
- Порядок блоков: models → slashCommands → embeddingsProvider → mcpServers.
- YAML валиден.

Если порядок нарушен — исправить, код 2.

### Шаг 4. Проверить `.continueignore`
- Исключает `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `.git/`, `*.log`,
  `EXCHANGE/AI_IN|AI_OUT|OUTBOX`.
- `DATA/` и `EXCHANGE/` (кроме исключённых) — индексируются.

### Шаг 5. Выполнить индексацию (CLI/скрипт)
```
ai-continue index --path F:\TO_DBI
```
- без интерактива;
- stdout/stderr → `F:\TO_DBI\logs\ds_cnt_005_index.log`;
- код → `F:\TO_DBI\logs\ds_cnt_005.exit`;
- ошибки → `F:\TO_DBI\logs\ds_cnt_005.err`.

Если CLI `ai-continue` недоступен (where ai-continue пуст) — код 3
(зависимость), останов, отчёт, эскалация.
При ином ненулевом коде — останов, отчёт, эскалация.

### Шаг 6. Проверить результат индексации
```
ai-continue index status --path F:\TO_DBI
dir F:\TO_DBI\.continue\index
```
Ожидаемо: индекс создан, размер > 0.

Индекс может храниться в `~/.continue/index` или
`F:\TO_DBI\.continue\index` — фактический путь зафиксировать в отчёте.

Если CLI не поддерживает `index status` — использовать
`dir F:\TO_DBI\.continue\index` как достаточную проверку.
Способ зафиксировать в отчёте.

Проверить, что в индексе нет исключённых каталогов:
- **основной способ** — лог индексации (список проиндексированных
  файлов);
- **дополнительно** — `@codebase`-запрос (например, «Что в logs?» —
  ответ не должен ссылаться на содержимое `logs/`).

Если лог не содержит списка файлов — использовать `@codebase`-запрос
как дополнительную проверку. Если ответ ссылается на `logs/` —
зафиксировать в отчёте, перепроверить `.continueignore`.

### Шаг 7. Контрольные запросы `@codebase`
```
ai-continue chat --query "@codebase Где описана матрица доступа TO_DBI?"
ai-continue chat --query "@codebase Что такое CNT в TO_DBI?"
ai-continue chat --query "@codebase Чем logs отличается от EXCHANGE\bot.log?"
ai-continue chat --query "@codebase Какие MCP-серверы разрешены?"
```
Ожидаемо:
- матрица доступа → `SEC_POLICY_AI.md`, раздел 3;
- CNT → Ai-Continue;
- logs vs bot.log → разграничены;
- allow-list MCP → shell, git, filesystem.

Если CLI не поддерживает `chat --query` — использовать альтернативный
способ (VS Code CLI + задача). Если и это невозможно — зафиксировать,
что проверка `@codebase` отложена до ручной.

### Шаг 8. Обновить отчёт `DS_CNT_005_report.md`
Дописать:
- CLI `ai-continue` установлен/добавлен в PATH (путь, версия,
  источник);
- индексация выполнена, код 0;
- индекс создан (фактический путь);
- проверка отсутствия исключённых каталогов — результат;
- контрольные запросы `@codebase` — результаты (или способ
  альтернативной проверки).

Убрать из «Проблемы» пункт «CLI не доступен».

### Шаг 9. Зафиксировать в `agents-short.md`
В блоке «Индексация @codebase» дополнить:
- CLI `ai-continue` — путь, версия.
- Команда индексации: `ai-continue index --path F:\TO_DBI`.

Если блок «Индексация @codebase» отсутствует — создать его.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать (только CLI/скрипт).
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Не индексировать `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `.git/`, `*.log`.

## Артефакты
- CLI `ai-continue` — доступен в PATH.
- Индекс создан (путь зафиксировать).
- `EXCHANGE\OUTBOX\DS_CNT_005_report.md` — обновлён.
- `.continue/rules/agents-short.md` — дополнен.
- `F:\TO_DBI\logs\ds_cnt_005a.log`, `ds_cnt_005a.exit`,
  `ds_cnt_005a.err`, `ds_cnt_005a.lock`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_005a_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. CLI `ai-continue` доступен в PATH, версия ≥ 0.9.x.
2. Индексация выполнена, код 0.
3. Индекс создан, размер > 0 (путь зафиксирован).
4. В индексе нет исключённых каталогов (`logs/`, `PATCH_IN/`,
   `PATCH_OUT/`, `*.log`) — проверено по логу, дополнительно
   по `@codebase`.
5. Контрольные запросы `@codebase` дают корректные ответы.
   Если CLI не поддерживает `chat --query` — использовать
   альтернативный способ; если и это невозможно — зафиксировать,
   что проверка `@codebase` отложена до ручной.
6. Отчёт `DS_CNT_005_report.md` обновлён.
7. `agents-short.md` дополнен.
8. Отчёт `DS_CNT_005a_report.md` в OUTBOX.