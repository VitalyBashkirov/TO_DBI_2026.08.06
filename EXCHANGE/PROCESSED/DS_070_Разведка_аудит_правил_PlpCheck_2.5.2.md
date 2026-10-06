# DS_070 — Разведка: аудит правил PlpCheck 2.5.2

**Дата:** 22.09.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** разведка
**Приоритет:** средний
**Зависит от:** DS_069
**Блокирует:** DS_071+

**См.:** `DS_STANDARD.md` (раздел 4 — шаблон разведки, раздел 2 — ограничения), `DS_CONTEXT.md` (§2.2, §6), `DS_FILES.md` (§2, §5, §6).

---

## 1. Цель

Сверить полный список правил PlpCheck 2.5.2 (html) с текущим состоянием рубрикаторов и маппингов. Определить:

1. Какие правила `plpcheck.<NAME>` есть в html, но **отсутствуют** у нас.
2. Какие есть **частично** (паттерн есть, `note` неполный, категория не та).
3. Какие категории PlpCheck не покрыты.
4. Приоритет добавления — по группам.

Разведка — **без правок исходников и рубрикаторов**.

---

## 2. Что искать

### 2.1. Источник — html (единственный)

```text
DATA\CFT Platform IDE Documentation\ide_dbi_project\20260922\rule-description-11310065634873899272.html
Формат ключей: class="type-badge" + onclick="filterBy('<KEY>', event)" (rubr-key отсутствует).

Перед парсингом — зафиксировать:

Метрика	Как получить
Размер (байт)	(Get-Item $f).Length
Дата модификации	(Get-Item $f).LastWriteTime
MD5	Get-FileHash $f -Algorithm MD5
check-card	(Select-String $f 'class="check-card"').Count
check-code	(Select-String $f 'class="check-code"').Count
type-badge	(Select-String $f 'type-badge').Count
Эти значения — в §7.1 отчёта.

Извлечь по каждому правилу:

Поле	Где в html
check-code	<span class="check-code">
check-title	<span class="check-title">
Категории (теги)	<span class="type-badge ..." onclick="filterBy('KEY', event)">
Требование Oracle	<div class="alert-box alert-warning" data-restriction-key="oracle">
Метод проверки	<div class="method-block">
Пример ошибки / исправления	<div class="code-comparison">
Комментарий-исключение	<div class="alert-box alert-info"> (если есть)
2.2. Наши источники
Что	Где
Паттерны сканера (regex)	DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json
Трансформации	DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json
Категории GUI	SRC\analyzer\scanner.py — PLPCHECK_CATEGORIES
Маппинг rule → category	SRC\analyzer\scanner.py — PLPCHECK_RULE_TO_CATEGORY
Маппинг кода PlpCheck	SRC\rule_engine.py — _resolve_code
Список правил (read-only)	DATA\Рубрикатор v5\1.RUBRICATOR_FILES v5.md
2.3. Что собрать
#	Что	Формат
1	Полный список plpcheck.<NAME> из html	NAME, TITLE, CATEGORY(JAVA/PLSQL/DBI/WEB/STYLE/SQL), ORACLE_REQUIRED
2	Сверка с PLPCHECK_CATEGORIES	NAME отсутствуют / лишние
3	Сверка с PLPCHECK_RULE_TO_CATEGORY	NAME отсутствуют / лишние
4	Сверка с _resolve_code	NAME отсутствуют в маппинге
5	Сверка с 4.RUBRICATOR_PROMPT v5.json	есть ли паттерн (regex)
6	Сверка с 5.RUBRICATOR_PARSER_SQL v5.json	есть ли transform
7	Группировка по приоритету	высокий / средний / низкий (§4)
Результат — в двух форматах:

temp\ds070_plpcheck_audit.csv — для просмотра;

temp\ds070_plpcheck_audit.json — для машинной обработки (DS_071+).

3. Воспроизвести
#	Что	Как
1	Парсинг html	Все <details class="check-card">
2	Извлечение check-code	По <span class="check-code">
3	Извлечение категорий	По <span class="type-badge ... onclick="filterBy('KEY')">
4	Проверка вхождения в JSON	grep_search по plpcheck.<NAME>
5	Проверка в маппингах	grep_search по PLPCHECK_CATEGORIES, PLPCHECK_RULE_TO_CATEGORY, _resolve_code
6	Сводная таблица	temp\ds070_plpcheck_audit.csv + .json
Чтение html — только:

powershell
Get-Content -Raw -Encoding UTF8 "<путь>"
# или
[System.IO.File]::ReadAllText("<путь>", [System.Text.Encoding]::UTF8)
Запись — только в temp\.

4. Критерии приоритета
Приоритет	Критерий
Высокий	Тег DBI и паттерн отсутствует в рубрикаторе
Средний	Тег JAVA/PLSQL и паттерн отсутствует или есть, но note/категория неполные
Низкий	Тег WEB/STYLE или правило есть, но неполное (только note)
5. Зафиксировать
Факты — пути, строки, имена правил, категории.

Diff — если что-то менялось (не должно).

MD5 — 4.RUBRICATOR_PROMPT, 5.RUBRICATOR_PARSER_SQL, html-источника.

Артефакты — temp\ds070_plpcheck_audit.csv, temp\ds070_plpcheck_audit.json.

6. Восстановить
Разведка read-only. Если что-то менялось — восстановить.

7. Отчёт
Стандартный (DS_STANDARD.md → раздел 3) + дополнительные разделы:

7.1. Источник и сводка
Источник: <путь>
MD5: <md5>
Размер: <N> байт
Дата модификации: <дата>
check-card: <N> check-code: <N> type-badge: <N>

Метрика	Значение
Всего правил в html	N
Есть в PLPCHECK_CATEGORIES	N₁
Есть в PLPCHECK_RULE_TO_CATEGORY	N₂
Есть в _resolve_code	N₃
Есть паттерн в 4.RUBRICATOR_PROMPT	N₄
Есть transform в 5.RUBRICATOR_PARSER_SQL	N₅
Отсутствуют полностью	N₆
7.2. Таблица «правило — категория — есть/нет — приоритет»
NAME	TITLE	CAT	ORACLE	PATTERN	TRANSFORM	CATEGORIES	RULE_TO_CAT	RESOLVE_CODE	Приоритет
…	…	…	…	…	…	…	…	…	…
7.3. Группы по приоритету
Высокий: список NAME.

Средний: список NAME.

Низкий: список NAME.

7.4. Категории PlpCheck — сверка
Категория	Есть в html	Есть в PLPCHECK_CATEGORIES	Комментарий
…	…	…	…
7.5. Рекомендация
Один абзац: что добавить в первую очередь, какие категории дополнить. Разбить на DS_071+ по группам.

7.6. Прочее
Если источник — 152 правила (а не 284) — зафиксировать факт.

Если ide_dbi_project\rule-description\rule-description.html идентичен по MD5 — зафиксировать.

8. Ограничения
Стандартные (DS_STANDARD.md → раздел 2). Дополнительно:

DATA\ — строго read-only. Любая запись — только в temp\.
Запрещено по путям DATA\*: Set-Content, Out-File, Remove-Item,
Move-Item, New-Item, Copy-Item (в DATA\).

Исходный html читать только через Get-Content -Raw -Encoding UTF8
или [System.IO.File]::ReadAllText(...).

Рубрикаторы (4.RUBRICATOR_PROMPT v5.json, 5.RUBRICATOR_PARSER_SQL v5.json) не менять.

Временные файлы — только в temp\.

Если при разведке выявится расхождение с DS_CONTEXT.md §2.2 / §6 — доложить автору DS.

9. Артефакты
EXCHANGE\OUTBOX\DS_070_report.md

temp\ds070_plpcheck_audit.csv

temp\ds070_plpcheck_audit.json

temp\ds070_run.py