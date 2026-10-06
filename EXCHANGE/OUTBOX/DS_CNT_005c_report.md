# DS_CNT_005c — Отчёт

**Дата:** 03.10.2026
**Статус:** Выполнено (улучшено, DS_CNT_014/015). Индекс: 26 файлов, 156 чанков.

## Что сделано
1. Согласование ИБ — получено (зафиксировано в предусловиях).
2. `tools\indexer\` создан: config.py, reader.py, embedder.py,
   store.py, indexer.py, query.py, cli.py.
3. `tools\run_cnt_005c_index.cmd` создан.
4. Тест: Ollama + nomic-embed-text работает (3/3, dim=768).
5. agents-short.md дополнен (секция «Свой индексатор»).
6. DS_CNT_000_regulation.md дополнен (п. 1.13).

## Что проверено
- Ollama отвечает: dim=768.
- SQLite + numpy: структура создана.
- CLI: `python -m tools.indexer.cli {index|query|stats}`.

## Детали тестового прогона
- Число файлов при тестовом прогоне: 3 (тестовые).
- `chunks.db` создан: да (`F:\TO_DBI\logs\indexer\chunks.db`).
- `embeddings.npy` создан: нет (при тестовом прогоне 3 файлов
  embeddings хранятся в chunks.db, отдельный .npy не генерировался).
- Размер индекса: `chunks.db` ≈ 48 КБ (3 записи).
- Результат `stats`: 3 chunks, dim=768, модель nomic-embed-text:latest.

## Результат
Скрипт готов. Массовый прогон (1003 файла) — ночной режим
(Ollama нестабильна при нагрузке >50 запросов подряд).

## Проблемы
- Ollama nomic-embed-text нестабильна при массовой загрузке
  (>50 запросов подряд — падает/зависает).
- Решение: rate limit 1 req/sec в ночном режиме (п. 1.14 регламента).

## Следующие шаги
1. Настроить ночной прогон с rate limit (run_cnt_005c_index.cmd).
2. Зарегистрировать в Task Scheduler (01:00–05:00).
3. После успешного ночного прогона — проверить query, обновить статус.


## Состояние Ollama (03.10.2026)

### Продуктив (CNT)
- qwen2.5-coder:7b — OK (allow-list, продуктив).
- qwen2.5-coder:1.5b-base — OK (allow-list, продуктив).
- nomic-embed-text:latest — OK (allow-list, продуктив).

### Разработка/тест
- qwen2.5-coder:1.5b — OK (разработка/тест, разработчик АРМа,
  KODA, ai_local_worker).
- llama3.1:8b — OK (разработка/тест).
- deepseek-coder:6.7b — OK (разработка/тест).

Решение: оставить как есть.
Обоснование: модели разработки/теста используются разработчиком
АРМа, KODA, ai_local_worker. В продуктивном AI-контуре CNT —
только модели продуктив.
Зафиксировано в: agents-short.md (блок «Модели Ollama»).

---

## Обновление DS_CNT_014/015 (04.10.2026)

### Изменения в config.py
- `CHUNK_SIZE = 256` (было 512)
- `CHUNK_OVERLAP = 64`
- `SCHEMA_VERSION = 2` (было `'1'`)
- `LARGE_FILE_LIMITS`: `.json`/`.sql` > 50 KB — пропуск
- `TEXT_EXTENSIONS = {'.md', '.txt'}` (было 9 расширений)
- `EXCLUDE_DIRS`: 26 записей (+SRC, tools, INBOX, OUTBOX, PROCESSED, .github...)
- `EXCLUDE_FILES`: +DS_031_NIGHTLY*, DS_054_AI-fallback_черновик.md
- `ROOT_EXCLUDE_GLOBS`: *.py, *.ps1, *.yml, *.json, *.txt, *.cmd, *.sh (корень)

### Изменения в reader.py
- Фильтр `LARGE_FILE_LIMITS` перед чтением
- `EXCLUDE_FILES` — точные пути
- `ROOT_EXCLUDE_GLOBS` — не-MD в корне
- `DATA/*.md` — только корень DATA (подкаталоги индексируются)

### Переиндексация
- `--full`: 26 файлов, 156 чанков, 0 ошибок, код 0
- Время: ~900 сек (rate limit 1 req/sec)

### Качество поиска (после DS_CNT_015)
| Запрос | Топ-1 | Критерий |
|---|---|---|
| «матрица доступа» | SEC_POLICY_AI.md chunk 3 | ✅ top-1 |
| «статус проекта» | PROJECT_STATUS.md chunk 0 | ✅ top-1 |
| «как оформить DS» | DS_STANDARD.md chunk 0 | ✅ top-1 |
| «svc_mcp» | SEC_POLICY_AI.md chunk 3 | ✅ top-1 |
| «exFAT» | DS_CNT_000_regulation.md chunk 4 | ✅ top-1 |
| «rate limit» | DS_CNT_000_regulation.md chunk 1 | ✅ top-1 |

### Исследование SEC_POLICY_AI.md, раздел 3
- Файл в индексе: **да** (4 чанка).
- Чанк 0 содержит «## 3. Матрица доступа TO_DBI» + таблицу.
- Таблица **разорвана** между чанками 0/1 (overlap 64 слов не спасает).
- Корректировка (аннотация перед таблицей) — **ухудшила** результат
  (top-2 → top-5). Откат. **Решение: Вариант C — оставить как есть.**
  Матрица в top-1 — приемлемо. Для точного ответа CNT читает
  SEC_POLICY_AI.md напрямую.