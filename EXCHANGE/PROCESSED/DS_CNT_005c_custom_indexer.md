# DS_CNT_005c. Свой скрипт индексации (Ollama + nomic-embed-text)

## Цель
Создать пакетный скрипт индексации для семантического поиска по
`F:\TO_DBI`, **вне Continue**. Использует Ollama (`nomic-embed-text`)
для эмбеддингов и локальное хранилище (SQLite + numpy) для индекса.
Назначение — пакетный (ночной) режим, которого нет в Continue.

**Важно:** этот индекс **не используется** Continue `@codebase`.
Это отдельный инструмент. Continue `@codebase` индексируется вручную
(DS_CNT_005b). Скрипт DS_CNT_005c — для собственных задач (поиск,
анализ, отчёты).

## Предусловия
- DS_CNT_000, DS_CNT_000a выполнены.
- DS_CNT_005b выполнен (или частично — подготовка; UI-шаги отложены).
- DS_CNT_004b выполнен (или частично — подготовка; UI-шаги отложены).
- Ollama на порту 11434, `nomic-embed-text` доступна.
- Python 3.10+ установлен.
- **Согласование с ИБ — получено.** Что согласовано:
  - Python-скрипт `F:\TO_DBI\tools\indexer\`;
  - библиотеки `sqlite3` (stdlib), `numpy` (внутренний реестр);
  - запись индекса в `F:\TO_DBI\logs\indexer\`;
  - вызов Ollama `http://localhost:11434`;
  - чтение `F:\TO_DBI` (кроме исключённых);
  - логи в `F:\TO_DBI\logs`.
- Библиотеки — только из внутреннего реестра ПО банка.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7,
  включая п. 1.12 про CLI, п. 1.13 про свой индексатор).

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- Embedding — векторное представление текста.
- Indexer — скрипт индексации.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Зафиксировать согласование ИБ
В отчёте `DS_CNT_005c_report.md` указать:
- дата согласования;
- кто согласовал;
- список согласованного (см. предусловия).

### Шаг 2. Создать структуру скрипта
```
F:\TO_DBI\tools\indexer\
  __init__.py
  config.py       — конфиг (пути, модель, исключения)
  reader.py       — чтение файлов (с учётом .continueignore)
  embedder.py     — вызов Ollama (nomic-embed-text)
  store.py        — хранилище (SQLite + numpy)
  indexer.py      — основной цикл
  query.py        — поиск по индексу
  cli.py          — CLI-интерфейс
F:\TO_DBI\tools\run_cnt_005c_index.cmd   — запуск (пакетный)
```

### Шаг 3. Реализовать модули

**`config.py`:**
- корень: `F:\TO_DBI`;
- модель: `nomic-embed-text`;
- endpoint: `http://localhost:11434`;
- исключения (из `.continueignore`):
  `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `.git/`, `*.log`, `*.tmp`,
  `EXCHANGE/AI_IN/`, `EXCHANGE/AI_OUT/`, `EXCHANGE/OUTBOX/`,
  `node_modules/`, `__pycache__/`;
- хранилище: `F:\TO_DBI\logs\indexer\` (роль АРМ пишет туда);
- чанк: 512 токенов, overlap 64;
- формат: SQLite (`chunks.db`) + numpy (`embeddings.npy`);
- размер батча: 16–32 чанка; при ошибке — уменьшить, retry.

**`reader.py`:**
- рекурсивный обход `F:\TO_DBI`;
- исключения по `.continueignore`;
- чтение текстовых файлов (`.md`, `.py`, `.sql`, `.yaml`, `.json`,
  `.cmd`, `.ps1`, `.txt`);
- пропуск бинарных;
- **файлы > 1 МБ** — пропускать (зафиксировать в отчёте) или резать
  на части (по согласованию).

**`embedder.py`:**
- вызов `http://localhost:11434/api/embeddings` (Ollama);
- модель `nomic-embed-text`;
- пакетная отправка чанков (батч 16–32);
- retry при ошибке (3 попытки, пауза 5 сек);
- при ошибке батча — уменьшить размер батча, повторить.

**`store.py`:**
- SQLite:
  - `chunks(id, file, chunk_no, text, hash)`;
  - `meta(key, value)` — версия схемы, модель, дата индексации;
- numpy: `embeddings.npy` — матрица векторов;
- обновление: если файл не изменился (по хешу) — не переиндексировать;
- полная переиндексация — по флагу `--full`;
- **версионирование:** при несовпадении версии схемы или модели —
  полная переиндексация (автоматически, с записью в лог).

**`indexer.py`:**
- читает файлы;
- режет на чанки;
- считает эмбеддинги;
- сохраняет в SQLite + numpy;
- логирует в `F:\TO_DBI\logs\ds_cnt_005c_index.log`;
- код возврата в `F:\TO_DBI\logs\ds_cnt_005c.exit`.

**`query.py`:**
- принимает текст запроса;
- считает эмбеддинг;
- ищет top-K (по умолчанию 5) по косинусной близости;
- выводит файл + чанк.

**`cli.py`:**
```
python -m tools.indexer.cli index --path F:\TO_DBI [--full]
python -m tools.indexer.cli query "матрица доступа" [--top 5]
python -m tools.indexer.cli stats
```

