# DS_102 — GUI → CLI resume-интеграция

## Цель
В GUI-режиме (кнопка «2. Исправить код» → «3. В Ai») обеспечить
передачу флага --resume в ai_local_worker.py, чтобы повторный
прогон не дублировал уже обработанные issues.

## Контекст
- ai_local_worker.py (строка ~885) поддерживает:
  - --resume (флаг): читает AI_REQUEST_*.processed.json из --out.
  - --skip-ids FILE: явный список id для пропуска.
- save_processed_ids / load_processed_ids (строка ~150) —
  создание/чтение <request>.processed.json.
- Текущий Popen в SRC\gui_app.py (разведка 07.10.2026):
  - Строка 5733–5737 — rule_based_fixer.py:
        proc = subprocess.Popen(
            [sys.executable, str(tools / 'rule_based_fixer.py'),
             '--in-dir', str(ai_in), '--out-dir', str(ai_out)],
            cwd=str(root), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    --resume НЕ передаётся. У rule_based_fixer флага нет —
    и не нужен (детерминированный фиксер, идемпотентен).
  - Строка 5746–5750 — ai_local_worker.py:
        proc = subprocess.Popen(
            [sys.executable, str(tools / 'ai_local_worker.py'),
             '--in-dir', str(ai_in), '--out-dir', str(ai_out)],
            cwd=str(root), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    --resume НЕ передаётся. ЭТО ЦЕЛЬ DS_102.
- DS_092 (E2e GUI resume test) — 5 тестов, покрывают
  прерывание/продолжение скана и фикса.
- DS_094 (CLI resume) — 8 тестов, покрывают --resume / --skip-ids
  в ai_local_worker.py.
- DS_102 — связка: GUI → CLI c --resume.

## Разведка (KODA, до правок)

1. Открыть SRC\gui_app.py, найти _run_fix (строка ~3721).
2. Подтвердить argv обоих Popen (5733, 5746).
3. Подтвердить, что у rule_based_fixer нет --resume.
4. Проверить save_processed_ids / load_processed_ids в
   ai_local_worker.py (строки ~150–170).
5. Проверить существующие тесты:
   - SRC\tests\test_ds092_e2e.py — resume через GUI.
   - SRC\tests\test_ds094_resume.py — resume CLI.
6. Зафиксировать в отчёте:
   - текущий argv;
   - имя файла .processed.json (формат);
   - куда именно добавлять --resume.

## Задание

### Фаза 1 — Правка Popen в gui_app.py

Файл: SRC\gui_app.py

В _run_fix, в Popen для ai_local_worker.py (строка ~5746):

Было:
    proc = subprocess.Popen(
        [sys.executable, str(tools / 'ai_local_worker.py'),
         '--in-dir', str(ai_in), '--out-dir', str(ai_out)],
        cwd=str(root), stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

Стало:
    proc = subprocess.Popen(
        [sys.executable, str(tools / 'ai_local_worker.py'),
         '--in-dir', str(ai_in), '--out-dir', str(ai_out),
         '--resume'],
        cwd=str(root), stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

Сохранить отступы, порядок аргументов, cwd, stdout, stderr —
без изменений. Добавляется только '--resume' в конец списка argv.

Popen для rule_based_fixer (5733) — НЕ трогать.

### Фаза 2 — Уточнение поведения

Проверить логику _run_fix:
1. Если <request>.processed.json существует в ai_out — повторный
   прогон через GUI пропустит обработанные issues.
2. Если .processed.json НЕТ — прогон как обычно (все issues).
3. Логика в ai_local_worker при --resume (строки ~974–979):
       skip_ids = set()
       if args.resume:
           skip_ids |= load_processed_ids(out)
       if skip_ids:
           log('resume: N id уже обработано (пропускаю)')
4. Убедиться, что GUI не мешает:
   - .processed.json лежит в ai_out (EXCHANGE\AI_OUT).
   - При повторном нажатии «3. В Ai» файл читается.
5. Проверить, что после успешного прогона .processed.json
   сохраняется (save_processed_ids в конце run_request).

### Фаза 3 — Тест

Добавить SRC\tests\test_ds102_gui_resume.py (новый).

Тест должен проверить:
1. GUI _run_fix передаёт '--resume' в argv ai_local_worker.
2. Повторный прогон через GUI не дублирует issues
   (использовать mock .processed.json).

Подход (по образцу test_ds092_e2e.py):
- Mock subprocess.Popen.
- Перехватить argv для ai_local_worker.
- Проверить: '--resume' в argv.
- Проверить: при существующем .processed.json skip_ids
  передаётся (mock load_processed_ids).

Если такой тест уже покрыт в test_ds092_e2e.py —
зафиксировать факт в отчёте, новый не создавать.

### Фаза 4 — Регресс

    python -m pytest SRC\tests\ -v

Ожидание: 57 PASSED + новый тест(ы).
Если добавлен 1 тест — 58 PASSED.

### Фаза 5 — Отчёт

Формат: EXCHANGE\OUTBOX\DS_102_report.md
- UTF-8 без BOM.
- РУССКИЙ. Транслит не использовать.

Содержание:
1. Разведка: текущий argv Popen ai_local_worker (цитата).
2. Правка: было/стало (цитата).
3. Уточнение поведения: что происходит при .processed.json.
4. Тест: сколько тестов, что проверяют.
5. Регресс: N PASSED.
6. Артефакты: SRC\gui_app.py, SRC\tests\test_ds102_*.py.
7. Вывод: GUI resume-интеграция работает.
8. Расхождения (если есть).

## Что НЕ делает KODA
- Не трогает ai_local_worker.py (уже поддерживает --resume).
- Не трогает rule_based_fixer.py (флага --resume нет).
- Не трогает SRC\ai_exchange.py.
- Не выполняет git/push/GP.

## Ограничения
- SRC — правка допустима только в gui_app.py и tests/.
- BOM — избегать (DS_STANDARD.md §6.1).
- Прогноз KODA не нужен.
- Логи — EXCHANGE/bot.log.

## Артефакты
- SRC\gui_app.py (правка Popen).
- SRC\tests\test_ds102_gui_resume.py (новый, если нужен).
- EXCHANGE\OUTBOX\DS_102_report.md.

## Ожидание (сводно)
- GUI _run_fix передаёт --resume в ai_local_worker.
- Повторный прогон не дублирует issues.
- pytest: 57+ PASSED.
- Открытая проблема №3 закрыта:
  «GUI не передаёт --resume / --skip-ids в CLI».