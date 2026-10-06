# DS_095 — Правило BOM в DS_STANDARD.md

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация (документация)
**Приоритет:** средний
**Зависит от:** DS_091a (pytest.ini + BOM)
**Блокирует:** —

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

## 1. Цель

Зафиксировать в `DS_STANDARD.md` правило: **не использовать `Out-File -Encoding UTF8`** (PowerShell 5.1) для файлов, которые читает Python/pytest. Заменить на метод .NET — **UTF-8 без BOM**.

**Обоснование:** три случая BOM в проекте:
1. DS_089a — `BOM fix` при прерывании (git log).
2. `pytest.ini` — BOM сломал парсинг: `unexpected line: '\ufeff[pytest]'`.
3. Потенциально — `.json`, `.cfg`, `.py`, созданные через `Out-File`.

## 2. Файл

`F:\TO_DBI\EXCHANGE\DS_STANDARD.md`

## 3. Что добавить

**Новый подраздел 6.1** в раздел 6 «Форматирование» (после таблицы-примера, до раздела 7 «Чего избегать»):

````markdown
### 6.1. Кодировка файлов и BOM

**Правило:** для файлов, которые читает Python/pytest/любой не-Windows-парсер, — **UTF-8 без BOM**.

| Расширение | Кодировка | Инструмент PowerShell |
|-----------|-----------|----------------------|
| `.py`, `.ini`, `.cfg`, `.json`, `.yaml`, `.toml` | **UTF-8 без BOM** | `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` |
| `.md`, `.log`, `.txt` (отчёты) | UTF-8 без BOM | `Set-Content -Encoding UTF8` (BOM допустим) |
| `.cmd`, `.bat` | ASCII / OEM | `Set-Content -Encoding ASCII` |

**Почему:** PowerShell 5.1 `Out-File -Encoding UTF8` **всегда** добавляет BOM (`EF BB BF`). Python, pytest, `.ini`-парсеры **не понимают** BOM → ошибки:

```
ERROR: F:\TO_DBI\pytest.ini:1: unexpected line: '\ufeff[pytest]'
```

**Правильно (PowerShell 5.1, без BOM):**

```powershell
[System.IO.File]::WriteAllText('F:\TO_DBI\pytest.ini', @"
[pytest]
testpaths = SRC/tests
"@, [System.Text.UTF8Encoding]::new($false))
```

**Правильно (UTF-8 с BOM допустим — для отчётов):**

```powershell
@"
# Отчёт
"@ | Set-Content -Encoding UTF8 F:\TO_DBI\EXCHANGE\OUTBOX\DS_XXX_report.md
```

**Проверка BOM:**

```powershell
Format-Hex -Path F:\TO_DBI\pytest.ini | Select-Object -First 1
```

**Первые 3 байта:**
- `EF BB BF` — **BOM есть** (плохо для `.py`/`.ini`/`.json`).
- Иначе — **BOM нет** (хорошо).

**Случаи в проекте:**
- DS_089a — BOM fix (git log).
- DS_091a — `pytest.ini` BOM сломал парсинг.
- Правило — **обязательное** для всех будущих DS.

4. Что НЕ менять
Разделы 1–5 DS_STANDARD.md — не трогать.

Раздел 6 — только добавить подраздел 6.1 в конец.

Разделы 7–9 — не трогать.

5. Проверка
#	Что	Ожидание
1	Get-Content F:\TO_DBI\EXCHANGE\DS_STANDARD.md	Раздел 6.1 присутствует
2	Select-String -Path ... -Pattern "6.1. Кодировка"	Строка найдена
3	Select-String -Path ... -Pattern "UTF8Encoding\(\$false\)"	Пример с методом .NET найден
4	Select-String -Path ... -Pattern "unexpected line"	Пример с ошибкой найден
5	Format-Hex -Path DS_STANDARD.md	BOM в .md допустим — не критично
6. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Менять только DS_STANDARD.md. Другие файлы не трогать. Не переписывать существующие разделы — только добавление.

7. Отчёт
Стандартный (DS_STANDARD.md → раздел 3) + разделы:

text
## Diff DS_STANDARD.md
- Добавлен подраздел 6.1 «Кодировка файлов и BOM»
- Строк добавлено: N
- Разделы 1–5, 7–9 не изменены

## Проверка BOM
- DS_STANDARD.md: BOM есть/нет (для .md не критично)

## Ссылки
- Раздел 6.1 в новом виде: <цитата>
8. Критерии успеха
Подраздел 6.1 добавлен в DS_STANDARD.md.

Примеры PowerShell (правильный + неправильный) есть.

Проверка BOM через Format-Hex описана.

Случаи DS_089a, DS_091a упомянуты.

Разделы 1–5, 7–9 не изменены.

9. Артефакты
F:\TO_DBI\EXCHANGE\DS_STANDARD.md (изменён)

EXCHANGE\OUTBOX\DS_095_report.md