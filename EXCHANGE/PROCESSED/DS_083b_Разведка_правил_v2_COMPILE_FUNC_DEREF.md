# DS_083b — Разведка правил v2 для rule-based fixer

Дата: 29.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: разведка (read-only) | Приоритет: средний
Зависит от: DS_082a, DS_083a | Блокирует: DS_084
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5),
     OUTBOX\DS_082a_report.md (§5.3), DS_083a_report.md

---

## 1. Цель

Разведка трёх правил для rule-based v2 (DS_084):
- COMPILE_MISSING_COND (13 issues);
- FUNC_ATTR_DEREFERENCE (7);
- DEREFERENCING_TO_OUT_PARAM (6).

Оценить: сколько issues реально станут тривиальными, что нужно
для алгоритма, риск ложных срабатываний.

Read-only. SRC, DATA, tools\ не менять.

---

## 2. Что делать

### 2.1. Источники примеров

- `temp\ds082b_req\AI_REQUEST_PSH_DEP_PRIV_GO_20260928_213624.md` (61-issue, из DS_082b);
- если файла нет — `EXCHANGE\AI_IN\AI_REQUEST_PSH_DEP_PRIV_GO_*.md`
  (96-issue из DS_080), отфильтровать три правила.

### 2.2. Для каждого правила (COMPILE_MISSING_COND, FUNC_ATTR_DEREFERENCE,
DEREFERENCING_TO_OUT_PARAM)

1. Собрать 3–5 примеров из AI_REQUEST.
2. Понять, есть ли детерминированный алгоритм:
   - COMPILE_MISSING_COND: `ref [X] := ::[X](...)` — что именно заменить?
   - FUNC_ATTR_DEREFERENCE: `.first..last loop` → `in all`? Не всегда?
   - DEREFERENCING_TO_OUT_PARAM: `outStr := outStr || errRec.x` — что заменить?
3. Оценить:
   - сколько % issues данного правила тривиальны;
   - что нужно для алгоритма (regex? контекст?);
   - риск ложных срабатываний.
4. Рекомендация: добавить в rule_based_rules.json (DS_084) или оставить в AI.

### 2.3. Опционально — BAD_PREFIX/PREFIX_TYPE

Если время позволяет: посмотреть **пропущенные** BAD_PREFIX/PREFIX_TYPE
из-за fallback (§4 п.5 отчёта DS_082a: короткие имена t1/i/m не покрываются).
Если найдутся — отметить, что улучшить в DS_084.

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | COMPILE_MISSING_COND | Алгоритм? %, риск |
| 2 | FUNC_ATTR_DEREFERENCE | Алгоритм? %, риск |
| 3 | DEREFERENCING_TO_OUT_PARAM | Алгоритм? %, риск |
| 4 | Регресс DS_082a | PASSED (изменений нет — read-only) |

---

## 4. Ограничения

- SRC\, DATA\, tools\ — НЕ МЕНЯТЬ (разведка).
- Логи: EXCHANGE\bot.log.
- temp\ — писать можно.

---

## 5. Отчёт (OUTBOX\DS_083b_report.md)

Стандарт + разделы:

5.1. COMPILE_MISSING_COND — примеры (3–5), алгоритм, %, риск.
5.2. FUNC_ATTR_DEREFERENCE — примеры (3–5), алгоритм, %, риск.
5.3. DEREFERENCING_TO_OUT_PARAM — примеры (3–5), алгоритм, %, риск.
5.4. BAD_PREFIX/PREFIX_TYPE — что улучшить (опционально).
5.5. Рекомендация для DS_084: какие правила добавить, ожидаемое покрытие.
5.6. Расхождения.

---

## 6. Артефакты

- EXCHANGE\OUTBOX\DS_083b_report.md
- temp\ds083b_rules_probe.json