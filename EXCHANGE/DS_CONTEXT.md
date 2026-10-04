# DS_CONTEXT — Общий контекст проекта

**Назначение:** факты, используемые в нескольких DS.
**Версия:** 3.0 от 02.10.2026 (после DS_078–DS_089b: AI-контур, Continue, GUI «Исправить код»).

---

## 1. Вендорские эталоны

### 1.1. `_is_in_comment_or_string` — эталона нет

Проверены: PROMPT v5.json, PARSER_SQL v5.json (87 правил), материалы курса PLPlus, rule-description.html (PlpCheck 2.5.2), v53.docx, тклоик.docx, Приложения 2.3.docx. **Алгоритм — собственный.**

Детали: `OUTBOX\DS_056_report.md`, `DS_056A` (закрыт).

### 1.2. `&debug(...)` — макро-подстановка

Не SQL*Plus-переменная. После раскрытия — вызов процедуры. Внутри `'...'` — литералы. Спец-обработка — `PLPlusFixer._update_renamed_vars`.

---

## 2. Рубрикатор

### 2.1. Файлы

| Файл | Назначение | Правил |
|------|-----------|--------|
| `DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json` | Правила v5.3.0 + **309 regex-паттернов сканера** | 332 |
| `DATA\Рубрикатор v5\5.RUBRICATOR_PARSER_SQL v5.json` | Трансформации | **148** |
| `DATA\Рубрикатор v5\1.RUBRICATOR_FILES v5.md` | Список правил (read-only) | — |
| `DATA\CFT Platform IDE Documentation\rule-description.html` | PlpCheck 2.5.2 | — |

**Правки regex — в оба файла** (DS_065).

### 2.2. PlpCheck-аудит (DS_071–DS_072e)

**74/74 NAME** зафиксированы в PARSER_SQL: **20 transform + 54 ignore/AI**.

Группы: A (10), B (5), C (19), D (15), E (24). Ключевое:

- **DS_072a_Уточнение_B:** `hybrid` не поддерживается `_pattern_bucket`; `MAX_SIZE_ID`/`PLATFORM_INTEGER_MISMATCH` → `ignore` + `needs_ai_fix`.
- **DS_072c:** 4 multiline-правила (`NOT_CLOSED_CURSOR`, `NOT_CLOSED_FILE`, `NOT_HANDLED_CURSOR_EXCEPTIONS`, `OBLIGATORY_IN_OTHERS`).
- **DS_073:** `apply_fix_multiline` в `_apply_issue_fixes` (первый проход).
- **DS_072e:** группа E — 24 детектора без автофикса.

### 2.3. Префиксы `rule_code`

`v53.` / `тдс20240828.` / `тклоик20240828.` / `plpcheck.` (PlpCheck 2.5.2).

### 2.4. Категории PlpCheck

Маппинг — `SRC\analyzer\scanner.py`: `PLPCHECK_RULE_TO_CATEGORY`, `PLPCHECK_CATEGORIES`. См. DS_065.

---

## 3. GUI

### 3.1. Ключевые факты

- `settings.json`: `rubricator_selected_rules`, `report_stats_min_files` (DS_058, DS_075).
- `_save_rubricator_state` (`gui_app.py:1889–1945`), `_on_rule_click` (838–858), `_load_rubricator_files` (765–791).

### 3.2. GUI «Исправить код» (DS_086–DS_089b)

Кнопки:
1. Сканировать] [2. Исправить код] [3. В AI]

text

| Состояние | Активна | Надпись |
|-----------|---------|---------|
| Старт / поля заполнены | 1. Сканировать | жирная |
| После скана | 2. Исправить код | жирная |
| После фикса | 3. В AI | жирная |

- **Скрыто** (DS_086): «Показывать SQL», «Сформировать задание», «От AI».
- **Прогресс-бар** (DS_088): для «3. В AI».
- **«Прервать / Продолжить»** (DS_089): пауза операций 1/2/3.
- Детали DS_089b: `OUTBOX\DS_089b_report.md`.

---

## 4. Соглашения по коду

