# DS_147 — Генерация тестовых .plp (TestGeneratorV2)

**Дата:** 2026-10-14
**Ветка:** feature/dockerization
**Статус:** закрыт

---

## 1. Цель

Создать инструмент генерации тестовых `.plp`-файлов с известным набором ошибок/паттернов для проверки:
- PLPlusScanner (регресс-тесты);
- фиксера K2;
- AI-контура K3/K4;
- демо/обучения.

---

## 2. Что сделано

### 2.1. Модуль TestGeneratorV2

Файл: `SRC/analyzer/test_generator_v2.py` (~15830 B, BOM=False).

Класс `TestGeneratorV2`:
- источник правил: `DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json` (332 правила);
- фильтры: `sources` (plpcheck/v53/тдс20240828/тклоик20240828), `priorities` (HIGH/MEDIUM/LOW);
- `categories` — ОТКЛЮЧЁН (маппинг PLPCHECK_CATEGORIES <-> subcategory отсутствует);
- режимы: `single` (один сводный файл) и `per-rule` (по файлу на правило);
- схема имён single: `test_<src>_<prio>_<cat>_<sel|all>_single_<YYYYMMDD_HHMMSS>.plp`;
- схема имён per-rule: `test_<safe_name>_<YYYYMMDD_HHMMSS>.plp`.

### 2.2. Тесты

Файл: `SRC/tests/test_ds147_gen_v2.py` (16 тестов).

Покрытие:
- импорт, конструктор, загрузка правил;
- фильтры sources/priorities/combo;
- safe_name (транслит);
- generate single / per-rule;
- single: PUBLIC PROCEDURE, нет дубля -- Правило:;
- procedure: нет begin внутри [+];
- meta: -- Теги: есть;
- BOM=False.

Регресс: **197 passed** (181 старых + 16 новых).

### 2.3. GUI-интеграция

Файл: `SRC/gui_app.py` (~349912 B).

Метод `_run_test_generation` делегирует в `TestGeneratorV2.generate(...)`:
- `selected_file_codes` -> `sources`;
- `_selected_priorities` -> `priorities`;
- `mode=single`;
- `out_dir=DATA/Тестовые файлы`.

Удалён блок инлайн-генерации (строки 4658-4874).

### 2.4. Стандарт

Файл: `EXCHANGE/DS_STANDARD.md` (+4678 B).

Добавлены параграфы:
- §6.6.28 — TestGeneratorV2;
- §6.6.29 — уроки PS here-string + Python;
- §6.6.30 — _split_declare (begin/end/declare);
- §6.6.31 — pytest Test* class: __test__ = False.

---

## 3. Артефакты

| Файл | Размер | BOM |
|------|--------|-----|
| `SRC/analyzer/test_generator_v2.py` | ~15830 B | False |
| `SRC/tests/test_ds147_gen_v2.py` | ~6800 B | False |
| `SRC/gui_app.py` | ~349912 B | False |
| `EXCHANGE/DS_STANDARD.md` | 67768 B | False |

---

## 4. Открытые вопросы

1. **`categories` отключён** — маппинг PLPCHECK_CATEGORIES (9 категорий из scanner.py) <-> subcategory в v5.json не найден. Фильтр по категориям — ответственность GUI перед вызовом generate().
2. **`PRIORITY_RULES`** содержит v53.* и тдс/тклоик, но НЕ содержит plpcheck.* в полном объёме (частично). GUI-фильтр приоритетов покрывает не все plpcheck-правила.
3. **`_run_test_generation_legacy`** (gui_app.py, 4893+) — мёртвый код, не вызывается. Оставлен.
4. **Старые генераторы** — `test_generator.py`, `test_generator_v50.py`, `generate_comprehensive_test.py` — исторические, не используются. Требуют решения: удалить или оставить.
5. **Валидация через PLPlusScanner** — отдельный DS (не входит в DS_147).
6. **CLI** — не сделан, только библиотека + GUI. Отдельный DS.

---

## 5. Рекомендации

1. **DS_147a** — CLI `tools/gen_test_plp.py`:
   - `--rules <code1,code2>` / `--all` / `--source plpcheck,v53` / `--priority HIGH,MEDIUM`;
   - `--mode single|per-rule`;
   - `--out <dir>`;
   - `--validate` (прогон PLPlusScanner, проверка ожидаемых ошибок).
2. **DS_147b** — валидация через PLPlusScanner:
   - после генерации прогнать сканер;
   - сверить найденные ошибки с ожидаемыми (rule_code).
3. **DS_147c** — `PRIORITY_RULES` для plpcheck:
   - дополнить `rubricator_priority_mapping.py`;
   - или перейти на `rule.priority` из v5.json.
4. **DS_147d** — маппинг PLPCHECK_CATEGORIES <-> subcategory:
   - таблица явных соответствий;
   - включить фильтр `categories` в `TestGeneratorV2`.

---

## 6. Коммиты

(заполняется при git commit)

---

## 7. Приложение — пример сгенерированного файла

Создан `DATA/Тестовые файлы/test_all_all_all_sel_single_20261014_171233.plp` (130 правил, v53 + тдс + тклоик).

Структура секции (эталон TestDeepSeek.plp):
- шапка: `-- Правило:`, `-- Описание:`, `-- Категория:`, `-- Подкатегория:`, `-- Приоритет:`, `-- Теги:`;
- блок JSON: `documentation_text`, `code_example_bad`, `code_example_good`, `fix_instruction`, `regex_patterns.for_search`;
- `PUBLIC PROCEDURE <safe_name> IS ... BEGIN ... BEGIN ... savepoint sp1; debug_pipe(...); -- [-] НЕПРАВИЛЬНО ... -- [+] ПРАВИЛЬНО ... RAISE; EXCEPTION WHEN OTHERS THEN ... ROLLBACK TO sp1; END; END;`.

