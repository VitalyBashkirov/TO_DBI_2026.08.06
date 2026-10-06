# DS_084 — Merge-фиксы в ai_local_worker

Дата: 29.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация + микроправка | Приоритет: средний
Зависит от: DS_082b, DS_083a | Блокирует: —
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5),
     OUTBOX\DS_082b_report.md (§5.3, §5.5), OUTBOX\DS_083a_report.md (§Recommendation)

---

## 1. Цель

Устранить 8 skipped (Category C) из DS_083a: несколько фиксов на одну
строку, apply_fixes оставляет первый (first-wins по DS_054 §2.6), остальные
падают на before mismatch.

Решение — worker-side merge: ai_local_worker.py перед записью AI_RESPONSE
объединяет фиксы одной строки. Ожидаемо: 52 → ~60 applied (+15%).

Не требует правки apply_fixes (DS_081 — не баг, DS_083a §A=0).
Не требует rule-based v2 (DS_083b — пессимистичная разведка, отложено).

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | tools\ai_local_worker.py | merge_fixes_by_line() — объединение фиксов одной строки перед write_response |
| 2 | tools\ai_local_worker_config.json | добавить "merge_same_line": true |

Не менять: SRC\, DATA\, tools\rule_based_fixer.py,
формат AI_REQUEST/AI_RESPONSE.

### 2.1. Алгоритм merge

**Точка вызова:** `run_request` — **после** цикла по батчам, **до**
`write_response`. Собрать `all_fixes` (все батчи) → `merge_fixes_by_line(all_fixes)`
→ `write_response`.

Алгоритм:

1. Сгруппировать all_fixes по `line`.
2. Для каждой группы (2+ фикса):
   1. Отсортировать фиксы по приоритету правила (§2.2).
   2. `result = None`
   3. Для каждого фикса f:
      - if `result is None`: `result = f.after` (первый фикс применяется напрямую)
      - else:
        - if `f.before` содержится в `result`:
          `result = result.replace(f.before, f.after)`
        - else: **skip f** (записать в metrics как merge_skipped)
   4. Итог: `result` — `after` merged-фикса; `before` — от первого фикса.
3. Группы с одним фиксом — без изменений.

### 2.2. Приоритеты правил (v1)

    PRIORITY = {
      "delete":  ["CODE_IN_COMMENT", "NOT_MENTIONED", "OBLIGATORY_IN_OTHERS"],
      "replace": ["BAD_PREFIX", "PREFIX_TYPE_IN_VAR_NAME", "WRONG_METHOD_SYNTAX",
                  "COMPILE_MISSING_COND", "FUNC_ATTR_DEREFERENCE", "UDF",
                  "SUBOPTIMAL_UNSELECTED_COL_USAGE", "COLUMNS_LIMIT_EXCEEDED"],
      "append":  [],
    }

Правило, которого нет в списке → приоритет "replace" по умолчанию.

### 2.3. Случаи из DS_083a (7 строк, 8 skipped)

| Line | Ids | Правила |
|------|-----|---------|
| 761 | 16, 17 | COMPILE_MISSING_COND × 2 |
| 1042 | 23, 24 | UDF + BAD_PREFIX |
| 1395 | 35, 36 | BAD_PREFIX + UDF |
| 1411 | 37, 38 | COLUMNS + UDF |
| 1466 | 41, 42, 43 | FUNC_ATTR + SUBOPT × 2 |
| 1731 | 48, 49 | FUNC_ATTR + SUBOPT |
| 1761 | 50, 51 | FUNC_ATTR + BAD_PREFIX |

**7 строк** с 2+ фиксами → **8 skipped** (одна строка с 3 фиксами → 2 skipped).

### 2.4. Если merge невозможен

Если f.before **не содержится** в result — оставить первый,
f — skip, записать в metrics как merge_skipped.

Не ломать текущее поведение — при `merge_same_line: false` merge
не делается, всё как было в DS_082b.

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | AI_REQUEST_PSH_DEP_PRIV_GO (61 issue) с merge | AI_RESPONSE с merged fixes, applied_auto > 52 |
| 2 | merge 2 фикса на одной строке | merged элемент с корректным before/after |
| 3 | merge 3 фикса (line 1466, ids 41+42+43) | один merged элемент |
| 4 | 2 фикса, f2.before не в f1.after | f1 применён, f2 → merge_skipped |
| 5 | merge_same_line: false | как DS_082b (applied_auto=52) |
| 6 | Регресс DS_054, DS_080, DS_081, DS_082a, DS_082b, DS_083a | PASSED |

Метрика: applied_auto на PSH_DEP_PRIV_GO с merge vs без merge.

---

## 4. Ограничения

- SRC\ — НЕ МЕНЯТЬ (правки только в tools\).
- tools\rule_based_fixer.py — НЕ МЕНЯТЬ.
- Формат AI_REQUEST/AI_RESPONSE — НЕ МЕНЯТЬ.
- Логи: EXCHANGE\bot.log + stdout.
- temp\ — писать можно.
- Не вызывать LM Studio, только Ollama (11434).

---

## 5. Отчёт (OUTBOX\DS_084_report.md)

Стандарт + разделы:

5.1. merge_fixes_by_line() — алгоритм, псевдокод.
5.2. Метрика: applied_auto до/после (52 → X).
5.3. Какие 8 skipped из DS_083a merged, какие — merge_skipped.
5.4. Тесты 1–6 — PASSED/FAILED + метрики.
5.5. Расхождения.

---

## 6. Артефакты

- tools\ai_local_worker.py (правка)
- tools\ai_local_worker_config.json (правка)
- EXCHANGE\OUTBOX\DS_084_report.md
- temp\ds084_extract.json