- Python — UTF-8 без BOM.
- OUTBOX — CRLF.
- bot.log — UTF-8 без BOM, `[ДД.ММ.ГГГГ ЧЧ:ММ:СС] DS XXX: <итог>`.

---

## 5. История решений (DS_078–DS_089b)

### AI-контур

| DS | Что | Метрика |
|----|-----|---------|
| DS_078 | Разведка AI | 8933 issues |
| DS_079 | Фильтр `ignore_set` + галка «Только AI» | 8933 → 301 |
| DS_080 | Фильтр `remaining_by_rule` + `only_ai` | 5067 → 96 |
| DS_081 | Rescan + `needs_manual` | — |
| DS_082a | Rule-based fixer | 96 → 35 |
| DS_082b | Local AI worker (Ollama) | 61 fix, 37 мин |
| DS_083a | Разбор 9 skipped (A=0, C=9) | — |
| DS_083b | Разведка правил v2 (отложено) | 0 %/28 %/0 % |
| DS_084 | `merge_fixes_by_line` | 9 → 1 |
| DS_085 | Batch 10 + fallback (2×5) | 37 → ~28 мин |

### GUI

| DS | Что |
|----|-----|
| DS_086 | Разведка GUI + скрытие элементов |
| DS_087 | Переименование + логика 1→2→3 |
| DS_088 | «3. В AI»: ai_local_worker, прогресс, AI_IN_PROCESSED |
| DS_089 | «Прервать / Продолжить» |
| DS_089b | Доработка (см. отчёт) |

---

## 6. Маппинг кодов PlpCheck

`SRC\rule_engine.py:_resolve_code`:
plpcheck.<NAME> → PlpCheck.<CAT>.<NAME>.п.<N>

text

Применён в `has_rule`, `get_rule`, `rule_buckets`, `apply_fix`. Фолбэк `BAD_PREFIX → PREFIX_TYPE` (DS_059). `_pattern_bucket` не поддерживает `hybrid` — паттерн без `transform` → `ignore`.

---

## 7. Regex — особенности

`sql_parser.py` — глобальный `IGNORECASE`; локально `(?-i)`; регистронезависимый lookahead `(?i:...)`. Два источника паттернов (PROMPT + PARSER_SQL) — синхронизировать.

---

## 8. Форматы отчётов

### 8.1. scan_report_*.md

Колонки: №, CLASS_ID, SHORT_NAME, SECTION, LINE, CHECK, LEVEL, TYPE, ERROR, PLAN.

**Счётчики** (DS_075):
Прогноз исправлений: X
Исправлено: Y
В AI: Z

text

**Метрики файлов** (DS_076):
Всего файлов: T
Файлов с проблемами: P
Файлов с изменениями: C

text

При дублях — `Всего проблем (с дублями): N` (DS_077). Топ-файлы (DS_075) — при `log_level=Подробный` и `T ≥ report_stats_min_files`.

### 8.2. scan_VVxVVx_*.md

PLAN (LINE, AUTO, ДЕЙСТВИЕ), «Прогноз» по всем строкам-мишеням, цепочка правил, единая позиция `>`, МКР = max(len(код_правила)) + 1. Приоритет удаления (DS_067_A). Сортировка (line, `not_mentioned` первым, алфавит check).

---

## 9. AI-контур

### 9.1. Полный цикл (PSH_DEP_PRIV_GO)
5067 issues
↓ детерминированный фиксер
195 fix, 76 правил остаток
↓ DS_080 «Только AI»
96 issues
↓ DS_082a rule-based
35 fix + 61 → AI
↓ DS_082b + DS_085 (batch 10 + fallback)
61 fix, ~28 мин
↓ DS_084 merge
~60 applied
↓ DS_081 rescan + needs_manual
1 needs_manual

text

**Автопокрытие:** 95/96 = **99 %**. **Время:** ~28 мин на файл (CPU).

### 9.2. Модели

