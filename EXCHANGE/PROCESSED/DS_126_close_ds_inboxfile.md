# DS_126. close_ds.ps1: параметр -InboxFile + авто-очистка INBOX

## Контекст

АРМ «Адаптация под DBI». Ветка feature/dockerization.
Роли: Автор DS — DeepSeek. Пользователь — Vitaly.
KODA не запускается (правило F, DS_125). Всё — вручную PowerShell.

## Проблема

Урок E (чат 21): при ручном выполнении DS файл задания из INBOX
обязательно удалять. Нарушено дважды: DS_122, DS_125.
close_ds.ps1 v2 создаёт PROCESSED/OUTBOX с нуля, но НЕ чистит INBOX.

## Цель

1. Добавить параметр -InboxFile в tools\close_ds.ps1.
2. При заданном -InboxFile: удалить файл из EXCHANGE\INBOX после
   создания PROCESSED-версии.
3. Обновить AGENTS.md L576 (раздел DS_123) — описание -InboxFile.
4. Добавить в DS_STANDARD.md §6.2.1 Уроки G, H и I.

## Изменения

### 1. tools\close_ds.ps1

- param-блок: добавлен [string]$InboxFile = '' (после $Branch).
- Новая секция [2.5/8] между [2/8] и [3/8]:
  - Если $InboxFile пустой — "[2.5] InboxFile не задан (ок)".
  - Если задан и существует — Remove-Item, "[2.5] INBOX удалён: ...".
  - Если задан и не существует — "[2.5] INBOX не найден (ок): ...".
- Существующий API не сломан (обратная совместимость).
- Файл записан С BOM (требование PS 5.1 + кириллица).

### 2. AGENTS.md L576 (раздел «Закрытие DS через PS»)

- В пример добавлен -InboxFile "EXCHANGE/INBOX/DS_XXX_описание.md".
- Добавлено описание: если задан — INBOX-файл удаляется после
  создания PROCESSED.

### 3. EXCHANGE\DS_STANDARD.md §6.2.1

Добавлены Уроки:
- п.4 (Урок G): -Filter в Get-ChildItem не поддерживает regex-классы.
- п.5 (Урок H): [Parser]::ParseFile / ParseInput и BOM.
- п.6 (Урок I): .ps1 с кириллицей требует BOM в PS 5.1.

## Проверка

1. Синтаксис close_ds.ps1: AST ParseFile -> 0 ошибок.
2. BOM: close_ds.ps1 = True; AGENTS.md, DS_STANDARD.md = False.
3. Тестовые сценарии [2.5/8]: 3 сценария — все OK.
4. После закрытия: INBOX пуст, PROCESSED/OUTBOX содержат файлы.

## Отчёт

EXCHANGE\OUTBOX\DS_126_close_ds_inboxfile_report.md