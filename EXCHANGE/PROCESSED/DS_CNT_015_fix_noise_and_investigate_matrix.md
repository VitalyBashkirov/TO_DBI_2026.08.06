# DS_CNT_015. Исключить шум + исследовать SEC_POLICY_AI.md (раздел 3)

## Цель
1) Исключить из индекса шум:
   - `DS_031_NIGHTLY.md` — тестовая задача;
   - `DS_031_NIGHTLY_report.md` — тестовый отчёт;
   - `DS_054_AI-fallback_черновик.md` — черновик.
2) Исследовать, почему `SEC_POLICY_AI.md`, раздел 3 «Матрица доступа
   TO_DBI» — **не в top-1** по запросу «матрица доступа».
3) По результатам исследования — при необходимости скорректировать
   чанк / overlap / текст `SEC_POLICY_AI.md`.

## Предусловия
- DS_CNT_014 приостановлен (шаги 1–8 выполнены, шаги 9–14 отложены).
- Индекс: Files 29, Chunks 160 (переиндексация выполнена).
- `config.py`: CHUNK_SIZE=256, CHUNK_OVERLAP=64, SCHEMA_VERSION=2,
  LARGE_FILE_LIMITS.
- `reader.py`: фильтр `LARGE_FILE_LIMITS`, `EXCLUDE_FILES`,
  `ROOT_EXCLUDE_GLOBS`, `DATA/*.md` (только корень).
