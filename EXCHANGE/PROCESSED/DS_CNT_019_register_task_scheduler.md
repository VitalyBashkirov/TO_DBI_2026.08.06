# DS_CNT_019. Регистрация Task Scheduler: TO_DBI_CNT_NightlyPipeline

## Цель
Зарегистрировать в Task Scheduler задачу `TO_DBI_CNT_NightlyPipeline` —
ночной автозапуск pipeline CNT (`run_cnt_007_nightly.cmd`) в окне
01:00–05:00. Регистрация — **по явному разрешению Администратора АРМа**.

## Предусловия
- DS_CNT_007 выполнен (pipeline работает, RC=0).
- DS_CNT_018 выполнен (pipeline на `qwen2.5-coder:3b`).
- DS_CNT_020 выполнен (CNT-цикл финализирован).
- `tools\run_cnt_007_nightly.cmd` — создан и проверен.
- Явное разрешение Администратора АРМа на регистрацию — **получено**.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (п. 1.16).
- Ночное окно 01:00–05:00 — по согласованию.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- Pipeline — индексация + /check-standard + /explain-log + отчёт.
- Task Scheduler — планировщик Windows.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Проверить наличие скрипта
```powershell
Get-Item F:\TO_DBI\tools\run_cnt_007_nightly.cmd | Select-Object FullName, Length, LastWriteTime
```

**Ожидаемо:** файл существует, размер > 0.

**Если нет** — останов, эскалация.

### Шаг 2. Проверить, что задача не зарегистрирована ранее
```powershell
Get-ScheduledTask -TaskName "TO_DBI_CNT_NightlyPipeline" -ErrorAction SilentlyContinue
```

**Ожидаемо:** пусто.

**Если задача есть** — удалить или обновить (см. Шаг 5).

### Шаг 3. Создать задачу в Task Scheduler

```powershell
$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c F:\TO_DBI\tools\run_cnt_007_nightly.cmd" `
    -WorkingDirectory "F:\TO_DBI"

$trigger = New-ScheduledTaskTrigger -Daily -At "01:00"

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries:$false `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName "TO_DBI_CNT_NightlyPipeline" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "DS_CNT_019: ночной pipeline CNT (индексация + check-standard + explain-log + отчёт). Модель: qwen2.5-coder:3b."
```

**Параметры:**
- **Trigger:** ежедневно, 01:00.
- **ExecutionTimeLimit:** 4 часа (максимум).
- **AllowStartIfOnBatteries:** false (не запускать на батарее).
- **MultipleInstances:** IgnoreNew (не запускать второй экземпляр).
- **Principal:** текущий пользователь, S4U (без пароля), RunLevel Limited.

### Шаг 4. Проверить регистрацию
```powershell
Get-ScheduledTask -TaskName "TO_DBI_CNT_NightlyPipeline" | Format-List TaskName, State, Description
```

**Ожидаемо:**
- `TaskName: TO_DBI_CNT_NightlyPipeline`;
- `State: Ready`;
- `Description: DS_CNT_019: ночной pipeline CNT...`.

### Шаг 5. Проверить триггер и действие
```powershell
$task = Get-ScheduledTask -TaskName "TO_DBI_CNT_NightlyPipeline"
$task.Triggers | Format-List
$task.Actions | Format-List
```

**Ожидаемо:**
- Trigger: Daily, At 01:00;
- Action: cmd.exe /c F:\TO_DBI\tools\run_cnt_007_nightly.cmd.

### Шаг 6. Тестовый ручной запуск (немедленно)
```powershell
Start-ScheduledTask -TaskName "TO_DBI_CNT_NightlyPipeline"
```

**Мониторинг:**
```powershell
Get-ScheduledTaskInfo -TaskName "TO_DBI_CNT_NightlyPipeline" | Select-Object LastRunTime, LastTaskResult, NextRunTime
```

