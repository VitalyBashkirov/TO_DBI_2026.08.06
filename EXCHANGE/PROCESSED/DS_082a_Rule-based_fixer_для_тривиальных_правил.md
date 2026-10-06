# DS_082a — Rule-based fixer для тривиальных правил

Дата: 28.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация (отдельный скрипт) | Приоритет: высокий
Зависит от: DS_054, DS_080, DS_081 | Блокирует: DS_082b
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§9.5), DS_FILES.md (§3),
     OUTBOX\DS_078_report.md (§5.3), DS_080_report.md, DS_081_report.md

---

## 1. Цель

Закрыть ~70% issues AI_REQUEST без вызова AI — через rule-based executor.
Скрипт читает AI_REQUEST, формирует AI_RESPONSE в том же формате. АРМ
применяет через существующий receive_from_ai (DS_081).

Разгружает AI для сложных правил (DS_082b). На CPU AI работает ~36 сек/issue —
rule-based экономит часы.

---

## 2. Что создаётся

| # | Файл | Что |
|---|------|-----|
| 1 | tools\rule_based_fixer.py | Основной скрипт (новый) |
| 2 | tools\rule_based_rules.json | Список тривиальных правил + шаблоны |

tools\ — новая папка. НЕ в .gitignore (скрипт — часть проекта, коммитить).

Не менять: SRC\, DATA\, формат AI_REQUEST/AI_RESPONSE, EXCHANGE\.

### 2.1. Тривиальные правила (v1)

| rule_code | Действие |
|-----------|----------|
| BAD_PREFIX | rename old→new (new из description) |
| PREFIX_TYPE_IN_VAR_NAME | rename old→new (new из description) |
| WRONG_METHOD_SYNTAX | replace `[X].Y` → `::[X].[Y]` |
| CODE_IN_COMMENT | delete строки (или диапазона) |
| QUOTING | `#` → `_` в идентификаторах |
| SIZELESS | `string` → `varchar2(255)` |
| NOT_MENTIONED | delete объявления |

### 2.2. Источник данных — AI_REQUEST

Plan в AI_REQUEST НЕ пишется. Извлекаем из блока «Проблемы для AI»:

- `line` — из «Строка:»;
- `rule_code` — из «Код правила:»;
- `code` — из «Текущий код:»;
- `description` — из «Описание:» (содержит подсказку new_name).

### 2.3. Алгоритмы по правилам

| rule_code | Источник new/after | Алгоритм |
|-----------|-------------------|----------|
| BAD_PREFIX | description: regex `переименуйте в "([^"]+)"` | Заменить первое вхождение старого имени (из code) на new_name |
| PREFIX_TYPE_IN_VAR_NAME | То же | То же |
| WRONG_METHOD_SYNTAX | description: regex `формате (::\[[^\]]+\]\.\[[^\]]+\])` | Заменить `[X].Y` на `::[X].[Y]` в code |
| CODE_IN_COMMENT | — | Если code начинается с `--` или `/*` → удалить строку. Диапазон — если в description «удалить диапазон строк N–M» |
| QUOTING | — | `#` → `_` только в идентификаторах (не в комментариях) |
| SIZELESS | description или code | `string` → `varchar2(255)` в code |
| NOT_MENTIONED | — | Удалить строку с объявлением (по code) |

Если алгоритм неприменим — issue пропускается, лог «skip rule_code=...».

### 2.4. Формат ответа (совместимость DS_054)

AI_RESPONSE_<source>_<ts>.md — Markdown + ```json [...]```:

    [{"id": <n>, "line": <n>, "before": "...", "after": "...",
      "reason": "rule-based: <rule_code>", "confidence": 0.99}]

confidence = 0.99 (rule-based — детерминированный) → classify_fix → auto.

### 2.5. CLI

    python tools\rule_based_fixer.py --request <path-to-file> --out <dir> \
                                     --rules tools\rule_based_rules.json

Batch (glob внутри Python, НЕ в cmd):

    python tools\rule_based_fixer.py --in-dir EXCHANGE\AI_IN \
                                     --out-dir EXCHANGE\AI_OUT

В CLI-примерах не использовать `*` — Windows cmd не раскрывает glob.

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | AI_REQUEST_PSH_DEP_PRIV_GO (96 issues) | AI_RESPONSE с ~65–70 элементами, ~26–30 пропущено (уйдут в AI) |
| 2 | Только тривиальные issues | 100% обработано |
| 3 | Правило без шаблона | issue пропущен, лог «skip rule_code=...» |
| 4 | apply_fixes на AI_RESPONSE | Все rule-based fix применились (dry-run) |
| 5 | Регресс DS_054, DS_080, DS_081 | PASSED |

Метрика: доля issues закрытых rule-based vs передано в AI.

---

## 4. Ограничения

- SRC\ — НЕ МЕНЯТЬ (скрипт в tools\).
- Формат AI_REQUEST/AI_RESPONSE — НЕ МЕНЯТЬ.
- Не вызывать AI (Ollama/LM Studio) в этом скрипте.
- Логи: только EXCHANGE\bot.log.
- temp\ — писать можно.

---

## 5. Отчёт (OUTBOX\DS_082a_report.md)

Стандарт + разделы:

5.1. tools\rule_based_fixer.py — структура, CLI.
5.2. tools\rule_based_rules.json — формат, список правил.
5.3. Метрика: сколько issues закрыто rule-based на PSH_DEP_PRIV_GO.
5.4. Тесты 1–5 — PASSED/FAILED + метрики.
5.5. Расхождения.

---

## 6. Артефакты

- tools\rule_based_fixer.py (новый)
- tools\rule_based_rules.json (новый)
- EXCHANGE\OUTBOX\DS_082a_report.md
- temp\ds082a_extract.json, temp\ds082a_out\ (тестовые AI_RESPONSE)