### Шаг 4. Создать `run_cnt_005c_index.cmd`
На основе `tools\_template_nightly.cmd`:
- `:check_deps`:
  - проверка `ds_cnt_005b.exit` = 0 (код 1), **если файл есть**.
    Если 005b выполнен без скрипта — проверять `ds_cnt_005b_report.md`
    (отчёт есть). Если ни того, ни другого — код 1;
  - проверка `ds_cnt_004b.exit` = 0 (код 1) — если 004b выполнен;
  - YAML `config.yaml` (код 2);
  - Ollama и `nomic-embed-text` (код 3);
  - каталоги `logs`, `tools` (код 4);
  - запись в `logs` (код 4);
  - Python 3.10+ доступен (код 3);
- `:run_main`:
  - запуск `python -m tools.indexer.cli index --path F:\TO_DBI`;
  - лог → `F:\TO_DBI\logs\ds_cnt_005c_index.log`;
  - код → `F:\TO_DBI\logs\ds_cnt_005c.exit`.

### Шаг 5. Первый прогон (вручную)
```
F:\TO_DBI\tools\run_cnt_005c_index.cmd
```
Проверить:
- `ds_cnt_005c.exit` = 0;
- `ds_cnt_005c_index.log` заполнен;
- `F:\TO_DBI\logs\indexer\chunks.db` создан;
- `F:\TO_DBI\logs\indexer\embeddings.npy` создан;
- число чанков > 0.

**Дополнительно:** проверить, что после прогона новые/изменённые
файлы — только в `F:\TO_DBI\logs\indexer\` и `F:\TO_DBI\logs\ds_cnt_005c*`.
Ничего не появилось в `DATA/`, `EXCHANGE/`, `PATCH_IN/`, `SRC/`.
Если появилось — останов, эскалация.

### Шаг 6. Проверить поиск
```
python -m tools.indexer.cli query "матрица доступа"
python -m tools.indexer.cli query "svc_mcp"
python -m tools.indexer.cli query "logs vs bot.log"
```
Ожидаемо (top-3):
- «матрица доступа» → `SEC_POLICY_AI.md`, раздел 3;
- «svc_mcp» → `agents-short.md` / `SEC_POLICY_AI.md`;
- «logs vs bot.log» → `agents-short.md`.

Если релевантный файл не в top-3 — зафиксировать в отчёте,
пересмотреть чанки/модель.

### Шаг 7. Зарегистрировать в расписании (по согласованию)
**Только после успешного ручного прогона (шаги 5–6).**
- Ночное окно 01:00–05:00.
- После `run_cnt_005_nightly.cmd`.
- Точное время — по согласованию с Администратором АРМа.

### Шаг 8. Обновить `agents-short.md`
Добавить блок «Свой индексатор (DS_CNT_005c)»:
```markdown
## Свой индексатор (DS_CNT_005c)
- Назначение: пакетный семантический поиск по F:\TO_DBI.
- Модель: nomic-embed-text (Ollama, 11434).
- Хранилище: F:\TO_DBI\logs\indexer\ (chunks.db, embeddings.npy).
- CLI: python -m tools.indexer.cli {index|query|stats}.
- Запуск: tools\run_cnt_005c_index.cmd.
- НЕ используется Continue @codebase (там — ручная индексация).
- При ошибке — не обходить, эскалировать.
```

### Шаг 9. Обновить регламент
В `DS_CNT_000_regulation.md` добавить п. 1.13:

```markdown
1.13. **Свой индексатор.** Для пакетного семантического поиска
используется собственный скрипт `tools\indexer\` (Ollama +
nomic-embed-text). Индекс — `F:\TO_DBI\logs\indexer\`. Не путать
с Continue @codebase (там — ручная индексация в UI).
```

**Примечание:** пункт 1.13 добавляется **после** 1.12 (DS_CNT_005b).
Если 005b не выполнен — добавить оба пункта (1.12 и 1.13) в 005c.
Не дублировать.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Библиотеки — только из внутреннего реестра ПО банка.
- Скрипт не пишет вне `F:\TO_DBI\logs` и `F:\TO_DBI\PATCH_OUT`.
- Не индексировать `logs/`, `PATCH_IN/`, `PATCH_OUT/`, `.git/`, `*.log`.

## Артефакты
- `F:\TO_DBI\tools\indexer\` — модули скрипта.
- `F:\TO_DBI\tools\run_cnt_005c_index.cmd` — запуск.
- `F:\TO_DBI\logs\indexer\chunks.db` — индекс.
- `F:\TO_DBI\logs\indexer\embeddings.npy` — вектора.
- `F:\TO_DBI\logs\ds_cnt_005c_index.log`, `ds_cnt_005c.exit`.
- `.continue/rules/agents-short.md` — дополнен.
- `EXCHANGE\DS_CNT_000_regulation.md` — дополнен (п. 1.13).
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_005c_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. Согласование ИБ зафиксировано в отчёте.
2. `tools\indexer\` создан, модули реализованы.
3. `run_cnt_005c_index.cmd` создан и проверен.
4. Индекс создан (`chunks.db`, `embeddings.npy`), число чанков > 0.
5. Поиск работает: релевантный файл в top-3.
6. Регистрация в расписании — после успешного ручного прогона.
7. `agents-short.md` дополнен.
8. `DS_CNT_000_regulation.md` дополнен (п. 1.13).
9. Отчёт `DS_CNT_005c_report.md` в OUTBOX.