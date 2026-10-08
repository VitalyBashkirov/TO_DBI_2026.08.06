# DS_118-fix2 — Точечный фикс: §6.5 пустые скобки + bot.log литерал r-n + закрытие хвоста bot.log

## Метаданные

- **Автор DS:** DeepSeek
- **Исполнитель:** KODA
- **Режим:** Agent
- **Дата:** 08.10.2026
- **Ветка:** feature/dockerization
- **Базовый HEAD:** b92d391 (DS_118-fix)
- **Приоритет:** средний

## Контекст

DS_118-fix выполнен, но фактическая проверка выявила 3 дефекта:

### Дефект 1. §6.5 DS_STANDARD.md — пустые скобки в заголовке

Строка 401:
### 6.5. Общие правила завершения ()

KODA убрал (DS_052), но оставил пустые скобки `()`. Косметический
дефект.

### Дефект 2. bot.log — литерал `r`n вместо перевода строки

Строка 1401 в bot.log:
[18.09.2026 17:11:00] DS 052: ... PROCESSED.`r`n[08.10.2026 14:49:35] DS 118: ...

KODA при разбиении склейки вставил escape-последовательность `r`n
как ТЕКСТ, а не как физический перевод строки. В PowerShell `r`n
работает только в двойных кавычках "..." — в одинарных '...' это
литерал. Строки DS_052 и DS_118 остались склеенными, просто теперь
между ними видимый текст `r`n.

### Дефект 3. M EXCHANGE/bot.log — незакоммиченный хвост

На момент старта DS_118-fix2:
 M EXCHANGE/bot.log

Вероятная причина: после коммита b92d391 (DS_118-fix) в bot.log
появилась новая запись (16:28:10 DS 082b) — источник требует
диагностики (pytest? отдельный скрипт?). Для DS_118-fix2 —
просто закоммитить bot.log вместе с правками A, B, C.

## Задача

### Часть A. Убрать `()` из заголовка §6.5 DS_STANDARD.md

**A.1.** Открыть `F:\TO_DBI\EXCHANGE\DS_STANDARD.md` (UTF-8).
**A.2.** Найти строку 401: `### 6.5. Общие правила завершения ()`.
**A.3.** Заменить на: `### 6.5. Общие правила завершения`.
**A.4.** Записать файл через `[System.IO.File]::WriteAllText` с
`[System.Text.UTF8Encoding]::new($false)` (без BOM).

### Часть B. Заменить литерал `r`n на настоящий перевод строки в bot.log

**B.1.** Прочитать `F:\TO_DBI\EXCHANGE\bot.log` целиком (UTF-8).
**B.2.** Найти фрагмент:

    Файл перенесён в PROCESSED.`r`n[08.10.2026 14:49:35]

**B.3.** Заменить на (с реальным переводом строки между `PROCESSED.`
и `[08.10.2026`):

    Файл перенесён в PROCESSED.
    [08.10.2026 14:49:35]

**B.4.** ВАЖНО: в PowerShell использовать `"..."` (двойные кавычки)
для интерполяции `r`n, ЛИБО использовать `[Environment]::NewLine`
или `[char]10` / `[char]13`. НЕ использовать одинарные кавычки '...'
с `r`n — это литерал.
**B.5.** Перезаписать файл через `[System.IO.File]::WriteAllText`
с `[System.Text.UTF8Encoding]::new($false)`.
**B.6.** Проверить: `Get-Content -Encoding UTF8 -Tail 8` показывает
строки DS_052, DS_118, DS_118-fix, DS_118-fix2 РАЗДЕЛЬНО, без `` `r`n ``.

### Часть C. Записать строку о DS_118-fix2 в bot.log

**C.1.** После части B — добавить в конец bot.log строку:

    [08.10.2026 HH:MM:SS] DS 118-fix2: Выполнено. Устранены дефекты DS_118-fix (§6.5 скобки, bot.log литерал). Файл перенесён в PROCESSED.

(дата/время — фактические на момент записи).

**C.2.** Запись через `Add-Content -Encoding UTF8` ИЛИ
`[System.IO.File]::AppendAllText` с `UTF8Encoding($false)`.
**C.3.** Проверить, что запись сделана ДО git add.

### Часть D. Диагностика источника M EXCHANGE/bot.log (для отчёта)

