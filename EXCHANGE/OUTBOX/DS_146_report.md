# DS_146 — DeepScanner удалён из GUI (отчёт)

**Дата:** 2026-10-14
**Автор:** DeepSeek (DS_146), пользователь Vitaly
**Ветка:** feature/dockerization
**Коммиты:** 5483ba2 (N3b), _TBD_ (N3c)
**Статус:** закрыт

---

## 1. Резюме

`DeepScanner` (кнопка/пункт меню «Сканировать. Алгоритм Deep», Ctrl+F5)
**удалён из GUI**. Причина: разведка показала, что это **не «глубокий»
алгоритм**, а **обёртка над `PLPlusScanner`** с **legacy-рубрикатором**
(`1.RUBRICATOR_FILES.md` + `3.RUBRICATOR_FIXES.md`), отличным от основного
пайплайна (`4.RUBRICATOR_PROMPT v5.json`).

В GUI DeepScan давал **тот же результат**, что и К1 «Сканировать» —
параметр `deep_mode` в `_run_scan` не использовался (§6.6.24).

Решение (вариант C+D): убрать из GUI, оставить как **CLI-инструмент** для
сравнительного анализа рубрикаторов.

---

## 2. Разведка (N2) — паспорт DeepScanner

### 2.1 Структура модуля

`SRC/analyzer/deep_scanner.py` (~660 строк, 36549 B до правок).

Класс `DeepScanner` — 19 методов:

| Группа | Методы |
|--------|--------|
| Логирование/UI (9) | `log`, `log_deep_think`, `_log_separator`, `set_progress`, `set_status`, `_default_log`, `_default_progress`, `_default_status` |
| Рубрикатор legacy (6) | `_load_rubricator_files`, `_load_rubricator_fixes`, `_parse_rule_code`, `_generate_default_rules`, `_is_rule_selected`, `load_rubricator` |
| Сопоставление правил (2) | `_get_pattern_for_rule`, `_get_selected_patterns` |
| Обработка файла (1) | `scan_file_with_details` |
| Точка входа (1) | `run` |

### 2.2 Ключевые факты

1. **DeepScanner НЕ сканирует сам.** В `run()` (строка ~491–551):
   - импорт `PLPlusScanner`;
   - создание `PLPlusScanner(config, list(patterns.keys()))`;
   - ручное навешивание `scanner.PATTERNS = patterns`;
   - вызов `scanner.scan_file(plp_file)` для каждого файла.

2. **Не «глубокий» алгоритм.** Никакого AST, цепочек вызовов,
   контекстных зависимостей. `scan_file_with_details` — тонкая обёртка
   над `scanner.scan_file()` + один дополнительный date-паттерн.

3. **Legacy-рубрикатор.** `_load_rubricator_files` читает
   `1.RUBRICATOR_FILES.md`, `_load_rubricator_fixes` — `3.RUBRICATOR_FIXES.md`.
   Основной пайплайн GUI использует `4.RUBRICATOR_PROMPT v5.json` (v5.3.0, 332 правила).

4. **Свой формат отчёта.** `logs_Deep/Deep_scan_report_<source>_<ts>.md` —
   простой MD (заголовок, дата, список `- file:line`). **Несовместим** с
   отчётом `PLPlusScanner.generate_report()` → K2 (fixer) его не распарсит.

5. **`logs_Deep/` (50+ файлов)** — от CLI-прогонов. В GUI DeepScan не вызывался.

6. **`_generate_default_rules`** — захардкоженный фолбэк, если legacy-рубрикатор
   не найден. Отдельная тема (не в этом DS).

### 2.3 Отличия от PLPlusScanner

| Аспект | PLPlusScanner | DeepScanner |
|--------|---------------|-------------|
| Сканирование | сам | вызывает PLPlusScanner |
| Рубрикатор | v5.json (332 правила) | legacy .md |
| Формат отчёта | `generate_report()` (HTML/MD с планом) | простой MD |
| AST/контекст | нет | **нет** (вопреки названию «Deep») |
| Применение | GUI основной | CLI сравнительный |

---

## 3. Решение (вариант C+D)

Vitaly (чат 36): **убрать из GUI, оставить как CLI**.

Обоснование:
- Deep не даёт «глубины» — только другой рубрикатор;
- в GUI `deep_mode` не использовался;
- пункт меню + Ctrl+F5 вводили в заблуждение;
- `logs_Deep/` подтверждает: Deep применялся как CLI;
- ценность — сравнительный анализ рубрикаторов.

---

## 4. Что сделано

### 4.1 N3a-fix — удаление UI

