# DS_135. Временные метки, статистика dedup, рекурсивный поиск

## СТАТУС ЗАДАНИЯ

ВОССТАНОВЛЕНО ПО ФАКТУ в чате 29.
Оригинальное задание DS_135 не сохранилось (нет ни в INBOX, ни в PROCESSED
на момент старта чата 29). Формулировка восстановлена по:
- стартовому файлу 29.Старт.txt,
- коммиту 6f5efb0 (DS_134+135+136),
- тесту SRC\tests\test_ds135_temporary.py,
- фактическому коду SRC\analyzer\scanner.py, SRC\gui_app.py,
  SRC\fixer\code_fixer.py.

DS_135 выполнен в чате 28, вошёл в коммит 6f5efb0.

## Контекст

Чат 28. Продолжение работы над GUI (АРМ «Адаптация под DBI»).
Ветка feature/dockerization.

Цель — исключить из обработки файлы с временными метками
_YYYYMMDD_HHMMSS_ в имени (создаются при отладке, засоряют
сканирование/фикс/AI).

## Задачи

1. Исключить файлы с временными метками из сканирования, фикса и AI.
2. Отметка в ЖВ и диалоге: «Пропущено файлов с временными метками: N».
3. В прогнозе заменить <не реализовано> на <3.В Ai>.
4. Блок «Общая статистика по всем найденным уникальным (dedup_issues)
   кодам рубрикаторов».
5. _result_dir_has_pattern_files / _source_dir_has_pattern_files —
   rglob вместо glob(**/*.plp) (DS_135-2d).

## Правки

### SRC\analyzer\scanner.py

- _TEMP_MARKER_RE = re.compile(r"_\d{8}_\d{6}_").
- Функция is_temporary_filename.
- Фильтр в _should_exclude.
- Счётчик self.skipped_temporary в scan_directory.
- skipped_temporary в return.

### SRC\gui_app.py

- L1287, L1304: return any(True for f in gen
  if not is_temporary_filename(f.name)).
- L1286, L1303: rglob вместо glob (DS_135-2d).
- Вывод «Пропущено файлов с временными метками» в ЖВ
  (после scan_directory).
- Параметр skipped_temporary в _show_scan_result_dialog.

### SRC\fixer\code_fixer.py

- L2712, L2716: <не реализовано> → <3.В Ai>.
- L2760+: блок «Общая статистика по всем найденным уникальным
  (dedup_issues) кодам рубрикаторов» (сортировка по убыванию,
  при равенстве — алфавит).

## Тесты

SRC\tests\test_ds135_temporary.py — новый, 12 тестов на
is_temporary_filename.

Полный регресс: pytest SRC\tests\ -q → 77 passed, exit=0.

## §5 Проверка

1. python -m pytest SRC\tests\ -q → 77 passed, exit=0.
2. python SRC\tests\test_ds133_buttons_state.py → 18/18 PASSED, exit=0
   (после DS_136a).
3. ast.parse — без ошибок.
4. BOM-check: scanner.py, gui_app.py, code_fixer.py,
   test_ds135_temporary.py — UTF-8 без BOM.

## Ограничения

- Не трогать legacy _update_buttons_state.
- deep_scanner.py — фильтр временных НЕ реализован в DS_135
  (открытая задача №4 из стартового файла 29).

## Артефакты

- Отчёт: EXCHANGE\OUTBOX\DS_135_temporary_marks_report.md.
- Задание: этот файл (восстановлено).
- Коммит: 6f5efb0 (DS_134+135+136).
- bot.log: обновить (правило 29: до коммита).