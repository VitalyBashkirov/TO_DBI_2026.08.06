# DS_082b — Local AI worker через Ollama

Дата: 28.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация (отдельный скрипт) | Приоритет: высокий
Зависит от: DS_054, DS_080, DS_081, DS_082a | Блокирует: —
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5), DS_FILES.md (§3),
     OUTBOX\DS_082a_report.md (§5.1, §5.2, §5.3)

---

## 1. Цель

Обработать AI_REQUEST через локальную Ollama (deepseek-coder:6.7b) —
сформировать AI_RESPONSE в формате DS_054, применимый через receive_from_ai
(DS_081). Закрыть 61 issue, оставшихся после rule-based fixer (DS_082a).

Не требует внешнего API. Работает локально, бесплатно, приватно.

---

## 2. Что создаётся

| # | Файл | Что |
|---|------|-----|
| 1 | tools\ai_local_worker.py | Основной скрипт (новый) |
| 2 | tools\ai_local_worker_config.json | Конфиг (новый) |

tools\ — существующая папка (после DS_082a). Не менять: SRC\, DATA\,
формат AI_REQUEST/AI_RESPONSE, tools\rule_based_fixer.py.

### 2.1. Алгоритм

1. Прочитать AI_REQUEST_*.md (парсер — см. §2.2).
2. Для каждого issue — построить элемент запроса (line, rule_code, code, hint).
3. Сгруппировать issues по batch_size (default 5).
4. Для каждого батча:
   - построить обёрточный промпт (§2.3);
   - POST http://localhost:11434/api/chat (stream=false);
   - распарсить JSON (extract_json_array из ai_exchange.py);
   - проверить: count == len(batch), id-ы совпадают.
5. Собрать все fixes в единый список.
6. Записать AI_RESPONSE_<source>_<ts>.md (формат DS_054, §2.4).

### 2.2. Парсер AI_REQUEST

Логика — как в rule_based_fixer.py:parse_request (§5.1 отчёта DS_082a).
Из блока «### Проблема N»:
- line — из «Строка:»;
- rule_code — из «Код правила:»;
- code — из «Текущий код:»;
- description — из «Описание:».

Если rule_based_fixer.py уже содержит parse_request — переиспользовать
импортом (from rule_based_fixer import parse_request). Если нет — скопировать.

### 2.3. Обёрточный промпт (проверено в тестах)

System: PL/SQL migration expert.

Prompt (английский, few-shot):
You are a PL/SQL to PostgreSQL migration expert. Fix the issues below.

EXAMPLE:
Issue: line 32, code: IS_EOD_NEW boolean;, rule: BAD_PREFIX, hint: rename to v_bIS_EOD_NEW
Fix: {"id": 1, "line": 32, "before": "...", "after": "...",
"reason": "...", "confidence": 0.95}

ISSUES:

line N, code: <code>, rule: <rule_code>, hint: <description>
...

Return ONLY a JSON array. No explanations, no markdown, no code fences.

text

Hint — из description issue (например, «переименуйте в "v_bX"»).

### 2.4. Формат AI_RESPONSE

AI_RESPONSE_<source>_<ts>.md — Markdown + ```json [...]```:

    [{"id": <n>, "line": <n>, "before": "...", "after": "...",
      "reason": "ai-local: deepseek-coder:6.7b", "confidence": <0.0-1.0>}]

confidence — из ответа модели (0.0–1.0).
reason — префикс "ai-local: <model>" + ответ модели.

### 2.5. Конфиг

    {
      "ollama_url": "http://localhost:11434",
      "model": "deepseek-coder:6.7b",
      "batch_size": 5,
      "temperature": 0.1,
      "num_ctx": 4096,
      "max_tokens": 2000,
      "timeout_sec": 600
    }

### 2.6. CLI

    python tools\ai_local_worker.py --request <file> --out <dir>
    python tools\ai_local_worker.py --in-dir EXCHANGE\AI_IN --out-dir EXCHANGE\AI_OUT

Glob — внутри Python, не в cmd.

### 2.7. Fallback

Если Ollama недоступна — лог «ollama unavailable» + exit 1.
Если batch вернул невалидный JSON — лог, issues этого батча пропускаются
(уйдут в needs_manual через DS_081).

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | AI_REQUEST_PSH_DEP_PRIV_GO (61 issue) через Ollama | AI_RESPONSE с ~55–61 элементом за ~20–30 минут |
| 2 | batch_size=1 | Медленно, но корректно |
| 3 | Ollama недоступна | Лог, exit 1 |
| 4 | Невалидный JSON от модели | Лог, батч пропущен |
| 5 | Регресс DS_054, DS_080, DS_081, DS_082a | PASSED |

Метрика: время на 61 issue, % валидных JSON, средний confidence.

---

## 4. Ограничения

- SRC\, DATA\ — НЕ МЕНЯТЬ.
- Формат AI_REQUEST/AI_RESPONSE — НЕ МЕНЯТЬ.
- tools\rule_based_fixer.py — НЕ МЕНЯТЬ (только переиспользование).
- Логи: только EXCHANGE\bot.log + stdout.
- temp\ — писать можно.
- Не вызывать LM Studio, только Ollama (11434).

---

## 5. Отчёт (OUTBOX\DS_082b_report.md)

Стандарт + разделы:

5.1. tools\ai_local_worker.py — структура, CLI.
5.2. Обёрточный промпт — пример.
5.3. Метрика: время, % валидного JSON, средний confidence.
5.4. Тесты 1–5 — PASSED/FAILED + метрики.
5.5. Расхождения.

---

## 6. Артефакты

- tools\ai_local_worker.py (новый)
- tools\ai_local_worker_config.json (новый)
- EXCHANGE\OUTBOX\DS_082b_report.md
- temp\ds082b_extract.json, temp\ds082b_out\ (тестовые AI_RESPONSE)