# DS_CNT_018. Pipeline на qwen2.5-coder:3b + повтор DS_CNT_007

## Цель
1) Обновить pipeline-скрипты: модель `qwen2.5-coder:1.5b` →
   `qwen2.5-coder:3b` (в `check_standard.ps1`, `explain_log.ps1`).
2) Обновить документацию:
   - `agents-short.md` — блок «Модели Ollama» (убрать 1.5b, добавить 3b);
   - `SEC_POLICY_AI.md`, раздел 5.1 — то же.
3) Повторить DS_CNT_007 (pipeline с 3b).
4) Проверить качество — осмысленные ответы, без галлюцинаций.
5) Обновить `DS_CNT_007_pilot_report.md` (новые результаты).

## Предусловия
- DS_CNT_007 выполнен (pipeline работает, но на 1.5b — слабое качество).
- DS_CNT_016 выполнен (отчёты финализированы).
- DS_CNT_015 выполнен (индекс: 26 файлов, 158 чанков).
- Ollama содержит:
  - `qwen2.5-coder:3b` (1.9 GB) — **новая**;
  - `qwen2.5-coder:7b` (4.7 GB);
  - `nomic-embed-text:latest`;
  - `qwen2.5-coder:1.5b-base`;
  - `llama3.1:8b`, `deepseek-coder:6.7b`.
- Модель `qwen2.5-coder:1.5b` **удалена**.
- Python 3.10+.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (включая п. 1.14).

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- Pipeline — связка: индексация + check-standard + explain-log + отчёт.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Обновить `tools\check_standard.ps1`
Заменить модель:

**Было:**
```powershell
model = "qwen2.5-coder:1.5b"
```

**Стало:**
```powershell
model = "qwen2.5-coder:3b"
```

Если модель указана в нескольких местах — заменить **везде**.

### Шаг 2. Обновить `tools\explain_log.ps1`
Аналогично:

**Было:**
```powershell
model = "qwen2.5-coder:1.5b"
```

**Стало:**
```powershell
model = "qwen2.5-coder:3b"
```

### Шаг 3. Проверить, что модель работает
```powershell
$body = @{
    model  = "qwen2.5-coder:3b"
    prompt = "Hello, respond in one sentence."
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
    -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
```

**Ожидаемо:** JSON с `response: "..."`.

### Шаг 4. Обновить `agents-short.md` — блок «Модели Ollama»
Найти блок «Модели Ollama (allow-list)». Заменить:

**Было:**
```markdown
### Разработка/тест
- qwen2.5-coder:1.5b — OK (разработка/тест, разработчик АРМа, KODA, ai_local_worker).
- llama3.1:8b — OK (разработка/тест).
- deepseek-coder:6.7b — OK (разработка/тест).
```

**Стало:**
```markdown
### Pipeline (ночные задачи)
- qwen2.5-coder:3b — OK (check-standard, explain-log).
  Компромисс между качеством и скоростью.

### Разработка/тест
- llama3.1:8b — OK (разработка/тест).
- deepseek-coder:6.7b — OK (разработка/тест).

Примечание: qwen2.5-coder:1.5b удалена (устарела, слабое качество).
```

### Шаг 5. Обновить `SEC_POLICY_AI.md`, раздел 5.1
Найти раздел 5.1 «Модели LLM». Заменить:

**Было:**
```markdown
**Разработка/тест (разработчик АРМа, KODA, ai_local_worker):**
- qwen2.5-coder:1.5b
- llama3.1:8b
- deepseek-coder:6.7b
```

**Стало:**
```markdown
**Pipeline (ночные задачи CNT):**
- qwen2.5-coder:3b — check-standard, explain-log.

**Разработка/тест (разработчик АРМа, KODA, ai_local_worker):**
- llama3.1:8b
- deepseek-coder:6.7b

Примечание: qwen2.5-coder:1.5b удалена (устарела).
```

### Шаг 6. Повторить DS_CNT_007 (pipeline)
```powershell
F:\TO_DBI\tools\run_cnt_007_nightly.cmd
```

**Ожидаемое время:** ~5–15 минут (3b на CPU).

**Мониторинг:**
```powershell
Get-Content F:\TO_DBI\logs\ds_cnt_007.log -Tail 20
```

### Шаг 7. Проверить результат
```powershell
Get-Content F:\TO_DBI\logs\ds_cnt_007.exit
Get-Content F:\TO_DBI\logs\ds_cnt_007.log -Tail 30
Get-ChildItem F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007*
Get-ChildItem F:\TO_DBI\logs\ds_cnt_007_*
```

**Ожидаемо:**
- `ds_cnt_007.exit` = `0`;
- `ds_cnt_007.log` — `DONE RC=0`;
- `OUTBOX\DS_CNT_007_pilot_report.md` — обновлён.

