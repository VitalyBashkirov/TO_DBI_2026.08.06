# DS_072b — Реализация: transform для группы B (5 правил)

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** высокий
**Зависит от:** DS_072a, DS_072a_Уточнение_A, DS_072a_Уточнение_B
**Блокирует:** DS_072c

**См.:** `DS_STANDARD.md` (раздел 5 — шаблон реализации, раздел 2 — ограничения), `DS_CONTEXT.md` (§2.1, §6, §7), `DS_FILES.md` (§6), `EXCHANGE\OUTBOX\DS_071_report.md` (§7.2, §7.3, §7.5).

---

## 1. Цель

Добавить **структурный `transform`** (в пределах строки, с контекстом) для 5 правил категории B из DS_071 §7.3.

| # | NAME | Замена (было → стало) |
|---|------|-----------------------|
| 1 | `ALIAS_COLUMN_VIEW` | Добавить алиас колонке в SELECT представления (`view X { select ... }`) |
| 2 | `INSERT_WITH_ID` | `%insert(obj, obj%id)` → `insert into ::[TBP] ... return ... into ref` |
| 3 | `MULTIPLE_MODIFIERS` | `%parent%state` → промежуточная переменная или `%parent(::[TYPE])%state` |
| 4 | `REFERENCED_TO_OBJECT` | `x.[OBJ_REF]` → `cast_to(::[REFERENCE], x.[OBJ_CLASS]\|\|':' \|\| x.[OBJ_REF])` |
| 5 | `SELECTLOCKWAIT` | `lock wait N` → `lock one by one` (или убрать `wait`) |

**Структурный transform** — замена в пределах строки, но с контекстом (lookahead/lookbehind, замена фрагмента). Эталоны: `WRONG_METHOD_SYNTAX` (DS_065), `PREFIX_TYPE_IN_VAR_NAME` (DS_066).

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Добавить `transform` для 5 NAME (`transform_type: "regex"`) |
| 2 | `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Синхронно (DS_065): `note` / `fix_instruction` для 5 NAME |
| 3 | `EXCHANGE\DS_CONTEXT.md` | §2.1, §9 — обновить |
| 4 | `EXCHANGE\DS_FILES.md` | §6, §9 — обновить |

**Синхронность (DS_065):** правки regex — **в оба** JSON.

---

## 3. Детали реализации

### 3.1. Формат `transform`

По образцу DS_059/DS_063/DS_065/DS_066. Пример:

```json
{
  "code": "PlpCheck.DBI.ADAPTATION.ALIAS_COLUMN_VIEW.п.X.Y",
  "transform_type": "regex",
  "transform": {
    "pattern": "...",
    "replacement": "...",
    "flags": "g"
  },
  "note": "..."
}
Точный формат — брать по эталонам WRONG_METHOD_SYNTAX, PREFIX_TYPE_IN_VAR_NAME.

3.2. По каждому правилу
3.2.1. ALIAS_COLUMN_VIEW
Семантика (html PlpCheck 2.5.2): в расширениях представлений — если у колонки нет алиаса, ширина колонок «слетает».

Сложность: добавление алиаса требует знания имени колонки. В общем случае — невозможно без метаданных.

Вариант A (простой): если колонка — известный реквизит [ATTR], добавить AS ATTR:

regex
(?<=\[)(\w+)(?=\])   →   \1 as \1
Вариант B (ignore): если regex не даёт однозначной замены → ignore (детектор).

Рекомендация: Вариант B — правило детекторное, семантика требует модели. Оставить ignore (в категории E, а не B).

Вердикт: исключить из DS_072b, перенести в ignore.

3.2.2. INSERT_WITH_ID
Семантика: %insert(obj, obj%id) → insert into ::[TBP] ... return ... into ref.

Сложность: структурная замена, но ограниченная конкретной конструкцией.

Regex:

regex
(\w+)\s*:=\s*::\[(\w+)\]%insert\((\w+),\s*\3%id\)
Replacement:

text
insert into ::[\2] t(t%id = \3%id, t%rowtype = \3%rowtype) return t into \1
Ограничение: только %insert(obj, obj%id) (2 параметра, второй — %id). Остальные — ignore.

Вердикт: оставить в DS_072b (структурный, regex возможен).

3.2.3. MULTIPLE_MODIFIERS
Семантика: %parent%state → промежуточная переменная или %parent(::[TYPE])%state.

