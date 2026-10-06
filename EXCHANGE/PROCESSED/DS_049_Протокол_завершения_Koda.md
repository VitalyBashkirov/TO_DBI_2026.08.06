# DS_049 — Протокол завершения Koda + автономная обработка INBOX

## Метаданные задачи

| Параметр | Значение |
|----------|----------|
| **Код задачи** | DS_049 |
| **Проект** | АРМ «Адаптация под DBI» (Народный банк) |
| **Предыдущие задачи** | DS_032–DS_048 |
| **Приоритет** | HIGH |
| **Статус** | К выполнению |
| **Исполнитель** | KODA (VS Code) |
| **Репозиторий** | `F:\TO_DBI\` |
| **Каталоги** | `EXCHANGE\INBOX\`, `EXCHANGE\PROCESSED\`, `EXCHANGE\OUTBOX\` |
| **Файл лога** | `F:\TO_DBI\EXCHANGE\bot.log` |

---

## Контекст задачи

### Что было раньше

**Бот** (`exchange_bot.py`) **работал** **автоматически** каждые 15 секунд и **переносил** файлы из `INBOX` в `PROCESSED`. **Проблема**: бот **не выполнял** задачи — просто переносил файлы. **Koda** не успевала прочитать файлы.

**Решение**: бот **отключён навсегда**. Автозапуск **удалён**.

### Что нужно сейчас

**Koda сама обрабатывает** `INBOX` по команде «DS»:

1. **Найти** все файлы `DS_XXX_*.md` в `INBOX`.
2. **Обработать** их последовательно (по возрастанию `XXX`).
3. **После успешного выполнения**:
   - Перенести файл в `PROCESSED`.
   - Создать отчёт в `OUTBOX\DS_XXX_отчет.md`.
   - Дописать запись в `bot.log`.
4. **Если задача задала вопрос** (не завершена) — **оставить** файл в `INBOX`.

### Текущее состояние

- Бот **отключён**.
- `bot.log` содержит одну запись (от старого бота).
- **Koda не имеет протокола завершения** — файлы остаются в `INBOX`.

---

## Задачи KODA

### ЗАДАЧА 1 — Диагностика

**Действие 1 — Проверить состояние `INBOX`**:

```
dir F:\TO_DBI\EXCHANGE\INBOX
```

**Прислать**: вывод.

**Действие 2 — Проверить `bot.log`**:

```
type F:\TO_DBI\EXCHANGE\bot.log
```

**Прислать**: вывод.

**Действие 3 — Проверить `PROCESSED` и `OUTBOX`**:

```
dir F:\TO_DBI\EXCHANGE\PROCESSED
dir F:\TO_DBI\EXCHANGE\OUTBOX
```

**Прислать**: вывод.

**Цель**: понять текущее состояние каталогов.

---

### ЗАДАЧА 2 — Создать скрипт автономной обработки INBOX

**Файл**: `F:\TO_DBI\SRC\process_inbox.py` (новый)

**Содержимое**:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS 049: Автономная обработка INBOX.
Обрабатывает файлы DS_XXX_*.md:
1. Читает задание.
2. Выполняет (логика — вне скрипта, Koda).
3. Переносит в PROCESSED.
4. Создаёт отчёт в OUTBOX.
5. Дописывает запись в bot.log.
"""
import os
import re
import shutil
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(r'F:\TO_DBI\EXCHANGE')
INBOX = BASE_DIR / 'INBOX'
PROCESSED = BASE_DIR / 'PROCESSED'
OUTBOX = BASE_DIR / 'OUTBOX'
BOT_LOG = BASE_DIR / 'bot.log'


def _log(message: str):
    """DS 049: запись в bot.log."""
    timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    line = f"[{timestamp}] {message}\n"
    with open(BOT_LOG, 'a', encoding='cp1251', errors='replace') as f:
        f.write(line)
    print(f"[LOG] {line.strip()}")


def list_inbox_tasks() -> list:
    """DS 049: список задач в INBOX (DS_XXX_*.md), отсортированный по номеру."""
    if not INBOX.exists():
        return []

    tasks = []
    for f in INBOX.glob('DS_*.md'):
        m = re.match(r'DS_(\d+)_(.+)\.md', f.name)
        if m:
            tasks.append((int(m.group(1)), f))
    tasks.sort(key=lambda t: t[0])
    return [f for _, f in tasks]


def read_task(task_file: Path) -> str:
    """DS 049: чтение задания."""
    with open(task_file, 'r', encoding='utf-8') as f:
        return f.read()


def move_to_processed(task_file: Path) -> Path:
    """DS 049: перенос файла в PROCESSED."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    target = PROCESSED / task_file.name
    shutil.move(str(task_file), str(target))
    return target


def write_report(task_file: Path, content: str):
    """DS 049: запись отчёта в OUTBOX."""
    OUTBOX.mkdir(parents=True, exist_ok=True)
    report_name = f"{task_file.stem}_отчет.md"
    report_path = OUTBOX / report_name
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return report_path


def main():
    """DS 049: главная функция — обход INBOX."""
    print("=" * 60)
    print("DS 049: Автономная обработка INBOX")
    print("=" * 60)

    tasks = list_inbox_tasks()

    if not tasks:
        print("[INFO] INBOX пуст — задач нет.")
        _log("DS 049: Проверка INBOX — задач нет.")
        return

    print(f"[INFO] Найдено задач: {len(tasks)}")
    for t in tasks:
        print(f"  - {t.name}")

    _log(f"DS 049: Найдено задач в INBOX: {len(tasks)}")
    print()

    for task_file in tasks:
        print(f"[TASK] Обработка: {task_file.name}")

        try:
            content = read_task(task_file)
        except Exception as e:
            _log(f"DS 049: ОШИБКА чтения {task_file.name} — {e}")
            continue

        print(f"[INFO] Задание прочитано ({len(content)} символов)")
        print(f"[INFO] Дальнейшая обработка — за Koda (см. промпт)")
        print()

    print("[INFO] Задачи найдены. Koda обрабатывает по очереди.")


if __name__ == '__main__':
    main()
```

