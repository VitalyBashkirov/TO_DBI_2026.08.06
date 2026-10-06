# DS_104 — Гигиена репозитория: версионирование PROCESSED/OUTBOX/bot.log + очистка мусора

## Цель
1. Включить в git:
   - EXCHANGE/PROCESSED/ — исполненные DS (воспроизводимость).
   - EXCHANGE/OUTBOX/ — отчёты KODA.
   - EXCHANGE/bot.log — лог операций (с исключением из *.log).
2. Удалить из индекса git мусор (42 .bak/.broken/.before + 4 .lnk + 2 отладочных).
3. Защитить репо от повторного замусоривания через .gitignore.

## Контекст (разведка 07.10.2026)
- Ветка: feature/dockerization на 39292b9, синхронизирована.
- pack: 1.25 MiB (репо физически невелико).
- PROCESSED: 149 файлов, 1 313 KB — в git: 0.
- OUTBOX: 47 файлов, 144 KB — в git: 0.
- bot.log: ~110–200 KB — в git: нет.
- .lnk в git: 4 файла (EXCHANGE/OUTBOX, Ollama, PATCH_IN, cleanup).
- Мусор в индексе: 42 файла (.bak_*, .broken_*, .before_*).
- Особый случай: test_all_models.ps1.broken_20261006_202441 (85.85 MB
  несжатый) в истории 39292b9, но pack 1.25 MiB — сильно сжимается.
  После git rm --cached удаляется из HEAD, но остаётся в истории.
  Перезапись истории НЕ требуется.

- .gitignore (важные строки):
    17: EXCHANGE/bot.log
    18: EXCHANGE/INBOX/
    19: EXCHANGE/OUTBOX/
    20: EXCHANGE/PROCESSED/
    21: EXCHANGE/result_dir_history.json
    ...
    38: *.bak (НЕ покрывает *.bak_<timestamp>)
    ...
    73: *.log (КОНФЛИКТУЕТ с EXCHANGE/bot.log — нужно исключение)

## Что делает KODA

### Фаза 1 — Правка .gitignore

Файл: F:\TO_DBI\.gitignore

ЗАМЕНИТЬ строки 17–20:

    # Было:
    EXCHANGE/bot.log
    EXCHANGE/INBOX/
    EXCHANGE/OUTBOX/
    EXCHANGE/PROCESSED/

    # Стало:
    # Exchange and log (нужные для воспроизводимости — версионируются)
    # EXCHANGE/bot.log         — версионируется (DS_104)
    EXCHANGE/INBOX/            — рабочая очередь (игнор)
    # EXCHANGE/OUTBOX/         — версионируется (DS_104)
    # EXCHANGE/PROCESSED/      — версионируется (DS_104)

Строку 21 (result_dir_history.json) — оставить.

ДОБАВИТЬ в конец .gitignore (после последней строки):

    # Cleanup DS_104: отладочные бэкапы, мусор, исключение для bot.log
    *.bak_*
    *.broken_*
    *.before_*
    *.lnk
    test_cyr.bat
    cleanup_report.csv
    !EXCHANGE/bot.log

ВАЖНО:
- Строка 73 *.log игнорирует все .log — исключение !EXCHANGE/bot.log
  переопределяет его (git: последнее правило выигрывает).
- Порядок важен: !EXCHANGE/bot.log идёт ПОСЛЕ *.log.
- UTF-8 без BOM (DS_STANDARD.md §6.1).

### Фаза 2 — Удалить мусор из индекса (git rm --cached)

ВАЖНО: --cached — файл удаляется только из индекса, на диске остаётся.

СПИСОК (42 файла .bak/.broken/.before):

