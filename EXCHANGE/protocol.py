# -*- coding: utf-8 -*-
"""DS 043: надёжный протокол завершения задачи (Часть B).

Использование:
    python F:/TO_DBI/EXCHANGE/protocol.py close <имя_файла_задания>
        - переносит файл из INBOX в PROCESSED и верифицирует протокол;
          при провале возвращает exit code 1 и пишет [ПРОВАЛ ПРОТОКОЛА] в bot.log.

    python F:/TO_DBI/EXCHANGE/protocol.py verify <имя_файла_задания>
        - только верификация (exit code 0/1).
"""
import sys, io, shutil
from pathlib import Path
from datetime import datetime

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass  # stdout уже закрыт/заменён (например, после root.destroy() в тестах)

EXCHANGE = Path(r'F:\TO_DBI\EXCHANGE')
INBOX = EXCHANGE / 'INBOX'
PROCESSED = EXCHANGE / 'PROCESSED'
OUTBOX = EXCHANGE / 'OUTBOX'
BOT_LOG = EXCHANGE / 'bot.log'


def _print(msg):
    """Безопасный вывод (stdout может быть закрыт в тестовом окружении)."""
    try:
        print(msg)
    except Exception:
        pass


def _log(msg):
    """Дописать в bot.log (cp1251, формат [ДД.ММ.ГГГГ ЧЧ:ММ:СС] <Сообщение>)."""
    line = '[%s] %s\r\n' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'), msg)
    try:
        with io.open(BOT_LOG, 'a', encoding='cp1251', errors='replace') as f:
            f.write(line)
    except Exception as e:
        _print('[DS 043] Ошибка записи bot.log: %s' % e)


def _check_bot_log_recent(task_file_name, minutes=5):
    """Есть ли запись с именем задачи за последние N минут."""
    if not BOT_LOG.exists():
        return False
    try:
        text = BOT_LOG.read_text(encoding='cp1251', errors='replace')
    except Exception:
        try:
            text = BOT_LOG.read_text(encoding='utf-8', errors='replace')
        except Exception:
            return False
    key = task_file_name.split('_')[0]  # например 'DS_043'
    now = datetime.now()
    for line in reversed(text.splitlines()):
        if key not in line:
            continue
        try:
            ts = datetime.strptime(line[1:20], '%d.%m.%Y %H:%M:%S')
        except Exception:
            continue
        if (now - ts).total_seconds() <= minutes * 60:
            return True
    return False


def _move_task_to_processed(task_file_name):
    """DS 043: надёжный перенос файла задания из INBOX в PROCESSED."""
    inbox_path = INBOX / task_file_name
    PROCESSED.mkdir(parents=True, exist_ok=True)

    if not inbox_path.exists():
        # Уже перенесён ранее — не ошибка
        if (PROCESSED / task_file_name).exists():
            _print('[DS 043] Файл уже в PROCESSED: %s' % task_file_name)
            return True
        _print('[DS 043] Файл %s не найден в INBOX' % task_file_name)
        return False

    target = PROCESSED / task_file_name
    try:
        shutil.move(str(inbox_path), str(target))
        _print('[DS 043] Файл перенесён: %s' % task_file_name)
        return True
    except Exception as e:
        _print('[DS 043] Ошибка переноса %s: %s' % (task_file_name, e))
        return False


def _verify_task_completion(task_file_name):
    """DS 043: верификация завершения задачи."""
    stem = Path(task_file_name).stem  # 'DS_043_...'
    code = task_file_name.split('_')[0] + '_' + task_file_name.split('_')[1]  # 'DS_043'
    checks = {
        'inbox_empty': not (INBOX / task_file_name).exists(),
        'in_processed': (PROCESSED / task_file_name).exists(),
        # отчёт ищем и по полному имени, и по коду задачи (DS_043*)
        'report_exists': any(OUTBOX.glob(stem + '*')) or any(OUTBOX.glob(code + '*')),
        'bot_log_updated': _check_bot_log_recent(task_file_name),
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        msg = '[ПРОВАЛ ПРОТОКОЛА] %s. Провалено: %s' % (task_file_name, ', '.join(failed))
        _print('[DS 043] ВНИМАНИЕ: протокол не завершён. Провалено: %s' % ', '.join(failed))
        _log(msg)
        return False
    _print('[DS 043] Протокол завершён: все проверки пройдены')
    return True


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ('close', 'verify'):
        print(__doc__)
        return 2
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == 'close':
        ok = _move_task_to_processed(name) and _verify_task_completion(name)
    else:
        ok = _verify_task_completion(name)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
