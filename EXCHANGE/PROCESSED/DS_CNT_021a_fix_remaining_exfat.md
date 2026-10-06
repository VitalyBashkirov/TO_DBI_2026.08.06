# DS_CNT_021a. Доработка документации: убрать остатки exFAT

## Цель
В **DS_CNT_021** KODA обновила часть файлов, но **пропустила два**:
- `.continue\rules\agents-short.md` — строка 106.
- `EXCHANGE\DS_CNT_000_regulation.md` — строки 16, 17, 186, 187.

Задача: **заменить/удалить** оставшиеся упоминания `exFAT` в **активных
документах**, отразить **текущее состояние** F: — NTFS + ACL.

**Исторические отчёты** (`DS_CNT_*_report.md`, `PROCESSED\*`) — **не
трогать**. Там `exFAT` — как история.

## Предусловия
- DS_CNT_021 выполнен частично.
- `SEC_POLICY_AI.md` — **уже обновлён** (`exFAT` нет).
- `agents-short.md` — **строка 106** содержит `exFAT`.
- `DS_CNT_000_regulation.md` — **4 строки** содержат `exFAT`.
- F: — NTFS, ACL для `svc_mcp` применены.
- Файлы в кодировке **UTF-8 без BOM**, EOL — **CRLF**.

## Терминология
- CNT = Ai-Continue.
- `F:\TO_DBI\logs` — логи операций АРМа. `EXCHANGE\bot.log` — лог АРМа.

## Шаги

### Шаг 1. Исправить `.continue\rules\agents-short.md`

**Файл:** `F:\TO_DBI\.continue\rules\agents-short.md`
**Строка:** 106

**Было:**
```
- F: — exFAT. ACL не применяются. Ограничения — через MCP-конфиг
```

**Стало:**
```
- F: — NTFS. ACL применены для `svc_mcp`: rw — logs, PATCH_OUT;
  ro — DATA, EXCHANGE, PATCH_IN; нет доступа — SRC, .git.
```

**Важно:** строку **разбить на две** (как показано). Иначе — длинная.

### Шаг 2. Исправить `EXCHANGE\DS_CNT_000_regulation.md`, п. 1.11

**Файл:** `F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md`
**Строки:** 16–17

**Было:**
```
1.11. **Файловая система F: — exFAT.**
F: — exFAT. Файловые ACL (icacls/Set-Acl) на ней не применяются.
```

**Стало:**
```
1.11. **Файловая система F: — NTFS.**
F: — NTFS. Файловые ACL применяются для `svc_mcp`:
- rw: logs, PATCH_OUT;
- ro: DATA, EXCHANGE, PATCH_IN;
- нет доступа: SRC, .git.
svc_mcp — вне групп.
```

### Шаг 3. Удалить строки 186–187 в `DS_CNT_000_regulation.md`

**Строки:**
```
- Не пытаться применить icacls/Set-Acl на F: (exFAT) - не сработает.
- Не считать отсутствие ACL на exFAT нарушением политики -
```

**Действие:** **удалить обе строки**. Для NTFS они **неактуальны**.

**Проверить контекст:** эти строки — в разделе 7.4 «Что НЕ делать». Удалить
**только** их. Если есть соседние строки про exFAT — удалить **все**
относящиеся к exFAT.

### Шаг 4. Проверка — `agents-short.md`

```powershell
Select-String -Path F:\TO_DBI\.continue\rules\agents-short.md -Pattern "exFAT"
```

**Ожидаемо:** **пусто**.

```powershell
Select-String -Path F:\TO_DBI\.continue\rules\agents-short.md -Pattern "NTFS"
```

**Ожидаемо:** **1 строка** с «NTFS + ACL».

### Шаг 5. Проверка — `DS_CNT_000_regulation.md`

```powershell
Select-String -Path F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md -Pattern "exFAT"
```

**Ожидаемо:** **пусто**.

```powershell
Select-String -Path F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md -Pattern "NTFS"
```

**Ожидаемо:** **1 строка** с «Файловая система F: — NTFS».

### Шаг 6. Проверить, что исторические файлы НЕ тронуты

```powershell
# В отчётах и PROCESSED exFAT должен остаться
Get-ChildItem F:\TO_DBI\EXCHANGE\OUTBOX -Filter "DS_CNT_*_report.md" |
    Select-String -Pattern "exFAT" |
    Select-Object Path, LineNumber | Measure-Object
```

**Ожидаемо:** **несколько** (история). **Это нормально.**

### Шаг 7. Записать в `bot.log`

```powershell
$now = Get-Date -Format "dd.MM.yyyy HH:mm:ss"
Add-Content F:\TO_DBI\EXCHANGE\bot.log "$now DS_CNT_021a: Убраны остатки exFAT в agents-short.md и DS_CNT_000_regulation.md."
```

### Шаг 8. Проверка кодировки

```powershell
# Проверить, что файлы остались UTF-8 без BOM
$files = @(
    "F:\TO_DBI\.continue\rules\agents-short.md",
    "F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md"
)
foreach ($f in $files) {
    $bytes = [System.IO.File]::ReadAllBytes($f)
    $hasBom = ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
    Write-Host "$f : BOM = $hasBom"
}
```

**Ожидаемо:** `BOM = False` для **обоих** (если исходные были без BOM).

## Ограничения
- SRC не трогать.
- `ai_local_worker.py`, `rule_based_fixer.py`, `scanner.py`,
  `code_fixer.py` — не трогать.
- MCP shell и MCP-скрипт — не использовать.
- Внешние AI не использовать.
- **Исторические отчёты** (`DS_CNT_*_report.md`, `PROCESSED\*`) —
  **не трогать**.
- Кодировка файлов — **UTF-8** (как было).
- EOL — **CRLF** (как было).

## Артефакты
- `F:\TO_DBI\.continue\rules\agents-short.md` — обновлён.
- `F:\TO_DBI\EXCHANGE\DS_CNT_000_regulation.md` — обновлён.
- `F:\TO_DBI\EXCHANGE\bot.log` — дополнен.
- Отчёт: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_CNT_021a_report.md`.

## Формат отчёта
По `EXCHANGE\DS_089b_report.md`. Разделы:
Что сделано / Что проверено / Результат / Проблемы / Следующие шаги.

## Критерии успеха
1. `agents-short.md` — **нет** упоминаний `exFAT`, есть `NTFS`.
2. `DS_CNT_000_regulation.md` — **нет** упоминаний `exFAT`, есть `NTFS`.
3. Исторические файлы (`DS_CNT_*_report.md`, `PROCESSED\*`) —
   **не тронуты**.
4. Кодировка UTF-8 без BOM — **сохранена** (или как было).
5. EOL — CRLF — **сохранён**.
6. `bot.log` — 1 запись.
7. Отчёт `DS_CNT_021a_report.md` в OUTBOX.