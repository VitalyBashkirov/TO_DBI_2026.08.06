#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exchange Bot - Pure Courier Mode (Variant C)
Runs every 15 seconds, checks INBOX, saves task copies to OUTBOX, archives processed.
"""

import os
import shutil
import time
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent / 'EXCHANGE'
INBOX = BASE_DIR / 'INBOX'
OUTBOX = BASE_DIR / 'OUTBOX'
PROCESSED = BASE_DIR / 'PROCESSED'

# Log file
LOG_FILE = BASE_DIR / 'bot.log'

# Create folders
for folder in [INBOX, OUTBOX, PROCESSED]:
    folder.mkdir(parents=True, exist_ok=True)


def write_log(message: str):
    """Write message to log file (2 MB limit)"""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 2 * 1024 * 1024:
        print(f"[INFO] Log file too large. Stopping logging.")
        return
    # ВАЖНО: используем newline='\r\n' для Windows CR LF
    with open(LOG_FILE, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")


# ==================== DS 048: протокол завершения задач ====================

def _log_bot(message: str):
    """DS 048: запись в bot.log (cp1251, формат [ДД.ММ.ГГГГ ЧЧ:ММ:СС] <Сообщение>)."""
    try:
        line = '[%s] %s\r\n' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'), message)
        with open(LOG_FILE, 'a', encoding='cp1251', errors='replace') as f:
            f.write(line)
    except Exception as e:
        print(f"[DS 048] Ошибка записи bot.log: {e}")


def _is_task_completed(koda_response: str) -> bool:
    """
    DS 048: проверка — Koda завершила задачу?
    Признаки завершения:
    - "-= Задание выполнил =-"
    - "-= DS_XXX успешно выполнен =-"
    - "Задача выполнена"
    - "Проект TO_DBI успешно обработан!"
    """
    if not koda_response:
        return False

    completion_markers = [
        "-= Задание выполнил =-",
        "-= Задание выполнено =-",
        "-= DS",  # "-= DS_XXX успешно выполнен =-"
        "Задача выполнена",
        "Проект TO_DBI успешно обработан",
    ]

    return any(marker in koda_response for marker in completion_markers)


def _is_task_waiting(koda_response: str) -> bool:
    """
    DS 048: проверка — Koda задала вопрос (ждёт ответа)?
    Признаки ожидания:
    - "Жду вашего решения"
    - "Жду подтверждения"
    - "Что делаем дальше"
    - "Как поступим"
    - "Уточните"
    """
    if not koda_response:
        return False

    waiting_markers = [
        "Жду вашего решения",
        "Жду подтверждения",
        "Что делаем дальше",
        "Как поступим",
        "Уточните",
    ]

    return any(marker in koda_response for marker in waiting_markers)


def _finalize_task(task_file: Path, koda_response: str):
    """
    DS 048: финализация задачи.

    - Если завершена — переносим в PROCESSED, пишем в bot.log.
    - Если ждёт ответа — оставляем в INBOX.
    - Если не завершена и не ждёт — оставляем в INBOX с предупреждением.
    """
    if _is_task_completed(koda_response):
        # Задача завершена — переносим
        PROCESSED.mkdir(parents=True, exist_ok=True)
        target = PROCESSED / task_file.name
        try:
            shutil.move(str(task_file), str(target))
            _log_bot(f"{task_file.name}: Выполнено. Файл перенесён в PROCESSED.")
            print(f"[DS 048] Файл перенесён в PROCESSED: {task_file.name}")
        except Exception as e:
            _log_bot(f"{task_file.name}: ОШИБКА переноса — {e}")
            print(f"[DS 048] Ошибка переноса {task_file.name}: {e}")
    elif _is_task_waiting(koda_response):
        # Koda ждёт ответа — оставляем
        _log_bot(f"{task_file.name}: Ожидание ответа пользователя. Файл остаётся в INBOX.")
        print(f"[DS 048] Файл остаётся в INBOX (Koda ждёт ответа): {task_file.name}")
    else:
        # Не завершена, не ждёт — оставляем с предупреждением
        _log_bot(f"{task_file.name}: Задача не завершена. Файл остаётся в INBOX.")
        print(f"[DS 048] Файл остаётся в INBOX (задача не завершена): {task_file.name}")
# ==================== конец DS 048 ====================


def process_task(task_file: Path, content: str):
    """
    Pure courier: save a copy of the task to OUTBOX and archive the original.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing task: {task_file.name}")
    write_log(f"[{datetime.now().strftime('%H:%M:%S')}] Processing task: {task_file.name}")
    
    # Save copy of task to OUTBOX
    response_filename = f"response_{task_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response_path = OUTBOX / response_filename
    
    response = {
        'status': 'courier_success',
        'task': task_file.name,
        'received_at': datetime.now().isoformat(),
        'content': content,
        'note': 'Task received. Koda will read this and execute according to AGENTS.md.'
    }
    
    # ВАЖНО: используем newline='\r\n' для Windows CR LF
    with open(response_path, 'w', encoding='utf-8', newline='\r\n') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
    
    print(f"[+] Response saved: {response_path}")
    write_log(f"[+] Response saved: {response_path}")
    
    # Move task to archive
    shutil.move(str(task_file), str(PROCESSED / task_file.name))
    print(f"[+] Task moved to archive: {PROCESSED / task_file.name}")
    write_log(f"[+] Task moved to archive: {PROCESSED / task_file.name}")


