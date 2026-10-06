# DS_101b — Живое подтверждение fallback DS_085 через мок-сервер Ollama

## Цель
Живое подтверждение fallback DS_085 (split 10 → 2×5) в
tools\ai_local_worker.py при invalid_json > 0.

Метод: локальный мок-сервер Ollama API, отвечающий невалидным
JSON на первый /api/chat и валидным — на последующие (подбатчи
fallback).

## Контекст
- DS_101 подтвердил AI-цикл и стабильность 7b (invalid_json=0,
  fallback не активировался).
- Fallback DS_085: tools\ai_local_worker.py, функции
  validate_batch_response (строка 368), run_fallback (строка 642).
- Условие fallback: fallback_on_invalid=True и len(batch) > 1
  при status='invalid'.
- Мок-сервер подменяет Ollama, не трогая SRC и реальную Ollama
  на порту 11434.
- Реальная Ollama: qwen2.5-coder:7b, порт 11434, не трогать.
- Мок-сервер: порт 11500, отдельный процесс.

## Разведка по коду (подтверждено Vitaly, 07.10.2026)

Файл: tools\ai_local_worker.py (45 195 B, mtime 05.10.2026 09:42:06).

### call_ollama (строка 222)
- Endpoint: POST /api/chat.
- URL: base_url.rstrip('/') + '/api/chat'.
- Возврат: dict ответа Ollama, или {'error': ...} (HTTP/таймаут),
  или None (сервис недоступен).
- ВАЖНО: {'error': ...} НЕ запускает fallback — batch пропускается.
- Fallback срабатывает только при невалидном JSON (parsed не прошёл
  validate_batch_response).

### content_of (строка 289)
- Извлекает content из ответа:
  1. answer['message']['content'] — основной путь;
  2. answer['response'] — fallback (для /api/generate).
- Мок должен вернуть message.content.

### build_prompt (строка 256)
- Формат issues в user content:
    line {N}, code: {code}, rule: {rule_code}, hint: {desc}
- ids НЕТ в prompt — только line.
- Количество issues упомянуто в инструкции:
    "Return ONLY a JSON array with exactly {len(batch)} elements"
- Мок: считать строки "line N," в user content (regex).

### normalize_fixes (строка 322)
- Читает поля из ответа модели:
  - line — для сопоставления с iss['line'] (обязательно).
  - after — либо строка, либо null (обязательно).
  - reason — опционально (default '').
  - confidence — опционально (default 0.0).
- НЕ читает: fix, before, id.
- before берётся из запроса (iss.get('code')), не из ответа.
- id берётся из iss['id'], не из ответа.
- Если для issue нет элемента с совпадающим line — берётся
  remaining[0] (по порядку). Если remaining пуст — [] (весь
  батч пропускается).

Вывод для мока: JSON-массив элементов вида
{"line": N, "after": "...", "reason": "...", "confidence": 0.95}.

## Что делает KODA
1. Прочитать раздел «Разведка по коду» выше — это готовые факты.
2. Создать tools\mock_ollama_invalid.py (Python 3.11, только stdlib).
3. py_compile OK.
4. Проверить, что мок запускается и слушает порт.
5. Сдать краткий отчёт EXCHANGE\OUTBOX\DS_101b_mock_ready.md.

## Что KODA НЕ делает
- Не запускает прогон ai_local_worker через мок.
- Не пишет DS_101b_report.md (отчёт — после прогона).
- Не трогает SRC.
- Не трогает реальную Ollama (порт 11434).
- Не выполняет git/push/GP.

## Задание

### Фаза 1 — Создать мок-сервер

Файл: tools\mock_ollama_invalid.py
Язык: Python 3.11.
Зависимости: только stdlib (http.server, json, sys, argparse,
threading, time, re, datetime).

#### API мок-сервера

GET /api/tags
Ответ:
{
  "models": [
    {"name": "qwen2.5-coder:7b", "model": "qwen2.5-coder:7b"}
  ]
}
ВАЖНО: GET /api/tags НЕ инкрементит счётчик запросов.

POST /api/chat
Ответ (формат Ollama):
{
  "model": "qwen2.5-coder:7b",
  "created_at": "<ISO-8601>",
  "message": {
    "role": "assistant",
    "content": "<строка>"
  },
  "done": true
}

/api/generate НЕ нужен (только chat).

