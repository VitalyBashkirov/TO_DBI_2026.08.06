# DS_130 — Удаление дубль-логгера write_log в exchange_bot.py

## Контекст

- Проект: TO_DBI. Ветка: feature/dockerization.
- База: b1c8210 (DS_129).
- Цель: устранить дубль-писатель bot.log — функцию write_log,
  которая перезаписывает файл (режим 'w') и пишет [HH:MM:SS] без даты.
- Канонический логгер: _log_bot — append, [YYYY-MM-DD HH:MM], \r\n.
- Внешних импортов exchange_bot нет (проверено разведкой).
- Приоритет: СРЕДНИЙ.

## Диагноз

exchange_bot.py содержал два логгера, пишущих в один LOG_FILE:

1. write_log (было L29-L36): open(LOG_FILE,'w') — ПЕРЕЗАПИСЬ;
   f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n" — без даты.
2. _log_bot (L41, теперь L32): open(LOG_FILE,'a') — append;
   '[%s] %s\r\n' % (strftime('%Y-%m-%d %H:%M'), message).

## Что сделано

1. Удалена def write_log (было L29-L36, 8 строк) + одна пустая после
   (L37). Итого удалено 9 строк.
2. L133: снят внешний префикс "[{...strftime('%H:%M:%S')}] ",
   write_log -> _log_bot.
3. L152, L157, L209, L217, L237: write_log -> _log_bot (.Replace).
4. Проверено: write_log в SRC не встречается.
5. exchange_bot.py: 268 -> 259 строк, size 10746 -> 10515 B, BOM=False.
6. bot.log: 471 строка, не изменился (код не запускался).
7. py_compile exit=0, pytest 65 passed.