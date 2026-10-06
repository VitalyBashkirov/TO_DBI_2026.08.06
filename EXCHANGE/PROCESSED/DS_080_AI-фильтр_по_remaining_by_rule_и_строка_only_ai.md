# DS_080 — AI-фильтр по remaining_by_rule + строка only_ai в заголовках

Дата: 28.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация + микроправка | Приоритет: высокий
Зависит от: DS_079 | Блокирует: —
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5), DS_FILES.md (§3),
     OUTBOX\DS_079_report.md (§5.6 п.1)

---

## §0. Микроправка заголовков логов

В шаблон заголовка scan_report_*.md и scan_VVVVVV_*.md добавить в блок
«Флаги замены» строку:

    only_ai: V      — отправлять только issues, требующие AI (filter: needs_ai_fix)

Печатать V (галка ВКЛ) / x (галка ВЫКЛ).

Файлы: SRC\gui_app.py — функция формирования заголовка (уточнить при чтении).

---

## 1. Цель

Устранить разрыв DS_079: галка «Только AI» фильтрует по ignore_set, что
дублирует существующее поведение АРМ. Метрики без галки и с галкой идентичны
(249 = 249 на patch_PSH_DEP_PRIV_GO).

Нужен реальный фильтр: только issues, оставшиеся нефиксированными после
детерминированного конвейера (needs_ai_fix > 0).

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | SRC\fixer\code_fixer.py | `_verify_file` — заполнять `scan_results["remaining_by_rule"]` |
| 2 | SRC\gui_app.py | `send_to_ai` — фильтр по remaining_by_rule (не по ignore_set) |
| 3 | SRC\gui_app.py | шаблон заголовка — строка only_ai (§0) |
| 4 | EXCHANGE\DS_CONTEXT.md | §9.5 — обновить критерий (см. §2.4) |

Не менять: ai_exchange.py, scanner.py, rule_engine.py, рубрикаторы, DATA\.

### 2.1. `remaining_by_rule` в `_verify_file`

Формат:

    remaining_by_rule: dict[str, list[int]]  # rule_code -> [номера строк]

Заполняется по остатку после `_apply_issue_fixes` при `ai_fallback`.
Складывается в `scan_results["remaining_by_rule"]` (по аналогии с `stats`).

Если `_verify_file` не имеет доступа к `scan_results` — вернуть структуру
и сохранить в вызывающем коде.

### 2.2. Фильтр в `send_to_ai`

Алгоритм:

1. Если галка «Только AI» ВЫКЛ → все issues (обратная совместимость).
2. Если ВКЛ:
   - взять `scan_results["remaining_by_rule"]`;
   - для каждого issue оставить, если `issue.rule_code in remaining_by_rule`
     И `issue.line in remaining_by_rule[issue.rule_code]`;
   - если `remaining_by_rule` отсутствует (старый scan_results) — fallback
     на ignore_set + предупреждение в bot.log.
3. Сгруппировать, write_request (формат без изменений).
4. Лог: «Отправлено N issues из M (фильтр: needs_ai_fix)».

### 2.3. Fallback

Если `remaining_by_rule` пуст или отсутствует — использовать ignore_set
(как сейчас). Логировать причину.

### 2.4. Обновление DS_CONTEXT.md §9.5

Заменить формулировку критерия:

> Issue попадает в AI_IN, если: (а) правило в PARSER_SQL имеет
> transform_type == "ignore", И (б) issue остался нефиксированным после
> _apply_issue_fixes (remaining_by_rule[rule_code] содержит номер строки issue).
> Только при галке «Только AI» ВКЛ; при ВЫКЛ — все issues (обратная совместимость).

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | patch_PSH_DEP_PRIV_GO, галка ВКЛ | В AI < 249 (ожидается 50–150) |
| 2 | patch_PSH_DEP_PRIV_GO, галка ВЫКЛ | В AI = 249 (регресс DS_079) |
| 3 | Заголовки логов | В шапке есть строка only_ai: V/x |
| 4 | Регресс DS_079, DS_054, DS_068 | PASSED |

Метрика в отчёт: таблица «файл | В AI было | В AI стало».

---

## 4. Ограничения

- SRC\analyzer\scanner.py, SRC\ai_exchange.py, SRC\rule_engine.py, DATA\ — НЕ МЕНЯТЬ.
- Формат AI_REQUEST_*.md — НЕ МЕНЯТЬ.
- Логи: только EXCHANGE\bot.log.
- temp\ — писать можно.
- Расхождение с DS_CONTEXT.md §9.5 — доложить автору DS.

---

## 5. Отчёт (OUTBOX\DS_080_report.md)

Стандарт + разделы:

5.0. §0 — что стало в шаблонах заголовков.
5.1. remaining_by_rule — где заполняется, формат, пример.
5.2. send_to_ai — строки правки, алгоритм.
5.3. Тесты 1–4 — PASSED/FAILED + метрики.
5.4. Метрика: таблица «файл | В AI было | В AI стало».
5.5. Fallback — когда срабатывает, что в bot.log.
5.6. Расхождения.

---

## 6. Артефакты

- EXCHANGE\OUTBOX\DS_080_report.md
- EXCHANGE\DS_CONTEXT.md (§9.5, только)
- temp\ds080_extract.json (если создавался)