| Модель | Провайдер | Роль | Порт |
|--------|-----------|------|------|
| `deepseek-coder:6.7b` | Ollama | **AI-фиксы** | 11434 |
| `qwen2.5-coder:7b` | Ollama | **Continue: chat/edit/apply** | 11434 |
| `qwen2.5-coder:1.5b-base` | Ollama | **Continue: autocomplete** | 11434 |
| `nomic-embed-text:latest` | Ollama | **Continue: embed** | 11434 |
| `llama-3.1-8b`, `deepseek-r1-distill-qwen-7b` | LM Studio | Резерв | 1234 |

**LM Studio + Ollama — не одновременно** (RAM).

### 9.3. Критерий AI-отбора

Issue → AI_IN, если:

1. правило в PARSER_SQL имеет `transform_type == "ignore"` (маппинг через `_resolve_code`);
2. правило **не исчезло** после `_apply_issue_fixes` — `remaining_by_rule[rule_code]` содержит **все** исходные строки.

**Over-include** — безопасно (фикс смещает строки; точное совпадение теряет до 80 %).

`remaining_by_rule` — в `_verify_file` → `fixer.verify_stats` → `scan_results` (только после «Исправить код»).

**Fallback:** пуст → `ignore_set` + `bot.log` «needs_ai_fix недоступен».

**Галка «Только AI»:** ВКЛ → фильтр; ВЫКЛ → все issues.

### 9.4. Компоненты

| # | Файл | Роль |
|---|------|------|
| 1 | `tools\rule_based_fixer.py` | Rule-based фиксер (7 правил) |
| 2 | `tools\rule_based_rules.json` | Конфиг правил |
| 3 | `tools\ai_local_worker.py` | AI worker (batch 10 + fallback 2×5) |
| 4 | `tools\ai_local_worker_config.json` | Конфиг (model, batch, num_ctx=4096) |
| 5 | `SRC\ai_exchange.py` | Обмен AI_IN/AI_OUT |

### 9.5. Continue + Ollama (инструмент разработки)

**Continue** — AI в VS Code (Chat/Edit/Autocomplete/Embed), локально через Ollama.

**Конфиги:**

- `~/.continue/config.yaml` — модели;
- `F:\TO_DBI\.continue\rules\agents-short.md` — **рабочее правило**;
- `F:\TO_DBI\AGENTS_SHORT.md` — **эталон** (git);
- `F:\TO_DBI\AGENTS.md` — **полный** (для KODA).

**Модели:** `qwen2.5-coder:7b` (chat, 8192), `qwen2.5-coder:1.5b-base` (autocomplete, 2048), `nomic-embed-text` (embed).

**Правило `agents-short.md`:** ~500 токенов (вместо ~4500 из полного `AGENTS.md`) — устраняет `Message exceeds context limit`.

**Секция `rules` в `config.yaml` — устаревшая, не работает.** Правила — только через `.continue/rules/*.md`.

---

## 10. prefix_type_in_var_name — алгоритм (DS_066)

**Правило:** `PlpCheck.STYLE.PREFIX_TYPE_IN_VAR_NAME.п.4.4` — `transform_type: "ignore"`.

**Формат:** `v_<тип><CamelCase>`.

| Тип | Префикс | Пример |
|-----|---------|--------|
| ref | r | `P_PARAM ref [...]` → `v_rParam` |
| varchar2 | v | `vDateRep` → `v_vDateRep` |
| `[STRING_*]` | s | `P_FILE_XML` → `v_sFile_Xml` |

**Отличие от bad_prefix:** формат без `_` (`v_iDp`) — DS_063. Форматы не унифицируются.
## DS_090 — Live-прогон CLI (PSH_DEP_PRIV_GO)
**Статус:** ЧАСТИЧНО | **Дата:** 02.10.2026 18:30
**Результат:** Rule-based 70 fixes / 62 skip (0.4 сек). AI batch 5: 35 fixes (112 сек).
~28 мин/файл — ЧАСТИЧНО подтверждён (13 сек/fix для batch 5).
Resume CLI: НЕдоступен (GUI-only).
**СТОП-развилки:** сканер не CLI, resume не в i_local_worker.py.
**Отчёт:** EXCHANGE\OUTBOX\DS_090_report.md
**Следующие шаги:** DS_091 (--skip-rule), DS_092 (resume CLI), DS_093 (validate_batch), DS_094 (GUI-прогон)

