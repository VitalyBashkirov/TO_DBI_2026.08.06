# DS_130 — Отчёт: удаление write_log в exchange_bot.py

## Итог

Дубль-логгер write_log удалён. Все 6 вызовов переведены на _log_bot.
exchange_bot.py: 268 -> 259 строк, BOM=False. pytest 65 passed.

## Причина

write_log открывал LOG_FILE в режиме 'w' — перезапись. Первый же
вызов снёс бы все 471 строку bot.log. Дополнительно: писал
[HH:MM:SS] без даты и \n вместо \r\n, расходясь с каноном
_log_bot (DS_050 / DS_129).

## Изменения

| Строка (было) | Было | Стало |
|---------------|------|-------|
| 29-36 | def write_log(...) | удалено |
| 37 | (пустая) | удалено вместе с функцией |
| 133 | write_log(f"[{...%H:%M:%S}] Processing task: ...") | _log_bot(f"Processing task: ...") |
| 152 | write_log(f"[+] Response saved: ...") | _log_bot(...) |
| 157 | write_log(f"[+] Task moved to archive: ...") | _log_bot(...) |
| 209 | write_log("[INFO] Exchange Courier started ...") | _log_bot(...) |
| 217 | write_log(f"[INFO] Found {len(tasks)} ...") | _log_bot(...) |
| 237 | write_log(f"[ERROR] Error processing ...") | _log_bot(...) |

_log_bot (L112, L115, L119, L123, L261 исходные) — не тронуты.

## Проверки

- write_log в SRC: 0 вхождений.
- _log_bot в SRC: 12 вхождений (1 опред. + 11 вызовов).
- exchange_bot.py: 259 строк, 10515 B, BOM=False.
- bot.log: 471 строка, 95495 B, не изменился.
- python -m py_compile: exit=0.
- pytest SRC\tests\ -q: 65 passed in 0.43s.

## Бэкап

SRC\exchange_bot.py.bak_ds130 (ignored, *.bak_*).

## Коммит

d0Xxxxx — DS_130: удалён дубль-логгер write_log в exchange_bot.py.