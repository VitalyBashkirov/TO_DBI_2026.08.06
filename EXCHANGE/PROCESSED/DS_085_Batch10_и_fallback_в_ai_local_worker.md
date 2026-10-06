# DS_085 — Batch 10 + fallback в ai_local_worker

Дата: 29.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация + микроправка | Приоритет: средний
Зависит от: DS_082b, DS_084 | Блокирует: —
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5),
     OUTBOX\DS_082b_report.md (§5.3, §5.5), OUTBOX\DS_084_report.md (§5.5)

---

## 1. Цель

Снизить время AI-обработки 61 issue с 37 мин (batch 5) до ~28 мин (batch 10).
Проблема batch 10: 1 сбой (9/10, invalid_json) из 7 батчей (DS_084, эксперимент).
Решение: fallback — при invalid_json в batch 10 -> split на 2x batch 5, retry.

Модель не меняется: deepseek-coder:6.7b через Ollama.

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | tools\ai_local_worker.py | fallback при invalid_json (split) |
| 2 | tools\ai_local_worker_config.json | batch_size: 10, fallback_batch_size: 5, fallback_on_invalid: true |

Не менять: SRC\, DATA\, tools\rule_based_fixer.py,
формат AI_REQUEST/AI_RESPONSE, merge_fixes_by_line (DS_084).

### 2.1. Алгоритм fallback

В `call_ollama` / `run_request`:

1. Отправить batch 10 в Ollama.
2. Распарсить JSON (extract_json_array).
3. Проверка валидности:
   - count == len(batch) И все line из ответа ∈ batch → принять;
   - иначе → invalid_json (включая: count < len, count > len,
     JSON пуст, line mismatch).
4. При invalid_json:
   1. Split batch 10 → 2×5.
   2. Отправить каждый подбатч.
   3. Для каждого подбатча:
      - если валидный → fix добавляются в общий список;
      - если invalid → issues подбатча → needs_manual
        (не в AI_RESPONSE).
   4. Метрика: fallback_count++, fallback_time += время двух подбатчей.

### 2.2. Поведение при batch 5 invalid

Не retry. Пропустить. Issues уйдут в needs_manual (через classify_fix
при receive_from_ai).

Логика: batch 5 даёт 0 invalid на практике (DS_084: 6/6 батчей). Если сбой —
редкость. Retry (batch 5) = +200 сек, риск снова invalid. Split 5->1 =
+200 сек. Пропуск = 0 сек.

### 2.3. Конфиг

    {
      "ollama_url": "http://localhost:11434",
      "model": "deepseek-coder:6.7b",
      "batch_size": 10,
      "fallback_batch_size": 5,
      "fallback_on_invalid": true,
      "temperature": 0.1,
      "num_ctx": 4096,
      "max_tokens": 2000,
      "timeout_sec": 600
    }

### 2.4. CLI (дополнительно)

    --batch-size N        оверрайд batch_size
    --no-fallback         отключить fallback (batch 10 без retry)
    --fallback-size N     оверрайд fallback_batch_size

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | Batch 10, 7 батчей, AI_REQUEST_PSH_DEP_PRIV_GO | 7 батчей, если invalid = 0 -> 61 fix |
| 2 | Mock: batch 10, ответ Ollama = 9 элементов | fallback triggered: 2×5, оба валидных, 10 fix merged |
| 3 | Batch 10, no-fallback, invalid батч | invalid батч пропущен, issues -> needs_manual |
| 4 | Fallback time vs batch 5 time | fallback <= +50% времени batch 5 |
| 5 | Регресс DS_054, DS_080, DS_081, DS_082a, DS_082b, DS_084 | PASSED |

Метрика: общее время, fallback_count, % валидных JSON.

Mock (тест 2): в temp\ds085_mock_invalid.py — подменить call_ollama
так, чтобы для одного батча вернуть 9 элементов. Проверить:
fallback triggered, 2×5, оба успешных.

---

## 4. Ограничения

- SRC\ — НЕ МЕНЯТЬ.
- tools\rule_based_fixer.py — НЕ МЕНЯТЬ.
- Формат AI_REQUEST/AI_RESPONSE — НЕ МЕНЯТЬ.
- merge_fixes_by_line (DS_084) — НЕ МЕНЯТЬ.
- Логи: EXCHANGE\bot.log + stdout.
- temp\ — писать можно.
- Не вызывать LM Studio, только Ollama (11434).

---

## 5. Отчёт (OUTBOX\DS_085_report.md)

Стандарт + разделы:

5.1. Алгоритм fallback — псевдокод.
5.2. Метрика: batch 5 (DS_082b) vs batch 10 + fallback.
5.3. Тесты 1–5 — PASSED/FAILED + метрики.
5.4. Расхождения.

---

## 6. Артефакты

- tools\ai_local_worker.py (правка)
- tools\ai_local_worker_config.json (правка)
- EXCHANGE\OUTBOX\DS_085_report.md
- temp\ds085_extract.json
- temp\ds085_mock_invalid.py (mock-тест)