Логика ответа на POST /api/chat:
- Счётчик запросов (глобальный, в памяти процесса).
- Запрос №1 .. №fail_count → content = "not a valid json at all"
  (невалидный).
- Запросы №fail_count+1 и далее → content = валидный JSON-массив:
    [
      {"line": <N>, "after": "mock fixed line",
       "reason": "mock fallback test", "confidence": 0.95},
      ...
    ]
  - Количество элементов = числу issues в батче.
  - Определение числа issues:
    1. Regex по user content: r'\bline\s+(\d+)\s*,'
       (собрать все номера по порядку).
    2. Если ни одного не найдено — вернуть default_count (10).
  - Каждому элементу:
    - line — из извлечённых номеров (по порядку).
    - after — "mock fixed line".
    - reason — "mock fallback test".
    - confidence — 0.95.

ВАЖНО: поле фикса называется after (не fix!).

#### HTTP-заголовки (ОБЯЗАТЕЛЬНО)

Для всех ответов:
- self.send_header('Content-Type', 'application/json; charset=utf-8')
- self.send_header('Content-Length', str(len(body_bytes)))
- self.end_headers()
- self.wfile.write(body_bytes)

Без Content-Length urllib.request может зависнуть.

#### CLI мок-сервера
python tools\mock_ollama_invalid.py --port 11500 --fail-first

Параметры:
- --port N (default 11500).
- --host H (default localhost).
- --fail-first (default True) — ломать первый запрос.
- --fail-count K (default 1) — сколько первых запросов ломать.
- --fail-content STR (default "not a valid json at all").
- --default-count N (default 10) — сколько элементов, если
  line-паттерн не найден.

Вывод в stdout (flush=True):
- "mock-ollama listening on http://localhost:<port>"
- По каждому POST:
  "req#N POST /api/chat → valid|invalid"
- По каждому GET:
  "req#N GET /api/tags → ok"

При SIGINT (Ctrl+C) — "mock-ollama stopped".

#### Порт-чек (ОБЯЗАТЕЛЬНО)
try:
    server = HTTPServer((host, port), MockOllamaHandler)
except OSError as exc:
    print(f"port {port} busy: {exc}")
    sys.exit(1)

#### Структура файла (ориентир)
- Класс MockOllamaHandler(BaseHTTPRequestHandler).
- Глобальные: counter (int), fail_count (int), lock (threading.Lock),
  fail_content (str), default_count (int).
- do_GET — /api/tags (НЕ инкрементит counter).
- do_POST — /api/chat (инкрементит counter).
- _increment_and_get() — вернуть номер запроса атомарно.
- _extract_lines(content) — regex "line N," → список int.
- _make_fix_array(lines) — список фиксов.
- _send_json(data) — с Content-Type и Content-Length.
- main() — argparse, HTTPServer, serve_forever().
- if __name__ == '__main__': main().

#### Требования к коду
- Python 3.11, без внешних зависимостей.
- UTF-8 без BOM (см. DS_STANDARD.md §6.1).
- Логи — print в stdout (flush=True).
- Порт-чек — см. выше.

### Фаза 2 — Локальная проверка мок-сервера (KODA)

1. py_compile:
   python -m py_compile tools\mock_ollama_invalid.py
   Ожидание: RC 0.

2. Запуск мок-сервера (в отдельном окне):
   python tools\mock_ollama_invalid.py --port 11500 --fail-first

3. Проверка GET /api/tags (в другом окне):
   Invoke-RestMethod http://localhost:11500/api/tags |
       ConvertTo-Json -Depth 5
   Ожидание: {"models": [{"name": "qwen2.5-coder:7b"}]}.
   В окне мока — строка "req#? GET /api/tags → ok", но счётчик
   POST не увеличился.

4. Проверка POST /api/chat — запрос №1:
   $body = '{"model":"qwen2.5-coder:7b","messages":[{"role":"user","content":"ISSUES:\n\nline 1, code: a, rule: X, hint: h\nline 2, code: b, rule: Y, hint: h2\nline 3, code: c, rule: Z, hint: h3"}]}'
   $r1 = Invoke-RestMethod -Method Post -Uri http://localhost:11500/api/chat `
       -Body $body -ContentType 'application/json'
   $r1 | ConvertTo-Json -Depth 5
   Ожидание: message.content = "not a valid json at all".

