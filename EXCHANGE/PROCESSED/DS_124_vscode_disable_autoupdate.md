# DS_124 — VSCode: отключить автообновление расширений

## Контекст

VSCode пытается обновить Koda 1.2.2 → 1.2.3, но Koda.gallerycdn.vsassets.io
блокируется DPI (TLS рвётся, TCP 443 проходит). Автообновление невозможно,
создаёт шум. Надо отключить.

## Файл

C:\Users\Виталий\AppData\Roaming\Code\User\settings.json

## Правка

Добавить два ключа в корневой объект JSON:

    "extensions.autoUpdate": false,
    "extensions.autoCheckUpdates": false

## Ограничения

- Сохранить UTF-8 (JSON без BOM).
- Не менять существующие ключи.
- Проверить валидность JSON после правки (см. §5).

## Проверка (§5 обязателен)

1. Get-Content $settingsPath → содержит оба новых ключа.
2. JSON валиден: Get-Content $settingsPath -Raw | ConvertFrom-Json.
3. Select-String $settingsPath -Pattern "autoUpdate" → 2 совпадения.

## Ожидаемый результат

- VSCode перестаёт проверять обновления расширений.
- Koda остаётся 1.2.2.