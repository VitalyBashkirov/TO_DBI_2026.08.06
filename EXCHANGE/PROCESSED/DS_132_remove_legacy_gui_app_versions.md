# DS_132. Удаление legacy-версий gui_app и чистка __pycache__

## Контекст

АРМ «Адаптация под DBI». Ветка feature/dockerization.
Разведка (PS, чат 26) подтвердила: в SRC лежат три ранние версии GUI,
которые не импортируются никем и не менялись с первого коммита 02ca385.

- SRC/gui_app_OLD.py        (42 375 B, коммит 02ca385)
- SRC/gui_app_NEW.py        (42 306 B, коммит 02ca385)
- SRC/gui_app_v25_backup.py (43 916 B, коммит 02ca385)

Живой файл — SRC/gui_app.py (347 481 B, активно правится: DS_115, DS_120,
DS_127, DS_129, DS_131). Три legacy-файла меньше его в 8 раз и содержат
класс DBIMigrationApp (в gui_app.py — DBIMigrationApp актуальный).

Импортов gui_app_OLD/NEW/v25_backup в SRC/**/*.py — нет.
Живых ссылок в актуальных .md/.json — нет.

## Цель

Удалить legacy-файлы безвозвратно (история сохранится в git 02ca385),
убрать их из .dockerignore, почистить все __pycache__ в рабочем дереве.

## Что делаем

1. git rm трёх файлов:
   - SRC/gui_app_OLD.py
   - SRC/gui_app_NEW.py
   - SRC/gui_app_v25_backup.py

2. .dockerignore: удалить строки 78-81 (комментарий «# Старые версии GUI»
   + 3 строки имён файлов). Строка 82 (пустая) остаётся как разделитель
   перед секцией «# Docker».

3. Очистить все __pycache__ в рабочем дереве F:\TO_DBI (9 каталогов):
   - EXCHANGE/__pycache__
   - SRC/__pycache__
   - SRC/analyzer/__pycache__
   - SRC/fixer/__pycache__
   - SRC/tests/__pycache__
   - SRC/utils/__pycache__
   - temp/__pycache__
   - tools/__pycache__
   - tools/indexer/__pycache__
   Все они ignored (.gitignore L2: __pycache__/, L3: *.pyc), git rm не нужен.
   Каталог .kilo/worktrees/admitted-melody/ НЕ трогать (чужой worktree).

4. Проверки (§5 обязателен):
   - git status -sb (после apply — clean, tracked-файлов legacy нет)
   - python -m pytest SRC/tests/ -q  -> 65 passed, exit=0
   - BOM-check .dockerignore -> False
   - git ls-files SRC/gui_app*.py -> остаётся только SRC/gui_app.py

## Что НЕ делаем

- Не трогаем SRC/gui_app.py (живой).
- Не трогаем SRC/tests/, SRC/analyzer/, SRC/fixer/, SRC/utils/ (только их __pycache__).
- Не трогаем .kilo/worktrees/ (отдельный worktree).
- Не трогаем bot.log иначе как одной записью DS_132.
- Не переименовываем исторические отчёты DS_100a..DS_131.

## Регламент имён

- Задание: EXCHANGE/INBOX/DS_132_remove_legacy_gui_app_versions.md
- Отчёт:   EXCHANGE/OUTBOX/DS_132_remove_legacy_gui_app_versions_report.md
  (UTF-8 без BOM, русский, плоский формат, без вложенных троек бэктиков)

## Порядок завершения (§6.3)

1. Выполнить шаги 1-4.
2. Запись в EXCHANGE/bot.log одной строкой:
   [%Y-%m-%d %H:%M] DS_132: удалены legacy gui_app_OLD/NEW/v25_backup
   (tracked, не импортировались с 02ca385). .dockerignore: -4 строки (78-81).
   Очищены 9 __pycache__ (ignored). pytest 65 passed.
3. Создать отчёт EXCHANGE/OUTBOX/DS_132_remove_legacy_gui_app_versions_report.md.
4. Перенести задание в EXCHANGE/PROCESSED/ (через close_ds.ps1 -InboxFile).
5. git add .dockerignore + git add EXCHANGE/OUTBOX/... + git add EXCHANGE/PROCESSED/...
   git commit -m "DS_132: удаление legacy gui_app_OLD/NEW/v25_backup + чистка __pycache__ + .dockerignore"
6. Push — по запросу (правило 10).

## Примечание

DS выполняется вручную PS-блоками (правило 36), без KODA.
Блоки: dry-run -> apply -> пост-проверка. Каждый блок пишет лог в F:\TO_DBI\PS\.

