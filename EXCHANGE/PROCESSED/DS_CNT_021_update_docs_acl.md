# DS_CNT_021. Обновление документации после миграции F: exFAT → NTFS + ACL

## Цель
Обновить документацию после:
1) миграции F: с exFAT на NTFS (04.10.2026);
2) применения ACL для `svc_mcp` (rw: logs, PATCH_OUT; ro: DATA,
   EXCHANGE, PATCH_IN; нет доступа: SRC, .git);
3) удаления `svc_mcp` из группы `Пользователи`.

Обновить:
- `EXCHANGE\SEC_POLICY_AI.md`, раздел 5.2;
- `.continue\rules\agents-short.md`, блок «Ограничения ИБ»;
- `EXCHANGE\DS_CNT_000_regulation.md`, п. 1.11;
- `EXCHANGE\OUTBOX\DS_CNT_004a_report.md`, статус;
- `EXCHANGE\OUTBOX\DS_CNT_000_report.md`, сводная таблица;
- `EXCHANGE\bot.log`, запись.

## Предусловия
- F: — NTFS (миграция завершена).
- ACL применены для `svc_mcp`.
- `svc_mcp` — вне групп.
- Индексатор: 26 файлов, 158 чанков.
- Документация: `SEC_POLICY_AI.md`, `agents-short.md`, регламент,
  отчёты — существуют.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- ACL — Access Control List.

## Шаги

### Шаг 1. Обновить `EXCHANGE\SEC_POLICY_AI.md`
В разделе **5.2** (или примечании к нему) **удалить** старый текст про exFAT и **добавить**:

```markdown
Примечание (NTFS + ACL): F: — NTFS. ACL применены для `svc_mcp`:
- **rw** (чтение + запись): `logs`, `PATCH_OUT`;
- **ro** (только чтение): `DATA`, `EXCHANGE`, `PATCH_IN`;
- **нет доступа**: `SRC`, `.git`.

`svc_mcp` — вне групп (не в `Пользователи`).
Ограничения MCP-конфига (MCP_SHELL_ALLOW, MCP_GIT_MODE,
MCP_FS_ROOTS_RW/RO) — дополнительно к ACL.
```

**Найти старую формулировку:** grep по файлу «exFAT», «ACL не применяются» — заменить.

### Шаг 2. Обновить `.continue\rules\agents-short.md`
В блоке **«Ограничения ИБ (кратко)»** заменить строки про exFAT:

**Было:**
```
- F: — exFAT. ACL не применяются. Ограничения — через MCP-конфиг.
```

**Стало:**
```
- F: — NTFS. ACL применены для `svc_mcp`: rw — logs, PATCH_OUT;
  ro — DATA, EXCHANGE, PATCH_IN; нет доступа — SRC, .git.
- `svc_mcp` — вне групп.
```

### Шаг 3. Обновить `EXCHANGE\DS_CNT_000_regulation.md`
В **п. 1.11** заменить:

**Было:**
```
1.11. Файловая система F: — exFAT.
F: — exFAT. Файловые ACL (icacls/Set-Acl) не применяются.
```

**Стало:**
```
1.11. Файловая система F: — NTFS.
F: — NTFS. Файловые ACL применяются для `svc_mcp`:
- rw: logs, PATCH_OUT;
- ro: DATA, EXCHANGE, PATCH_IN;
- нет доступа: SRC, .git.
svc_mcp — вне групп.
```

### Шаг 4. Обновить `EXCHANGE\OUTBOX\DS_CNT_004a_report.md`
Заменить статус:

**Было:**
```
**Статус:** Частично (код 0, шаг 4 отложен)
```

**Стало:**
```
**Статус:** Выполнено (ACL применены 04.10.2026)
```

В «Что сделано» добавить:
```
5. ACL применены для `svc_mcp`:
   - rw: logs, PATCH_OUT;
   - ro: DATA, EXCHANGE, PATCH_IN;
   - deny WD,AD: DATA, EXCHANGE, PATCH_IN;
   - нет доступа: SRC, .git.
   `svc_mcp` удалён из группы Пользователи.
```

В «Проблемы» — удалить пункт про невозможность ACL (exFAT).

### Шаг 5. Обновить `EXCHANGE\OUTBOX\DS_CNT_000_report.md`
В сводной таблице:

| DS | Статус | Код | Отчёт |
|---|---|---|---|
| 004a | **Выполнено** | 0 | DS_CNT_004a_report.md |

Добавить примечание:
```
Примечание: 04.10.2026 — миграция F: exFAT → NTFS завершена.
ACL применены для `svc_mcp`. `svc_mcp` — вне групп.
```

### Шаг 6. Записать в `EXCHANGE\bot.log`
```powershell
$now = Get-Date -Format "dd.MM.yyyy HH:mm:ss"
Add-Content F:\TO_DBI\EXCHANGE\bot.log "$now Миграция F: exFAT → NTFS завершена."
Add-Content F:\TO_DBI\EXCHANGE\bot.log "$now ACL применены для svc_mcp: rw - logs, PATCH_OUT; ro - DATA, EXCHANGE, PATCH_IN; deny WD,AD - DATA, EXCHANGE, PATCH_IN; нет доступа - SRC, .git."
Add-Content F:\TO_DBI\EXCHANGE\bot.log "$now svc_mcp удалён из группы Пользователи. DS_CNT_004a - выполнено."
```

### Шаг 7. Проверить консистентность
- `SEC_POLICY_AI.md` — нет упоминаний «exFAT» и «ACL не применяются».
- `agents-short.md` — блок «Ограничения ИБ» обновлён.
- `DS_CNT_000_regulation.md` — п. 1.11 обновлён.
- `DS_CNT_004a_report.md` — статус «выполнено».
- `DS_CNT_000_report.md` — таблица обновлена.
- `bot.log` — 3 записи.

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- Соблюдать матрицу доступа.

## Артефакты
- `EXCHANGE\SEC_POLICY_AI.md` — обновлён.
- `.continue\rules\agents-short.md` — обновлён.
- `EXCHANGE\DS_CNT_000_regulation.md` — п. 1.11 обновлён.
- `EXCHANGE\OUTBOX\DS_CNT_004a_report.md` — обновлён.
- `EXCHANGE\OUTBOX\DS_CNT_000_report.md` — обновлён.
- `EXCHANGE\bot.log` — 3 записи.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_021_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `SEC_POLICY_AI.md` — нет «exFAT», есть «NTFS + ACL».
2. `agents-short.md` — блок «Ограничения ИБ» обновлён.
3. `DS_CNT_000_regulation.md` — п. 1.11 обновлён.
4. `DS_CNT_004a_report.md` — статус «Выполнено».
5. `DS_CNT_000_report.md` — таблица: 004a → «Выполнено».
6. `bot.log` — 3 записи.
7. Отчёт `DS_CNT_021_report.md` в OUTBOX.