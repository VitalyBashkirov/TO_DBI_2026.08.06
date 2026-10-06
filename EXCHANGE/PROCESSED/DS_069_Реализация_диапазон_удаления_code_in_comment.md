# DS_069 — Реализация: диапазон удаления для code_in_comment

**Дата:** 22.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** средний
**Зависит от:** DS_068 (разведка)
**Блокирует:** —

**См.:** `DS_STANDARD.md` (раздел 5 — шаблон реализации, раздел 2 — ограничения), `DS_CONTEXT.md` (§8.2, §9.5), `DS_FILES.md` (§2, §3), отчёт `DS_068_report.md`.

---

## 1. Цель

Закрыть §9.5 `DS_CONTEXT.md` (диапазон удаления): заменить заглушку `(удалить строку)` для `code_in_comment` на `(удалить диапазон строк N–M)` при многострочном блоке.

Основание — DS_068 §6.3, вариант 1 (поля `block_start`/`block_end` в `Issue`).

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `SRC\analyzer\scanner.py` | `Issue` (dataclass, ~427–448): добавить поля `block_start: int = 0`, `block_end: int = 0` |
| 2 | `SRC\analyzer\scanner.py` | `_check_plp_code_in_comment` (~1130–1194): возвращать `block_start`/`block_end` (6-ка вместо 4-ки) |
| 3 | `SRC\analyzer\scanner.py` | `scan_file`: принять 6-ку, записать в `Issue.block_start` / `Issue.block_end` |
| 4 | `SRC\fixer\code_fixer.py` | `save_scan_only_log` (~2380): вместо `(удалить строку)` — `(удалить диапазон строк N–M)` при `block_start != block_end`; иначе `(удалить строку)` |
| 5 | `EXCHANGE\DS_CONTEXT.md` | §9.5: перенести пункт «Диапазон удаления» в ЗАКРЫТО |
| 6 | `EXCHANGE\DS_FILES.md` | §2 (`Issue`), §3 (`save_scan_only_log`), §9 (история) — обновить |

---

## 3. Детали реализации

### 3.1. `Issue` (scanner.py)

Добавить после `match_fragment` (по образцу DS_064_A):

```python
block_start: int = 0
block_end: int = 0
0 = диапазон не задан (не code_in_comment).

3.2. _check_plp_code_in_comment (scanner.py)
Возвращать 6-ку: (opener_line, msg, orig, block_start, block_end), где:

block_start = opener_line;

block_end = строка закрывающего */ (или последняя строка файла при незакрытом блоке — см. §3.4).

При репорте issue — заполнять block_start/block_end.

3.3. save_scan_only_log (code_fixer.py)
В ветке вывода итогового текста для code_in_comment:

python
if issue.issue_type == 'code_in_comment' and issue.block_end > issue.block_start:
    final_text = f'(удалить диапазон строк {issue.block_start}–{issue.block_end})'
else:
    final_text = '(удалить строку)'
Символ – (U+2013, en dash) — как в DS_067 §5.2.

3.4. Незакрытый блок (новое, по решению автора DS)
Сейчас _check_plp_code_in_comment при незакрытом блоке (/* без */ до EOF) не репортит issue (DS_068 §6.2, крайний случай 1).

Требование: репортить issue с block_end = len(lines) (последняя строка файла). В save_scan_only_log — (удалить диапазон строк N–M) (т.к. block_end > block_start).

Если block_start == block_end == EOF (блок из одной строки, незакрытый) — (удалить строку).

4. Тесты
Файл: temp\test_ds069_fixes.py. Кейсы:

#	Кейс	Ожидание
1	Многострочный блок /* … */ (99–121)	(удалить диапазон строк 99–121)
2	Однострочный блок /* x := 1; */	(удалить строку)
3	Незакрытый блок /* … EOF	issue репортится, (удалить диапазон строк N–M)
4	Вложенный /* /* */	opener, диапазон до первого */
5	---комментарий (не блок)	(удалить строку) (без изменений)
6	PLAN: code_in_comment — приоритет удаления (DS_067_A)	одна строка, (удалить диапазон строк N–M)
7	Регресс DS_067 (15/15)	PASSED
8	Регресс DS_067_A (15/15)	PASSED
9	Регресс DS_067_B (7/7)	PASSED
10	Регресс DS_066 (13/13)	PASSED
11	Регресс DS_056 (15/15)	PASSED
12	Регресс DS_064_A (5/5)	PASSED
13	Регресс DS_065 (7/7)	PASSED
5. Прогнать регресс
Все тесты DS_032–DS_068 не должны сломаться.

6. Отчёт
Стандартный (DS_STANDARD.md → раздел 3). Дополнительно:

§6. До/после — пример на REPS_EXP_115_1 (строка 99 /** /).

§7. Актуализация тестов — если регресс-тесты DS_067/DS_067_A требуют правок (при изменении формата).

7. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

Менять только: SRC\analyzer\scanner.py, SRC\fixer\code_fixer.py, EXCHANGE\DS_CONTEXT.md, EXCHANGE\DS_FILES.md.

Тесты — только в temp\.

gui_app.py, оба JSON (4.RUBRICATOR_PROMPT, 5.RUBRICATOR_PARSER_SQL) — не трогать.

AI-пометку — не трогать (решение DS_068 §6.3: оставить как есть).

Если при реализации выявится расхождение с DS_068 — остановиться, доложить автору DS.

8. Артефакты
EXCHANGE\OUTBOX\DS_069_report.md

temp\test_ds069_fixes.py, temp\ds069_run.py

EXCHANGE\DS_CONTEXT.md (v2.2), EXCHANGE\DS_FILES.md (v1.4)