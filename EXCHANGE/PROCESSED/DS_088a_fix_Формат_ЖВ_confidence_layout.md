# DS_088a_fix — Формат ЖВ + пороги confidence + layout

Дата: 30.09.2026 | Автор: DeepSeek | Исполнитель: KODA
Тип: доработка | Приоритет: средний
Зависит от: DS_088a, DS_088a_DIAG (разведка выполнена)
Блокирует: DS_088b
См.: DS_STANDARD.md (§2, §3, §5)

---

## 1. Цель

Три доработки к DS_088a:

A. **Формат прогресса в ЖВ** — вместо `batch n/N ids=[...]` выводить
   `Батч(10) X/Y: текущий — file.plp (ids=[...]: fixes=K время=...с conf=[...])`.

B. **Пороги confidence** — вынести в `SRC\settings.json`, читать из config
   в GUI, передавать в `ai_exchange.process_all_responses` через **сигнатуры**
   (логика `ai_exchange.py` не меняется). Добавить **два поля** на форму
   рядом с «Только Ai».

C. **Layout** — сдвинуть «Открыть рубикатор» / «Генерация тестовых .plp»
   правее; подфлаги «2. Рубикатор PlpCheck» — в **две колонки**;
   остальные элементы — поднять на освободившееся место.

**НЕ МЕНЯТЬ:** логику цикла (DS_088a), `send_to_ai`, воркеры, логику
`ai_exchange.py` (только сигнатуры).

**Разведка уже выполнена** (DS_088a_fix — INBOX, отчёт «Ожидание»).
Решения по развилкам:
- Mapping `id → source` — (B): id только в `AI_REQUEST_*.md` (`### Проблема N`),
  источник — `- Источник:` там же. **Запрос одно-файловый** — сценарий
  «разные файлы в батче» **не реализовывать**.
- Пороги confidence — (C): в `SRC\ai_exchange.py` (`CONF_AUTO=0.8`,
  `CONF_MEDIUM=0.5`, строки 59–60). **Разрешено (б):** `ai_exchange.py`
  получает пороги через **опциональные сигнатуры**, логика не меняется.
- Подфлаги PlpCheck — (A): статически, `PLPCHECK_CATEGORIES` (8) +
  «Выбрать все» = 9 чекбоксов, `pack` в одну колонку. Двухколоночная
  вёрстка — допустима.
- Признак fallback — найден: `... — fallback`, `fallback: split 10 -> 2`.

---

## 2. Что делать

### 2.1. Разведка (уточнить перед правкой)

| Что | Где |
|-----|-----|
| `_monitor_worker` | `SRC\gui_app.py` (DS_088a) |
| `_ai_batch_size` | `SRC\gui_app.py` (DS_088a) |
| `receive_from_ai` | `SRC\gui_app.py` |
| `process_all_responses` | `SRC\ai_exchange.py` |
| `apply_fixes` | `SRC\ai_exchange.py` |
| `CONF_AUTO` / `CONF_MEDIUM` | `SRC\ai_exchange.py:59–60` |
| `ai_only_var` (флаг «Только Ai») | `SRC\gui_app.py` — где в layout |
| `PLPCHECK_CATEGORIES` | `SRC\gui_app.py` — где цикл создания подфлагов |
| `SRC\settings.json` | есть ли ключи `conf_*` |

**Если `conf_*` уже есть в `settings.json`** — не дублировать, использовать.
**Если сигнатуры `process_all_responses` / `apply_fixes` не совпадают
с ожидаемыми** — СТОП, вопрос автору DS.

### 2.2. Формат ЖВ (часть A)

Парсить stdout воркера в `_monitor_worker`:

**Вход (stdout воркера):**
batch 1/1 ids=[1]: fixes=1 время=53.6с conf=[0.95]

text

**Выход (ЖВ):**
[HH:MM:SS] Батч(10) 1/1: текущий — file_abc.plp (ids=[1]: fixes=1 время=53.6с conf=[0.95])

text

Где:
- **`10`** — `batch_size` из `tools\ai_local_worker_config.json`;
- **`1/1`** — из `batch X/Y`;
- **`file_abc.plp`** — через mapping `id → source` (§2.3);
- **`(ids=[...]: fixes=K время=...с conf=[...])`** — из stdout как есть.

**Fallback:** определить по stdout (признак найден:
`... — fallback`, `fallback: split 10 -> 2`). Если найден — добавить
`(fallback 2×5)`.

**Не парсится** — писать строку как есть (fallback).

### 2.3. Mapping `id → source` (часть A)

**Запрос одно-файловый** (подтверждено разведкой).
Источник файла — из `AI_REQUEST_*.md`, строка `- Источник:`.

