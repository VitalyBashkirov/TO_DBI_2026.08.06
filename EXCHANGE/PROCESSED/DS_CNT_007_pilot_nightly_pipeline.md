# DS_CNT_007. Пилотный ночной прогон связки (свой индекс + slash + отчёт)

## Цель
Провести пилотный ночной прогон связки инструментов CNT:
1) обновить свой индекс (`run_cnt_005c_index.cmd`) — инкрементально;
2) выполнить `/check-standard` на выбранном файле;
3) выполнить `/explain-log` на `EXCHANGE\bot.log`;
4) сформировать отчёт в `EXCHANGE\OUTBOX\`.

**Назначение:** проверить, что связка работает **пакетно** (ночью),
без оператора.

## Предусловия
- DS_CNT_015 выполнен (индекс: 26 файлов, 156 чанков).
- DS_CNT_016 выполнен (отчёты финализированы).
- `tools\run_cnt_005c_index.cmd` создан и проверен.
- `tools\indexer\cli.py` работает (`python -m tools.indexer.cli`).
- Slash-команды `/check-standard`, `/explain-log` настроены в
  `~/.continue/config.yaml` (DS_CNT_001).
- `EXCHANGE\bot.log` доступен.
- Ollama на порту 11434, `nomic-embed-text` + `qwen2.5-coder:7b`.
- Ночное окно 01:00–05:00 (по согласованию).
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md`.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- Связка — индекс + slash-команды + отчёт.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Подготовка — выбрать файл для `/check-standard`
**Файл:** `EXCHANGE\SEC_POLICY_AI.md`.
**Обоснование:** ключевой документ, есть эталон (`DS_STANDARD.md`).

### Шаг 2. Инкрементальная переиндексация
```powershell
F:\TO_DBI\tools\run_cnt_005c_index.cmd
```

**Ожидаемое время:** ~1–2 минуты (инкрементально, 26 файлов).

**Проверка:**
```powershell
python -m tools.indexer.cli stats
```
Ожидаемо: Files ~26, Chunks ~156.

### Шаг 3. `/check-standard` на `SEC_POLICY_AI.md`
**Способ:** через CLI (`ai-continue` отсутствует), поэтому — через
**прямой запрос к Ollama** или через свой индексатор.

**Вариант A — через свой индексатор:**
```powershell
cd F:\TO_DBI
python -m tools.indexer.cli query "check-standard SEC_POLICY_AI"
```
Не совсем то — индексатор не проверяет стандарт.

**Вариант B — через Ollama напрямую:**
```powershell
$prompt = @"
Ты — автор DS в TO_DBI. Стандарт: EXCHANGE\DS_STANDARD.md (раздел 2).
Проверь файл EXCHANGE\SEC_POLICY_AI.md на соответствие.
Укажи нарушения и правки.
"@

$body = @{
  model = "qwen2.5-coder:7b"
  prompt = $prompt
  stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
  -Method Post -Body $body -ContentType "application/json"
```

**Вариант C — через свой скрипт:**
Создать `tools\check_standard.py` (если нужно).

**Рекомендация:** Вариант B (прямой запрос к Ollama) — минимальные
изменения.

### Шаг 4. `/explain-log` на `EXCHANGE\bot.log`
**Способ:** прямой запрос к Ollama.

```powershell
$log = Get-Content F:\TO_DBI\EXCHANGE\bot.log -Tail 200 -Raw

$prompt = @"
Разбери последние 200 строк bot.log TO_DBI.
Укажи ошибки, предупреждения, аномалии.
Предложи шаги диагностики.

Лог:
$log
"@

$body = @{
  model = "qwen2.5-coder:7b"
  prompt = $prompt
  stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
  -Method Post -Body $body -ContentType "application/json"
```

### Шаг 5. Сформировать отчёт
Создать `EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md`:

```markdown
# DS_CNT_007 — Пилотный ночной прогон

**Дата:** <YYYY-MM-DD HH:MM:SS>
**Статус:** <Выполнено / Частично>

## Что сделано
1. Инкрементальная переиндексация — <результат>.
2. /check-standard на SEC_POLICY_AI.md — <результат>.
3. /explain-log на bot.log — <результат>.

## Что проверено
- Индекс: Files ~26, Chunks ~156.
- /check-standard — <вывод>.
- /explain-log — <вывод>.

## Результат
<Связка работает пакетно / есть проблемы>.

## Проблемы
<...>

## Следующие шаги
<...>
```

### Шаг 6. Зарегистрировать в Task Scheduler
**После успешного ручного прогона.**

Создать задачу:
- Название: `TO_DBI_CNT_NightlyPipeline`;
- Триггер: ежедневно, 01:00;
- Действие: `F:\TO_DBI\tools\run_cnt_007_nightly.cmd` (создать);
- Условие: питание от сети;
- Настройка: не запускать при разряженной батарее.

**Скрипт `run_cnt_007_nightly.cmd`:**
```cmd
@echo off
setlocal
REM DS_CNT_007: ночной прогон связки
call F:\TO_DBI\tools\run_cnt_005c_index.cmd
if errorlevel 1 exit /b %errorlevel%
REM check-standard (Ollama)
powershell -File F:\TO_DBI\tools\check_standard.ps1
if errorlevel 1 exit /b %errorlevel%
REM explain-log (Ollama)
powershell -File F:\TO_DBI\tools\explain_log.ps1
if errorlevel 1 exit /b %errorlevel%
REM Отчёт
powershell -File F:\TO_DBI\tools\make_pilot_report.ps1
exit /b 0
```

### Шаг 7. Проверить первый ночной прогон
**Утром после первого автозапуска:**
- `Get-Content F:\TO_DBI\logs\ds_cnt_007.log`;
- `Get-Content F:\TO_DBI\logs\ds_cnt_007.exit`;
- `Get-Content F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md`.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Rate limit 1 req/sec — обязателен.
- Task Scheduler — только после успешного ручного прогона.

## Артефакты
- `F:\TO_DBI\logs\ds_cnt_005c_index.log` — лог переиндексации.
- `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md` — отчёт.
- `F:\TO_DBI\tools\run_cnt_007_nightly.cmd` — скрипт ночного прогона.
- `F:\TO_DBI\tools\check_standard.ps1` — скрипт check-standard.
- `F:\TO_DBI\tools\explain_log.ps1` — скрипт explain-log.
- `F:\TO_DBI\tools\make_pilot_report.ps1` — скрипт отчёта.
- `F:\TO_DBI\logs\ds_cnt_007.log`, `ds_cnt_007.exit`.
- Task Scheduler: `TO_DBI_CNT_NightlyPipeline`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. Инкрементальная переиндексация — код 0.
2. `/check-standard` на `SEC_POLICY_AI.md` — результат получен.
3. `/explain-log` на `bot.log` — результат получен.
4. Отчёт `DS_CNT_007_pilot_report.md` в OUTBOX.
5. Task Scheduler — задача `TO_DBI_CNT_NightlyPipeline` создана.
6. Скрипты `run_cnt_007_nightly.cmd`, `check_standard.ps1`,
   `explain_log.ps1`, `make_pilot_report.ps1` созданы.
7. Первый ночной прогон — проверен утром.
8. Отчёт `DS_CNT_007_report.md` в OUTBOX.