def _read_text_safe(path: Path) -> str:
    """DS 048: чтение файла с автоопределением кодировки."""
    for enc in ('utf-8', 'utf-8-sig', 'cp1251', 'latin-1'):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding='utf-8', errors='replace')


def _find_koda_response(task_file: Path) -> str:
    """
    DS 048: найти ответ Koda для задачи в OUTBOX.

    Ищем файлы DS_XXX_* (по коду задачи, например DS_999), изменённые
    после появления задания в INBOX. Возвращаем текст ответа
    (пустая строка — если ответа нет).
    """
    code = task_file.name.split('_')[0] + '_' + task_file.name.split('_')[1]  # DS_999
    try:
        task_mtime = task_file.stat().st_mtime
    except OSError:
        task_mtime = 0.0

    candidates = [p for p in OUTBOX.glob(code + '*') if p.is_file()]
    # Свежайший ответ
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for p in candidates:
        if p.stat().st_mtime >= task_mtime:
            try:
                return _read_text_safe(p)
            except Exception:
                continue
    return ""


def main():
    """
    Continuous courier: watches INBOX every 15 seconds.
    DS 048: финализация задач — по ответу Koda (OUTBOX) файл
    переносится в PROCESSED либо остаётся в INBOX.
    """
    print(f"[INFO] Exchange Courier started (continuous mode)")
    print(f"[INFO] Watching: {INBOX}")
    print(f"[INFO] Saving to: {OUTBOX}")
    print(f"[INFO] Log file: {LOG_FILE}")
    print(f"[INFO] Press Ctrl+C to stop\n")

    write_log("[INFO] Exchange Courier started (continuous mode)")

    while True:
        # Check INBOX for tasks
        tasks = list(INBOX.glob('*'))

        if tasks:
            print(f"[INFO] Found {len(tasks)} task(s).")
            write_log(f"[INFO] Found {len(tasks)} task(s).")

            for task_file in tasks:
                try:
                    # Read file with encoding detection
                    try:
                        with open(task_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        try:
                            with open(task_file, 'r', encoding='cp1251') as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            with open(task_file, 'r', encoding='latin-1') as f:
                                content = f.read()

                    process_task(task_file, content)

                except Exception as e:
                    print(f"[ERROR] Error processing {task_file.name}: {e}")
                    write_log(f"[ERROR] Error processing {task_file.name}: {e}")

                    # Save error to OUTBOX
                    error_response = {
                        'status': 'error',
                        'task': task_file.name,
                        'error': str(e)
                    }
                    error_path = OUTBOX / f"error_{task_file.stem}.json"
                    with open(error_path, 'w', encoding='utf-8', newline='\r\n') as f:
                        json.dump(error_response, f, ensure_ascii=False, indent=2)

        # DS 048: финализация задач — анализ ответов Koda в OUTBOX
        # (после process_task файл уже мог быть перенесён курьером — тогда пропускаем)
        for task_file in list(INBOX.glob('DS_*')):
            if not task_file.is_file():
                continue
            try:
                koda_response = _find_koda_response(task_file)
                if koda_response:
                    _finalize_task(task_file, koda_response)
                # Нет ответа — файл остаётся в INBOX, ждём Koda
            except Exception as e:
                print(f"[DS 048] Ошибка финализации {task_file.name}: {e}")
                _log_bot(f"{task_file.name}: ОШИБКА финализации — {e}")

        # Wait 15 seconds
        time.sleep(15)


if __name__ == '__main__':
    main()