# DS_CNT_004a. Завершение этапа 004: MCP-конфиг вместо ACL (exFAT)

## Цель
Завершить этап 004 (mcpServers) с учётом exFAT:
- `mcpServers` добавлен в `config.yaml` — сделано (DS_CNT_004);
- `svc_mcp` создан — сделано (в этой сессии);
- ACL на F: не применяется (exFAT) — ограничения реализованы
  через MCP-конфиг.

Этап 004a: проверить и зафиксировать, что ограничения `svc_mcp`
реализованы через MCP-конфиг; обновить отчёт DS_CNT_004.

## Порядок выполнения
DS_CNT_000a выполняется ПЕРВЫМ. Строки про exFAT и `svc_mcp`
в `agents-short.md` добавлены в DS_CNT_000a (шаг 4).
DS_CNT_004a (шаг 5) эти строки пропускает.
Если 004a выполняется раньше 000a — добавить строки здесь,
и 000a пропустит (фиксируется в отчёте).

## Предусловия
- DS_CNT_000 выполнен, DS_CNT_000a выполнен (регламент дополнен
  пунктом про exFAT).
- DS_CNT_004 выполнен: `mcpServers` в `config.yaml`.
- `svc_mcp` создан (эта сессия).
- F: — exFAT. `icacls`/`Set-Acl` не применяются.
- CLI `ai-continue` может быть недоступен. Если недоступен — шаг 4
  откладывается до DS_CNT_005a, фиксируется в отчёте как «частично».
- Регламент: `EXCHANGE\DS_CNT_000_regulation.md` (разделы 1–7,
  включая п. 1.11 про exFAT).

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.
- `svc_mcp` — служебная учётка для MCP-серверов.
- MCP-конфиг — блок `mcpServers` в `~/.continue/config.yaml`.

## Матрица доступа (роль АРМ для CNT)
- чтение: DATA, EXCHANGE, PATCH_IN;
- запись: logs, PATCH_OUT;
- запрет: запись в DATA, EXCHANGE, PATCH_IN.

## Соответствие «матрица доступа → MCP-конфиг»

| Требование | Параметр MCP-конфига | Значение |
|---|---|---|
| shell: только allow-list команд | `MCP_SHELL_ALLOW` | `python,git status,dir,ls` |
| git: только read-only | `MCP_GIT_MODE` | `readonly` |
| fs rw: logs, PATCH_OUT | `MCP_FS_ROOTS_RW` | `F:\TO_DBI\logs;F:\TO_DBI\PATCH_OUT` |
| fs ro: DATA, EXCHANGE, PATCH_IN | `MCP_FS_ROOTS_RO` | `F:\TO_DBI\DATA;F:\TO_DBI\EXCHANGE;F:\TO_DBI\PATCH_IN` |
| запрет записи в DATA, EXCHANGE, PATCH_IN | не входят в `ROOTS_RW` | — |
| запрет доступа к SRC, .git, секретам | не входят ни в `ROOTS_RW`, ни в `ROOTS_RO` | — |

## Шаги

### Шаг 1. Проверить `svc_mcp`
- Учётка `svc_mcp` существует (создана в этой сессии).
- Не входит в Administrators.
- Зафиксировать в отчёте: дата создания, кто создал.
- Проверить командой:
  ```
  net user svc_mcp
  net localgroup Administrators
  ```
  Ожидаемо: `net user svc_mcp` возвращает параметры локальной учётки;
  если ошибка — учётки нет, создать. `svc_mcp` не в списке
  Administrators.
  Альтернатива: `whoami /groups` под `svc_mcp`.

### Шаг 2. Проверить MCP-конфиг в `~/.continue/config.yaml`
Проверить блок `mcpServers`:

```yaml
mcpServers:
  - name: shell
    command: python
    args: ["-m", "mcp_shell_server"]
    env:
      MCP_SHELL_ALLOW: "python,git status,dir,ls"
      MCP_SHELL_CWD: "F:\\TO_DBI"

  - name: git
    command: python
    args: ["-m", "mcp_git_server"]
    env:
      MCP_GIT_MODE: "readonly"
      MCP_GIT_CWD: "F:\\TO_DBI"

  - name: filesystem
    command: python
    args: ["-m", "mcp_filesystem_server"]
    env:
      MCP_FS_ROOTS_RW: "F:\\TO_DBI\\logs;F:\\TO_DBI\\PATCH_OUT"
      MCP_FS_ROOTS_RO: "F:\\TO_DBI\\DATA;F:\\TO_DBI\\EXCHANGE;F:\\TO_DBI\\PATCH_IN"
      MCP_FS_MODE: "rw+ro"
```

Проверить:
- `MCP_SHELL_ALLOW` — только `python,git status,dir,ls`;
- `MCP_GIT_MODE` — `readonly`;
- `MCP_FS_ROOTS_RW` — только `logs`, `PATCH_OUT`;
- `MCP_FS_ROOTS_RO` — только `DATA`, `EXCHANGE`, `PATCH_IN`;
- `SRC`, `.git`, `tools\ai_local_worker.py`, `%USERPROFILE%\.ssh`,
  `%APPDATA%`, `C:\Windows` — не входят ни в один из ROOTS.

