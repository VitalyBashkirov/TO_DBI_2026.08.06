# DS_CNT_004b. Закрытие шага 4 DS_CNT_004a: проверка MCP под svc_mcp

## Цель
Закрыть шаг 4 DS_CNT_004a — проверку, что MCP-серверы (shell, git,
filesystem) запускаются под учёткой `svc_mcp` и корректно работают
в рамках MCP-конфига. В DS_CNT_004a шаг 4 был отложен: CLI `ai-continue`
отсутствует, проверка — только в UI Continue.

## Предусловия
- DS_CNT_000, DS_CNT_000a выполнены.
- DS_CNT_004 выполнен (mcpServers в config.yaml).
- DS_CNT_004a выполнен частично: `svc_mcp` создан, MCP-конфиг
  проверен, шаг 4 (запуск MCP под `svc_mcp`) — отложен.
- DS_CNT_005b выполнен (ручная индексация Continue).
- Ai-Continue установлен в VS Code (GUI).
- Ollama на порту 11434.
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 2–7,
  включая п. 1.11 про exFAT, п. 1.12 про отсутствие CLI).

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- `svc_mcp` — служебная учётка для MCP-серверов.
- MCP-конфиг — блок `mcpServers` в `~/.continue/config.yaml`.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Проверить `svc_mcp`
```
net user svc_mcp
net localgroup Administrators
```
Ожидаемо: учётка активна; не в Administrators.

### Шаг 2. Проверить MCP-конфиг в `~/.continue/config.yaml`
Убедиться, что блок `mcpServers` соответствует exFAT-версии:
- `MCP_SHELL_ALLOW` — `python,git status,dir,ls`;
- `MCP_GIT_MODE` — `readonly`;
- `MCP_FS_ROOTS_RW` — `F:\TO_DBI\logs;F:\TO_DBI\PATCH_OUT`;
- `MCP_FS_ROOTS_RO` — `F:\TO_DBI\DATA;F:\TO_DBI\EXCHANGE;F:\TO_DBI\PATCH_IN`.

### Шаг 3. Открыть VS Code и Continue
- Открыть VS Code.
- Открыть воркспейс `F:\TO_DBI`.
- Открыть панель Continue.

### Шаг 4. Проверить MCP-серверы в UI Continue
- Continue → Settings → MCP Servers (или иконка MCP в панели).
- Убедиться, что три сервера (shell, git, filesystem) — **Connected** /
  **Running** / **OK** (зависит от версии).
- Если сервер не поднялся — зафиксировать ошибку в отчёте, эскалация.

### Шаг 5. Проверить, под какой учёткой запущены MCP-серверы
- `tasklist /v /fi "IMAGENAME eq python.exe"` — если отображает учётку.
- Если `tasklist` не показывает учётку (для консольных процессов) —
  PowerShell: `Get-Process python | Select-Object -ExpandProperty StartInfo`.
- Альтернатива — лог MCP-сервера (если ведёт).
- Если MCP запущены под `svc_mcp` — OK. Если под другой учёткой —
  зафиксировать в отчёте, эскалация.

### Шаг 6. Проверить ограничения MCP в UI
- Continue → Settings → MCP Servers → shell:
  - попробовать команду вне allow-list (например, `whoami`) —
    должна быть отклонена.
- Continue → Settings → MCP Servers → git:
  - попробовать `git commit` — должен быть отклонён (read-only).
- Continue → Settings → MCP Servers → filesystem:
  - попробовать запись в `DATA/`, `EXCHANGE/`, `PATCH_IN/` —
    должна быть отклонена;
  - попробовать запись в `logs/`, `PATCH_OUT/` — разрешена.

Результаты зафиксировать в отчёте.

### Шаг 7. Обновить отчёт `DS_CNT_004a_report.md`
Дописать:
- шаг 4 (проверка MCP под `svc_mcp`) — выполнен;
- MCP-серверы — Connected/OK;
- учётка, под которой запущены MCP — `svc_mcp` (или иная, эскалация);
- ограничения MCP — проверены (allow-list, read-only, ROOTS);
- статус DS_CNT_004a — «выполнено» (было «частично»).

Убрать из «Проблемы»:
- «CLI `ai-continue` недоступен — проверка запуска MCP отложена» —
  закрыто (проверка выполнена в UI Continue).

Оставить:
- «F: — exFAT, ACL невозможен; перевод на NTFS — отдельная задача».

### Шаг 8. Обновить `agents-short.md`
В блоке «MCP — конкретика» (или «Ограничения ИБ (кратко)») уточнить:
- MCP-серверы запускаются под учёткой `svc_mcp`;
- проверка — в UI Continue → Settings → MCP Servers;
- CLI `ai-continue` отсутствует (п. 1.12 регламента).

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Не пытаться применять `icacls`/`Set-Acl` на F: (exFAT).

## Артефакты
- `EXCHANGE\OUTBOX\DS_CNT_004a_report.md` — обновлён.
- `.continue/rules/agents-short.md` — дополнен.
- `F:\TO_DBI\logs\ds_cnt_004b.log`, `ds_cnt_004b.exit`,
  `ds_cnt_004b.err`, `ds_cnt_004b.lock`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_004b_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. MCP-серверы (shell, git, filesystem) — Connected/OK в UI Continue.
2. Учётка запуска MCP — `svc_mcp` (или зафиксировано иное, эскалация).
3. Ограничения MCP проверены: allow-list, read-only, ROOTS.
4. `DS_CNT_004a_report.md` обновлён (статус — «выполнено»).
5. `agents-short.md` дополнен.
6. Отчёт `DS_CNT_004b_report.md` в OUTBOX.