Ollama и LM Studio.bat.bak_20261005_141456
Ollama и LM Studio.bat.bak_bom_20261005_150032
Ollama и LM Studio.bat.bak_catfix2_20261005_171501
Ollama и LM Studio.bat.bak_crlf_20261005_153808
Ollama и LM Studio.bat.bak_gotom_20261005_170459
Ollama и LM Studio.bat.bak_movetop_20261005_170101
Ollama и LM Studio.bat.bak_noPhi35_20261005_144114
Ollama и LM Studio.bat.bak_nobom_20261005_150631
Ollama и LM Studio.bat.bak_noconcat_20261005_170752
Ollama и LM Studio.bat.bak_prep_add_20261005_163210
Ollama и LM Studio.bat.bak_prep_fix_20261005_165536
Ollama и LM Studio.bat.bak_psargs_20261005_165916
Ollama и LM Studio.bat.bak_stage1_20261005_162924
Ollama и LM Studio.bat.bak_stage2_20261005_162946
cleanup_report.csv
test_all_models.ps1.bak_20261005_142504
test_all_models.ps1.bak_20261005_142542
test_all_models.ps1.bak_ascii_20261005_143351
test_all_models.ps1.bak_backend2_20261005_161701
test_all_models.ps1.bak_backend_20261005_161602
test_all_models.ps1.bak_bom_20261005_143226
test_all_models.ps1.bak_broken_20261005_171736
test_all_models.ps1.bak_catfix2_20261005_171438
test_all_models.ps1.bak_catparse_20261005_171809
test_all_models.ps1.bak_catparse_20261006_203137
test_all_models.ps1.bak_comma_20261005_161733
test_all_models.ps1.bak_cyr3_20261006_203218
test_all_models.ps1.bak_cyrfix_20261006_201302
test_all_models.ps1.bak_final_20261005_143119
test_all_models.ps1.bak_okex_20261006_204004
test_all_models.ps1.before_bomfix_20261005_142946
test_all_models.ps1.broken_20261006_202441
test_cyr.bat
tools/check_standard.py.bak_dedup2_20261006_215621
tools/check_standard.py.bak_dedup3_20261006_220438
tools/check_standard.py.bak_dedup_20261006_215527
tools/check_standard.py.bak_utf8_20261006_215340
tools/check_standard.py.bak_utf8_20261006_215424
tools/explain_log.py.bak_dedup3_20261006_220438
tools/explain_log.py.bak_utf8_20261006_210846
tools/run_cnt_007_nightly.cmd.bak_chcp_20261006_213331
tools/run_cnt_007_nightly.cmd.bak_chcp_20261006_213408

ДОПОЛНИТЕЛЬНО — удалить 4 ярлыка .lnk:

"EXCHANGE/OUTBOX — ярлык.lnk"
"Ollama и LM Studio.lnk"
"PATCH_IN — ярлык.lnk"
"Запускать из под админа cleanup.lnk"

(Точные имена получить: git ls-files | Select-String "\.lnk")

Также удалить (если в git):
- test_cyr.bat
- cleanup_report.csv

### Фаза 3 — Добавить в git нужное

    git add "EXCHANGE/PROCESSED/"
    git add "EXCHANGE/OUTBOX/"
    git add -f "EXCHANGE/bot.log"

ВАЖНО: -f для bot.log, если git всё ещё считает его игнорируемым
(на случай, если !EXCHANGE/bot.log не сработал сразу — git иногда
кэширует ignore).

Проверка:
    (git status --short "EXCHANGE/PROCESSED/" | Measure-Object).Count
    (git status --short "EXCHANGE/OUTBOX/" | Measure-Object).Count
    git status --short "EXCHANGE/bot.log"

Ожидание:
- PROCESSED: ~149 файлов.
- OUTBOX: ~47 файлов.
- bot.log: 1 (A или M).

### Фаза 4 — Коммит и push

    git add .gitignore
    git status --short | Select-Object -First 30
    git commit -m "DS_104: гигиена репо — версионирование PROCESSED/OUTBOX/bot.log, удаление 46 файлов мусора"
    git push origin feature/dockerization

### Фаза 5 — Проверка

1. Размер pack после:
    git count-objects -vH
   Ожидание: size-pack ≈ 1.25 MiB (не растёт существенно).

2. Что в git:
    (git ls-files "EXCHANGE/PROCESSED/" | Measure-Object).Count
    (git ls-files "EXCHANGE/OUTBOX/" | Measure-Object).Count
    git ls-files "EXCHANGE/bot.log"

3. Мусор отсутствует:
    git ls-files | Where-Object { $_ -match "\.bak_" -or $_ -match "\.broken_" -or $_ -match "\.lnk" }
   Ожидание: пусто.

4. Рабочее дерево:
    git status
   Ожидание: clean.

5. Ветка:
    git branch -vv
   Ожидание: синхронизирована с origin.

## Формат отчёта EXCHANGE\OUTBOX\DS_104_report.md
- UTF-8 без BOM.
- РУССКИЙ. Транслит не использовать.
- Разделы:
  1. Правка .gitignore (было/стало).
  2. git rm --cached — список (42 .bak + 4 .lnk + 2 отладочных).
  3. git add — PROCESSED (N), OUTBOX (N), bot.log.
  4. Коммит: hash, файлов.
  5. Push: успех/ошибка.
  6. Проверка: pack size до/после, мусор отсутствует.
  7. Вывод.

## Ограничения
- Не переписывать историю git (никаких rebase/filter-branch).
- SRC не трогать.
- git rm --cached (не git rm).
- bot.log не удалять с диска, только добавить в git.
- GP не выполнять автоматически (только по запросу).
- Прогноз KODA не нужен.
- Логи — EXCHANGE/bot.log.

## Артефакты
- F:\TO_DBI\.gitignore (правка).
- Новый коммит DS_104.
- EXCHANGE\OUTBOX\DS_104_report.md.