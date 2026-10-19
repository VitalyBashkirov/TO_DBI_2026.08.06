# -*- coding: utf-8 -*-
"""DS_152: запись сводного отчёта в EXCHANGE/OUTBOX/DS_152_summary_report.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "EXCHANGE" / "OUTBOX" / "DS_152_summary_report.md"

TEXT = """# DS_152: Сводный отчёт — покрытие К1–К4 и «Генерация тестовых .plp» по фильтрам рубрикаторов

**Дата:** 19.10.2026
**Автор:** DeepSeek (DS_152)
**Ветка:** `feature/dockerization`
**Базовый регресс:** 293 passed

## 1. Главная задача чата 43

Проверить, как GUI применяет фильтры **rules / priorities / categories / sources** из `v5.json` ко всем 4 источникам (`plpcheck`, `v53`, `тдс20240828`, `тклоик20240828`) на всех этапах:
- **К1** — «1. Сканировать» (`_run_scan`)
- **К2** — «2. Исправить код» (`fixer`)
- **К3** — «3. В Ai» (`send_to_ai`)
- **К4** — «4. Из Ai» (`receive_from_ai`)
- **Генерация** — «Генерация тестовых .plp» (`_run_test_generation` / `gen_test_plp.py`)

## 2. Матрица покрытия (К × фильтры)

| Кнопка / функция | sources | priorities | categories | rules (`matched_rules` / `rules_arg`) |
|---|---|---|---|---|
| **К1 (Сканировать)** | `test_ds144d_a_ast.py`, `test_ds147e_ast.py` | `test_ds144d_a_ast.py` (AST) | `test_ds144d_e_ast.py` (E2-фикс) | `test_ds152b_gui_matched_rules_ast.py` (AST) |
| **К2 (Исправить код)** | `test_ds144c_k1_k2_pytest.py` | `test_ds144d_a_ast.py` (AST) | `test_ds144d_e_ast.py` | `test_ds152b_gui_matched_rules_ast.py` (AST) |
| **К3 (В Ai)** | `test_ds152c_ai_k3k4_ast.py` (инвариант) | — (не применимо) | — (не применимо) | `test_ds152c_ai_k3k4_ast.py` (`_ai_rubricators`) |
| **К4 (Из Ai)** | `test_ds152c_ai_k3k4_ast.py` (инвариант) | — (не применимо) | — (не применимо) | — (не применимо) |
| **Генерация .plp** | `test_ds147d_ast.py`, `test_ds147e_ast.py` | `test_ds147a_ast.py` (парсинг) | `test_ds147d_ast.py` (hybrid A/B) | `test_ds152a_gen_rules_filter_ast.py` (`--rules` CSV, missing, empty) |

**Обозначения:**
- **sources** — фильтр по коду файла рубрикатора (`v53`/`PlpCheck`/`тдс`/`тклоик`), префиксная нормализация.
- **priorities** — фильтр по `rule.priority` (`HIGH`/`MEDIUM`/`LOW`) из `v5.json`.
- **categories** — фильтр по категории (7 агрегатов A + subcategory B), только для `plpcheck`.
- **rules** — прямой фильтр по коду правила (CSV в CLI `--rules`, `matched_rules` в GUI).

## 3. Ключевые инварианты (зафиксированы тестами)

### 3.1. К3/К4 не фильтруют по `selected_rules` напрямую
`send_to_ai` и `receive_from_ai` **не содержат** `self.selected_rules` в AST. Фильтрация правил происходит **только на этапе К1** (скан). Это гарантирует, что:
- К3 отправляет в AI **уже отфильтрованные** issue (результат `scan_results`).
- К4 применяет **все** фиксы из `AI_RESPONSE` (по `line_no` + `rule_code`), не сверяясь с `selected_rules`.

**Файл:** `SRC/tests/test_ds152c_ai_k3k4_ast.py` (2 AST-теста).

### 3.2. `_ai_rubricators` возвращает только активные коды
Для шапки `AI_REQUEST` (`- Рубрикатор:`) используются только те рубрикаторы, где `var.get() == True`.
**Файл:** `SRC/tests/test_ds152c_ai_k3k4_ast.py` (2 функциональных теста).

### 3.3. `--rules` в `gen_test_plp.py` — строгий CSV-фильтр
- `""` → `None` → все правила источника.
- `"a,b"` → ровно `a` и `b` (порядок сохраняется).
- `"a, b, ,c"` → пустые элементы отбрасываются.
- Несуществующий код → `[WARN]` + пропуск (не падение).

**Файл:** `SRC/tests/test_ds152a_gen_rules_filter_ast.py` (4 теста).

### 3.4. `matched_rules` — маппинг file_code → префиксы правил
`_get_rules_for_selected_files` использует словарь `file_prefixes` с ключами: `v53`, `v50`, `PlpCheck`, `тдс20240828`, `тклоик20240828`.
Fallback без рубрикатора → возврат кодов файлов (не правил).

**Файл:** `SRC/tests/test_ds152b_gui_matched_rules_ast.py` (5 тестов).

## 4. Что осталось за рамками DS_152 (пробелы)

| Область | Пробел | Приоритет |
|---|---|---|
| **К3 (send_to_ai)** | Нет функционального теста на `ai_exchange.write_request(...)` с полными `rubs` | Средний |
| **К2 (fixer)** | `priorities` покрыт только AST, нет функционального теста «HIGH/MEDIUM/LOW → фильтр правил» | Средний |
| **Генерация .plp** | `--priorities HIGH` не покрыт функционально | Низкий |
| **`tkloik`** | Всего 1 тест, нет теста на `categories` для `tkloik` | Низкий |

Эти пробелы **не блокируют** главную задачу: все 4 кнопки + генерация работают, фильтры применяются.

## 5. Итог DS_152 (a/b/c)

| Подшаг | Коммит | Тестов | Файл |
|---|---|---|---|
| **DS_152-a** | `c09f7ea` | 4 | `test_ds152a_gen_rules_filter_ast.py` |
| **DS_152-b** | `31dda8a` | 5 | `test_ds152b_gui_matched_rules_ast.py` |
| **DS_152-c** | `37f5af7` | 4 | `test_ds152c_ai_k3k4_ast.py` |
| **Итого** | — | **+13** | — |

**Базовый регресс до DS_152:** 276 passed.
**После DS_152:** 293 passed (+13 DS_152 + 4 DS_150 из чата 43).

## 6. Ссылки

- `SRC/gui_app.py` — `send_to_ai` (5563), `receive_from_ai` (5776), `_get_rules_for_selected_files` (2936), `_ai_rubricators` (5522), `_run_test_generation` (~4650).
- `tools/gen_test_plp.py` — CLI-генератор (DS_147a).
- `SRC/analyzer/test_generator_v2.py` — `TestGeneratorV2.select_rules`.
- `DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json` — 332 правила (plpcheck 152, v53 98, тдс 39, тклоик 43).
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(TEXT, encoding="utf-8")
print(f"OK: written {OUT} ({len(TEXT)} chars)")