**Прислать**: содержимое созданного файла.

---

### ЗАДАЧА 3 — Протокол завершения для Koda

**Файл**: `F:\TO_DBI\AGENTS.md`

**Действие**: Добавить раздел «Протокол завершения (DS_049)»:

````markdown
## Протокол завершения (DS_049)

**Koda** при обработке задач **DS_XXX_*.md** в `INBOX\` **обязана** выполнить следующие шаги **после завершения каждой задачи**:

### 1. Перенос файла в PROCESSED

```powershell
Move-Item "F:\TO_DBI\EXCHANGE\INBOX\DS_XXX_*.md" "F:\TO_DBI\EXCHANGE\PROCESSED\"
```

**Проверка**:

```powershell
dir "F:\TO_DBI\EXCHANGE\INBOX\DS_XXX_*.md"
```

**Ожидаемо**: файла нет.

### 2. Создание отчёта в OUTBOX

**Файл**: `F:\TO_DBI\EXCHANGE\OUTBOX\DS_XXX_отчет.md`.

**Содержимое**:

```markdown
# DS_XXX — Отчёт о выполнении

**Дата**: YYYY-MM-DD HH:MM:SS
**Задача**: DS_XXX_<название>.md
**Статус**: ✅ Выполнено / ⚠️ Ожидание ответа / ❌ Ошибка

## Что сделано

1. ...
2. ...

## Артефакты

- `SRC\...` — изменённые файлы.
- `temp\test_dsXXX_*.py` — тесты.

## Результаты тестов

- test_dsXXX_*.py — N/N PASSED.
- Регресс DS_032–DS_049 — M/M PASSED.

## Следующие шаги

