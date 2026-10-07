# DS_112 — pytest-шум + git-гигиена

**Дата:** 2026-10-07
**Автор:** DeepSeek
**Тип:** реализация
**Приоритет:** низкий

## 1. Цель

Устранить pytest-шум (3a, 3b) и закрепить git-гигиену (G1, G2).

**Причина:**
- **3a:** `print` в `_finish_abortable_operation` (gui_app.py, строки 1836, 1842, 1846) — pytest печатает `[DS_108a] Ошибка сброса...` / `[DS 042] Ошибка сброса...`. Реальный риск отсутствует (вызов обёрнут в try/except), но шум.
- **3b:** тесты печатают `[!] Файл не найден: F:\TO_DBI\SRC\tests\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json`. Каталог `SRC\tests\DATA` отсутствует. Тесты PASSED и без файла — достаточно заглушки.
- **G1:** `git add` с обратным слэшем даёт `fatal: pathspec ... did not match any files` (споткнулись 2 раза в DS_111).
- **G2:** §1 DS_049 не проверяет наличие файла в PROCESSED после `Move-Item` — ложное срабатывание при сбое.

## 2. Что менять

### 2.1. `SRC\gui_app.py` (3a)

**Правка 3a-1.** Добавить `import logging` + `logger` после блока UTF-8 (строки 10-14):

Было:
```python
import sys
import io
# Принудительное переключение на UTF-8 для корректного вывода в консоли
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from typing import List, Tuple, Optional
2.2. SRC\tests\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json (3b)
Создать каталоги:

text
SRC\tests\DATA\
SRC\tests\DATA\Рубрикатор v5\
Создать файл SRC\tests\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json (UTF-8 без BOM, ~200 B) — заглушка:

json
{
  "version": "5.3.0-stub-ds112",
  "comment": "Заглушка для тестов (DS_112). Оригинал: F:\\TO_DBI\\DATA\\Рубрикатор v5\\4.RUBRICATOR_PROMPT v5.json",
  "rules": {}
}
Перед созданием — проверить игнор:

powershell
git check-ignore -v "SRC/tests/DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json"
Если игнорируется — остановиться, сообщить в отчёте (нужно будет исключение в .gitignore).

2.3. AGENTS.md — G1: прямые слэши в git
В раздел «Git-процедуры (DS_051)» — добавить после строки про EOL:

Пути в git: использовать прямые слэши (/) в путях git add / git restore / git ls-files и т.п. Обратные слэши (\) в Windows могут дать fatal: pathspec ... did not match any files.

2.4. AGENTS.md — G2: проверка PROCESSED после Move-Item
В §1 «Перенос файла в PROCESSED» — добавить после блока dir INBOX:

Было:

powershell
**Проверка**:

```powershell
dir "F:\TO_DBI\EXCHANGE\INBOX\DS_XXX_*.md"
Ожидаемо: файла нет.

text

Станет:
```powershell
**Проверка**:

```powershell
dir "F:\TO_DBI\EXCHANGE\INBOX\DS_XXX_*.md"
Ожидаемо: файла нет.

Проверка переноса:

powershell
Get-ChildItem "F:\TO_DBI\EXCHANGE\PROCESSED\DS_XXX_*.md"
Ожидаемо: файл есть. Если файла нет в PROCESSED — перенос не выполнен; не переходить к §2, разобраться.

text

## 3. Ограничения

- Не трогать SRC, кроме `SRC\gui_app.py` (3a) и нового `SRC\tests\DATA\...` (3b).
- Не трогать `.gitattributes` (полный, оставить как есть).
- Не трогать `DS_STANDARD.md` (уже обновлён в DS_111).
- Запись `.py/.md/.json` — только `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))`.
- Чтение — только `Get-Content -Encoding UTF8`.
- Один коммит + push.

## 4. Проверка (§5 — обязательно)

В отчёт KODA включить вывод:
- `Select-String` по `gui_app.py` (проверка `logger.debug` × 3, `import logging`);
- `Select-String` по `AGENTS.md` (G1, G2);
- BOM-check: `gui_app.py`, `AGENTS.md`, новый JSON;
- `Test-Path` нового каталога и файла;
- `git check-ignore` нового файла (не игнорируется);
- `git log -1 --oneline`;
- `pytest -q` → 65 PASSED, шум `[DS_108a]` / `[!] Файл не найден` **отсутствует**.

## 5. Отчёт

Файл: `EXCHANGE\OUTBOX\DS_112_pytest_noise_git_hygiene_report.md`
Структура — по `DS_STANDARD.md` §3 (6 разделов, §5 = Проверка).

## 6. Git

- Один коммит: `DS_112: pytest-шум (logger.debug) + git-гигиена (прямые слэши, проверка PROCESSED)`.
- **GIT + PUSH** (push в `origin/feature/dockerization`).