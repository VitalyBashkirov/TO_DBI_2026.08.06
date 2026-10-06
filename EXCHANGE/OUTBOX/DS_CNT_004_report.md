# DS_CNT_004 — Отчёт

**Дата:** 03.10.2026
**Статус:** Выполнено (код 0)

## Что сделано
- Добавлен блок `mcpServers` в `config.yaml` (shell, git, filesystem).
- Обновлён `agents-short.md` — раздел «MCP — конкретика».

## Что проверено
- YAML валиден.
- mcpServers: shell, git, filesystem.
- env-параметры соответствуют матрице доступа.

## Артефакты
- `.continue/config.yaml` (mcpServers)
- `.continue/rules/agents-short.md`
- `logs/ds_cnt_004.log`, `logs/ds_cnt_004.exit`

## Проблемы
- ~~Учётка `svc_mcp` не создана (требует согласования с ИБ).~~
  **Решено:** `svc_mcp` создан 03.10.2026 (UAC), пароль Never expires,
  флаги 512+32+65536 (normal + pwd_cant_change + pwd_never_expires).
- **`icacls` неприменим: F: — exFAT.** NTFS ACL не поддерживаются.
  `icacls /grant` и `Set-Acl` выполняются без ошибок, но ACL не
  устанавливаются («No permissions are set. All users have full
  control.»). Аппаратный контроль доступа к каталогам невозможен.
- Обходной путь: ограничение на уровне конфигурации MCP
  (`ALLOWED_COMMANDS`, `REPO_PATH` в `mcpServers` config.yaml).
  Файловый ACL — при переводе F: на NTFS.

## Следующие шаги
Этап 005. Ограничение svc_mcp — через config.yaml MCP, не icacls.
