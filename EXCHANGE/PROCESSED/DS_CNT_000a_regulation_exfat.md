# DS_CNT_000a. Дополнение регламента: exFAT и ограничения без ACL

## Цель
Дополнить `EXCHANGE\DS_CNT_000_regulation.md` пунктом про exFAT:
- F: — exFAT, файловые ACL (icacls/Set-Acl) не применяются;
- ограничения `svc_mcp` реализуются на уровне MCP-конфига;
- перевод F: на NTFS — отдельная инфраструктурная задача.

Также дополнить `EXCHANGE\SEC_POLICY_AI.md` и `agents-short.md`
записями про exFAT.

DS_CNT_004a (exFAT-версия) использует п. 1.11 настоящего регламента.

## Порядок выполнения
DS_CNT_000a выполняется ПЕРВЫМ (до DS_CNT_004a). Строки про exFAT
и `svc_mcp` в `agents-short.md` добавляет DS_CNT_000a (шаг 4).
DS_CNT_004a (шаг 5) эти строки пропускает.

## Предусловия
- DS_CNT_000 выполнен: `EXCHANGE\DS_CNT_000_regulation.md` создан.
- DS_CNT_002 выполнен: `EXCHANGE\SEC_POLICY_AI.md` создан.
- DS_CNT_001 выполнен: `.continue/rules/agents-short.md` создан.
- DS_CNT_004 выполнен частично: `svc_mcp` создан, ACL не применён (exFAT).
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 1–7).

## Терминология
- CNT = Ai-Continue.
- ACL — Access Control List (список контроля доступа), функция NTFS.
- exFAT — файловая система без ACL.
- `svc_mcp` — служебная учётка для MCP-серверов.
- MCP-конфиг — блок `mcpServers` в `~/.continue/config.yaml`
  (`MCP_SHELL_ALLOW`, `MCP_GIT_MODE`, `MCP_FS_ROOTS_RW/RO`).

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Шаги

### Шаг 1. Дополнить `DS_CNT_000_regulation.md`
Добавить в раздел 1 новый пункт 1.11 (после 1.10):

```markdown
1.11. **Файловая система F: — exFAT.**
F: — exFAT. Файловые ACL (icacls/Set-Acl) на ней не применяются.
Ограничения прав `svc_mcp` реализуются:
- на уровне MCP-конфига: `MCP_SHELL_ALLOW` (allow-list команд),
  `MCP_GIT_MODE: readonly`, `MCP_FS_ROOTS_RW` (logs, PATCH_OUT),
  `MCP_FS_ROOTS_RO` (DATA, EXCHANGE, PATCH_IN);
- на уровне регламента: CNT не пишет в DATA/EXCHANGE/PATCH_IN,
  не делает commit/push/checkout, не запускает произвольные shell.
Перевод F: на NTFS — отдельная инфраструктурная задача, требует
согласования с Администратором АРМа и ИБ, резервной копии данных
и окна простоя. В текущий DS-цикл CNT не входит.
```

### Шаг 2. Дополнить раздел 7 регламента
В раздел 7.4 «Что НЕ делать» добавить:

```markdown
- Не пытаться применить `icacls`/`Set-Acl` на F: (exFAT) — не сработает.
- Не считать отсутствие ACL на exFAT нарушением политики —
  ограничения обеспечиваются MCP-конфигом.
```

### Шаг 3. Дополнить `SEC_POLICY_AI.md`
В **конец** раздела 5.2 «MCP-серверы (allow-list)» добавить
**примечание** (не изменяя таблицу allow-list). Альтернатива —
раздел 12.1:

```markdown
Примечание (exFAT): F: — exFAT, файловые ACL не применяются.
Ограничения MCP-серверов реализуются параметрами MCP-конфига:
`MCP_SHELL_ALLOW`, `MCP_GIT_MODE`, `MCP_FS_ROOTS_RW/RO`.
Это слабее ACL (действует только внутри MCP-сервера), но приемлемо
на текущем этапе. Перевод F: на NTFS — отдельная задача.
```

### Шаг 4. Дополнить `agents-short.md`
В раздел «Пакетный ночной режим (DS_CNT_000)» (или в блок
«Ограничения ИБ (кратко)») добавить строки:

```markdown
- F: — exFAT. ACL не применяются. Ограничения — через MCP-конфиг
  (`MCP_SHELL_ALLOW`, `MCP_GIT_MODE`, `MCP_FS_ROOTS_RW/RO`).
- `svc_mcp` — служебная учётка для MCP-серверов.
- Не пытаться применять `icacls`/`Set-Acl` на F:.
```

Строки добавляет **DS_CNT_000a**. DS_CNT_004a (шаг 5) эти строки
пропускает (не дублирует).

### Шаг 5. Обновить отчёт `DS_CNT_000_report.md`
Дописать:
- регламент дополнен пунктом 1.11 (exFAT);
- `SEC_POLICY_AI.md` дополнен примечанием про exFAT (раздел 5.2);
- `agents-short.md` дополнен строками про exFAT и `svc_mcp`.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Соблюдать матрицу доступа.
- Не пытаться применять ACL на exFAT.
- Не дублировать строки в `agents-short.md` (это делает 000a, не 004a).

## Артефакты
- `EXCHANGE\DS_CNT_000_regulation.md` — дополнен (п. 1.11, п. 7.4).
- `EXCHANGE\SEC_POLICY_AI.md` — дополнен (раздел 5.2, примечание).
- `.continue/rules/agents-short.md` — дополнен.
- `EXCHANGE\OUTBOX\DS_CNT_000_report.md` — обновлён.
- `F:\TO_DBI\logs\ds_cnt_000a.log`, `ds_cnt_000a.exit`,
  `ds_cnt_000a.err`, `ds_cnt_000a.lock`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_000a_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `DS_CNT_000_regulation.md` содержит п. 1.11 (exFAT) и дополнение 7.4.
2. `SEC_POLICY_AI.md` содержит примечание про exFAT в разделе 5.2.
3. `agents-short.md` содержит строки про exFAT и `svc_mcp`.
4. Отчёт `DS_CNT_000_report.md` обновлён.
5. Отчёт `DS_CNT_000a_report.md` в OUTBOX.