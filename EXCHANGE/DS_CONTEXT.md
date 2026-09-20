# DS_CONTEXT — Общий контекст проекта

**Назначение:** факты, которые используются в нескольких DS. Ссылаться вместо повторения в каждой задаче.

---

## 1. Вендорские эталоны

### 1.1. `_is_in_comment_or_string` — эталон отсутствует

Проверенные источники:

- `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` — только коды проверок.
- `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` — 87 правил трансформации, алгоритма нет.
- `DATA\CFT Platform IDE Documentation\Программирование_PLPlus_Материалы_курса.doc` — «`--` до конца строки; `/* */` между символами».
- `DATA\CFT Platform IDE Documentation\rule-description.html` (PlpCheck 2.5.2) — требование «не анализировать код в комментариях», алгоритма нет.
- `DATA\CFT Platform IDE Documentation\Рекомендации по адаптации...v53.docx` — `&` — макрос; `"` внутри `'...'` — не терминатор.
- `DATA\CFT Platform IDE Documentation\тклоик20240828...docx` — стиль кода.
- `DATA\CFT Platform IDE Documentation\CFT Platform IDE. Приложения 2.3.docx` — грамматика `str ::= 'character_sequence'` не описывает `''` и q-quoting.

**Вывод:** алгоритм — собственный, на основе синтаксиса PL/SQL/PLPlus и поведения PlpCheck.
**Детали:** `EXCHANGE\OUTBOX\DS_056_report.md`, `DS_056A` (закрыт).

### 1.2. `&debug(...)` — макро-подстановка

- Не SQL*Plus-переменная.
- После раскрытия — обычный вызов процедуры.
- Переменные внутри `'...'` — литералы; спец-обработка только `PLPlusFixer._update_renamed_vars` (см. `DOCUMENTATION_ARM.md` 212, 246).

---

## 2. Структура рубрикатора

### 2.1. Файлы

| Файл | Назначение | Правил |
|------|-----------|--------|
| `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Правила проверок v5.3.0 | 332 |
| `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Парсер (трансформации) | 75 |
| `DATA\Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил с признаками | — |
| `DATA\CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2 | — |

### 2.2. Префиксы `rule_code`

| Префикс | Источник |
|---------|----------|
| `v53.` | `4.RUBRICATOR_PROMPT v5.json` |
| `тдс20240828.` | `тдс20240828.Требования...` |
| `тклоик20240828.` | `тклоик20240828.Требования...` |
| `plpcheck.` | `rule-description.html` (PlpCheck 2.5.2) |

### 2.3. Формат `1.RUBRICATOR_FILES v5.md`

- Строки вида `|N|±|rule_code|...`.
- Признак `+` — включено, `−` (U+2212, **не** U+00B1) — выключено.
- **`1.RUBRICATOR_FILES v5.md` — read-only для GUI.** Состояние чекбоксов хранится в `settings.json`.

---

## 3. GUI

### 3.1. Ключевые факты (из DS_058-разведки)

- Пишет в рубрикатор: `_save_rubricator_state` (`SRC\gui_app.py:1889–1945`), вызывается из `save_settings()` (1887) по `on_close` (3845) или Ctrl+S.
- Клик по чекбоксу (`_on_rule_click`, 838–858) — только `rules_changed = True`.
- Чтение: `_load_rubricator_files` (765–791), используется в `_populate_rules_tree`.
- `settings.json` — нет ключа для чекбоксов рубрикатора (добавляется в DS_058+DS_057).

### 3.2. Схема `settings.json` (согласовано)

```json
{
  "rubricator_selected_rules": {
    "v53.rule_code_1": true,
    "тдс20240828.DML_JOIN.стр.1": true,
    "plpcheck.CODE_IN_COMMENT": false
  }
}
```

- Формат: словарь `{"<rule_code>": true|false}`.
- Идемпотентен.
- Начальное состояние (нет ключа): прочитать `1.RUBRICATOR_FILES v5.md`, сохранить в `settings.json` (вариант C).
- Новые правила: дополнять со значением `false`, сохраняя существующие.

---

## 4. Соглашения по коду

- Python — UTF-8 без BOM.
- OUTBOX — CRLF.
- `bot.log` — UTF-8 без BOM, формат `[ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <итог>`.
- Стиль логов и отчётов — русский, формальный.

---

## 5. История ключевых решений

| Дата | Решение | Обоснование |
|------|---------|-------------|
| 19.09.2026 | DS_056B отменён | Вендорского эталона нет, все источники проверены |
| 19.09.2026 | DS_056A — разделение `is_in_comment_or_string` / `advance_lexer_state` | Многократный вызов для одной строки требует чистоты функции |
| 19.09.2026 | DS_058+DS_057 объединены | Одна область кода (`gui_app.py`) |
| 19.09.2026 | `1.RUBRICATOR_FILES v5.md` — read-only для GUI | Баг `−`→`+`; состояние в `settings.json` |
| 19.09.2026 | Бот `exchange_bot.py` отключён. Перенос файлов — вручную (DS_049). | Бот не запущен (нет процесса, автозапуска). KODA работает без него. Раздел DS_048 удалён из `AGENTS.md`. |