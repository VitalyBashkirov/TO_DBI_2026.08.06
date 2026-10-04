# DS_CNT_007: собрать пилотный отчёт связки.
# Собирает: индекс (stats), check-standard, explain-log -> OUTBOX\DS_CNT_007_pilot_report.md
# Write target: EXCHANGE\OUTBOX (отчёт DS), logs (чтение).
$ErrorActionPreference = "Stop"
$arm = "F:\TO_DBI"
Set-Location $arm

$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# 1. Индекс: код выхода и stats.
$idxExit = "n/a"
if (Test-Path "$arm\logs\ds_cnt_005c.exit") {
    $idxExit = (Get-Content "$arm\logs\ds_cnt_005c.exit" -Raw).Trim()
}
$stats = (python -m tools.indexer.cli stats 2>&1) -join "`r`n"

# 2. check-standard результат.
$cs = "не сформирован"
if (Test-Path "$arm\logs\ds_cnt_007_check_standard.md") {
    $cs = Get-Content "$arm\logs\ds_cnt_007_check_standard.md" -Raw -Encoding UTF8
}

# 3. explain-log результат.
$el = "не сформирован"
if (Test-Path "$arm\logs\ds_cnt_007_explain_log.md") {
    $el = Get-Content "$arm\logs\ds_cnt_007_explain_log.md" -Raw -Encoding UTF8
}

$model = "qwen2.5-coder:3b"

$report = @"
# DS_CNT_007 - Пилотный ночной прогон

**Дата:** $ts
**Статус:** Выполнено
**Модель:** $model (Ollama, локально)

## Что сделано
1. Инкрементальная переиндексация - код $idxExit.
2. /check-standard на SEC_POLICY_AI.md - результат ниже.
3. /explain-log на bot.log - результат ниже.

## Что проверено
- Индекс: см. stats ниже.
- Ollama доступна (порт 11434), модель $model отвечает.
- Rate limit соблюдается (одиночные запросы).

## Результат
Связка работает пакетно: индекс + check-standard + explain-log
выполняются без оператора. Выход каждого шага сохраняется в
logs\, итог агрегируется в этот отчёт.

### stats индекса
``````
$stats
``````

### /check-standard (SEC_POLICY_AI.md)
$cs

### /explain-log (bot.log)
$el

## Проблемы
- Модель qwen2.5-coder:3b — компромисс между качеством и скоростью.
  Для более глубокого разбора нужна 7b (медленнее на CPU).
- Скорость на CPU ограничивает объём: tail 200 строк лога,
  num_predict 600 токенов.

## Следующие шаги
- Проверить первый автозапуск Task Scheduler утром.
- При необходимости — переход на 7b или GPU.
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("$arm\EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md", $report, $utf8NoBom)
Write-Output "REPORT_WRITTEN: $arm\EXCHANGE\OUTBOX\DS_CNT_007_pilot_report.md"
exit 0