5. Проверка POST /api/chat — запрос №2 (тот же body):
   $r2 = Invoke-RestMethod -Method Post -Uri http://localhost:11500/api/chat `
       -Body $body -ContentType 'application/json'
   $r2 | ConvertTo-Json -Depth 5
   Ожидание: message.content = JSON-массив из 3 элементов:
   [{"line":1,"after":"mock fixed line",...},
    {"line":2,...},{"line":3,...}].

6. Остановить мок-сервер: Ctrl+C.
   Ожидание: "mock-ollama stopped".

### Фаза 3 — Отчёт DS_101b_mock_ready.md

Формат: EXCHANGE\OUTBOX\DS_101b_mock_ready.md
- UTF-8 без BOM.
- РУССКИЙ. Транслит не использовать.

Содержание:
1. Файл создан (путь, размер, дата, первые 3 байта hex, строк).
2. py_compile: RC.
3. Проверка /api/tags: результат (цитата), счётчик POST
   не увеличился.
4. Проверка /api/chat №1: результат (content).
5. Проверка /api/chat №2: результат (content — массив из 3).
6. Управление: как запускать, как останавливать (Ctrl+C).
7. Ограничения соблюдены (SRC, Ollama 11434, git).
8. Итог: мок-сервер готов к использованию.

Структуру разделов отчёта можно взять из типового шаблона
DS_101b_mock_ready.md (согласован).

## Формат отчёта (для этой фазы)
Только EXCHANGE\OUTBOX\DS_101b_mock_ready.md, кратко.
Полный DS_101b_report.md — ПОСЛЕ прогона (Vitaly + DS).

## Ограничения
- SRC не трогать.
- Реальную Ollama (порт 11434) не трогать.
- Не запускать ai_local_worker через мок (отдельный шаг — Vitaly).
- Git/push/GP не выполнять.
- Прогноз KODA не нужен.
- Логи — EXCHANGE\bot.log.

## Артефакты KODA
- tools\mock_ollama_invalid.py (новый).
- EXCHANGE\OUTBOX\DS_101b_mock_ready.md (отчёт KODA).

## После KODA (Vitaly, отдельный шаг)
Vitaly:
1. Запускает мок-сервер (в отдельном окне):
   python tools\mock_ollama_invalid.py --port 11500 --fail-first
2. Прогоняет ai_local_worker:
   python tools\ai_local_worker.py `
       --request "F:\TO_DBI\EXCHANGE\AI_IN\AI_REQUEST_PSH_DEP_PRIV_GO_20260930_071636.md" `
       --out "F:\TO_DBI\EXCHANGE\OUTBOX\DS_101b_out" `
       --ollama-url "http://localhost:11500" `
       --model qwen2.5-coder:7b `
       --batch-size 10 `
       --fallback-size 5 `
       --timeout 600 `
       --verbose `
       --metrics "F:\TO_DBI\EXCHANGE\OUTBOX\DS_101b_metrics.json"
3. Проверяет маркеры fallback в bot.log.
4. Останавливает мок-сервер.
5. Присылает вывод DS.
DS формирует DS_101b_report.md.

## Ожидание fallback при прогоне (справочно)
В stdout ai_local_worker ожидается:
- "batch 1/4 ids=[1..10]: невалидный JSON (ожидалось 10) — fallback"
- "  fallback: split 10 -> 2 (по 5)"
- "  fallback sub 1/2 ids=[1..5]: fixes=5 ..."
- "  fallback sub 2/2 ids=[6..10]: fixes=5 ..."
- "  fallback: валидных подбатчей 2/2 ..."
- Далее батчи 2/4, 3/4, 4/4 — валидные (counter > 1 → valid).

Метрики (ожидание):
- fallback_count = 1
- fallback_subbatches_ok = 2
- fallback_subbatches_total = 2
- invalid_json = 1
- fixed = 36

ВАЖНО: fallback sub 1/2 и sub 2/2 получают валидный ответ
от мока (counter > 1). Мок отдаёт столько элементов, сколько
line-номеров в подбатче (5 для sub 1/2, 5 для sub 2/2).

## Примечание по мок-серверу и реальной Ollama
- Мок на порту 11500, реальная Ollama на 11434 — не пересекаются.
- ai_local_worker подключается к 11500 через --ollama-url.
- Реальная Ollama не задействована в прогоне DS_101b.
- После прогона мок останавливается (Ctrl+C), порт освобождается.