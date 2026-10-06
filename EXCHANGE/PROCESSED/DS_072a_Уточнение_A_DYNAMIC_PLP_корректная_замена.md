# DS_072a_Уточнение_A — DYNAMIC_PLP: корректная замена

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** уточнение
**Приоритет:** высокий
**Зависит от:** DS_072a
**Блокирует:** —

**См.:** `DS_STANDARD.md` (раздел 5 — шаблон реализации, раздел 2 — ограничения), `DS_CONTEXT.md` (§2.1, §6, §7), `DS_FILES.md` (§6), `EXCHANGE\OUTBOX\DS_072a_report.md` (§4, §6, §7).

---

## 1. Цель

Исправить **некорректный `transform`** для правила `DYNAMIC_PLP`, добавленный в DS_072a.

**Проблема (из DS_072a §4, §6):**
- Реализовано обобщение `rownum < N` → `fetch N-1` для **любого** `N`.
- Пример из §6: `... where rownum < 2 into ...` → `... where fetch 1 into ...` — **синтаксически сломано** (`where fetch 1 into` — не SQL).
- Замена выходит за рамки DS_071 §7.2: там было только `rownum < 2` → `fetch 1`.

**Требование:** откатить обобщение, оставить **только** `rownum < 2` → `fetch 1`, синтаксически корректно.

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Правка `transform` для `DYNAMIC_PLP` |
| 2 | `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Синхронно (DS_065): `fix_instruction` для `DYNAMIC_PLP` |
| 3 | `EXCHANGE\DS_CONTEXT.md` | §2.1 / §9 — примечание DS_072a_Уточнение_A |
| 4 | `EXCHANGE\DS_FILES.md` | §6 / §9 — история |

---

## 3. Детали реализации

### 3.1. Было (DS_072a — ошибочно)

Regex: `rownum\s*<\s*(\d+)` → `fetch (\1-1)` — **обобщение**, **синтаксически сломано**.

### 3.2. Стало (правильно)

**Только** конкретный случай: `where rownum < 2` → `fetch 1`.

Regex (пример — уточнить по эталону):

```json
{
  "transform_type": "regex",
  "pattern": "where\\s+rownum\\s*<\\s*2\\b",
  "replacement": "",
  "post_action": "append_fetch_1"
}
Синтаксис:

Было: select ... where rownum < 2 into ...

Стало: select ... fetch 1 into ...

Или, если regex не справляется с переносом fetch в конец SELECT, — два варианта:

Вариант A (простой regex):

json
{
  "transform_type": "regex",
  "pattern": "rownum\\s*<\\s*2\\b",
  "replacement": "1 = 1",
  "note": "Заменить 'rownum < 2' на '1 = 1'; затем вручную добавить fetch 1 перед into"
}
Вариант B (перенести в ignore):

Если regex не даёт корректной замены в одну строку — откатить transform, оставить правило детектором (как rownum в DBI.ADAPTATION, DS_071 §7.3 категория E).

Рекомендация: Вариант B. DYNAMIC_PLP изначально классифицирован как A (простой), но фактически — не простой (нужен структурный перенос fetch). Возврат в E (детектор) — безопаснее, чем ломать SQL.

3.3. Убрать обобщение
Из PARSER_SQL:

удалить обобщённый паттерн rownum\s*<\s*(\d+) → fetch (\1-1);

не добавлять ничего нового для DYNAMIC_PLP, если выбран §3.2 вариант B.

4. Тесты
Файл: temp\test_ds072a_a.py.

#	Вход	Ожидание
1	PLP_N('select x(x.[DOCUMENT_NUM]) in ::[MAIN_DOCUM] all where rownum < 2 into Result;')	PLP_N('select x(x.[DOCUMENT_NUM]) in ::[MAIN_DOCUM] all fetch 1 into Result;') ИЛИ без изменений (вариант B)
2	rownum < 5	не менять (нет замены)
3	rownum = 1	не менять
4	where rownum < 2 and x = 1	не менять (сложный контекст)
Регресс: DS_032–DS_072a PASSED.

5. Отчёт
Стандартный (DS_STANDARD.md → раздел 3). Дополнительно:

§6. До/после — DYNAMIC_PLP.

§7. Обоснование выбора варианта (A или B).

6. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

KODA не создаёт в EXCHANGE\ новых каталогов, кроме регламентированных. Логирование — только в bot.log.

DATA\ — правка разрешена только для 5.RUBRICATOR_PARSER_SQL v5.json и 4.RUBRICATOR_PROMPT v5.json.

Синхронность — в оба JSON (DS_065).

Если при реализации выявится, что корректная замена невозможна в одну строку — выбрать вариант B (ignore), не ломать SQL.

7. Артефакты
EXCHANGE\OUTBOX\DS_072a_Уточнение_A_report.md

temp\test_ds072a_a.py

temp\ds072a_a_run.py

DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json (обновлён)

DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json (обновлён)

EXCHANGE\DS_CONTEXT.md (v2.2)

EXCHANGE\DS_FILES.md (v1.4)