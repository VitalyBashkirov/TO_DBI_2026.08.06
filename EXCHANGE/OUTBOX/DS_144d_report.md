# DS_144d — Отчёт: тестирование АРМа по параметрам рубрикаторов (вариант B)

**Дата:** 2026-10-19
**Ветка:** feature/dockerization
**Автор DS:** DeepSeek
**Статус:** ЗАКРЫТ (a–e), 276 passed

## 1. Контекст

DS_144d (вариант B) — проверка того, как GUI применяет фильтры рубрикатора
(rules / priorities / categories / sources из v5.json) ко всем 4 источникам
(plpcheck / v53 / тдс20240828 / тклоик20240828).

Базовая линия: 257 passed. Итог: 276 passed (+19 тестов, 5 коммитов).

## 2. Под-шаги

### DS_144d-a — аудит фильтров (коммит 42f9b26)

- GUI `_run_test_generation` передаёт 4 фильтра в TestGeneratorV2:
  `sources=selected_file_codes`, `priorities=_selected_priorities`,
  `categories=plpcheck_categories_filter`, `rules` (через matched_rules).
- `TestGeneratorV2._passes_filters` обрабатывает `self.sources`, `self.priorities`, `self.categories`.
- `categories` — гибрид A (`PLPCHECK_RULE_TO_CATEGORY`, 7 агрегатов) + B (`subcategory` из v5.json).
- `PLPCHECK_RULE_TO_CATEGORY` определён в `SRC/analyzer/scanner.py`.
- Факты v5.json: 332 правила; source plpcheck=152, v53=98, тдс=39, тклоик=43;
  subcategory=61 (plpcheck=34); category=9; priority HIGH=189/MEDIUM=79/LOW=64.
- **Дефект E2 (слепок):** `categories` (PlpCheck-специфичные) передавались в TestGeneratorV2
  для ВСЕХ источников, поэтому PlpCheck-фильтр категорий протекал на v53/тдс/тклоик
  и отфильтровывал все не-plpcheck правила в OTHER.
- Тесты: `SRC/tests/test_ds144d_a_ast.py` (6 тестов).

### DS_144d-b — полнота маппинга (коммит d9601be)

- Диагностика: 8 DEV.* subcategory (16 plpcheck-правил) были неявно OTHER.
- Решение B2c: явный маппинг для всех 16 DEV.* правил:
  - 10 → STYLE.SYNTAX; 3 → WEB.ADAPTATION; 3 → OTHER (FIXME_NOT_ALLOWED, METHOD_AVAILABILITY, NATIONAL_CURRENCY).
- Распределение до: OTHER=17, STYLE.SYNTAX=1, WEB.ADAPTATION=7.
- Распределение после: OTHER=4, STYLE.SYNTAX=11, WEB.ADAPTATION=10. mapping size=152.
- Тесты: `SRC/tests/test_ds144d_b_ast.py` (4 теста).

### DS_144d-c — удаление rubricator_priority_mapping.py (коммит 503ef61)

- Legacy-файл (15162 байт, PRIORITY_RULES), runtime-импортов 0.
- DS_147c и DS_149d-доп уже заменили его на `rule.priority` из v5.json.
- Удалён из репо; обновлены docs (AGENTS.md, DOCUMENTATION_ARM.md, PROMPTS/DS_PROJECT_CONTEXT.md).
- Тесты: `SRC/tests/test_ds144d_c_ast.py` (3 теста).

### DS_144d-d — замена legacy-комментариев PRIORITY_RULES (коммит 844dc71)

- 6 комментариев в gui_app.py заменены на актуальные ссылки на `rule.priority` из v5.json.
- D2: исправлен отступ `# Формируем ...` (стр. 4763).
- Тесты: `SRC/tests/test_ds144d_d_ast.py` (3 теста).

### DS_144d-e — фикс дефекта E2 (коммит 657b984)

- В `_run_test_generation` `categories` (PlpCheck) теперь передаются только если
  `sources` непусто и все его элементы нормализуются в `plpcheck`; иначе `categories=None`.
- Тесты: `SRC/tests/test_ds144d_e_ast.py` (3 теста).
- Обновлены 2 старых теста-слепка: test_ds144d_a_e2_defect_fixed, test_ds147d_gui_passes_categories.

## 3. Открытия и решения

- **Количество subcategory:** 61 уникальных в v5.json; plpcheck-only = 34 (в старте было 33 — устарело).
- **Утечка DEV.*:** 16 plpcheck-правил были неявно OTHER → явно замаплены (b).
- **Дефект E2:** PlpCheck-категории протекали на v53/тдс/тклоик → починено (e).
- **Legacy-чистка:** rubricator_priority_mapping.py удалён (c); комментарии PRIORITY_RULES заменены (d).

## 4. Итог

| Шаг | Коммит | Тесты | Регресс |
|-----|--------|-------|---------|
| Базовая линия | — | — | 257 passed |
| DS_144d-a | 42f9b26 | +6 | 263 passed |
| DS_144d-b | d9601be | +4 | 267 passed |
| DS_144d-c | 503ef61 | +3 | 270 passed |
| DS_144d-d | 844dc71 | +3 | 273 passed |
| DS_144d-e | 657b984 | +3 | 276 passed |

**Всего:** +19 тестов, 257 → 276 passed, 5 коммитов, все запушены в origin/feature/dockerization.

## 5. Уроки чата 42

- 6u: диагностические скрипты в SRC/tests/ — `ROOT = parents[2]` (не parents[1]).
- 6v: regex для конкретного словаря — привязывать к имени словаря и границам { }.
- 6w: перед записью файла — dry-run с diff-предпросмотром, применять только с `--apply`.
- 6x/6y: `python -c` и `git` внутри `Start-Transcript` могут терять stdout; запускать отдельно без Transcript.
- 6z: кириллица в PS 5.1 here-string @'@ портится; использовать ASCII или WriteAllLines с chr(39).
- 6aa: нельзя вставлять присваивания/if/for внутрь аргументов вызова функции; выносить блок перед вызовом.
- 6ab: при фиксе теста-слепка обновлять ВСЕ тесты, которые этот дефект фиксируют.
- 6ac: если PS-блок упал на парсере, частичный WriteAllLines мог выполниться; проверять перед перезапуском.

## 6. Известные не-проблемы (не связаны с DS_144d)

- `# Формируем ...` в gui_app.py имел неверный отступ до DS_144d-d; исправлено в D2.

---

*Отчёт сгенерирован при закрытии DS_144d-e, 2026-10-19.*
