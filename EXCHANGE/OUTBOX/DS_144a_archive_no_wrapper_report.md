# DS_144a — Отчёт: архив без обёртки ИППУ

## Задача

Архив при «Архивировать результат» (K2) должен:
- иметь имя = ИППУ ИК (patch_PSH_DEP_PRIV_GO.zip);
- содержать внутри сразу содержимое ИППУ (без обёртки patch_XXX/).

## Что было

_run_archive (gui_app.py:4328), строка 4342:
    arcname = file_path.relative_to(results_dir.parent)
results_dir.parent = PATCH_OUT. Для файла PATCH_OUT/patch_X/sub/a.plp
arcname = patch_X/sub/a.plp — с обёрткой ИППУ.

## Что стало

Строка 4344:
    arcname = file_path.relative_to(results_dir)
Для того же файла arcname = sub/a.plp — без обёртки.

## Проверки

- pytest DS_144a: 4 passed.
- pytest регресс: 122 passed (118 + 4).
- ast.parse: OK.
- BOM: no BOM (gui_app.py, test).
- Размер gui_app.py: 350909 B (+171 B).

## Файлы

- SRC\gui_app.py — 2 правки (docstring + arcname).
- SRC\tests\test_ds144a_archive_pytest.py — новый, 3108 B.
- tools\_archive\gui_app.py.bak_ds144a — бэкап.
