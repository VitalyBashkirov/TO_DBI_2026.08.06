# DS_118 — Процессный фикс: порядок операций при завершении DS + кодировка bot.log + закрытие хвоста отчёта

## Метаданные

- **Автор DS:** DeepSeek
- **Исполнитель:** KODA
- **Дата:** 08.10.2026
- **Ветка:** feature/dockerization
- **Базовый HEAD:** f95871687734a71668b2a7676971f8c4342b7ad2
- **Приоритет:** средний/высокий

## Проблема

### Проблема 1. Порядок операций при завершении DS

KODA четыре раза подряд (DS_116, DS_117, DS_117-fix, а также при GP-цикле
08.10.2026) оставлял хвосты в рабочем дереве:

- DS_116/DS_117/DS_117-fix: `M EXCHANGE/bot.log` — запись в bot.log
  делалась ПОСЛЕ коммита.
- GP-цикл 08.10.2026 (f958716): `?? EXCHANGE/OUTBOX/DS_118_prep_gp_cleanup_report.md`
  — отчёт создан ПОСЛЕ коммита, не попал в него.

Корневая причина: в AGENTS.md раздел «Порядок завершения» (строка 174)
и раздел «Запись в bot.log» (строка 326) описывают шаги, но НЕ фиксируют
жёсткую последовательность относительно `git add` и `git commit`.
В DS_STANDARD.md правила порядка операций нет вовсе.

### Проблема 2. Кодировка bot.log при чтении

Запись в bot.log через `Add-Content -Encoding UTF8` пишет UTF-8 без BOM
корректно. Но при ЧТЕНИИ через `Get-Content` без явного `-Encoding UTF8`
в PowerShell 5.1 файл интерпретируется как CP866/CP1251, и кириллица
превращается в кракозябры вида:

    [08.10.2026 13:49:26] GIT_20261008_1349 GP. Р’С‹РїРѕР»РЅРµРЅРѕ. ...

Это не порча файла — это дефект чтения. Факт подтверждён предполётной
проверкой 08.10.2026: при `Get-Content -Encoding UTF8` строка читается
корректно. Но диагностически опасно: можно принять рабочий файл за
битый и начать «чинить» его.

## Задача

### Часть A. Правило порядка операций при завершении DS

**A.1. Правка AGENTS.md, раздел «Порядок завершения» (строка 174)**

Дополнить существующий раздел явной жёсткой последовательностью:

    1. Выполнить правки по заданию DS.
    2. Создать отчёт KODA в EXCHANGE\OUTBOX\ (UTF-8 без BOM).
    3. Перенести задание из EXCHANGE\INBOX\ в EXCHANGE\PROCESSED\.
    4. Записать строку в EXCHANGE\bot.log (формат DS_050, см. §6.1).
    5. git add всех изменённых и новых файлов, включая:
       - файлы правок по заданию,
       - EXCHANGE\bot.log,
       - EXCHANGE\PROCESSED\<задание>.md,
       - EXCHANGE\OUTBOX\<отчёт>.md.
    6. git commit -m "<метка> Выполнено".
    7. git status -sb → ожидается clean (кроме файлов из игнора).
    8. git push origin feature/dockerization.
    9. git status -sb → clean, ahead 0.

    ЗАПРЕЩЕНО: создавать отчёт, переносить задание в PROCESSED или
    писать в bot.log ПОСЛЕ git add / git commit. Любая из этих операций
    после коммита оставляет хвост в рабочем дереве.

**A.2. Правка DS_STANDARD.md**

Добавить новый раздел **§6.3 «Порядок операций при завершении DS»**
сразу после §6.2 (строка 228), перед §9 (строка 334).

Содержание §6.3 — та же жёсткая последовательность из A.1,
со ссылкой на AGENTS.md «Порядок завершения». Согласовать с §3.1
(язык отчёта) и §3.2 (имена отчётов).

### Часть B. Правило кодировки bot.log

**B.1. AGENTS.md, строка 326 (`### 3. Запись в bot.log`) и
строка 356 (`## Формат записей в bot.log (DS_050)`)**

