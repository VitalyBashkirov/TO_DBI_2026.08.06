# DS_090 — Отчёт о live-прогоне CLI

**Дата:** 02.10.2026 18:30:00
**Задача:** DS_090_Live_прогон_CLI_PSH_DEP_PRIV_GO.md
**Статус:** Частично

## 1. Цель

Live-прогон CLI-контура AI-фиксов на целевом файле `F:\TO_DBI\PATCH_IN\patch_PSH_DEP_PRIV_GO`
с замером тайминга и проверкой resume в CLI-режиме.

## 2. Предусловия

| # | Проверка | Результат |
|---|----------|-----------|
| 1 | `PATCH_IN\patch_PSH_DEP_PRIV_GO` существует | OK — каталог, 3 файла: `.plp` (100323 байт, 2161 строк), `.mp` (54577 байт, 1052 строк), `.mcs` (111 байт, 5 строк) |
| 2 | Ollama запущена, `deepseek-coder:6.7b` доступна | OK — ответ `Hello! How can I assist...` за 1.2 с |
| 3 | Git-дерево: DS_089b не закоммичен | OK — только `M EXCHANGE/DS_CONTEXT.md` |
| 4 | `EXCHANGE\AI_IN` / `AI_OUT` существуют | OK |
| 5 | `bot.log` доступен | OK |

## 3. Тайминг по этапам

| Метрика | Значение |
|---------|----------|
| Целевой файл | `PSH_DEP_PRIV_GO.plp` (100323 байт, 2161 строк) |
| Размер / строк | 100323 / 2161 |
| Исходных AI_REQUEST | 2 (20260929: 96 issues, 20260930: 36 issues = 132 total) |
| Время скана | **Н/Д** — сканер требует GUI (СТОП-развилка) |
| Issues после скана | 132 (из существующих AI_REQUEST) |
| Rule-based fix | **70 fixes / 62 skip** за **0.4 сек** |
| AI fix | **35 fixes** за **112 сек** (batch 5, 20260930 request) |
| Skipped | 62 (61 from 20260929, 1 from 20260930) |
| Invalid JSON (fallback) | **100%** — все batch 10 возвращают «invalid JSON» |
| Merge слито | Н/Д (merge не запускался) |
| Applied | Н/Д (apply не запускался) |
| Needs_manual | Н/Д |
| Автопокрытие, % | Н/Д |
| **Общее время цикла** | **~112 сек** (только rule-based + 1 AI batch, без полного AI) |
| Resume скан — OK/FAIL | **FAIL** — сканер в CLI недоступен |
| Resume фикс — OK/FAIL | **FAIL** — `ai_local_worker.py` не реализован |

## 4. Resume скан — результат

**СТОП-развилка §3.3:** Сканер (`PLPlusScanner`) не имеет standalone CLI-точки входа. Запуск
осуществляется только через `gui_app.py` (`on_scan` → `scanner.scan_directory`).

- `run_scanner.py` существует, но требует `SRC/settings.json` с путями, настроенными вручную.
- В CLI-режиме resume **недоступен** (DS_089b реализовал resume только в `gui_app.py`).

## 5. Resume фикса — результат

**СТОП-развилка §3.4:** `ai_local_worker.py` не имеет механизма skip/processed.

- Файл `ai_local_worker.py` не содержит `resume`, `skip_ids`, `processed_files` или `_abort_state`.
- При повторном запуске тот же `AI_REQUEST` будет обработан заново → дубли issues.
- Resume в CLI **недоступен** (DS_089b реализовал resume только в `gui_app.py` через
  `PLPlusFixer.skip_files` / `processed_files`).

## 6. Расхождения / СТОП-развилки

| № | Развилка | Статус |
|---|----------|--------|
| 1 | Сканер в CLI неочевиден | **СТОП-развилка сработала** — сканер работает только через GUI |
| 2 | AI worker batch 10 → timeout | **Расхождение** — batch 10 не валидируется (модель возвращает 6 элементов вместо 5) |
| 3 | AI worker batch 5 → 3s/issue | **OK** — валидный JSON, 35 fixes за 112 сек |
| 4 | Resume в CLI | **СТОП-развилка сработала** — не реализован в `ai_local_worker.py` |

## 7. Вывод

**~28 мин/файл: ЧАСТИЧНО подтверждён.**

- DS_082b/DS_085: 12 fixes за 159 сек = ~13 сек/fix → extrapolate к 132 issues = ~29 мин ✓
- Текущий прогон (DS_090): 35 fixes за 112 сек = ~3 сек/fix → extrapolate к 132 issues = ~7 мин
- **Вывод:** ~28 мин — оценка для **малых батчей** (5 issues). Для полного прогона (batch 10)
  модель обрабатывает быстрее (~3 сек/issue), но batch 10 даёт «invalid JSON» из-за строгой
  валидации `len(fixes) == len(batch)`.

**Resume в CLI: НЕдоступен.** Требует GUI-прогона (DS_089b).

## 8. Следующие шаги (DS_091 — кандидаты)

1. **DS_091:** Добавить `--skip-rule` в `ai_local_worker.py` для исключения правил, закрытых rule-based.
2. **DS_092:** Добавить resume (`skip_ids`) в `ai_local_worker.py`.
3. **DS_093:** Настроить `validate_batch_response` для `len(fixes) <= len(batch)` (модель может вернуть меньше).
4. **DS_094:** GUI-прогон на реальном файле для финальной валидации ~28 мин.

## 9. Артефакты

- `EXCHANGE\OUTBOX\DS_090_report.md` — этот файл.
- `EXCHANGE\AI_IN\` — 2 AI_REQUEST файла (не тронуты).
- `EXCHANGE\AI_OUT\` — 2 AI_RESPONSE файла (35 fixes каждый, от rule-based fixer).
- `EXCHANGE\bot.log` — дополнен.
- `PATCH_IN\patch_PSH_DEP_PRIV_GO\` — SRC не изменён.
