# DS_083a — Разбор 9 skipped в apply_fixes

Дата: 29.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: разведка + возможное исправление | Приоритет: средний
Зависит от: DS_081, DS_082b | Блокирует: DS_083b
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5),
     OUTBOX\DS_082b_report.md (§5.3, §5.5)

---

## 1. Цель

Разобрать 9 skipped из 61 в тесте 5 DS_082b (applied_auto=52, skipped=9).
Понять причину. Если баг в apply_fixes (DS_081) — исправить.

---

## 2. Что делать

### 2.1. Сбор данных по 9 skipped

1. Проверить `temp\ds082b_extract.json` — есть ли там skipped-детали
   (построчно: id, rule_code, line, причина).
2. Если данных нет — **воспроизвести** прогон `apply_fixes` на
   `temp\ds082b_out\AI_RESPONSE_PSH_DEP_PRIV_GO_*.md` с логированием
   причины skip для каждого issue:
   - before mismatch (before из AI_RESPONSE != фактическая строка файла);
   - line не найдена;
   - duplicate line в батче (first-wins);
   - after=None (noop);
   - другое.

### 2.2. Классификация

Каждый skipped — в одну категорию:
- A. Баг в apply_fixes (DS_081) — исправить;
- B. before mismatch из-за модели (DS_082b) — задокументировать;
- C. Норма (after=None, noop, duplicate) — задокументировать.

### 2.3. Если A — исправить apply_fixes

Минимальная правка. Не ломать DS_054 (46/46), DS_081 (31/31).

Не менять: SRC\analyzer\scanner.py, SRC\ai_exchange.py, DATA\,
tools\rule_based_fixer.py, tools\ai_local_worker.py.

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | Разбор 9 skipped | Таблица (см. §5.1) |
| 2 | Классификация | A/B/C, число в каждой |
| 3 | Если A — фикс apply_fixes | Пропущенные применяются, регресс DS_081 PASSED |
| 4 | Регресс DS_054, DS_080, DS_081, DS_082a, DS_082b | PASSED |

Метрика: «52 → X applied» на AI_RESPONSE DS_082b (batch 5).

---

## 4. Ограничения

- SRC\analyzer\scanner.py, SRC\ai_exchange.py, DATA\ — НЕ МЕНЯТЬ.
- SRC\fixer\code_fixer.py — НЕ МЕНЯТЬ.
- SRC\gui_app.py — только apply_fixes (если баг подтверждён).
- tools\rule_based_fixer.py, tools\ai_local_worker.py — НЕ МЕНЯТЬ.
- Логи: EXCHANGE\bot.log.
- temp\ — писать можно.

---

## 5. Отчёт (OUTBOX\DS_083a_report.md)

Стандарт + разделы:

5.1. Таблица 9 skipped:

    id | rule_code | line | before_response | before_file | after_response | причина

    - before_response — `before` из AI_RESPONSE (что вернула модель);
    - before_file — фактическая строка файла на этой позиции;
    - after_response — `after` из AI_RESPONSE.

5.2. Классификация A/B/C — сколько в каждой.
5.3. Если A — что исправлено в apply_fixes, метрика «52 → X applied».
5.4. Расхождения.

---

## 6. Артефакты

- EXCHANGE\OUTBOX\DS_083a_report.md
- temp\ds083a_skipped_analysis.json