Сложность: замена требует знания типа %parent.

Вариант A: x%parent%state → x%parent(::[TYPE])%state — но TYPE неизвестен.

Вариант B: ignore — детектор.

Рекомендация: Вариант B — правило семантическое, regex не даёт однозначной замены.

Вердикт: исключить из DS_072b, перенести в ignore.

3.2.4. REFERENCED_TO_OBJECT
Семантика: x.[OBJ_REF] → cast_to(::[REFERENCE], x.[OBJ_CLASS]||':'||x.[OBJ_REF]).

Сложность: требует наличия x.[OBJ_CLASS] — не всегда есть.

Regex (в view main):

regex
(?<=select\s)(\w+)\.\[(\w+)\]\s*:\s*(\w+_REF)\b
Replacement:

text
cast_to(::[REFERENCE], \1.[\2_CLASS]||':'||\1.[\2]) : \3
Ограничение: если [\2_CLASS] отсутствует — ignore.

Вердикт: оставить в DS_072b — но с fallback.

3.2.5. SELECTLOCKWAIT
Семантика: lock wait N → в PG нет wait.

Regex:

regex
lock\s+wait\s+\d+
Replacement:

text
lock one by one
Вердикт: оставить в DS_072b — простая структурная замена.

3.3. Итоговый состав DS_072b
После отсева (2 правила в ignore):

#	NAME	Категория
1	INSERT_WITH_ID	B (regex)
2	REFERENCED_TO_OBJECT	B (regex + fallback)
3	SELECTLOCKWAIT	B (regex)
Отсеяны в ignore:

ALIAS_COLUMN_VIEW — семантическое (нужны метаданные).

MULTIPLE_MODIFIERS — семантическое (нужен тип).

Всего: 3 правила в DS_072b.

4. Тесты
Файл: temp\test_ds072b.py.

#	NAME	Вход	Выход
1	INSERT_WITH_ID	txt_job_ref := ::[TEXT_JOBS]%insert(txt_job, txt_job%id);	insert into ::[TEXT_JOBS] t(t%id = txt_job%id, t%rowtype = txt_job%rowtype) return t into txt_job_ref;
2	REFERENCED_TO_OBJECT	select x(x.[OBJ_REF] : C_OBJ_REF) in ::[TBP]	select x(cast_to(::[REFERENCE], x.[OBJ_CLASS]||':' || x.[OBJ_REF]) : C_OBJ_REF) in ::[TBP]
3	SELECTLOCKWAIT	... in ::[MAIN_DOCUM] lock wait 5	... in ::[MAIN_DOCUM] lock one by one
4	INSERT_WITH_ID — негативный	%insert(obj) (1 параметр)	не менять
5	REFERENCED_TO_OBJECT — негативный	x.[OBJ_REF] без OBJ_CLASS	не менять
6	SELECTLOCKWAIT — негативный	lock one by one	не менять
Регресс: DS_032–DS_072a_Уточнение_B PASSED.

5. Прогнать регресс
Все тесты DS_032–DS_072a_Уточнение_B PASSED.

6. Отчёт
Стандартный (DS_STANDARD.md → раздел 3). Дополнительно:

§6. До/после — по 3 правилам.

§7. Актуализация тестов — если регресс требует правок.

§8. Отсев ALIAS_COLUMN_VIEW, MULTIPLE_MODIFIERS → ignore — обоснование.

7. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

KODA не создаёт в EXCHANGE\ новых каталогов, кроме регламентированных (INBOX, OUTBOX, PROCESSED, bot.log). Логирование — только в EXCHANGE\bot.log.

Запись в temp\ — разрешена.

DATA\ — правка разрешена только для 5.RUBRICATOR_PARSER_SQL v5.json и 4.RUBRICATOR_PROMPT v5.json.

Синхронность regex — в оба JSON (DS_065).

Не трогать scanner.py, code_fixer.py, gui_app.py.

Если при реализации выявится, что INSERT_WITH_ID, REFERENCED_TO_OBJECT или SELECTLOCKWAIT не дают однозначной замены в одну строку — перенести в ignore, не ломать SQL.

8. Артефакты
EXCHANGE\OUTBOX\DS_072b_report.md

temp\test_ds072b.py

temp\ds072b_run.py

DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json (обновлён)

DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json (обновлён)

EXCHANGE\DS_CONTEXT.md (v2.2)

EXCHANGE\DS_FILES.md (v1.4)