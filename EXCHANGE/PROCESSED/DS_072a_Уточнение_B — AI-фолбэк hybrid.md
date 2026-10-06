# DS_072a_Уточнение_B — AI-фолбэк: hybrid

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** уточнение
**Приоритет:** средний
**Зависит от:** DS_072a
**Блокирует:** —

**См.:** `DS_STANDARD.md` (раздел 5, раздел 2), `DS_CONTEXT.md` (§2.1, §6, §7, §9), `DS_FILES.md` (§3, §5, §6), `EXCHANGE\OUTBOX\DS_072a_report.md` (§1, §4).

---

## 1. Цель

Уточнить механизм **AI-фолбэка** для правил `MAX_SIZE_ID` и `PLATFORM_INTEGER_MISMATCH`, добавленных в DS_072a.

**Проблема (из DS_072a §4):**
- В задании (DS_072a §3.2): `transform_type: "hybrid"` с `algorithmic_hint` + `fallback_instruction`.
- Фактически: `hybrid` **не поддерживается** `rule_engine._pattern_bucket` → правила уходят в `ignore`.
- Работает через `needs_ai_fix` (DS_054), но **не как `hybrid`**.

**Требование:** привести в соответствие — **либо** поддержать `hybrid`, **либо** явно зафиксировать упрощение.

---

## 2. Варианты решения

### Вариант 1 — Поддержать `hybrid` в `rule_engine._pattern_bucket`

**Что делать:**

- `SRC\rule_engine.py` → `_pattern_bucket`: добавить обработку `transform_type: "hybrid"`.
- Логика: если `transform_type == "hybrid"`:
  - сначала `transform` (regex);
  - если regex не сработал → `fallback_instruction` → `needs_ai_fix` (DS_054).
- Тесты: `temp\test_ds072a_b_hybrid.py`.

**Плюс:** полное соответствие DS_072a §3.2.
**Минус:** правка `rule_engine.py` (слой кода, не рубрикатор).

### Вариант 2 — Явно зафиксировать упрощение

**Что делать:**

- В `5.RUBRICATOR_PARSER_SQL v5.json` для `MAX_SIZE_ID` и `PLATFORM_INTEGER_MISMATCH`:
  - `transform_type: "ignore"` (вместо `hybrid`);
  - `note`: «AI-фолбэк через `needs_ai_fix` (DS_054); `hybrid` не поддерживается».
- В `DS_CONTEXT.md` §9.5 (или §2.1): зафиксировать факт.
- В `DS_FILES.md` §3: отметить.

**Плюс:** без правки кода, честно задокументировано.
**Минус:** `hybrid` остаётся нереализованным.

### Вариант 3 — Полноценный AI-фолбэк (крупная задача)

Отдельная DS_073 — реализация `hybrid` + интеграция с `ai_exchange.py`. Долго.

---

## 3. Рекомендация

**Вариант 2 — на текущий момент.**

**Обоснование:**

- `needs_ai_fix` (DS_054) уже работает — правила попадают в AI-очередь.
- `hybrid` — избыточно для 2 правил.
- Правка `rule_engine.py` (Вариант 1) — откладывается до DS_073+ (если появится потребность).

**Что сделать по Варианту 2:**

1. `5.RUBRICATOR_PARSER_SQL v5.json`:
   - для `MAX_SIZE_ID`, `PLATFORM_INTEGER_MISMATCH` — `transform_type: "ignore"`;
   - `note`: «AI-фолбэк через `needs_ai_fix` (DS_054); `hybrid` не поддерживается `_pattern_bucket`».
2. `4.RUBRICATOR_PROMPT v5.json` — синхронно `fix_instruction`.
3. `DS_CONTEXT.md` §9.5: «AI-фолбэк для MAX_SIZE_ID / PLATFORM_INTEGER_MISMATCH — через `needs_ai_fix`, `hybrid` не реализован».
4. `DS_FILES.md` §3: отметить.

---

## 4. Тесты

Файл: `temp\test_ds072a_b.py`.

| # | Что | Ожидание |
|---|-----|----------|
| 1 | `MAX_SIZE_ID` — regex сработал | автофикс (`[NUM10]` → `number`) |
| 2 | `MAX_SIZE_ID` — regex **не** сработал | `needs_ai_fix` = True (при `ai_fallback`) |
| 3 | `PLATFORM_INTEGER_MISMATCH` — API из списка | автофикс (`integer` → `number`) |
| 4 | `PLATFORM_INTEGER_MISMATCH` — API не из списка | `needs_ai_fix` = True |
| 5 | `transform_type` в JSON | `ignore` (не `hybrid`) |

**Регресс:** DS_032–DS_072a PASSED.

---

## 5. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3). Дополнительно:

- §6. До/после — JSON-фрагменты для 2 правил.
- §7. Фиксация в `DS_CONTEXT.md`.

---

## 6. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). Дополнительно:

- **KODA не создаёт в `EXCHANGE\` новых каталогов**, кроме регламентированных. Логирование — только в `bot.log`.
- `DATA\` — правка **разрешена только для `5.RUBRICATOR_PARSER_SQL v5.json` и `4.RUBRICATOR_PROMPT v5.json`**.
- Синхронность — **в оба** JSON (DS_065).
- `rule_engine.py` — **не трогать** (Вариант 2).

---

## 7. Артефакты

- `EXCHANGE\OUTBOX\DS_072a_Уточнение_B_report.md`
- `temp\test_ds072a_b.py`
- `temp\ds072a_b_run.py`
- `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` (обновлён)
- `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` (обновлён)
- `EXCHANGE\DS_CONTEXT.md` (v2.2)
- `EXCHANGE\DS_FILES.md` (v1.4)