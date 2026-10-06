# DS_101c — Фикс мок-сервера Ollama: обрезка лишних line из EXAMPLE

## Цель
Устранить баг в tools\mock_ollama_invalid.py: мок возвращает на 1
элемент больше, чем issues в батче, из-за line-номера в блоке
EXAMPLE промпта.

## Контекст
- DS_101b подтвердил fallback DS_085 (split 10→2×5).
- НО: все 8 подбатчей fallback получили invalid, fixed=0.
- Причина (подтверждена диагностикой Vitaly, 07.10):
  - build_prompt содержит строку
    "EXAMPLE: Issue: line 32, code: IS_EOD_NEW ...".
  - Мок regex '\bline\s+(\d+)\s*,' захватывает line 32 из EXAMPLE.
  - Мок возвращает 11 элементов для batch=10, 6 для sub 5.
  - validate_batch_response: len(parsed) > len(batch) → False → invalid.
- Диагностика Vitaly:
  R2 = [{"line":32,...},{"line":1,...},{"line":2,...},{"line":3,...}]
  — 4 элемента вместо 3.

## Что делает KODA
1. Прочитать tools\mock_ollama_invalid.py.
2. Изменить логику формирования ответа (см. ниже).
3. py_compile OK.
4. Локально проверить: R2 возвращает ровно N элементов.
5. Сдать краткий отчёт EXCHANGE\OUTBOX\DS_101c_report.md.

## Что KODA НЕ делает
- Не запускает ai_local_worker через мок.
- Не трогает SRC.
- Не трогает реальную Ollama (11434).
- Не выполняет git/push/GP.

## Задание

### Фаза 1 — Изменить логику мока

Файл: tools\mock_ollama_invalid.py

**Текущая проблема:**
Мок определяет число issues по regex '\bline\s+(\d+)\s*,'
на всём user content. В content есть EXAMPLE с "line 32," —
захватывается лишнее.

**Решение (Вариант B — надёжный):**
Извлекать число issues из инструкции промпта:
    "Return ONLY a JSON array with exactly N elements"
Regex: r'exactly\s+(\d+)\s+elements'

Алгоритм:
1. Сначала искать "exactly N elements" в user content.
2. Если найдено — N = int, вернуть ровно N элементов.
3. Если не найдено — fallback: парсить lines после "ISSUES:"
   (отсекать EXAMPLE), взять len(lines).
4. Если и это не сработало — default_count (10).

**При формировании массива фиксов:**
- Если N найдено, а lines < N — дополнить элементами
  {"line": <последний+1>, "after": "mock fixed line", ...}.
- Если lines > N — обрезать до N.
- Если lines пуст — использовать range(1, N+1).

**Сохранить поля:**
{"line": N, "after": "mock fixed line",
 "reason": "mock fallback test", "confidence": 0.95}

**Методы:**
- _extract_count(content) — новый. Ищет "exactly N elements".
- _extract_lines(content) — оставить, но применять ТОЛЬКО к
  секции после "ISSUES:" (если метод используется).
- _make_fix_array(n, lines) — принять явно N.
- В do_POST — вызвать _extract_count, потом _make_fix_array.

### Фаза 2 — Локальная проверка (KODA)

1. py_compile:
   python -m py_compile tools\mock_ollama_invalid.py
   Ожидание: RC 0.

2. Запуск мок-сервера:
   python tools\mock_ollama_invalid.py --port 11500 --fail-first

3. Тест с реальным prompt (симуляция batch=3 с EXAMPLE):
   $prompt = @"
   EXAMPLE:
   Issue: line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, hint: rename
   Fix: {"id": 1, "line": 32, ...}

   ISSUES:

   line 1, code: a, rule: X, hint: h
   line 2, code: b, rule: Y, hint: h2
   line 3, code: c, rule: Z, hint: h3

   Return ONLY a JSON array with exactly 3 elements ...
   "@
   $body = @{model="qwen2.5-coder:7b";messages=@(@{role="user";content=$prompt})} | ConvertTo-Json -Depth 5 -Compress
   $r1 = Invoke-RestMethod -Method Post -Uri http://localhost:11500/api/chat -Body $body -ContentType 'application/json'
   Write-Host "R1: $($r1.message.content)"
   $r2 = Invoke-RestMethod -Method Post -Uri http://localhost:11500/api/chat -Body $body -ContentType 'application/json'
   Write-Host "R2: $($r2.message.content)"

4. Ожидание:
   - R1 = "not a valid json at all".
   - R2 = JSON-массив РОВНО из 3 элементов.
   - line НЕ включает 32.

5. Тест с batch=10 (симуляция):
   Повторить с 10 lines + "exactly 10 elements".
   Ожидание: R2 = массив ровно из 10 элементов.

6. Тест с batch=5 (fallback sub):
   Повторить с 5 lines + "exactly 5 elements".
   Ожидание: R2 = массив ровно из 5 элементов.

7. Остановить мок: Ctrl+C.
   Ожидание: "mock-ollama stopped".

### Фаза 3 — Отчёт DS_101c_report.md

Формат: EXCHANGE\OUTBOX\DS_101c_report.md
- UTF-8 без BOM.
- РУССКИЙ.

Содержание:
1. Изменения в mock_ollama_invalid.py (diff или описание).
2. py_compile: RC.
3. Тест batch=3: R1, R2 (цитата).
4. Тест batch=10: R2 (цитата, длина массива).
5. Тест batch=5: R2 (цитата, длина массива).
6. Итог: мок возвращает ровно N элементов.

## Ограничения
- SRC не трогать.
- Реальную Ollama (11434) не трогать.
- Не запускать ai_local_worker через мок.
- Git/push/GP не выполнять.
- Прогноз KODA не нужен.

## Артефакты KODA
- tools\mock_ollama_invalid.py (изменён).
- EXCHANGE\OUTBOX\DS_101c_report.md.

## После KODA (Vitaly, отдельный шаг)
Повторный прогон DS_101b:
1. Запустить мок:
   python tools\mock_ollama_invalid.py --port 11500 --fail-first
2. Прогнать ai_local_worker (та же команда, что в DS_101b).
3. Ожидание:
   - batch 1/4: invalid → fallback → sub 1/2 valid (5) + sub 2/2 valid (5)
   - batches 2/4, 3/4, 4/4: valid (10, 10, 6)
   - fixed=36
   - fallback_count=1
   - fallback_subbatches_ok=2/2
   - invalid_json=1