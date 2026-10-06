# DS_CNT_005b_UI. Ручные UI-шаги: индексация @codebase и проверка MCP

## Цель
Инструкция для оператора: выполнить ручные шаги DS_CNT_005b (индексация
`@codebase` в UI Continue) и DS_CNT_004b (проверка MCP-серверов в UI
Continue). Автоматические шаги этих DS уже выполнены; осталось UI.

## Предусловия
- DS_CNT_005b (автоматическая часть) выполнен.
- DS_CNT_004b (автоматическая часть) выполнен.
- Ai-Continue установлен в VS Code.
- Ollama на порту 11434, `nomic-embed-text` доступна.
- VS Code запущен.
- Воркспейс `F:\TO_DBI` доступен.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (п. 1.11 — exFAT,
  п. 1.12 — CLI отсутствует).

## Терминология
- CNT = Ai-Continue.
- UI Continue — панель Ai-Continue в VS Code.

## Часть A. Индексация @codebase (DS_CNT_005b, шаги 4–7)

### A.1. Открыть VS Code и Continue
1. Запустить VS Code.
2. Открыть папку `F:\TO_DBI` (File → Open Folder).
3. Открыть панель Continue (иконка в боковой панели или Ctrl+Shift+P
   → «Continue: Focus on Continue»).

### A.2. Запустить индексацию
1. В панели Continue открыть Settings (иконка шестерёнки).
2. Найти раздел **Index** (или **Indexing**).
3. Нажать **«Index workspace»** / **«Build index»** / **«Rebuild»**
   (зависит от версии).
4. Дождаться завершения. Прогресс отображается в UI.
5. Если кнопки нет:
   - в чате Continue набрать `@codebase` и отправить;
   - Continue предложит «Index your workspace» — нажать.

**Примечание:** индексация — только вручную. Task Scheduler
не применять.

### A.3. Проверить результат индексации
1. Continue → Settings → Index.
2. Убедиться: статус **«Indexed»**, число файлов **> 0**.
3. Зафиксировать фактический путь индекса:
   - `~/.continue/index` или
   - `F:\TO_DBI\.continue\index`.

### A.4. Проверить, что исключённые каталоги не в индексе
1. Continue → Settings → Index → **Files** (если показывает список).
2. Убедиться, что в списке **нет**:
   - `logs/`
   - `PATCH_IN/`
   - `PATCH_OUT/`
   - `*.log`
3. Если список не отображается — проверить косвенно:
   - в чате: `@codebase Что в logs?`
   - ответ **не должен** ссылаться на содержимое `logs/`.

### A.5. Контрольные запросы @codebase
В чате Continue выполнить по очереди:
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

Результаты зафиксировать в отчёте `DS_CNT_005b_report.md`.

### A.6. Обновить отчёт DS_CNT_005b_report.md
Дописать:
- индексация выполнена (дата, время);
- индекс создан (путь, число файлов);
- проверка исключённых каталогов — результат;
- контрольные запросы `@codebase` — результаты.
- статус: «выполнено» (было «частично»).

---

## Часть B. Проверка MCP (DS_CNT_004b, шаги 3–6)

### B.1. Открыть VS Code и Continue
1. VS Code уже открыт (см. A.1).
2. Панель Continue открыта.

### B.2. Проверить MCP-серверы
1. Continue → Settings → **MCP Servers** (или иконка MCP).
2. Убедиться, что три сервера:
   - **shell** — Connected / Running / OK;
   - **git** — Connected / Running / OK;
   - **filesystem** — Connected / Running / OK.
3. Если сервер не поднялся — зафиксировать ошибку в отчёте, эскалация.

### B.3. Проверить, под какой учёткой запущены MCP
1. Открыть терминал (cmd или PowerShell).
2. Выполнить:
   ```
   tasklist /v /fi "IMAGENAME eq python.exe"
   ```
3. Если учётка не отображается — PowerShell:
   ```
   Get-Process python | Select-Object -ExpandProperty StartInfo
   ```
4. Альтернатива — Process Explorer (свойства процесса → User).
5. Ожидаемо: MCP-процессы запущены под **`svc_mcp`**.
6. Если под другой учёткой — зафиксировать в отчёте, эскалация.

### B.4. Проверить ограничения MCP
В чате Continue (через MCP-инструменты или slash-команды):

**shell — allow-list:**
- Попробовать команду вне allow-list: `whoami` или `dir C:\Windows`.
- Ожидаемо: **отклонена**.

**git — read-only:**
- Попробовать `git commit -m "test"`.
- Ожидаемо: **отклонён** (read-only).

**filesystem — ROOTS:**
- Попробовать запись в `F:\TO_DBI\DATA\test.txt`.
- Ожидаемо: **отклонена**.
- Попробовать запись в `F:\TO_DBI\EXCHANGE\test.txt`.
- Ожидаемо: **отклонена**.
- Попробовать запись в `F:\TO_DBI\PATCH_IN\test.txt`.
- Ожидаемо: **отклонена**.
- Попробовать запись в `F:\TO_DBI\logs\test.txt`.
- Ожидаемо: **разрешена**.
- Попробовать запись в `F:\TO_DBI\PATCH_OUT\test.txt`.
- Ожидаемо: **разрешена**.

Результаты зафиксировать в отчёте `DS_CNT_004b_report.md`.

### B.5. Обновить отчёт DS_CNT_004b_report.md
Дописать:
- MCP-серверы — Connected/OK;
- учётка запуска — `svc_mcp` (или иная, эскалация);
- ограничения MCP — проверены;
- статус: «выполнено» (было «частично»).

### B.6. Обновить DS_CNT_004a_report.md
Дописать:
- шаг 4 (проверка MCP под `svc_mcp`) — закрыт;
- статус DS_CNT_004a: «выполнено» (было «частично»).

---

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать (только UI Continue).
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Не пытаться применять `icacls`/`Set-Acl` на F: (exFAT).

## Артефакты
- `EXCHANGE\OUTBOX\DS_CNT_005b_report.md` — обновлён (статус
  «выполнено»).
- `EXCHANGE\OUTBOX\DS_CNT_004b_report.md` — обновлён (статус
  «выполнено»).
- `EXCHANGE\OUTBOX\DS_CNT_004a_report.md` — обновлён (шаг 4 закрыт).
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_005b_UI_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. Индексация `@codebase` выполнена в UI Continue.
2. Индекс создан, число файлов > 0.
3. В индексе нет исключённых каталогов.
4. Контрольные запросы `@codebase` — корректные ответы.
5. MCP-серверы — Connected/OK.
6. Учётка запуска MCP — `svc_mcp` (или иная, эскалация).
7. Ограничения MCP — проверены.
8. Отчёты 005b, 004b, 004a — обновлены.