# DS_135 — Временные метки, статистика dedup, рекурсивный поиск

## 1. Задача

Чат 28. Продолжение работы над GUI (АРМ «Адаптация под DBI»).
Ветка feature/dockerization.

Цель — исключить из обработки файлы с временными метками
_YYYYMMDD_HHMMSS_ в имени (создаются при отладке, засоряют
сканирование / фикс / AI).

Задачи:

1. Исключить файлы с временными метками из сканирования, фикса, AI.
2. Отметка в ЖВ и диалоге: «Пропущено файлов с временными метками: N».
3. В прогнозе заменить <не реализовано> на <3.В Ai>.
4. Блок «Общая статистика по всем найденным уникальным (dedup_issues)
   кодам рубрикаторов».
5. _result_dir_has_pattern_files / _source_dir_has_pattern_files —
   rglob вместо glob(**/*.plp) (DS_135-2d).

Примечание: оригинальное задание DS_135 не сохранилось. Восстановлено
по факту в чате 29 — см. EXCHANGE\PROCESSED\DS_135_temporary_marks.md,
раздел «СТАТУС ЗАДАНИЯ».

## 2. Что сделано

### 2.1. scanner.py — временные метки (выполнено)

- _TEMP_MARKER_RE = re.compile(r"_\d{8}_\d{6}_").
- Функция is_temporary_filename(name) -> bool.
- Фильтр в _should_exclude.
- Счётчик self.skipped_temporary в scan_directory.
- skipped_temporary в return scan_directory.

### 2.2. gui_app.py — фильтр и рекурсивный поиск (выполнено)

- L1287, L1304: return any(True for f in gen
  if not is_temporary_filename(f.name)).
- L1286, L1303: rglob вместо glob (DS_135-2d) — рекурсивный поиск
  файлов по шаблону в result/source, включая подкаталоги.
- Вывод «Пропущено файлов с временными метками» в ЖВ
  (после scan_directory).
- Параметр skipped_temporary в _show_scan_result_dialog.

### 2.3. code_fixer.py — прогноз и dedup-статистика (выполнено)

- L2712, L2716: <не реализовано> → <3.В Ai>.
- L2760+: блок «Общая статистика по всем найденным уникальным
  (dedup_issues) кодам рубрикаторов» (сортировка по убыванию,
  при равенстве — алфавит).

### 2.4. DS_135-2f — фикс активации К3 (выполнено)

Подзадача внутри DS_135. Причина: _update_main_buttons вызывалась
до _finish_abortable_operation при scan_running=True → выход
без пересчёта, К3 остаётся disabled после К2.

Правка:
- Удалено из _run_fix (L4239-4240): self.root.after(0,
  self._update_main_buttons).
- Добавлено в _finish_abortable_operation (после scan_running = False):
  self._update_main_buttons().

### 2.5. DS_135-2g — guard в _update_main_buttons (выполнено)

Причина: 3 теста (test_ds089a, test_ds108) вызывают
_finish_abortable_operation через new без init →
AttributeError: source_dir_var.

Правка: _update_main_buttons (L1332-1335):
    if not hasattr(self, 'source_dir_var')
       or not hasattr(self, 'result_dir_var'):
        return

Правило N14 / Урок CC.

## 3. Файлы и правки

SRC\analyzer\scanner.py:
- _TEMP_MARKER_RE, is_temporary_filename, _should_exclude,
  scan_directory (self.skipped_temporary).

SRC\gui_app.py:
- L1286-1287, L1303-1304 — rglob + is_temporary_filename.
- Вывод «Пропущено файлов с временными метками» в ЖВ.
- _show_scan_result_dialog — параметр skipped_temporary.
- _finish_abortable_operation — self._update_main_buttons()
  (DS_135-2f).
- _update_main_buttons L1332-1335 — guard hasattr (DS_135-2g).

SRC\fixer\code_fixer.py:
- L2712, L2716 — <не реализовано> → <3.В Ai>.
- L2760+ — блок dedup-статистики.

## 4. Тесты

Новый: SRC\tests\test_ds135_temporary.py (12 тестов на
is_temporary_filename, 73 строки, BOM=False).

Полный регресс: pytest SRC\tests\ -q → 77 passed, exit=0.

## 5. Проверка (§5)

1. python -m pytest SRC\tests\ -q → 77 passed, exit=0.
2. python SRC\tests\test_ds133_buttons_state.py →
   18/18 PASSED, exit=0 (после DS_136a).
3. ast.parse gui_app.py → без ошибок.
4. BOM-check: scanner.py, gui_app.py, code_fixer.py,
   test_ds135_temporary.py — UTF-8 без BOM.

## 6. Артефакты

- Коммит: 6f5efb0 — "DS_134+135+136: GUI-фиксы (K4/K3), временные
  метки, критерий K2, статистика".
- Push: 3db4cc4..6f5efb0 в origin/feature/dockerization, выполнен.
- Задание: EXCHANGE\PROCESSED\DS_135_temporary_marks.md
  (восстановлено в чате 29).
- Отчёт: этот файл.

## 7. Отступления от задания

Q1. deep_scanner.py — фильтр временных НЕ реализован в DS_135.
    Открытая задача №4 из стартового файла 29. Требует отдельного
    DS либо включения в DS_137.

Q2. DS_135-2f и DS_135-2g — подзадачи внутри DS_135, не описанные
    в восстановленном задании (восстановлены по факту из стартового
    файла 29). Отражены в отчёте DS_134 (К3, guard hasattr).

Q3. _result_dir_has_pattern_files / _source_dir_has_pattern_files
    в задании DS_136 описаны как glob + scan_recursive_var, но
    фактически (после DS_135-2d) используют p.rglob всегда.
    Это DS_135-2d переопределил поведение — согласовано с
    обеими функциями-сёстрами.

## 8. Открытые вопросы

1. deep_scanner.py — фильтр временных. Решить в DS_137 или
   отдельном DS.

2. test_ds135_temporary.py — pytest-стиль или if __name__ == '__main__'?
   Уточнить перед pytest-миграцией (правило N12).

3. settings.json не в git (Урок CC) — правки локальны.