# DS_072b_Уточнение_A — INSERT_WITH_ID: корректная замена

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** уточнение
**Приоритет:** высокий
**Зависит от:** DS_072b
**Блокирует:** —

**См.:** `DS_STANDARD.md` (раздел 5, раздел 2), `DS_CONTEXT.md` (§2.1, §6, §7), `DS_FILES.md` (§6), `EXCHANGE\OUTBOX\DS_072b_report.md` (§6).

---

## 1. Цель

Исправить **некорректный `transform`** для правила `INSERT_WITH_ID`, добавленный в DS_072b.

**Проблема (DS_072b §6):**

- Реализовано: `txt_job_ref := ::[TEXT_JOBS]%insert(txt_job, txt_job%id);` → `txt_job_ref := insert into ::[TEXT_JOBS] t(t%id = txt_job%id, t%rowtype = txt_job%rowtype) return t into txt_job_ref;`
- **Синтаксически сломано:** `txt_job_ref := insert into ...` — **не PL/SQL**. Присваивание `:=` не работает с `insert`.

**Требование:** убрать `X := ` перед `insert`; заменить исходную конструкцию целиком.

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Правка `transform` для `INSERT_WITH_ID` |
| 2 | `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Синхронно (DS_065): `fix_instruction` |
| 3 | `EXCHANGE\DS_CONTEXT.md` | §2.1 / §9 — примечание DS_072b_Уточнение_A |
| 4 | `EXCHANGE\DS_FILES.md` | §6 / §9 — история |

---

## 3. Правильная замена

**Было (DS_072b — ошибочно):**

```plp
txt_job_ref := insert into ::[TEXT_JOBS] t(t%id = txt_job%id, t%rowtype = txt_job%rowtype) return t into txt_job_ref;
Стало (правильно):

plp
insert into ::[TEXT_JOBS] t(t%id = txt_job%id, t%rowtype = txt_job%rowtype) return t into txt_job_ref;
Изменения:

Удалить txt_job_ref := перед insert.

Сохранить return t into txt_job_ref (целевая переменная).

3.1. Regex-подход
Вариант A — расширить replace_scope до всей строки:

json
{
  "transform_type": "regex",
  "replace_scope": "line",
  "pattern": "^(\\s*)(\\w+)\\s*:=\\s*::\\[(\\w+)\\]%insert\\((\\w+),\\s*\\4%id\\)\\s*;",
  "replacement": "\\1insert into ::[\\3] t(t%id = \\4%id, t%rowtype = \\4%rowtype) return t into \\2;"
}
Ключевое: replace_scope: "line" (не "match"). Заменяется вся строка, а не только фрагмент.

Вариант B — если replace_scope: "line" не поддерживается:

Оставить replace_scope: "match", но добавить lookbehind для захвата X :=:

json
{
  "pattern": "(\\w+)\\s*:=\\s*::\\[(\\w+)\\]%insert\\((\\w+),\\s*\\3%id\\)",
  "replacement": "insert into ::[\\2] t(t%id = \\3%id, t%rowtype = \\3%rowtype) return t into \\1"
}
Вариант C — если ни A, ни B не работают:

Откатить transform, оставить ignore (детектор).

Правило: INSERT_WITH_ID — семантическое (требует структурного переноса).

Рекомендация: Вариант A (replace_scope: "line"). Если движок не поддерживает — B. Если и B не работает — C (ignore).

4. Тесты
Файл: temp\test_ds072b_a.py.

#	Вход	Ожидание
1	txt_job_ref := ::[TEXT_JOBS]%insert(txt_job, txt_job%id);	insert into ::[TEXT_JOBS] t(t%id = txt_job%id, t%rowtype = txt_job%rowtype) return t into txt_job_ref;
2	Негативный: txt_job_ref := insert into ...	не должно появляться
3	Негативный: %insert(obj) (1 параметр)	не менять
4	Негативный: %insert(obj, other%id)	не менять (второй параметр — не obj%id)
5	Негативный: %insert(obj, obj.field)	не менять
Регресс: DS_032–DS_072b PASSED.

5. Отчёт
Стандартный (DS_STANDARD.md → раздел 3). Дополнительно:

§6. До/после — INSERT_WITH_ID (корректно).

§7. Обоснование выбора regex-варианта (A/B/C).

6. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

KODA не создаёт в EXCHANGE\ новых каталогов, кроме регламентированных. Логирование — только в bot.log.

DATA\ — правка разрешена только для 5.RUBRICATOR_PARSER_SQL v5.json и 4.RUBRICATOR_PROMPT v5.json.

Синхронность — в оба JSON (DS_065).

Если корректная замена невозможна — выбрать Вариант C (ignore), не ломать SQL.

7. Артефакты
EXCHANGE\OUTBOX\DS_072b_Уточнение_A_report.md

temp\test_ds072b_a.py

temp\ds072b_a_run.py

DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json (обновлён)

DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json (обновлён)

EXCHANGE\DS_CONTEXT.md (v2.2)

EXCHANGE\DS_FILES.md (v1.4)

