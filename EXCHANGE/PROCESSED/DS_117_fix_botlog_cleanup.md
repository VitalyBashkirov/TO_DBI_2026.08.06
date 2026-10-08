# DS_117-fix — закрытие хвостов DS_117: bot.log renormalize + PROCESSED add + cleanup

## Контекст

Чат 18. Ветка feature/dockerization на ad8f368 (ahead 1 относительно origin).
DS_117 (добавление *.tsx в .gitattributes + BodyName в §6.2) ВЫПОЛНЕН и закоммичен.

После DS_117 верификация выявила 3 хвоста, не закрытых при коммите:

1. `M EXCHANGE/bot.log` — EOL-шум (CRLF в рабочей копии vs LF в HEAD).
   Диагностика: git diff --ignore-all-space показывает 475 чистых вставок,
   905 «удалений» — артефакт EOL. Содержимое корректно, нужно
   renormalize для чистого diff.

2. `?? EXCHANGE/PROCESSED/DS_117_gitattributes_tsx_bodyname.md` — задание
   в PROCESSED, но НЕ добавлено в git (регламент DS_STANDARD §3.2 + урок чата 17).

3. `?? format/` и `?? lang/` — артефакты тестов от 07.10.2026 (6+6 файлов
   summary_*.csv/md, test_20261007_*.csv/md). К DS_117 отношения не имеют,
   в git не нужны. Не покрыты .gitignore.

## Задание

### Часть A — bot.log: нормализация EOL

Файл: `F:\TO_DBI\EXCHANGE\bot.log`

Выполнить:
```
git add --renormalize EXCHANGE/bot.log
```

Это приведёт EOL к нормализованному виду (LF) без изменения содержимого.
После этого `git diff --cached --stat` должен показать ~475 вставок
(содержательные записи 07–08.10.2026), а не 1380/905.

Проверка:
- `git diff --cached --ignore-all-space --stat -- EXCHANGE/bot.log` — должен
  совпасть с `git diff --cached --stat -- EXCHANGE/bot.log` (без EOL-шума).

### Часть B — задание DS_117 в git

Файл: `F:\TO_DBI\EXCHANGE\PROCESSED\DS_117_gitattributes_tsx_bodyname.md`

Выполнить:
```
git add EXCHANGE/PROCESSED/DS_117_gitattributes_tsx_bodyname.md
```

Прямые слэши (регламент §18).

### Часть C — удалить format/ и lang/

Каталоги:
- `F:\TO_DBI\format\` (6 файлов)
- `F:\TO_DBI\lang\` (6 файлов)

Выполнить рекурсивное удаление:
```
Remove-Item -LiteralPath 'F:\TO_DBI\format' -Recurse -Force
Remove-Item -LiteralPath 'F:\TO_DBI\lang'   -Recurse -Force
```

Перед удалением — убедиться, что это действительно артефакты тестов
(summary_*.csv, test_20261007_*.csv/md), а не нужные данные.

### Часть D — .gitignore: защита от повтора

Файл: `F:\TO_DBI\.gitignore`

Добавить секцию (в конец файла, после существующих секций):

```
# Test artifacts — scanner reports (DS_117-fix)
format/
lang/
```

Требования:
- Не удалять существующие правила.
- Не менять существующие секции.
- BOM не добавлять (текущий .gitignore — проверить, ожидается False).
- Запись: `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` или
  `Add-Content -Encoding UTF8` с последующей проверкой BOM.

### Часть E — коммит и push

Один коммит (или два, если A и C+D логически разделимы — на усмотрение KODA):
```
DS_117-fix: bot.log renormalize + PROCESSED add + ignore format/lang
```

После коммита:
```
git push origin feature/dockerization
```

bot.log — запись о DS_117-fix:
```
[YYYY-MM-DD HH:MM:SS] DS_117-fix: Выполнено. bot.log renormalize (EOL),
DS_117 в PROCESSED (git add), format/ и lang/ удалены + .gitignore.
PUSH в origin/feature/dockerization (ad8f368..<new>).
```

## Ограничения

- SRC не трогать.
- gui_app.py не трогать.
- Не менять .gitattributes (DS_117 закрыт).
- Не менять DS_STANDARD.md (DS_117 закрыт).
- Никаких return / @"..."@ в ручных блоках PowerShell.
- Прямые слэши в git add.
- Логи — только EXCHANGE\bot.log.

## §5 (Проверка) — обязательно

В отчёт KODA включить:

1. **BOM-check** .gitignore, .gitattributes → ожидается False.
2. **git status -sb** → после коммита clean, ahead 0 (после push).
3. **git log --oneline -3** → новый коммит DS_117-fix сверху.
4. **git diff HEAD~1 --stat** → 3 файла: EXCHANGE/bot.log,
   EXCHANGE/PROCESSED/DS_117_*.md, .gitignore.
5. **Проверка format/ и lang/** → Test-Path возвращает False (удалены).
6. **Select-String по .gitignore** — паттерны `format/`, `lang/` → обе строки есть.
7. **pytest** → exit code 0 (65 passed).
8. **git branch -vv** → feature/dockerization синхронизирован с origin.
9. **git diff --cached --ignore-all-space --stat** для bot.log — подтверждение,
   что renormalize убрал EOL-шум (опционально, если коммит уже сделан —
   `git show --stat HEAD -- EXCHANGE/bot.log`).

## Итог DS_117-fix

После выполнения:
- bot.log — в git, diff чистый (без EOL-шума).
- DS_117 задание — в PROCESSED, в git.
- format/, lang/ — удалены, в .gitignore.
- Ветка запушена, ahead 0.
- Дерево чистое, готово к DS_118 (CLI-сканер).