- `.continueignore` сужен до ~25 файлов.
- Ollama на порту 11434, `nomic-embed-text` доступна (dim=768).
- Python 3.10+.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md`.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- Чанк — фрагмент текста для эмбеддинга.
- Top-1 / Top-3 / Top-5 — позиции в результатах поиска.
- Шум — нерелевантные файлы в результатах поиска.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Добавить шум в `.continueignore`
В `F:\TO_DBI\.continueignore` добавить:

```gitignore
# === Шум в индексе ===
EXCHANGE/DS_031_NIGHTLY.md
EXCHANGE/DS_031_NIGHTLY_report.md
EXCHANGE/DS_054_AI-fallback_черновик.md
```

**Обоснование:**
- `DS_031_NIGHTLY.md` — тестовая задача ночного процесса (03.10.2026),
  забивала top-1 на запросах «матрица доступа», «как оформить DS»,
  «статус проекта».
- `DS_031_NIGHTLY_report.md` — тестовый отчёт, аналогично.
- `DS_054_AI-fallback_черновик.md` — черновик (по названию), не нужен
  в индексе.

### Шаг 2. Переиндексация
```powershell
cd F:\TO_DBI
python -m tools.indexer.cli index --full
```

**Ожидаемое время:** ~2–3 минуты (26 файлов).

**Если `--full` превышает таймаут терминала** — использовать
инкрементальный догон (по опыту DS_CNT_014):
```powershell
python -m tools.indexer.cli index
```
Повторять, пока не завершится.

**Проверка:**
```powershell
python -m tools.indexer.cli stats
```
Ожидаемо: Files ~26, Chunks ~150.

### Шаг 3. Проверить качество поиска после исключения шума

```powershell
python -m tools.indexer.cli query "матрица доступа" --top 5
python -m tools.indexer.cli query "статус проекта" --top 5
python -m tools.indexer.cli query "как оформить DS" --top 5
python -m tools.indexer.cli query "svc_mcp" --top 5
python -m tools.indexer.cli query "exFAT" --top 5
python -m tools.indexer.cli query "rate limit" --top 5
```

**Ожидаемо:**
- «матрица доступа» → `SEC_POLICY_AI.md` в top-1 или top-2;
- «статус проекта» → `PROJECT_STATUS.md` в top-1;
- «как оформить DS» → `DS_STANDARD.md` или `DS_PROJECT_CONTEXT.md`
  в top-1;
- «svc_mcp» → `SEC_POLICY_AI.md` или `agents-short.md` в top-1;
- «exFAT» → `DS_CNT_000_regulation.md` в top-1;
- «rate limit» → `DS_CNT_000_regulation.md` в top-1.

### Шаг 4. Исследовать проблему с `SEC_POLICY_AI.md`, раздел 3

**Цель:** понять, почему матрица доступа **не в top-1**.

#### 4.1. Проверить, что `SEC_POLICY_AI.md` в индексе
```powershell
python -m tools.indexer.cli query "SEC_POLICY_AI" --top 5
python -m tools.indexer.cli query "политика ИБ" --top 5
```
Ожидаемо: `SEC_POLICY_AI.md` — в top-5.

#### 4.2. Проверить, что раздел 3 (матрица) в индексе
```powershell
python -m tools.indexer.cli query "таблица матрица доступа роли" --top 10
python -m tools.indexer.cli query "Администратор АРМ ИБ" --top 10
python -m tools.indexer.cli query "logs PATCH_IN PATCH_OUT" --top 10
python -m tools.indexer.cli query "DATA EXCHANGE add del ren" --top 10
```
Ожидаемо: `SEC_POLICY_AI.md` с матрицей — в top-10.

#### 4.3. Посмотреть чанки `SEC_POLICY_AI.md`

**Вариант A — через SQLite:**
```powershell
cd F:\TO_DBI
python -c "
import sqlite3
conn = sqlite3.connect('logs/indexer/chunks.db')
cur = conn.cursor()
cur.execute(\"SELECT id, file, chunk_no, LENGTH(text) FROM chunks WHERE file LIKE '%SEC_POLICY%' ORDER BY chunk_no\")
rows = cur.fetchall()
print(f'Всего чанков SEC_POLICY_AI.md: {len(rows)}')
for row in rows:
    print(f'  id={row[0]} chunk={row[2]} len={row[3]}')
conn.close()
"
```

**Вариант B — дамп текста чанков:**
```powershell
cd F:\TO_DBI
python -c "
import sqlite3
conn = sqlite3.connect('logs/indexer/chunks.db')
cur = conn.cursor()
cur.execute(\"SELECT chunk_no, text FROM chunks WHERE file LIKE '%SEC_POLICY%' ORDER BY chunk_no\")
for chunk_no, text in cur.fetchall():
    print(f'=== chunk {chunk_no} ===')
    print(text[:500])
    print()
conn.close()
"
```

**Что искать:**
- Сколько чанков у `SEC_POLICY_AI.md`.
- Есть ли чанк с «## 3. Матрица доступа TO_DBI».
- **Не разрезан ли** чанк (таблица может быть разорвана).

#### 4.4. Сформулировать вывод

| Симптом | Причина | Решение |
|---|---|---|
| Файл не в индексе | `.continueignore` | Проверить, исправить |
| Файл в индексе, но раздел 3 — не в чанке | Чанк разрезан | Увеличить CHUNK_SIZE (256 → 384 или 512) |
| Файл в индексе, чанк есть, но не в top-10 | Слабый эмбеддинг | Увеличить CHUNK_OVERLAP; добавить текстовое описание матрицы |
| Файл в индексе, чанк есть, в top-10, но не top-1 | Шум | Исключить шум (шаг 1) |

### Шаг 5. По результатам исследования — корректировки

**Вариант A — таблица разрезана чанком.**
- **Решение:** увеличить `CHUNK_SIZE` до 384.
- **Минус:** чанк больше → точность ниже для текста.

**Вариант B — эмбеддинг слабый.**
- **Решение:** в `SEC_POLICY_AI.md` добавить **текстовое описание**
  матрицы после таблицы:
  ```markdown
  **Матрица доступа (текстом):**
  Роли: Администратор АРМа, Пользователь АРМа, АРМ, ИБ.
  Каталоги: DATA, EXCHANGE, logs, PATCH_IN, PATCH_OUT.
  Роль АРМ: чтение DATA/EXCHANGE/PATCH_IN; запись logs/PATCH_OUT.
  ```
- **Плюс:** эмбеддинг получает текст, а не только таблицу.

**Вариант C — оставить как есть.**
- Матрица в top-5 — **приемлемо**.
- Для точного ответа — CNT читает `SEC_POLICY_AI.md` напрямую.

**Решение зафиксировать в отчёте.**

### Шаг 6. Обновить отчёт `DS_CNT_005c_report.md`
Дописать:
- исключены `DS_031_NIGHTLY*`, `DS_054_AI-fallback_черновик.md`;
- переиндексация выполнена (Files ~26, Chunks ~150);
- исследование `SEC_POLICY_AI.md`, раздел 3 — выводы;
- корректировки (если были);
- статус: «выполнено (улучшено)».

### Шаг 7. Обновить `CNT_REFERENCE.md` (если нужно)
В §6 «Индексатор (свой)» — уточнить:
- исключены шумовые файлы (`DS_031_NIGHTLY*`,
  `DS_054_AI-fallback_черновик.md`);
- параметры чанка (если изменились).

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Скрипт не пишет вне `F:\TO_DBI\logs` и `F:\TO_DBI\PATCH_OUT`.
- Rate limit 1 req/sec — обязателен.

## Артефакты
- `F:\TO_DBI\.continueignore` — дополнен.
- `F:\TO_DBI\logs\indexer\chunks.db` — переиндексирован.
- `F:\TO_DBI\logs\indexer\embeddings.npy` — переиндексирован.
- `F:\TO_DBI\logs\ds_cnt_005c_index.log` — лог.
- `F:\TO_DBI\logs\ds_cnt_005c.exit` — код.
- `EXCHANGE\OUTBOX\DS_CNT_005c_report.md` — обновлён.
- `EXCHANGE\CNT_REFERENCE.md` — обновлён (если нужно).
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_015_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `DS_031_NIGHTLY.md`, `DS_031_NIGHTLY_report.md`,
   `DS_054_AI-fallback_черновик.md` — исключены из `.continueignore`.
2. Переиндексация выполнена, код 0.
3. Files: ~26, Chunks: ~150.
4. «матрица доступа» → `SEC_POLICY_AI.md` в top-1 или top-2.
5. «статус проекта» → `PROJECT_STATUS.md` в top-1.
6. «как оформить DS» → `DS_STANDARD.md` или `DS_PROJECT_CONTEXT.md`
   в top-1.
7. `SEC_POLICY_AI.md`, раздел 3 — исследован:
   - в индексе? да/нет;
   - чанк разрезан? да/нет;
   - эмбеддинг слабый? да/нет;
   - вывод.
8. Корректировки (если были) — применены.
9. `DS_CNT_005c_report.md` обновлён.
10. `CNT_REFERENCE.md` обновлён (если нужно).
11. Отчёт `DS_CNT_015_report.md` в OUTBOX.