Дополнить явным правилом:

    ЗАПИСЬ в bot.log:
    Add-Content -Path "F:\TO_DBI\EXCHANGE\bot.log" `
                -Value $line -Encoding UTF8
    или (предпочтительно, без BOM-нюансов):
    [System.IO.File]::AppendAllText(
        "F:\TO_DBI\EXCHANGE\bot.log",
        $line + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false))

    ЧТЕНИЕ bot.log (диагностика, проверки):
    Get-Content -Path "F:\TO_DBI\EXCHANGE\bot.log" -Encoding UTF8 -Tail N

    ВАЖНО: без -Encoding UTF8 при чтении PowerShell 5.1 интерпретирует
    файл как CP866/CP1251, кириллица отображается как кракозябры
    (Р°, Р±, РІ, вЂ"). Это дефект ЧТЕНИЯ, не порча файла. Не «чинить»
    файл — перечитать с -Encoding UTF8.

**B.2. DS_STANDARD.md §6.1 (BOM)**

Дополнить §6.1 абзацем про чтение bot.log и про диагностику кракозябр.
Согласовать с существующим правилом записи UTF-8 без BOM.

### Часть C. Закрытие текущего хвоста

В рабочем дереве на момент старта DS_118:

    ?? EXCHANGE/OUTBOX/DS_118_prep_gp_cleanup_report.md

**C.1.** Добавить этот файл в коммит DS_118
(`git add EXCHANGE/OUTBOX/DS_118_prep_gp_cleanup_report.md`).
**C.2.** Больше ничего с ним не делать — он корректен (1899 B, BOM=False).

## Файлы, затрагиваемые DS_118

| Файл | Действие |
|------|----------|
| F:\TO_DBI\AGENTS.md | правка строк 174, 326, 356 |
| F:\TO_DBI\EXCHANGE\DS_STANDARD.md | новый §6.3 + дополнение §6.1 |
| F:\TO_DBI\EXCHANGE\OUTBOX\DS_118_prep_gp_cleanup_report.md | добавить в коммит |
| F:\TO_DBI\EXCHANGE\bot.log | запись о DS_118 |
| F:\TO_DBI\EXCHANGE\OUTBOX\DS_118_process_order_and_botlog_encoding_report.md | создать отчёт |
| F:\TO_DBI\EXCHANGE\PROCESSED\DS_118_process_order_and_botlog_encoding.md | перенести задание |

## Что НЕ делать

- НЕ трогать SRC\ без явного указания.
- НЕ менять .gitattributes, .gitignore.
- НЕ использовать return в ручных блоках PowerShell.
- НЕ использовать @"..."@ (here-string) с бэктиками/кавычками/кириллицей.
- НЕ использовать обратные слэши в git add при явном перечислении файлов.
- НЕ делать git push --force.
- НЕ создавать отчёт/запись в bot.log после git add / commit.

## §5. Проверка (обязательна в отчёте KODA)

1. **BOM-check** ключевых файлов из корня проекта:
   AGENTS.md, EXCHANGE\DS_STANDARD.md, EXCHANGE\bot.log,
   EXCHANGE\OUTBOX\DS_118_process_order_and_botlog_encoding_report.md —
   все BOM=False.
2. **Select-String** по AGENTS.md: наличие жёсткой последовательности
   (маркер «ЗАПРЕЩЕНО: создавать отчёт»).
3. **Select-String** по DS_STANDARD.md: наличие раздела
   «Порядок операций при завершении DS».
4. **git log --oneline -3** — верхний коммит DS_118.
5. **git status -sb** после push — clean, ahead 0.
6. **git branch -vv** — синхронизация с origin/feature/dockerization.
7. **Get-Content bot.log -Encoding UTF8 -Tail 3** — последняя строка
   DS_118 читается без кракозябр.

## Ожидаемый результат

- AGENTS.md содержит жёсткую последовательность завершения DS.
- DS_STANDARD.md содержит §6.3 «Порядок операций при завершении DS».
- AGENTS.md / DS_STANDARD.md §6.1 содержат правило чтения bot.log
  с -Encoding UTF8.
- Хвост `?? EXCHANGE/OUTBOX/DS_118_prep_gp_cleanup_report.md` закрыт.
- git status clean, ahead 0.
- Отчёт KODA в EXCHANGE\OUTBOX\ (UTF-8 без BOM, русский, без транслита).