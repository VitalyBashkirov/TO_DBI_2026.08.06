# DS_124 — отчёт: VSCode отключение автообновления расширений

**Статус:** Выполнено вручную PowerShell (KODA не запускалась).
**Дата:** 09.10.2026 01:24:55

## Что сделано

- В settings.json добавлены два ключа:
    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false
- settings.json перезаписан с нормальными отступами (2-space).

## Изменённые файлы

- C:\Users\Виталий\AppData\Roaming\Code\User\settings.json (вне git-репозитория).

## Проверка (§5)

1. JSON валиден: ConvertFrom-Json -> OK.
2. autoUpdate: L16, autoCheckUpdates: L17 — 2 совпадения.
3. BOM: False.

## Ожидаемый результат

- VSCode перестаёт проверять обновления расширений.
- Koda остаётся 1.2.2.

## Задание

EXCHANGE\PROCESSED\DS_124_vscode_disable_autoupdate.md