- `gui_app.py` — удалены:
  - пункт меню «Сканировать. Алгоритм Deep» (строка 444);
  - bind `<Control-F5>` (строка 462);
  - метод `start_deep_scan` (строки 4018..4042, 25 строк).
- `_run_scan` / `start_scan` — **не тронуты**.
- Параметр `deep_mode` — оставлен (по п.2(i)).
- Строки 1145, 2947 (кнопка «DeepScan» в отчётах) — **не тронуты**.

**Первый подход (N3a) сломал файл:** `str.replace(anchor + "\n", "")` на CRLF
оставил `\r`, удвоил отступы → `IndentationError`. **N3a-fix** переделан через
`splitlines(keepends=True)` — см. §6.6.27.

### 4.2 N3b — docstring + §6.6.26/§6.6.27

- `gui_app.py` — docstring `_run_scan` обновлён (упоминание DS_146, CLI, legacy).
- `deep_scanner.py` — шапка docstring: «CLI-only, не в GUI, legacy-рубрикатор».
- `DS_STANDARD.md` — добавлены:
  - **§6.6.26** — DS_146: DeepScanner удалён из GUI;
  - **§6.6.27** — CRLF-safe правки .py через `splitlines`.
- **Коммит 1:** 5483ba2, 3 файла, +65/−38.

### 4.3 N3c — тесты + отчёт

- `SRC/tests/test_ds146_deep_scan_removed_pytest.py` — 12 AST-only проверок.
- `EXCHANGE/OUTBOX/DS_146_report.md` — этот отчёт.
- **Коммит 2:** _TBD_.

---

## 5. Изменённые файлы

| Файл | Было (B) | Стало (B) | Δ |
|------|----------|-----------|---|
| `SRC/gui_app.py` | 357231 | ~355700 | ~−1500 |
| `SRC/analyzer/deep_scanner.py` | 36549 | 36950 | +401 |
| `EXCHANGE/DS_STANDARD.md` | 60363 | 61877 | +1514 |
| `SRC/tests/test_ds146_..._pytest.py` | — | новый | +~170 строк |
| `EXCHANGE/OUTBOX/DS_146_report.md` | — | новый | — |

---

## 6. Тесты

Новый файл: `test_ds146_deep_scan_removed_pytest.py` — 12 проверок:

1. AST: нет `FunctionDef` `start_deep_scan`.
2. AST: нет `Attribute` `start_deep_scan`.
3. AST: нет строкового литерала `'<Control-F5>'`.
4. AST: нет строкового литерала с `'Алгоритм Deep'`.
5. AST: `def start_scan` — 1.
6. AST: `def _run_scan` — 1.
7. AST: `def start_fix` — 1.
8. AST: `_run_scan` сохраняет параметр `deep_mode` (default=False).
9. `DeepScanner` импортируется, `run` существует.
10. AST: `deep_scanner.py` импортирует `PLPlusScanner`.
11. `DS_STANDARD.md` содержит §6.6.26 и §6.6.27.
12. Smoke: `DeepScanner.run()` на пустом каталоге — не падает.

**Важно:** проверки **AST-only** — не зависят от упоминаний `start_deep_scan`
в docstring. См. §6.6.27.

Регресс: 169 (было) + 12 (DS_146) = **~181 passed**.

---

## 7. Ссылки

- **§6.6.24** — историческая постановка (DS_145, чат 35).
- **§6.6.26** — DS_146: DeepScanner удалён из GUI.
- **§6.6.27** — CRLF-safe правки .py через `splitlines`.
- **DS_145** — фильтр временных имён в `deep_scanner.py` (чат 35).
- **`analyzer/deep_scanner.py`** — CLI-инструмент (сохранён).

---

## 8. Открытые вопросы / замечания

1. **`_generate_default_rules`** — захардкоженный фолбэк в DeepScanner.
   Если legacy-рубрикатор не найден, Deep генерирует правила «по памяти».
   Возможно, **отдельный DS** (но не в этом чате).

2. **Legacy-рубрикатор** (`1.RUBRICATOR_FILES.md` + `3.RUBRICATOR_FIXES.md`) —
   поддерживается ли он ещё? Если нет — Deep станет неактуален.
   Возможно, **отдельный DS**.

3. **`deep_scanner.py` и DS_145** — фильтр временных имён (`is_temporary_filename`)
   сохранён. Работает в CLI.

---

**Итог:** DeepScanner убран из GUI как вводящая в заблуждение функция.
Оставлен как CLI-инструмент. Документация (§6.6.26, §6.6.27) обновлена.