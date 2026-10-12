# DS_144b — Отчёт: K2: копирование ИК → КР по шаблону + галка + тултипы

## Задача

См. задание EXCHANGE/PROCESSED/DS_144b_k2_copy_pattern.md.

Кратко:
- Перед фиксом в K2 копировать в КР файлы по шаблону из ИК.
- Переименовать галку «Только модифицированные файлы» → «Только файлы по шаблону».
- Добавить тултипы для 4 галок секции 3.

## Что сделано

### Часть A. Новый метод _copy_files_to_result

SRC/gui_app.py:
- Удалён метод _copy_directory_structure.
- Добавлены:
  - _matches_pattern(rel_path, masks) — glob-маски с поддержкой '**/'.
  - _copy_files_to_result(source_dir, result_dir, pattern, preserve_structure,
    only_edited, edited_files) -> dict.

Логика:
- pattern пуст -> aborted='Не указаны шаблоны файлов'.
- .plp: фильтр по edited_files (only_edited=True) или по маскам.
- не-.plp: копировать всегда (для контекста).
- preserve_structure=True: зеркало путей; False: плоско, коллизия -> aborted.
- Idempotent: существующий файл -> skip.

### Часть B. Правка _run_fix

- Убран старый блок копирования (should_copy_structure + _copy_directory_structure).
- После scanner.scan_directory добавлен вызов _copy_files_to_result с
  edited_files = set(scanner.get_issues_by_file().keys()).
- При aborted: лог + _show_copyable_dialog + прерывание.
- Галка переименована: «Только модифицированные файлы» -> «Только файлы по шаблону».

### Часть C. Тултипы

Новый метод _apply_section3_tooltips в SRC/gui_app.py:
- Программный поиск 4 чекбоксов по тексту в self.options_frame.
- Создание 4 Tooltip (сохраняются в self._tooltip_*).
- Вызывается из _apply_button_tooltips после self._update_ai_button_state().

Тексты — дословно из задания.

### Часть E. Тесты

SRC/tests/test_ds144b_copy_pattern_pytest.py — 14 тестов:
- empty/whitespace → aborted;
- **/*.plp, *.plp, **/*.*, *.* — комбинации;
- only_edited полный и частичный;
- preserve_structure и flat;
- коллизия при flat;
- не-.plp всегда;
- idempotent;
- multi-mask ('**/*.plp;**/*.mcs').

## Проверки

- pytest DS_144b: 14 passed.
- pytest регресс: 136 passed (118 + 4 DS_144a + 14 DS_144b).
- ast.parse: OK.
- BOM: no BOM (gui_app.py, test_ds144b).
- Размер gui_app.py: 350909 -> 356907 B (+5998 B за DS_144b).
- git diff --stat: gui_app.py +233/-87.

## Файлы

- SRC/gui_app.py — основной (правки A, B, C).
- SRC/tests/test_ds144b_copy_pattern_pytest.py — новый, 8086 B.
- tools/_archive/gui_app.py.bak_ds144b_a / _b / _c — бэкапы.
- EXCHANGE/PROCESSED/DS_144b_k2_copy_pattern.md — задание (из INBOX).

## Не входит

- K1 = скан + зеркало (DS_144c).
- K2 без повторного скана (DS_144c).
- .mcs, .mp, .pck (DS_144d).
