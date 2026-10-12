# DS_144a — Архив с именем ИППУ, внутри — без обёртки

## Требование

При включённой галке «Архивировать результат» (K2 «Исправить код»):

- Имя архива = имя последнего уровня ИК (ИППУ), например patch_PSH_DEP_PRIV_GO.zip.
- Внутри архива — сразу содержимое ИППУ (sub/a.plp, b.plp), без обёртки patch_PSH_DEP_PRIV_GO/.

## Что сделано

Файл SRC\gui_app.py, метод _run_archive (строка ~4328):

1. Заменено: arcname = file_path.relative_to(results_dir.parent)
   на:      arcname = file_path.relative_to(results_dir)

2. Обновлён docstring метода.

3. Добавлен тест SRC\tests\test_ds144a_archive_pytest.py (4 теста).

## Результат

- pytest: 122 passed (было 118, +4).
- BOM: no BOM (gui_app.py, test).
- Размер gui_app.py: 350909 B (+171 B).