### Шаг 8. Проверить качество `/check-standard`
```powershell
Get-Content F:\TO_DBI\logs\ds_cnt_007_check_standard.md -Head 80
```

**Что искать:**
- **осмысленные** ответы (не шаблонные);
- **нет галлюцинаций** (не «файл не содержит команды GIT»);
- **релевантные** замечания по `SEC_POLICY_AI.md`.

**Сравнить с 1.5b:**
- 1.5b — шаблонные ответы, галлюцинации;
- 3b — ожидается лучше.

### Шаг 9. Проверить качество `/explain-log`
```powershell
Get-Content F:\TO_DBI\logs\ds_cnt_007_explain_log.md -Head 80
```

**Что искать:**
- **нет зацикливаний** (не повторяется одна фраза);
- **осмысленный** разбор `bot.log`;
- **конкретные** ошибки/предупреждения.

### Шаг 10. Обновить `DS_CNT_007_pilot_report.md`
Дописать в `EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md`:

```markdown
## Обновление (DS_CNT_018, <дата>)
- Модель pipeline обновлена: qwen2.5-coder:1.5b → qwen2.5-coder:3b.
- Повторный прогон: RC=0.
- Качество check-standard: <оценка>.
- Качество explain-log: <оценка>.
- Сравнение с 1.5b: <кратко>.
```

Или создать `DS_CNT_018_report.md` в OUTBOX (полный отчёт).

### Шаг 11. Обновить `CNT_REFERENCE.md` §7 (если есть)
В разделе §7 «Ночной pipeline» уточнить:
- модель: `qwen2.5-coder:3b` (было 1.5b);
- обоснование: компромисс между качеством и скоростью.

### Шаг 12. Обновить регламент — п. 1.16 (если нужно)
Если п. 1.16 добавлен в DS_CNT_007 — уточнить модель.

Если не добавлен — добавить:

```markdown
1.16. **Ночной pipeline CNT (DS_CNT_007).**
Скрипт: `tools\run_cnt_007_nightly.cmd`.
Состав: инкрементальная переиндексация + /check-standard +
/explain-log + отчёт.
Модель: `qwen2.5-coder:3b` (Ollama, порт 11434).
Task Scheduler: `TO_DBI_CNT_NightlyPipeline`, 01:00 (по согласованию).
Логи: `logs\ds_cnt_007.log`, `ds_cnt_007.exit`.
Отчёты: `EXCHANGE\OUTBOX\DS_CNT_007_*.md`.
Rate limit 1 req/sec — обязателен.
```

### Шаг 13. Записать в `bot.log`
```powershell
$now = Get-Date -Format "dd.MM.yyyy HH:mm:ss"
Add-Content F:\TO_DBI\EXCHANGE\bot.log "$now DS_CNT_018: pipeline обновлён на qwen2.5-coder:3b. Повтор DS_CNT_007 — RC=0."
```

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Rate limit 1 req/sec — обязателен.

## Артефакты
- `F:\TO_DBI\tools\check_standard.ps1` — модель 3b.
- `F:\TO_DBI\tools\explain_log.ps1` — модель 3b.
- `.continue\rules\agents-short.md` — блок «Модели Ollama».
- `EXCHANGE\SEC_POLICY_AI.md` — раздел 5.1.
- `F:\TO_DBI\logs\ds_cnt_007.log`, `ds_cnt_007.exit`.
- `F:\TO_DBI\logs\ds_cnt_007_check_standard.md` — новый результат.
- `F:\TO_DBI\logs\ds_cnt_007_explain_log.md` — новый результат.
- `EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md` — обновлён.
- `EXCHANGE\CNT_REFERENCE.md` — §7 (если есть).
- `EXCHANGE\DS_CNT_000_regulation.md` — п. 1.16.
- `EXCHANGE\bot.log` — дополнен.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_018_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `check_standard.ps1` — модель `qwen2.5-coder:3b`.
2. `explain_log.ps1` — модель `qwen2.5-coder:3b`.
3. `agents-short.md` — блок «Модели Ollama» обновлён.
4. `SEC_POLICY_AI.md` — раздел 5.1 обновлён.
5. Повторный прогон — `ds_cnt_007.exit` = `0`.
6. `/check-standard` — осмысленные ответы (без галлюцинаций).
7. `/explain-log` — без зацикливаний.
8. `DS_CNT_007_pilot_report.md` — обновлён.
9. `CNT_REFERENCE.md` §7 — обновлён (если есть).
10. Регламент п. 1.16 — обновлён.
11. `bot.log` — дополнен.
12. Отчёт `DS_CNT_018_report.md` в OUTBOX.