**D.1.** В отчёте зафиксировать факт: `M EXCHANGE/bot.log` был на
момент старта DS_118-fix2.
**D.2.** Найти в bot.log записи, появившиеся ПОСЛЕ коммита b92d391:
`Get-Content -Encoding UTF8 -Tail 20` — последняя запись до наших
правок (16:28:10, «DS 082b: AI_REQUEST_test.md: dry-run...»).
**D.3.** В отчёт добавить **гипотезу**: источник — pytest (при
прогоне `python -m pytest SRC\tests\ -q` появляется эта запись)
ИЛИ отдельный скрипт DS_082b. Правку НЕ делать — это отдельный DS.
**D.4.** В отчёт добавить **рекомендацию**: отдельный DS на
предотвращение записи в bot.log во время pytest/DS_082b.

## Порядок завершения (жёстко, см. AGENTS.md, строка 185+)

1. Выполнить правки A, B, C.
2. Создать отчёт `EXCHANGE/OUTBOX/DS_118_fix2_botlog_and_section_cleanup_report.md`
   (UTF-8 без BOM, русский).
3. Перенести задание в `EXCHANGE/PROCESSED/DS_118_fix2_botlog_and_section_cleanup.md`.
4. Запись в `EXCHANGE/bot.log` (часть C — уже сделана на шаге 1).
5. `git add` всех изменённых/новых файлов, включая:
   - `EXCHANGE/DS_STANDARD.md`,
   - **`EXCHANGE/bot.log`** (закрывает `M EXCHANGE/bot.log`),
   - `EXCHANGE/PROCESSED/DS_118_fix2_botlog_and_section_cleanup.md`,
   - `EXCHANGE/OUTBOX/DS_118_fix2_botlog_and_section_cleanup_report.md`.
6. `git commit -m "DS_118-fix2: section 6.5 cleanup + bot.log newline. Выполнено"`.
7. `git status -sb` → clean (кроме файлов из игнора).
8. `git push origin feature/dockerization`.
9. `git status -sb` → clean, ahead 0.

**ЗАПРЕЩЕНО:** создавать отчёт / писать в bot.log ПОСЛЕ git add / commit.

## Что НЕ делать

- НЕ трогать SRC\.
- НЕ менять .gitattributes, .gitignore.
- НЕ использовать одинарные кавычки '...' с escape-последовательностями
  `r`n — это литерал, а не перевод строки.
- НЕ использовать return в ручных блоках PowerShell.
- НЕ использовать @"..."@ (here-string) с бэктиками/кавычками/кириллицей.
- НЕ делать git push --force.
- НЕ переписывать историю.
- НЕ пытаться чинить источник записи в bot.log — это отдельный DS.

## §5. Проверка (обязательна в отчёте KODA)

1. **BOM-check**: AGENTS.md, EXCHANGE\DS_STANDARD.md, EXCHANGE\bot.log,
   EXCHANGE\OUTBOX\DS_118_fix2_botlog_and_section_cleanup_report.md
   — все BOM=False.
2. **Select-String** по DS_STANDARD.md:
   `Select-String -Path 'EXCHANGE\DS_STANDARD.md' -Pattern '^#{2,4} 6\.5\.'`
   — заголовок без `()`. Также проверить, что нет строки с `()`.
3. **Select-String** по bot.log:
   `Select-String -Path 'EXCHANGE\bot.log' -Pattern '\x60r\x60n'`
   — должно быть пусто.
4. **Get-Content bot.log -Encoding UTF8 -Tail 8** — строки DS_052,
   DS_118, DS_118-fix, DS_118-fix2 — раздельные, без кракозябр.
5. **git log --oneline -3** — верхний коммит DS_118-fix2.
6. **git status -sb** после push — clean, ahead 0.
7. **git branch -vv** — синхронизация с origin.
8. **Особое внимание:** `M EXCHANGE/bot.log` ДОЛЖЕН быть закрыт
   (закоммичен вместе с правками A, B, C). Если `M EXCHANGE/bot.log`
   появился СНОВА после push — зафиксировать в отчёте факт и время,
   НЕ пытаться закрыть в этом DS.

## Ожидаемый результат

- §6.5 без `()`.
- bot.log: нет литерала `` `r`n ``; строки DS_052/DS_118/DS_118-fix2
  раздельные.
- `M EXCHANGE/bot.log` закрыт (закоммичен).
- BOM=False у всех ключевых файлов.
- git status clean, ahead 0.
- Отчёт KODA в EXCHANGE\OUTBOX\ с диагностикой источника M bot.log
  и рекомендацией на отдельный DS.

## Завершение

Когда KODA заканчивает выполнение задания, вывести строку:

    -= Задание выполнил =-

Если KODA выводит:

    -= Нет заданий в INBOX =-

— завершить выполнение задания.