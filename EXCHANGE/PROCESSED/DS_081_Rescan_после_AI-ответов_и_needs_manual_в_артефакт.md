# DS_081 — Rescan после AI-ответов + needs_manual в артефакт

Дата: 28.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация + микроправка | Приоритет: высокий
Зависит от: DS_054, DS_080 | Блокирует: —
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5), DS_FILES.md (§3),
     OUTBOX\DS_078_report.md (§5.3 п.6, п.7), OUTBOX\DS_080_report.md (§5.6 п.3)

---

## §0. Микроправка DS_CONTEXT.md §9.5

Уточнить формулировку критерия AI-отбора (обоснование — DS_080 §5.6 п.3,
в сам текст §9.5 ссылку НЕ включать).

Заменить абзац про (б) на:

> …правило не исчезло полностью после _apply_issue_fixes. remaining_by_rule
> (rule_code → [номера строк исходного скана]) содержит ВСЕ исходные строки
> правила, если после фикса правило не исчезло. Это безопасный over-include:
> фикс смещает номера строк (удаление/переименование), точное совпадение
> теряет до 80% реальных проблем.

---

## 1. Цель

Закрыть два разрыва DS_078 §5.3:

- п.6 — нет rescan после receive_from_ai (не видно, что осталось после AI);
- п.7 — needs_manual не сохраняется в артефакт (нечего разбирать вручную).

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | SRC\gui_app.py | receive_from_ai — rescan файлов, по которым пришли ответы |
| 2 | SRC\ai_exchange.py | summarize — опц. структура (обратная совместимость) |
| 3 | SRC\ai_exchange.py | save_needs_manual — Markdown в OUTBOX |
| 4 | EXCHANGE\DS_CONTEXT.md | §9.5 — уточнение (см. §0) |

Не менять: scanner.py, rule_engine.py, code_fixer.py, рубрикаторы, DATA\,
формат AI_REQUEST/AI_RESPONSE.

### 2.1. rescan в receive_from_ai (п.6)

Алгоритм:

1. Собрать список источников (source), по которым в AI_OUT есть AI_RESPONSE.
2. Применить ответы (process_all_responses — как сейчас).
3. Для каждого применённого source:
   - найти файл по source (path из AI_REQUEST Метаданные);
   - выполнить повторный скан + _verify_file (как «Исправить код» для одного файла);
   - записать в bot.log: «Rescan <source>: было N, стало M».
4. Сводка в журнал: «Rescan: K файлов; было N, стало M».

Не делать полный rescan всего каталога — только AI-затронутые файлы.

### 2.2. summarize — расширение (п.7)

Текущий возврат — list[str]. Добавить структурированный режим:

    summarize(..., structured: bool = False)
    # False (default) — list[str] (обратная совместимость)
    # True — dict: {"lines": [...], "by_confidence": {
    #          "auto": [...], "medium": [...], "manual": [...], "noop": [...]}}

Элемент списка manual:
    {"file": <path>, "line": <int>, "rule_code": <str>,
     "before": <str>, "reason": <str>, "confidence": <float>}

Если у summarize уже есть параметр-флаг — использовать существующий
(адаптация под текущий код, обратная совместимость сохраняется).

### 2.3. save_needs_manual

Новый метод в ai_exchange.py:

    save_needs_manual(summary: dict) -> Path

OUTBOX — из константы модуля (если константы нет — добавить).

Формат (Markdown):

    # needs_manual — <ДД.ММ.ГГГГ ЧЧ:ММ:СС>

    Всего: N (auto: A, medium: M, manual: U, noop: Z)

    | файл | строка | правило | before | reason |
    |------|--------|---------|--------|--------|
    | <path> | <line> | <rule_code> | `<code>` | <reason> |

Имя файла: needs_manual_<YYYYMMDD_HHMMSS>.md в EXCHANGE\OUTBOX\.

Если manual пусто — файл не создаётся, в bot.log: «needs_manual: 0».

### 2.4. Интеграция в receive_from_ai

После process_all_responses:

    summary = ai_exchange.summarize(..., structured=True)
    if summary["by_confidence"]["manual"]:
        path = ai_exchange.save_needs_manual(summary)
        bot.log: "needs_manual: N -> <path>"

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | receive_from_ai с 1 AI-ответом | rescan 1 файла; bot.log «Rescan: 1; было N, стало M» |
| 2 | receive_from_ai, синтетика 2 manual + 1 auto | needs_manual_*.md создан; в таблице ровно 2 строки; заголовок «Всего: 3 (auto: 1, medium: 0, manual: 2, noop: 0)» |
| 3 | receive_from_ai без needs_manual | файл не создан; bot.log «needs_manual: 0» |
| 4 | summarize(structured=False) | возвращает list[str] (регресс DS_054) |
| 5 | summarize(structured=True) | возвращает dict с by_confidence |
| 6 | Регресс DS_054, DS_079, DS_080 | PASSED |

Метрика в отчёт: на patch_PSH_DEP_PRIV_GO — сколько needs_manual после AI
(ожидается 0, AI не подключён; тест — на синтетике).

---

## 4. Ограничения

- SRC\analyzer\scanner.py, SRC\fixer\code_fixer.py, SRC\rule_engine.py, DATA\ — НЕ МЕНЯТЬ.
- Формат AI_REQUEST/AI_RESPONSE — НЕ МЕНЯТЬ.
- Полный rescan каталога — НЕ ДЕЛАТЬ (только AI-затронутые файлы).
- Логи: только EXCHANGE\bot.log.
- temp\ — писать можно.

---

## 5. Отчёт (OUTBOX\DS_081_report.md)

Стандарт + разделы:

5.0. §0 — что стало в DS_CONTEXT.md §9.5.
5.1. rescan — где, как, на каких файлах.
5.2. summarize — сигнатура до/после, обратная совместимость.
5.3. save_needs_manual — формат, пример файла.
5.4. Тесты 1–6 — PASSED/FAILED + метрики.
5.5. Регресс DS_054, DS_079, DS_080.
5.6. Расхождения.

---

## 6. Артефакты

- EXCHANGE\OUTBOX\DS_081_report.md
- EXCHANGE\DS_CONTEXT.md (§9.5, только)
- temp\ — синтетика для needs_manual (если создавалась)