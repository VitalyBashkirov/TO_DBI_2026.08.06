#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS 049: Автономная обработка INBOX.
Обрабатывает файлы DS_XXX_*.md:
1. Читает задание.
2. Выполняет (логика - вне скрипта, Koda).
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
    """DS 050: запись в bot.log (UTF-8, формат ДД.ММ.ГГГГ ЧЧ:ММ:СС)."""
    timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    line = f"[{timestamp}] {message}\n"
    with open(BOT_LOG, 'a', encoding='utf-8', errors='replace') as f:
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
    """DS 049: главная функция - обход INBOX."""
    print("=" * 60)
    print("DS 049: Автономная обработка INBOX")
    print("=" * 60)

    tasks = list_inbox_tasks()

    if not tasks:
        print("[INFO] INBOX пуст - задач нет.")
        _log("DS 049: Проверка INBOX - задач нет.")
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
            _log(f"DS 049: ОШИБКА чтения {task_file.name} - {e}")
            continue

        print(f"[INFO] Задание прочитано ({len(content)} символов)")
        print(f"[INFO] Дальнейшая обработка - за Koda (см. промпт)")
        print()

    print("[INFO] Задачи найдены. Koda обрабатывает по очереди.")


if __name__ == '__main__':
    main()
