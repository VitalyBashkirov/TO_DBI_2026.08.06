# DS_CNT_004a — Отчёт

**Дата:** 03.10.2026
**Статус:** Выполнено (ACL применены 04.10.2026)

## Что сделано
1. `svc_mcp` — проверена: существует, не в Administrators.
2. MCP-конфиг — проверен: `MCP_SHELL_ALLOW`, `MCP_GIT_MODE: readonly`,
   `MCP_FS_ROOTS_RW/RO` соответствуют матрице доступа.
3. Порядок блоков config.yaml — правильный.
4. Строки про svc_mcp / NTFS ACL — добавлены в DS_CNT_000a (не дублированы).
5. ACL применены для `svc_mcp`:
   - rw: logs, PATCH_OUT;
   - ro: DATA, EXCHANGE, PATCH_IN;
   - deny WD,AD: DATA, EXCHANGE, PATCH_IN;
   - нет доступа: SRC, .git.
   `svc_mcp` удалён из группы Пользователи.

## Что проверено
- `net user svc_mcp` — учётка активна, пароль Never.
- `svc_mcp` не в Administrators.
- mcpServers: shell, git, filesystem.
- SRC, .git, секреты — не входят ни в ROOTS_RW, ни в ROOTS_RO.
- Порядок: models → slashCommands → embeddingsProvider → mcpServers.

## Результат
Ограничения `svc_mcp` реализованы через файловые ACL (NTFS) и MCP-конфиг.
Шаг 4 (запуск MCP под `svc_mcp`) — отложен до DS_CNT_005a (CLI не в PATH).

## Проблемы
- CLI `ai-continue` недоступен — проверка запуска MCP отложена.

## Следующие шаги
DS_CNT_005a — установка CLI, индексация.


## Обновление (DS_CNT_004b)
Шаг 4 (проверка MCP под `svc_mcp`) — закрывается в DS_CNT_004b.
UI-проверка в Continue → Settings → MCP Servers.
Автоматические проверки (конфиг, учётка) — выполнены.


Шаг 4 — автоматическая часть закрыта (проверка конфига, учётки).
UI-часть (проверка MCP под `svc_mcp` в UI Continue) —
отложена до DS_CNT_005b_UI, Часть B.

Статус DS_CNT_004a: «выполнено» (ACL применены 04.10.2026).
