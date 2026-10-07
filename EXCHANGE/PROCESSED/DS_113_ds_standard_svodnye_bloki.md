# DS_113 — DS_STANDARD.md: техника сводных блоков PowerShell

**Дата:** 2026-10-07
**Автор DS:** DeepSeek
**Исполнитель:** KODA
**Ветка:** feature/dockerization
**Приоритет:** средний

## 1. Цель

Зафиксировать в `EXCHANGE\DS_STANDARD.md` технику безопасного составления
сводных блоков PowerShell для ручного запуска. Уроки чата 15 (DS_111, DS_112):
два запуска были сломаны из-за `return` и `@"..."@` с кириллицей.

Изменения — **только документация**. `SRC\` не трогать.

## 2. Что менять

### 2.1. `EXCHANGE\DS_STANDARD.md` — новый подраздел §6.2

Вставить **после** существующего §6 «Форматирование» (строка 150)
и **перед** §7 «Чего избегать» (строка 230).

Заголовок: `### 6.2. Техника сводных блоков PowerShell (ручной запуск)`

Содержание (ниже — дословно):

---

**§6.2. Техника сводных блоков PowerShell (ручной запуск)**

Сводный блок — это набор команд PowerShell, который KODA/пользователь
вставляет в консоль **одной вставкой** и запускает одной кнопкой.

**Обязательные элементы (см. также §2 и §6.1):**

1. **Команда 0 — кодировка** (первой строкой):
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $OutputEncoding = [System.Text.Encoding]::UTF8
   chcp 65001
   ```
2. Секции с заголовками: `# --- N. <назначение> ---`.
3. Готовность к одной кнопке (без промежуточного ввода).
4. Ожидание — таблицей **вне** блока.
5. Чтение — `-Encoding UTF8`; запись .py/.ini/.json/.md —
   `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))`.

**Запреты (проверено практикой, чат 15):**

1. **`return` в ручных блоках** — непредсказуем при интерактивной вставке,
   может завершить весь блок. Сломал первый запуск DS_112.
   **Не использовать.** Для выхода — `if (...) { <действие> } else { <действие> }`
   без `return`.

2. **`@"..."@` (here-string) с бэктиками, кавычками или кириллицей** —
   парсер не закрывает строку, консоль «зависает». Сломал второй запуск DS_112.
   **Не использовать.** Для записи многострочного текста — `-join` массив строк:
   ```powershell
   $lines = @(
     '# Заголовок',
     '',
     'Текст с кириллицей и "кавычками".'
   )
   $text = $lines -join "`r`n"
   [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))
   ```

3. **`Get-ChildItem` + `Format-Table`** — отложенный вывод, сбивает с толку.
   Правильно: `Write-Host "$($_.Name)"` или явный `Out-String`.

4. **`$LASTEXITCODE` после `Select-String`** — не работает для «нашёл/не нашёл»:
   `Select-String` всегда возвращает 0.
   Использовать `-match` / `Out-String` + проверку переменной:
   ```powershell
   $found = Select-String -Path $file -Pattern $pat -Encoding UTF8
   if ($found) { Write-Host "НАЙДЕНО" } else { Write-Host "НЕ НАЙДЕНО" }
   ```

5. **Большие блоки дробить** на маленькие шаги с проверкой после каждого:
   `Select-String` / `Test-Path` / `Write-Host`.

**Git-гигиена (связано):**