**Ожидаемо (через 5–15 минут):**
- `LastRunTime` — сейчас;
- `LastTaskResult` — `0` (успех);
- `NextRunTime` — следующая ночь, 01:00.

**Проверить результаты:**
```powershell
Get-Content F:\TO_DBI\logs\ds_cnt_007.exit
Get-ChildItem F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007*
```

### Шаг 7. Проверить «запуск от текущего пользователя»
```powershell
$task = Get-ScheduledTask -TaskName "TO_DBI_CNT_NightlyPipeline"
$task.Principal | Format-List UserId, LogonType, RunLevel
```

**Ожидаемо:**
- `UserId`: `<domain>\<user>`;
- `LogonType`: S4U;
- `RunLevel`: Limited.

### Шаг 8. Обновить регламент — п. 1.16
Уточнить, что Task Scheduler **зарегистрирован**:

```markdown
1.16. **Ночной pipeline CNT (DS_CNT_007/019).**
Скрипт: `tools\run_cnt_007_nightly.cmd`.
Состав: инкрементальная переиндексация + /check-standard +
/explain-log + отчёт.
Модель: `qwen2.5-coder:3b` (Ollama, порт 11434).
Task Scheduler: `TO_DBI_CNT_NightlyPipeline`, 01:00 — **зарегистрирован**.
Логи: `logs\ds_cnt_007.log`, `ds_cnt_007.exit`.
Отчёты: `EXCHANGE\OUTBOX\DS_CNT_007_*.md`.
Rate limit 1 req/sec — обязателен.
```

### Шаг 9. Обновить `CNT_REFERENCE.md` — §7
Уточнить, что задача **зарегистрирована**.

### Шаг 10. Записать в `bot.log`
```powershell
$now = Get-Date -Format "dd.MM.yyyy HH:mm:ss"
Add-Content F:\TO_DBI\EXCHANGE\bot.log "$now DS_CNT_019: Task Scheduler TO_DBI_CNT_NightlyPipeline зарегистрирован (01:00, daily). Тестовый запуск — RC=0."
```

### Шаг 11. Утром после первого автозапуска — проверить
```powershell
Get-ScheduledTaskInfo -TaskName "TO_DBI_CNT_NightlyPipeline" | Select-Object LastRunTime, LastTaskResult, NextRunTime
Get-Content F:\TO_DBI\logs\ds_cnt_007.exit
Get-Content F:\TO_DBI\logs\ds_cnt_007.log -Tail 20
Get-ChildItem F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_007*
```

**Ожидаемо:**
- `LastTaskResult` = `0`;
- свежие артефакты в OUTBOX;
- `NextRunTime` — следующая ночь, 01:00.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Task Scheduler — **только по разрешению** Администратора АРМа.
- Не трогать стандартные задачи Windows (`IndexerAutomaticMaintenance`
  и т. п.).
- Точное время (01:00) — по согласованию.

## Артефакты
- Task Scheduler: `TO_DBI_CNT_NightlyPipeline` (State: Ready).
- `EXCHANGE\DS_CNT_000_regulation.md` — п. 1.16 обновлён.
- `EXCHANGE\CNT_REFERENCE.md` — §7 обновлён.
- `EXCHANGE\bot.log` — дополнен.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_019_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. Задача `TO_DBI_CNT_NightlyPipeline` зарегистрирована (State: Ready).
2. Триггер: ежедневно, 01:00.
3. Действие: `cmd.exe /c F:\TO_DBI\tools\run_cnt_007_nightly.cmd`.
4. Тестовый ручной запуск — `LastTaskResult` = `0`.
5. Артефакты pipeline (`DS_CNT_007_*`) — в OUTBOX.
6. Регламент п. 1.16 обновлён.
7. `CNT_REFERENCE.md` §7 обновлён.
8. `bot.log` — дополнен.
9. Утром после первого автозапуска — проверено (exit=0).
10. Отчёт `DS_CNT_019_report.md` в OUTBOX.