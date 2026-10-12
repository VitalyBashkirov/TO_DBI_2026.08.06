# DS_144b — K2: копирование ИК → КР по шаблону + галка + тултипы

## Контекст

Чат 33. Арм «Адаптация под DBI». АРМ K1 = Сканировать, K2 = Исправить код.
Сейчас в K2: перед фиксом вызывается _copy_directory_structure (копирует всё
кроме .plp), затем fixer.fix_directory правит .plp из ИК, записывая только
файлы С ПРОБЛЕМАМИ. В КР попадают не все .plp из ИК.

Требуется: перед фиксом в K2 копировать в КР все .plp, попадающие под
шаблон (или только те, в которые нужно внести правки), с сохранением
структуры подкаталогов (по галке).

## Часть A. Новый метод _copy_files_to_result

В SRC/gui_app.py класс DBIMigrationApp:

- Удалить метод _copy_directory_structure (строки ~2387-2424).
- Добавить метод _copy_files_to_result(source_dir, result_dir, pattern,
  preserve_structure, only_edited, edited_files=None) -> dict.

Логика метода:

1. pattern.strip() пуст -> вернуть {'aborted': 'Не указаны шаблоны файлов'}.
2. Разбить pattern по ';', обрезать пробелы, отбросить пустые -> masks.
3. Пройти source_dir.rglob('*'), только is_file().
4. Для каждого файла:
   - .plp:
     - only_edited=True и abs_path не в edited_files -> skip;
     - only_edited=False и не подходит ни под одну маску -> skip;
   - не-.plp (тексты, конфиги) -> копировать ВСЕГДА (для контекста),
     без проверки маски.
5. Соответствие маске (хелпер _matches_pattern):
   - маска содержит '**/' или '**' -> любой уровень;
   - маска без '**' -> только корень (rel.parent == Path('.')).
6. Путь в КР:
   - preserve_structure=True -> result_dir / file.relative_to(source_dir);
   - preserve_structure=False -> result_dir / file.name (плоско).
7. Коллизии при preserve_structure=False: два разных файла дают один
   rel-путь -> aborted = 'Коллизия имён: <name>', прерывание.
8. Копирование: target.parent.mkdir(parents=True, exist_ok=True);
   shutil.copy2(file, target).
9. Существующий файл в КР -> skip (idempotent).
10. Вернуть {'copied': int, 'skipped': int, 'errors': int,
    'aborted': str | None}.

## Часть B. Правка _run_fix (K2)

В SRC/gui_app.py, метод _run_fix, блок ~3967-3978:

- Заменить вызов _copy_directory_structure на _copy_files_to_result.
- Передавать:
    pattern             = self.file_pattern_var.get(),
    preserve_structure  = self.preserve_structure_var.get(),
    only_edited         = self.only_modified_var.get(),
    edited_files        = set(scanner.get_issues_by_file().keys()),
- Вызов делать ПОСЛЕ scanner.scan_directory (строка ~4110), но ДО
  fixer.fix_directory (строка ~4183).
- При result['aborted']:
    - лог self.log(aborted, 'error');
    - self._show_copyable_dialog('Ошибка', aborted, kind='error');
    - return (прервать _run_fix целиком).

## Часть C. Переименование галки

SRC/gui_app.py, строка ~773:
    text="Только модифицированные файлы" ->
    text="Только файлы по шаблону"

Переменную only_modified_var НЕ переименовывать (много ссылок, settings.json).
Ключ only_modified в settings.json сохраняется.

## Часть D. Тултипы (секция 3)

Механизм: класс Tooltip (строка 100). Создавать ПОСЛЕ создания виджетов.
Сохранять в self._tooltip_* (иначе GC уничтожит).

Сохранить чекбоксы в атрибуты:
  - self.chk_only_pattern (строка ~773)
  - self.chk_preserve_structure (строка ~775)
  - self.chk_fix_only_found (строка ~795)
  - self.archive_result_check — уже сохранён (строка ~889)

Тексты (дословно):

1) «Только файлы по шаблону»:
   Что копировать в каталог результатов.
   Вкл. — только файлы, в которые нужно внести правки по шаблону
   (это могут быть .plp;.pck;.mcs;.mp и др.).
   Выкл. — все файлы, соответствующие шаблону (поле «Шаблон» в секции 1).
   (это могут быть .plp;.pck;.mcs;.mp и др.) копируются всегда
   для контекста.

2) «Сохранить структуру каталогов»:
   В каталоге результатов сохранять структуру подкаталогов исходного
   каталога. Если выключено — все файлы плоско, а при коллизии имён
   операция прерывается.

3) «"Исправить код" — только пометить найденные теги --NEW YYYY-MM-DD»:
   Не применять детерминированные исправления, только добавлять маркеры
   --NEW YYYY-MM-DD к найденным проблемам.

4) «Архивировать результат»:
   После исправления упаковать каталог результатов в ZIP с именем
   последнего уровня исходного каталога. Внутри архива — сразу
   содержимое, без обёртки ИППУ.

## Часть E. Тесты

Новый файл SRC/tests/test_ds144b_copy_pattern_pytest.py:

- test_copy_pattern_empty_aborts: pattern='' -> aborted.
- test_copy_pattern_only_plp_recursive: **/*.plp, edited=empty,
  only_edited=False -> все .plp из корня и подкаталогов.
- test_copy_pattern_only_plp_root: *.plp -> только корень.
- test_copy_pattern_all_files_recursive: **/*.* -> все файлы.
- test_copy_pattern_all_files_root: *.* -> только корень.
- test_copy_pattern_only_edited: only_edited=True -> только .plp с issues.
- test_copy_pattern_preserve_structure: preserve=True -> зеркало путей.
- test_copy_pattern_flat: preserve=False -> плоско.
- test_copy_pattern_collision_aborts: preserve=False + два файла
  с одним именем в разных подкаталогах -> aborted.
- test_copy_pattern_non_plp_always: .plp только по шаблону, .txt всегда.
- test_copy_pattern_idempotent: повторный вызов -> skip существующих.

Тесты не требуют Tkinter — вызывают метод на фиктивном объекте
(SimpleNamespace) с минимальным self (root, log, ...).

## Критерии приёмки

- pytest: все существующие + новые тесты — passed.
- ast.parse: OK.
- BOM: no BOM для gui_app.py и тестового файла.
- Ручной smoke на тестовом каталоге: K2 -> в КР все .plp по шаблону,
  не- .plp тоже скопированы, структура сохранена.

## Не входит

- K1 = скан + зеркало (DS_144c).
- K2 без повторного скана (DS_144c).
- .mcs, .mp, .pck (DS_144d).
