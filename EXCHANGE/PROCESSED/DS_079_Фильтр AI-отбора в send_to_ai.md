# DS_079 — Фильтр AI-отбора в send_to_ai

Дата: 26.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: реализация + микроправка | Приоритет: высокий
Зависит от: DS_054, DS_068, DS_072a_Уточнение_B, DS_072e, DS_078
Блокирует: DS_080 (rescan после AI-ответов)
См.: DS_STANDARD.md (§2, §3, §5), DS_CONTEXT.md (§2.1, §9, §9.5), DS_FILES.md (§3)

---

## §0. Микроправка DS_CONTEXT.md §9.5

Зафиксировать критерий AI-отбора (1 абзац):

> Issue попадает в AI_IN, если: (а) правило в `5.RUBRICATOR_PARSER_SQL v5.json`
> имеет `transform_type == "ignore"`, И (б) после `_verify_file` по этому правилу
> остались нефиксированные issues (`needs_ai_fix > 0`).

Только §9.5. Остальное — не трогать.

---

## 1. Цель

Устранить разрыв: `send_to_ai` (gui_app.py:4391) шлёт все issues сканирования
(DS_078 §5.3 п.2). На DEPN это дало 6 AI_REQUEST × 8933 issues. По замыслу DS_054
в AI_IN должны уходить только проблемы, требующие AI.

Итог: фильтр по критерию §0 + галка в GUI.

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | SRC\gui_app.py | `send_to_ai` — применить фильтр; добавить галку |
| 2 | SRC\fixer\code_fixer.py | `_verify_file` — опц.: `remaining_by_rule` (см. §2.3) |
| 3 | EXCHANGE\DS_CONTEXT.md | §9.5 — критерий AI-отбора (§0) |

Не менять: ai_exchange.py (формат — по DS_054, обратная совместимость), scanner.py,
рубрикаторы, DATA\.

### 2.1. Галка в GUI

| Параметр | Значение |
|----------|----------|
| Метка | «Только AI» |
| Тип | `Checkbutton` (tk) / `QCheckBox` (Qt) |
| Расположение | рядом с `btn_to_ai` (gui_app.py:651–656) |
| По умолчанию | включена (только AI) |
| Тултип | «Отправлять только issues, требующие AI (transform_type=ignore + needs_ai_fix>0)» |

При включённой галке — фильтр применяется. При выключенной — текущее поведение
(все issues; для отладки и обратной совместимости).

### 2.2. Фильтр в send_to_ai

Алгоритм (псевдокод, KODA адаптирует под текущий код):

1. Прочитать `5.RUBRICATOR_PARSER_SQL v5.json` → множество `rule_code` с
   `transform_type == "ignore"` (кэшировать в методе).
2. Взять `scan_results`; для каждого issue:
   - оставить, если `issue.rule_code in ignore_set` И `remaining_by_rule` содержит
     `issue.rule_code` с номером строки issue (см. §2.3);
   - если `remaining_by_rule` недоступен — фильтр только по `ignore_set`
     + предупреждение в bot.log: «needs_ai_fix недоступен, фильтр по ignore_set».
3. Сгруппировать по файлам, вызвать `write_request` на каждый (формат — без изменений).
4. Если после фильтра пусто — messagebox «Нет issues, требующих AI» + запись в bot.log.
5. Логировать: «отправлено N issues из M (фильтр: только AI)».

### 2.3. `remaining_by_rule` в `_verify_file`

Если в `scan_results` нет привязки «issue → needs_ai_fix», добавить в
`_verify_file` (code_fixer.py:~1353) атрибут/структуру:

    remaining_by_rule: dict[str, list[int]]  # rule_code -> [номера строк]

Заполняется по остатку после `_apply_issue_fixes` при `ai_fallback`. Используется
в `send_to_ai` для фильтра. Если и без этого фильтр реализуем — НЕ трогать
code_fixer.py.

---

## 3. Тесты

| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | DEPN, галка ВКЛ | AI_REQUEST: 6; issues: M (M<<8933) |
| 2 | DEPN, галка ВЫКЛ | AI_REQUEST: 6 × 8933 (регресс DS_078 §5.6) |
| 3 | DEPN, галка ВКЛ, подкаталог с 1 малым .plp | 1 AI_REQUEST; issues = M_filtered |
| 4 | Регресс DS_054 (46/46), DS_068, DS_072a_Уточнение_B | PASSED |

Метрика в отчёт: таблица «файл | было issues | стало issues | AI_REQUEST было/стало».

---

## 4. Ограничения

- SRC\analyzer\scanner.py, SRC\ai_exchange.py, DATA\ — НЕ МЕНЯТЬ.
- SRC\fixer\code_fixer.py — только §2.3 (`remaining_by_rule`). Если фильтр
  реализуем без него — НЕ трогать.
- Формат AI_REQUEST_*.md — НЕ МЕНЯТЬ (обратная совместимость с ручным каналом).
- Логи: только EXCHANGE\bot.log. SRC\bot.log, SRC\*.log, EXCHANGE\LOG\* — запрещены.
- temp\ — писать можно.
- Расхождение с DS_CONTEXT.md §9.5 — доложить автору DS.

---

## 5. Отчёт (OUTBOX\DS_079_report.md)

Стандарт (DS_STANDARD.md §3) + разделы:

5.1. §0 — что стало в DS_CONTEXT.md §9.5.

5.2. Что изменено: gui_app.py (строки), code_fixer.py (если менялся), DS_CONTEXT.md.

5.3. Галка: метка, расположение, значение по умолчанию, скриншот/текст.

5.4. Тесты 1–4 (§3) — PASSED/FAILED + метрики.

5.5. Метрика DEPN: таблица «файл | было issues | стало issues».

5.6. Расхождения — если выявлены.

---

## 6. Артефакты

- EXCHANGE\OUTBOX\DS_079_report.md
- EXCHANGE\DS_CONTEXT.md (§9.5, только)
- temp\ds079_run.py (скрипт прогона DEPN, если создавался)