# DS_CNT_014 — Отчёт

**Дата:** 03.10.2026
**Статус:** Завершён (шаги 1–8 выполнены напрямую; шаги 9–14
закрыты через DS_CNT_015, 04.10.2026).

## Что сделано (шаги 1–8)

| Шаг | Что | Результат |
|---|---|---|
| 1 | `tools\indexer\config.py` | `CHUNK_SIZE = 256`, `CHUNK_OVERLAP = 64`, `SCHEMA_VERSION = 2`, `LARGE_FILE_LIMITS` (.json/.sql > 50 KB) |
| 2 | `tools\indexer\reader.py` | фильтр `LARGE_FILE_LIMITS` перед чтением |
| 3 | `.continueignore` | заменён на финальный список |
| 4 | Старый индекс удалён | `logs\indexer\*` |
| 5 | Переиндексация | `python -m tools.indexer.cli index --full` + инкрементальный догон |
| 6 | Статистика | Files: 29, Chunks: 160, NPY: 160×768 |
| 7 | Качество поиска | «rate limit Ollama» → top-3 релевантных (см. «Результат») |
| 8 | «Не пишет вне logs» | индексация создала файлы только в `logs\indexer\` |

## Что проверено

- Ollama (порт 11434) отвечает, `nomic-embed-text:latest` доступна (dim=768).
- Список индексируемых файлов: 29 (без SRC, tools, temp, reports, INBOX, OUTBOX, .github).
- Исключения работают: `ALGORITHM_FLOWCHART.md` — исключён, `ALGORITHM_FLOWCHART_new.md` — нет; корневые `*.py`/`*.ps1` — исключены; `SRC/`, `tools/`, `.github/`, `INBOX/`, `.continue\config.yaml` — исключены; `.continue\rules\agents-short.md` — индексируется.
- `DATA\*.md` (корень: DS_037, DS_039) — исключены; `DATA\Рубрикатор v5\*.md` — индексируются.
- Мусора в результатах поиска — нет.

## Результат

Query «rate limit Ollama», top-3:

| # | score | файл |
|---|---|---|
| 1 | 0.585 | EXCHANGE\DS_CNT_000_regulation.md |
| 2 | 0.531 | PROJECT_STATUS\PROJECT_STATUS.md |
| 3 | 0.524 | EXCHANGE\SEC_POLICY_AI.md |

Индекс: 29 файлов / 160 чанков / 160 эмбеддингов (nomic-embed-text, dim=768).

Отклонение от ожидания задачи (~25 файлов): **29 файлов**. Лишние:
`ALGORITHM_FLOWCHART_new.md`, `EXCHANGE\DS_031_NIGHTLY.md`,
`EXCHANGE\DS_031_NIGHTLY_report.md`, `EXCHANGE\DS_054_AI-fallback_черновик.md`.

## Проблемы

1. **`--full` не уложился в 10 минут.** Rate limit 1 req/sec × 160 чанков больше
   таймаута терминала. Решение: инкрементальный догон `index` (без `--full`) —
   30 чанков за 169 сек. Итог: 160/160 embedded, код 0.
2. **`TEXT_EXTENSIONS` сужены до `.md`/`.txt`** (было 9 расширений). Иначе в индекс
   попадали корневые `*.py`/`*.json`/`*.yml`/`*.ps1` (~54 лишних файла).
3. **Добавлены `ROOT_EXCLUDE_GLOBS` и `EXCLUDE_FILES`** в `config.py` — в DS не были
   указаны явно, но необходимы для сужения до ~25 файлов (корень проекта содержит
   ~40 тестовых `.py`).
4. **`SCHEMA_VERSION = 2`** (int, было `'1'` str) — как в DS.

## Следующие шаги

**Закрыто в DS_CNT_015 (04.10.2026):**
- §9–12: CNT_REFERENCE.md v1.2 (§6, §7, §8).
- §13: DS_CNT_005c_report.md — статус «выполнено (улучшено)».
- §14: DS_CNT_000_report.md — сводная таблица (в DS_CNT_016).

- `DS_CNT_014_apply_koda_and_update_reference.md` — файл не найден
  в INBOX/PROCESSED (предположительно удалён). Не блокирует.

## Артефакты

- `F:\TO_DBI\.continueignore` — обновлён.
- `F:\TO_DBI\tools\indexer\config.py` — чанк 256/64, `SCHEMA_VERSION = 2`,
  `LARGE_FILE_LIMITS`, `EXCLUDE_DIRS` (26), `EXCLUDE_SUBPATHS`, `EXCLUDE_FILES`,
  `ROOT_EXCLUDE_GLOBS`, `TEXT_EXTENSIONS` (.md/.txt).
- `F:\TO_DBI\tools\indexer\reader.py` — фильтры `LARGE_FILE_LIMITS`,
  `EXCLUDE_FILES`, `ROOT_EXCLUDE_GLOBS`, `DATA/*.md` (только корень).
- `F:\TO_DBI\logs\indexer\chunks.db` — переиндексирован (160 чанков).
- `F:\TO_DBI\logs\indexer\embeddings.npy` — 160×768.
- `F:\TO_DBI\logs\ds_cnt_005c_index.log` — лог переиндексации.
- `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_014_report.md` — этот отчёт.