```python
# пример (точную структуру уточнить по факту):
# в AI_REQUEST_*.md:  - Источник: F:\...\file_abc.plp
source = extract_source_from_request_md(request_path)
Сценарий «несколько файлов в батче» не реализовывать.

2.4. Пороги confidence (часть B)
Решение: (б) — через сигнатуры.

Шаг 1. В SRC\settings.json в корень (плоско) добавить:

json
"conf_low": 0.5,
"conf_high": 0.8
Шаг 2. В SRC\ai_exchange.py — добавить опциональные параметры
в process_all_responses и apply_fixes:

python
# было:
def process_all_responses(...): ...
def apply_fixes(...): ...

# стало:
def process_all_responses(..., conf_low=CONF_MEDIUM, conf_high=CONF_AUTO): ...
def apply_fixes(..., conf_low=CONF_MEDIUM, conf_high=CONF_AUTO): ...
Логика НЕ меняется — только сигнатуры. Старые вызовы (без параметров)
работают с дефолтами.

Шаг 3. В SRC\gui_app.py receive_from_ai — читать из settings.json
и передавать:

python
conf_low = settings.get('conf_low', 0.5)
conf_high = settings.get('conf_high', 0.8)
ai_exchange.process_all_responses(..., conf_low=conf_low, conf_high=conf_high)
2.5. Форма: два поля + метка (часть B)
Рядом с флагом «Только Ai» (справа):

text
Пороги confidence:
< [0.5] — needs_manual
[0.5] – [0.8] — средняя
> [0.8] — авто
Два поля ввода (Entry, тип float), метка-подпись.

Tooltip:

«Порог confidence для авто-применения AI-фиксов. Фиксы с confidence ≥ этого значения применяются автоматически.»

Контроль диапазона: 0.0 ≤ x ≤ 1.0. При выходе — сообщение в ЖВ

возврат к предыдущему.

Запись в ЖВ при изменении:

text
[HH:MM:SS] Пороги confidence изменены: low=0.6, high=0.85
Сохранение — в SRC\settings.json (read-modify-write, как UI-флаги
DS_086).

2.6. Сдвиг кнопок (часть C)
«Открыть рубикатор» и «Генерация тестовых .plp» — сдвинуть правее
(освободить место под поля confidence).

2.7. Подфлаги «2. Рубикатор PlpCheck» — в две колонки (часть C)
Статически (подтверждено): PLPCHECK_CATEGORIES (8) +
«Выбрать все» = 9 чекбоксов, pack в одну колонку.

Переверстать в две колонки (grid с двумя колонками).

Элементы в две колонки: подфлаги «2. Рубикатор PlpCheck»
(«Выбрать все PlpCheck-категории», «PLSQL_OPTIMIZATION», «JAVA_OPTIMIZATION»,
«DBI_ADAPTATION», «SQL_CHECKS», «WEB_ADAPTATION», «STYLE.PREFIXES», …).

Поднять на освободившееся место:

«Фильтр по приоритету» (HIGH / MEDIUM / LOW);

«Флаги детерминированного фикса (DS_053)» (regex / hybrid / ai_fallback /
ignore / backup / other + «Имя дополнительного лога»).

3. Тесты
#	Тест	Ожидание
1	Формат ЖВ batch 1/5	Батч(10) 1/5: текущий — file.plp (ids=[...]: ...)
2	Fallback	строка содержит (fallback 2×5)
3	Mapping id → source	file.plp корректный (из - Источник:)
4	process_all_responses сигнатура	принимает conf_low / conf_high
5	apply_fixes сигнатура	принимает conf_low / conf_high
6	Пороги из config	receive_from_ai передаёт из settings.json
7	Обратная совместимость	старые вызовы работают (дефолты)
8	Поля confidence	2 поля на форме, рядом с «Только Ai»
9	Tooltip	при наведении — текст из §2.5
10	Контроль диапазона	ввод 1.5 → сообщение, откат
11	Запись в ЖВ	при изменении — строка
12	Сохранение	settings.json обновлён
13	Сдвиг кнопок	«Открыть рубикатор» / «Генерация тестовых .plp» — правее
14	Подфлаги в две колонки	визуально (9 чекбоксов)
15	Подъём элементов	«Фильтр по приоритету» + «Флаги DS_053» — выше
16	Регресс DS_086/087/088a	PASSED
4. Ограничения
Правка: SRC\gui_app.py, SRC\settings.json, SRC\ai_exchange.py
(только сигнатуры process_all_responses и apply_fixes —
логика не меняется).

НЕ МЕНЯТЬ: tools\ai_local_worker.py, tools\rule_based_fixer.py,
SRC\analyzer\, SRC\fixer\, SRC\rule_engine.py.

Логи: EXCHANGE\bot.log + ЖВ. temp\ — можно.

GIT — НЕ КОММИТИТЬ.

5. Отчёт (OUTBOX\DS_088a_fix_report.md)
Разведка уже выполнена (см. предыдущий отчёт). В этом отчёте — реализация:

5.1. Формат ЖВ — примеры (вход/выход).
5.2. Mapping id → source — как реализовано.
5.3. Fallback — как.
5.4. Пороги — settings.json + сигнатуры ai_exchange.py + проброс в GUI.
5.5. Обратная совместимость — проверка старых вызовов.
5.6. Поля confidence — расположение, tooltip, контроль диапазона.
5.7. Сдвиг кнопок + подфлаги в две колонки + подъём.
5.8. Тесты 1–16 — PASSED/FAILED.
5.9. Расхождения / стоп.

6. Артефакты
SRC\gui_app.py (правка)

SRC\settings.json (правка)

SRC\ai_exchange.py (правка — только сигнатуры)

EXCHANGE\OUTBOX\DS_088a_fix_report.md