- ...
```

### 3. Запись в bot.log

```powershell
Add-Content "F:\TO_DBI\EXCHANGE\bot.log" "[HH:MM:SS] DS_XXX: Выполнено. <краткое описание>. Файл перенесён в PROCESSED."
```

**Формат**:

```
[15:45:30] DS_049: Выполнено. Протокол завершения Koda. Файл перенесён в PROCESSED.
```

### 4. Финальная проверка

- ✅ `INBOX` — пуст.
- ✅ Файл в `PROCESSED`.
- ✅ Отчёт в `OUTBOX`.
- ✅ Запись в `bot.log`.

**Если** что-то не выполнено — **не переносить** файл в `PROCESSED`.

### 5. Случай «Koda задала вопрос»

**Если** задача не завершена (Koda задала вопрос):

- Файл **остаётся** в `INBOX`.
- Запись в `bot.log`: `[HH:MM:SS] DS_XXX: Ожидание ответа пользователя. Файл остаётся в INBOX.`
- Отчёт в `OUTBOX` — создать (со статусом «Ожидание»).
Прислать: фрагмент добавленного раздела.

ЗАДАЧА 4 — Тест на реальной задаче
Действие 1 — Создать тестовую задачу:

Файл: F:\TO_DBI\EXCHANGE\INBOX\DS_997_Тест_протокола.md

Содержимое:

markdown
# DS_997 — Тест протокола

## Задача

Прочитать этот файл и выполнить протокол завершения (DS_049):

1. Перенести файл в `PROCESSED`.
2. Создать отчёт в `OUTBOX\DS_997_отчет.md`.
3. Дописать в `bot.log`.
4. Проверить — `INBOX` пуст.

**Это** — тестовая задача. **Ничего не менять** в коде.
Действие 2 — Запустить Koda:

В VS Code → Koda-агент → команда «DS».

Действие 3 — Проверить результат:

powershell
dir "F:\TO_DBI\EXCHANGE\INBOX"
dir "F:\TO_DBI\EXCHANGE\PROCESSED" | Select-String "DS_997"
dir "F:\TO_DBI\EXCHANGE\OUTBOX" | Select-String "DS_997"
Get-Content "F:\TO_DBI\EXCHANGE\bot.log" -Tail 5
Ожидаемо:

INBOX — пусто.

DS_997_Тест_протокола.md — в PROCESSED.

DS_997_отчет.md — в OUTBOX.

bot.log — запись о DS_997.

Прислать: вывод 4 команд.

ЗАДАЧА 5 — Обработать накопленные задачи в INBOX
Если в INBOX есть другие задачи — обработать их по протоколу.

Проверить:

text
dir F:\TO_DBI\EXCHANGE\INBOX
Прислать: вывод.

Критерии приёмки DS_049
№	Критерий	Признак
1	Скрипт process_inbox.py создан	Файл
2	AGENTS.md — раздел «Протокол завершения» добавлен	Файл
3	Тестовая задача DS_997 создана	Файл
4	Koda обработала DS_997	Тест
5	DS_997 — в PROCESSED	dir
6	DS_997_отчет.md — в OUTBOX	dir
7	bot.log — запись	bot.log
8	INBOX — пусто	dir
Приложение А — Что НЕ делать
❌ Не восстанавливать бота (exchange_bot.py).

❌ Не запускать автозапуск (run_bot_hidden.vbs).

❌ Не менять логику сканера / фиксера — только протокол.

❌ Не ломать существующие тесты DS_032–DS_049.

❌ Не переносить файл в PROCESSED, если задача не завершена (Koda задала вопрос).

Приложение Б — Структура каталогов
text
F:\TO_DBI\EXCHANGE\
├── INBOX\                — новые задачи (DS_XXX_*.md)
├── PROCESSED\            — обработанные задачи
├── OUTBOX\               — отчёты о выполнении
└── bot.log               — лог выполнения
Отчёт о выполнении
Диагностика — состояние INBOX, PROCESSED, OUTBOX, bot.log.

Скрипт process_inbox.py — создан.

AGENTS.md — раздел «Протокол завершения (DS_049)» — добавлен.

Тестовая задача DS_997 — создана.

Результат обработки DS_997:

INBOX — пусто.

DS_997 — в PROCESSED.

DS_997_отчет.md — в OUTBOX.

bot.log — запись.

Конец задания DS_049.