6. **`git add` — только прямые слэши** (`/`). Обратные (`\`) дают `fatal pathspec`.
7. **После переноса INBOX → PROCESSED** — проверять `Test-Path` в PROCESSED.
8. **DS-задание может оказаться в OUTBOX вместо INBOX** — проверять
   фактическое расположение перед переносом.

---

### 2.2. `EXCHANGE\DS_STANDARD.md` — обновить §9.1 (чек-лист)

В §9.1 «§5 обязателен в отчёте KODA» добавить пункт:

- **§5 (Проверка)** обязательно включает вывод `Select-String` / BOM-check /
  `git log` / pytest — и **не использует `return` / `@"..."@`** в ручных блоках
  (см. §6.2).

## 3. Стандартные ограничения

- Не трогать `SRC\` (ни .py, ни .json, ни .ini).
- Не трогать `AGENTS.md` (это отдельный DS).
- Не трогать `.gitattributes` (это DS_114).
- Логи — только `EXCHANGE\bot.log`.
- Отчёт — `EXCHANGE\OUTBOX\DS_113_ds_standard_svodnye_bloki_report.md`.
- Задание — `EXCHANGE\PROCESSED\DS_113_ds_standard_svodnye_bloki.md`.
- Кодировка .md — UTF-8 **без BOM**
  (`[System.IO.File]::WriteAllText(..., UTF8Encoding($false))`).
- **Русский язык** отчёта (DS_STANDARD.md §3.1). Транслит запрещён.
- Git add — прямые слэши.

## 4. Разведка (перед правкой)

Выполнить и зафиксировать в §5 отчёта:

1. `Select-String -Path "EXCHANGE\DS_STANDARD.md" -Pattern "^### 6\." -Encoding UTF8`
   — убедиться, что §6.1 существует, а §6.2 — нет.
2. `Select-String -Path "EXCHANGE\DS_STANDARD.md" -Pattern "^## 7\." -Encoding UTF8`
   — найти точку вставки (перед §7).
3. `Select-String -Path "EXCHANGE\DS_STANDARD.md" -Pattern "^## 9\." -Encoding UTF8`
   — найти §9.1 для правки.
4. `(Get-Content "EXCHANGE\DS_STANDARD.md" -Encoding UTF8).Count` — текущее
   число строк (для контроля).

## 5. Реализация

### Шаг 1. Вставка §6.2

- Прочитать `DS_STANDARD.md` (`Get-Content -Encoding UTF8`).
- Найти индекс строки `## 7. Чего избегать`.
- Вставить перед ней блок §6.2 (текст из §2.1 выше).
- Сохранить через `WriteAllText` + `UTF8Encoding($false)`.
- **Не использовать** `@"..."@` — только `-join` массив строк.

### Шаг 2. Правка §9.1

- Найти блок §9.1.
- Добавить пункт про §5 (см. §2.2 выше).
- Сохранить тем же способом.

### Шаг 3. Проверка

- `Select-String` по `### 6.2` — должно найтись.
- `Select-String` по `Select-String` внутри §6.2 — должно найтись
  (упоминание в тексте).
- BOM-check: `BOM=False`.
- `git diff --stat` — только `EXCHANGE/DS_STANDARD.md`.

### Шаг 4. Отчёт

- `EXCHANGE\OUTBOX\DS_113_ds_standard_svodnye_bloki_report.md` (UTF-8 без BOM, русский).
- §5 обязателен: вывод Select-String / BOM / git log.

### Шаг 5. Перенос задания

- Переместить `DS_113_ds_standard_svodnye_bloki.md`
  из `EXCHANGE\INBOX\` (или откуда фактически) в `EXCHANGE\PROCESSED\`.
- **Проверить** `Test-Path` в PROCESSED.

## 6. Формат отчёта

Стандартный (DS_STANDARD.md §3, 6 разделов):
1. Что сделано
2. Изменённые файлы
3. Результат тестов (pytest — exit code)
4. Расхождения
5. **Проверка** (Select-String / BOM / git log — обязательно)
6. Артефакты (коммит, push)

## 7. Git

- **Не коммитить** без отдельной команды `GIT` от Vitaly.
- Имя коммита (если будет): `DS_113: DS_STANDARD.md — техника сводных блоков PowerShell (уроки чата 15)`.
- Push — только по команде `PUSH`.

## 8. Ожидание

- `DS_STANDARD.md`: +1 подраздел §6.2 (~60 строк), правка §9.1 (~3 строки).
- `SRC\` — **не тронут**.
- pytest — **не запускается** (нет изменений в коде), но в §5 отчёта указать
  «код не менялся, pytest не требуется» или прогнать для контроля (exit 0).