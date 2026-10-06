# DS_073 — Интеграция apply_fix_multiline в code_fixer

**Дата:** 23.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** высокий
**Зависит от:** DS_072c_Реализация
**Блокирует:** DS_072d_Реализация

**См.:** `DS_STANDARD.md` (раздел 5, раздел 2), `DS_CONTEXT.md` (§2.1, §6, §7, §9), `DS_FILES.md` (§2, §3, §6), `AGENTS.md` (раздел «Логирование»), `EXCHANGE\OUTBOX\DS_072c_Реализация_report.md` (§4, §8).

---

## 1. Цель

**Подключить** `apply_fix_multiline` (реализован в DS_072c) в прод-фиксер `code_fixer.py`, чтобы **заработали** 4 multiline-правила группы C + 3 ожидаемых группы D.

**Проблема (DS_072c_Реализация §4):**
- `apply_fix_multiline` — реализован в `sql_parser.py` + `RuleEngine`.
- Но `code_fixer.py:_apply_issue_fixes` вызывает **построчный** `apply_fix` — multiline-паттерны **пропускаются**.
- **Результат:** 4 правила C2 (`NOT_CLOSED_CURSOR`, `NOT_CLOSED_FILE`, `NOT_HANDLED_CURSOR_EXCEPTIONS`, `OBLIGATORY_IN_OTHERS`) **не автофиксятся** в GUI.

**Требование:** в `_apply_issue_fixes` — **вызов** `apply_fix_multiline` **до** построчного `apply_fix`, чтобы multiline-правила срабатывали.

---

## 2. Что менять

| # | Файл | Что |
|---|------|-----|
| 1 | `SRC\fixer\code_fixer.py` | `_apply_issue_fixes` — интеграция `apply_fix_multiline` |
| 2 | `EXCHANGE\DS_CONTEXT.md` | §2.1, §9 — обновить (после закрытия) |
| 3 | `EXCHANGE\DS_FILES.md` | §3, §9 — обновить |

**Не трогать:**
- `SRC\analyzer\scanner.py` — не требуется.
- `SRC\rule_engine.py` — `apply_fix_multiline` уже есть.
- `SRC\analyzer\sql_parser.py` — уже есть.
- `gui_app.py`.
- Рубрикаторы.

---

## 3. Детали реализации

### 3.1. Где вызывать

В `code_fixer.py` → `PLPlusFixer._apply_issue_fixes` — **основной цикл** фиксера. Перед построчным `apply_fix` проверить:

- **bucket** правила — если в `rule_buckets[rule_code]` есть `"multiline"`, — вызвать `apply_fix_multiline`.
- Иначе — построчный `apply_fix` (как сейчас).

### 3.2. Как вызывать

```python
result = self.rule_engine.apply_fix_multiline(
    text=block_text,          # текст блока (не одна строка)
    rule_code=issue.issue_type,
    flags=self.flags,
)
if result:
    new_text, bucket, kind = result
    # применить new_text к блоку
else:
    # fallback — построчный apply_fix
Ключевое: text= — не одна строка, а блок (например, содержимое begin…end или весь файл — на усмотрение KODA, с обоснованием).

3.3. Как определить block_text
Вариант A (простой): весь файл (source_text) — если multiline-паттерн найдётся где угодно, заменить.

Вариант B (точный): блок вокруг issue — по block_start / block_end (DS_069) или эвристике.

Вариант C (гибрид): если Issue.block_start/block_end — использовать; иначе — весь файл.

Рекомендация: Вариант C — использует block_start/block_end (уже есть в Issue после DS_069), fallback — весь файл.

3.4. Порядок применения
Сначала multiline-правила.

Потом построчные (apply_fix).

Иначе: построчный apply_fix может «испортить» строку до multiline.

3.5. Идемпотентность
После multiline-замены — не применять построчный apply_fix к той же issue (правило уже исправлено).

Пометить issue как обработанную.

4. Тесты
4.1. Позитивные
temp\test_ds073.py:

#	NAME	Вход	Ожидание
1	NOT_CLOSED_CURSOR	vcur.open; begin null; end;	vcur.open; begin null; vcur.close(); end;
2	NOT_CLOSED_FILE	iFile := stdio.f_open(...); begin null; end;	…; begin null; stdio.f_close(iFile); end;
3	NOT_HANDLED_CURSOR_EXCEPTIONS	vcur.open; begin null; exception when others then vcur.close(); end;	…; begin null; vcur.close(); exception when others then vcur.close(); end;
4	OBLIGATORY_IN_OTHERS	execute is begin [NUM] := P_NUM; exception when others then ...	… begin &sp(SET); [NUM] := P_NUM; …
4.2. Негативные / регресс
#	Что	Ожидание
5	Построчные правила (A, B) — не затронуты	PASSED
6	apply_fix_multiline на не-multiline правило	не сработало, fallback — построчный
7	Регресс DS_032–DS_072d_Разведка	PASSED
4.3. Регресс
Все тесты DS_032–DS_072d_Разведка — PASSED.

5. Отчёт
Стандартный (DS_STANDARD.md → раздел 3). Дополнительно:

§6. До/после — 4 multiline-правила.

§7. Актуализация тестов.

§8. Как встроено в _apply_issue_fixes — схема.

6. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

KODA не создаёт в EXCHANGE\ новых каталогов, кроме регламентированных (INBOX, OUTBOX, PROCESSED, bot.log).

bot.log — только EXCHANGE\bot.log. Запись в SRC\bot.log, SRC\*.log, EXCHANGE\LOG\* — запрещена (этап 6 DS_072c, AGENTS.md).

Запись в temp\ — разрешена.

SRC\fixer\code_fixer.py — разрешён для этой задачи.

DATA\ — НЕ ТРОГАТЬ (рубрикаторы уже готовы, DS_072c).

Не трогать scanner.py, rule_engine.py, sql_parser.py, gui_app.py.

Если интеграция требует правок вне code_fixer.py — остановиться, доложить автору DS.

Если multiline-замена ломает существующие тесты — откатить, доложить.

7. Артефакты
EXCHANGE\OUTBOX\DS_073_report.md

temp\test_ds073.py

temp\ds073_run.py

SRC\fixer\code_fixer.py (обновлён)

EXCHANGE\DS_CONTEXT.md (v2.5)

EXCHANGE\DS_FILES.md (v1.7)