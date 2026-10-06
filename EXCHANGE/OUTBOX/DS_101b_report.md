# DS_101b — Live-подтверждение fallback DS_085 через мок-сервер Ollama

## 1. Что сделано
- Создан мок-сервер tools\mock_ollama_invalid.py (KODA, DS_101b).
- Исправлен баг с EXAMPLE-блоком (KODA, DS_101c).
- Проведён live-прогон ai_local_worker через мок.
- Fallback DS_085 (split 10→2×5) подтверждён live.

## 2. Мок-сервер
- Путь: tools\mock_ollama_invalid.py
- Размер: 7 000 B (209 строк), UTF-8 без BOM.
- Порт: 11500.
- API: GET /api/tags, POST /api/chat.
- Поведение:
  - Запрос №1 → invalid ("not a valid json at all").
  - Запросы №2+ → valid JSON-массив.
  - Число элементов = N из "exactly N elements" в промпте.
- py_compile: RC 0.

## 3. Прогон ai_local_worker через мок
Команда:
python tools\ai_local_worker.py `
    --request "...AI_REQUEST_PSH_DEP_PRIV_GO_20260930_071636.md" `
    --out "...EXCHANGE\OUTBOX\DS_101b_out" `
    --ollama-url "http://localhost:11500" `
    --model qwen2.5-coder:7b `
    --batch-size 10 `
    --fallback-size 5 `
    --timeout 600 `
    --verbose `
    --metrics "...EXCHANGE\OUTBOX\DS_101b_metrics.json"

Результат:
- 36 issues, 4 батча (10+10+10+6).
- fixed = 36 (100%).
- invalid_json = 0.
- fallback_count = 1.
- fallback_subbatches_ok = 2/2.
- fallback_time_sec = 4.1.
- RC = 0, DURATION = 12.5 с.

## 4. Маркеры fallback в bot.log

Строка 1304:
[07.10.2026 03:51:09] DS 082b: AI_REQUEST_PSH_DEP_PRIV_GO_20260930_071636.md:
итог 36 из 36 (100%), batch=4, invalid_json=0, skip_batch=0,
fallback=1 (2/2 ok, 4.1с), avg_time=2.1с, avg_conf=0.95,
class={'auto': 36, 'medium': 0, 'manual': 0, 'noop': 0},
response=AI_RESPONSE_PSH_DEP_PRIV_GO_20260930_071636.md

В stdout:
- "batch 1/4 ids=[1..10]: невалидный JSON (ожидалось 10) — fallback"
- "fallback: split 10 -> 2 по 5"
- "fallback sub 1/2 ids=[1..5]: fixes=5 время=2.1с"
- "fallback sub 2/2 ids=[6..10]: fixes=5 время=2.0с"
- "fallback: валидных подбатчей 2/2, fixes=10"

## 5. Метрики DS_101b_metrics.json
{
  "issues": 36,
  "batch_size": 10,
  "fallback_batch_size": 5,
  "fallback_on_invalid": true,
  "batches": 4,
  "fixed": 36,
  "skipped_batches": 0,
  "invalid_json": 0,
  "ollama_errors": 0,
  "fallback_count": 1,
  "fallback_time_sec": 4.1,
  "fallback_subbatches_ok": 2,
  "fallback_subbatches_total": 2,
  "batch_times_sec": [2.1, 2.1, 2.0, 2.0, 2.1, 2.1],
  "model": "qwen2.5-coder:7b",
  "classification": {"auto": 36, "medium": 0, "manual": 0, "noop": 0},
  "merge": {"enabled": true, "merged_lines": 0, "skipped_in_merge": 0}
}

Пояснение: invalid_json=0 при fallback_count=1 — корректно.
В коде (строки 781-800) invalid_json инкрементится только если
fallback не сработал или отключён. При успешном fallback
инкрементится fallback_count.

## 6. Артефакты
- tools\mock_ollama_invalid.py (7 000 B).
- EXCHANGE\OUTBOX\DS_101b_out\AI_RESPONSE_PSH_DEP_PRIV_GO_20260930_071636.md (8 746 B).
- EXCHANGE\OUTBOX\DS_101b_out\AI_REQUEST_PSH_DEP_PRIV_GO_20260930_071636.processed.json (479 B).
- EXCHANGE\OUTBOX\DS_101b_metrics.json.
- EXCHANGE\bot.log (строки 1304+).
- EXCHANGE\OUTBOX\DS_101b_mock_ready.md (отчёт KODA).
- EXCHANGE\OUTBOX\DS_101c_report.md (отчёт KODA по фиксу).

## 7. Вывод

Fallback DS_085 (split 10→2×5) ПОДТВЕРЖДЁН LIVE:
- Активируется при invalid JSON от Ollama.
- Корректно делит батч 10 на 2 подбатча по 5.
- Собирает fixes из подбатчей.
- Не теряет issues (36 из 36).

Открытая проблема №1 (стартовый контекст): ЗАКРЫТА.

## 8. Расхождения
- invalid_json=0 при fallback_count=1 — не расхождение, объяснено в п.5.

## 9. Таблица «параметр | значение | источник»

| Параметр | Значение | Источник |
|----------|----------|----------|
| Мок | tools\mock_ollama_invalid.py | файл |
| Мок-сервер: invalid на №1 | да | лог мока |
| Мок-сервер: valid на №2+ | да | лог мока |
| Модель | qwen2.5-coder:7b | metrics.json |
| batch_size | 10 | metrics.json |
| fallback_batch_size | 5 | metrics.json |
| issues | 36 | metrics.json |
| fixed | 36 (100%) | metrics.json |
| fallback_count | 1 | metrics.json |
| fallback_subbatches_ok | 2 | metrics.json |
| fallback_subbatches_total | 2 | metrics.json |
| invalid_json | 0 | metrics.json |
| RC | 0 | консоль |
| DURATION | 12.5 с | консоль |