Если что-то не так — исправить, код 2.

### Шаг 3. Проверить порядок блоков `config.yaml`
Порядок: models → slashCommands → embeddingsProvider → mcpServers.
Если нарушен — исправить, код 2.

### Шаг 4. Проверить MCP-серверы (если CLI доступен)
```
ai-continue mcp list
ai-continue mcp check --config ~/.continue/config.yaml
```
Ожидаемо: три сервера (shell, git, filesystem) — OK.

Порядок: сначала `mcp list` (базовая проверка), затем `mcp check`
(если поддерживается CLI). Если CLI не поддерживает `mcp check` —
`mcp list` достаточно. Способ зафиксировать в отчёте.

Проверить, что MCP-серверы запускаются **под учёткой `svc_mcp`**:
- `tasklist /v /fi "IMAGENAME eq python.exe"` — если отображает учётку;
- если `tasklist` не показывает учётку (для консольных процессов) —
  PowerShell: `Get-Process python | Select-Object -ExpandProperty StartInfo`;
- альтернатива — лог MCP-сервера.
Если под другой учёткой — зафиксировать в отчёте, эскалация.

Если CLI `ai-continue` недоступен — зафиксировать в отчёте, отложить
до DS_CNT_005a (там CLI устанавливается).
В этом случае этап 004a считается «частично» (код 0 с оговоркой).
В отчёте `DS_CNT_004a_report.md` явно указать статус:
- «выполнено» — если шаг 4 выполнен;
- «частично» — если шаг 4 отложен до 005a.

### Шаг 5. Строки про exFAT и `svc_mcp` в `agents-short.md`
Строки про exFAT и `svc_mcp` добавлены в DS_CNT_000a (шаг 4).
DS_CNT_004a этот шаг **пропускает** (не дублирует).
Если 004a выполняется раньше 000a — добавить строки здесь:

```markdown
- MCP-серверы: shell (allow-list), git (read-only),
  filesystem (rw: logs, PATCH_OUT; ro: DATA, EXCHANGE, PATCH_IN).
- F: — exFAT. ACL не применяются. Ограничения — через MCP-конфиг
  (MCP_SHELL_ALLOW, MCP_GIT_MODE, MCP_FS_ROOTS_RW/RO).
- `svc_mcp` — служебная учётка для MCP-серверов.
- Не пытаться применять `icacls`/`Set-Acl` на F:.
- MCP-серверы не имеют доступа к SRC, .git, ai_local_worker.py,
  %USERPROFILE%\.ssh, %APPDATA%, C:\Windows.
```

Если блок «Ограничения ИБ (кратко)» отсутствует — создать его.
В отчёте зафиксировать: строки добавлены в 000a (не в 004a).

### Шаг 6. Обновить отчёт `DS_CNT_004_report.md`
Дописать в отчёт:
- `svc_mcp` создан (дата, кто создал);
- ACL не применяется (exFAT) — зафиксировано;
- ограничения реализованы через MCP-конфиг (параметры);
- MCP-серверы — проверено / отложено (в зависимости от CLI);
- учётка, под которой запускаются MCP-серверы — зафиксировать;
- статус этапа 004a — «выполнено» / «частично».

Убрать из «Проблемы»:
- «svc_mcp не создана» — закрыто;
- «icacls не проверялся» — заменено на «ACL не применяется (exFAT),
  ограничения — через MCP-конфиг».

Оставить/добавить в «Проблемы»:
- «F: — exFAT, ACL невозможен; перевод на NTFS — отдельная задача».

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать (только CLI/скрипт).
- Внешние AI не использовать.
- LM Studio одновременно с Ollama не открывать.
- Не расширять allow-list без согласования с ИБ.
- Соблюдать матрицу доступа.
- Не пытаться применять `icacls`/`Set-Acl` на F: (exFAT).
- Не дублировать строки в `agents-short.md` (это делает 000a).

## Артефакты
- `svc_mcp` — создан.
- `~/.continue/config.yaml` — MCP-конфиг проверен.
- `.continue/rules/agents-short.md` — дополнен (в 000a).
- `EXCHANGE\OUTBOX\DS_CNT_004_report.md` — обновлён.
- `F:\TO_DBI\logs\ds_cnt_004a.log`, `ds_cnt_004a.exit`,
  `ds_cnt_004a.err`, `ds_cnt_004a.lock`.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_004a_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. Учётка `svc_mcp` существует, не в Administrators.
2. MCP-конфиг соответствует таблице «матрица доступа → MCP-конфиг».
3. Порядок блоков `config.yaml` — правильный.
4. MCP-серверы (shell, git, filesystem) — OK (шаг 4 выполнен) —
   статус «выполнено». Или шаг 4 отложен до DS_CNT_005a — статус
   «частично». В отчёте явно указан статус.
5. MCP-серверы запускаются под учёткой `svc_mcp` (или зафиксировано
   иное, эскалация).
6. Строки про exFAT и `svc_mcp` в `agents-short.md` добавлены
   в DS_CNT_000a (или здесь, если 004a выполнен первым).
7. Отчёт `DS_CNT_004_report.md` обновлён.
8. Отчёт `DS_CNT_004a_report.md` в OUTBOX.