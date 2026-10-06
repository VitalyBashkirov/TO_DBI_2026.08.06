# DS_096a — Фикс BOM в `ai_local_worker_config.json` + фикс `test_ds094_resume.py::t4`

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация (fix)
**Приоритет:** высокий
**Зависит от:** DS_094, DS_095
**Блокирует:** DS_096 (git)

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

## 1. Цель

Устранить два бага, выявленных после DS_094:

1. **BOM в `tools\ai_local_worker_config.json`** — Python `json.load` не читает BOM → warning, default config.
2. **`test_ds094_resume.py::test_t4_run_request_skip_ids`** — pytest сообщает PASSED, но внутри теста `[FAIL]`. Тест не сигнализирует о реальном сбое.

## 2. Баг №1: BOM в config

### 2.1. Подтверждение

```
00000000   EF BB BF 7B 0D 0A 20 20 20 20 22 6D 61 78 5F 74  ï»¿{..    "max_t
```

`EF BB BF` — BOM. Файл создан через `Out-File -Encoding UTF8`.

### 2.2. Что менять

Перезаписать `F:\TO_DBI\tools\ai_local_worker_config.json` **без BOM**.

**Содержимое** (не менять, только убрать BOM):
```json
{
    "max_tokens":  2000,
    "timeout_sec":  600,
    "ollama_url":  "http://localhost:11434",
    "batch_size":  10,
    "fallback_on_invalid":  true,
    "num_ctx":  4096,
    "merge_same_line":  true,
    "model":  "deepseek-coder:6.7b",
    "fallback_batch_size":  5,
    "temperature":  0.1
}
```

**Способ записи (PowerShell, без BOM):**
```powershell
[System.IO.File]::WriteAllText(
    'F:\TO_DBI\tools\ai_local_worker_config.json',
    (Get-Content 'F:\TO_DBI\tools\ai_local_worker_config.json' -Raw -Encoding UTF8),
    [System.Text.UTF8Encoding]::new($false))
```

### 2.3. Проверка

```powershell
Format-Hex -Path F:\TO_DBI\tools\ai_local_worker_config.json | Select-Object -First 1
```

Первые 3 байта — **не** `EF BB BF`.

**Проверка json.load:**
```powershell
python -c "import json; print(json.load(open(r'F:\TO_DBI\tools\ai_local_worker_config.json', encoding='utf-8'))['model'])"
```

Ожидание: `deepseek-coder:6.7b`, **без warning**.

## 3. Баг №2: test_t4 — PASSED при FAIL

### 3.1. Подтверждение

```
[FAIL] # 4 run_request skip_ids: issues filtrovany  :: issues=0
PASSED
```

### 3.2. Что менять

В `SRC\tests\test_ds094_resume.py`, метод `test_t4_run_request_skip_ids`:

**Проблема:** проверка не приводит к падению теста (нет `assert` или `assert` подавлен `try/except`).

**Что сделать:**

1. Найти метод `test_t4_run_request_skip_ids`.
2. Убедиться, что в нём есть **`self.assertEqual`** или **`assert`** на результат.
3. Если проверка провалилась — тест **должен падать** (FAILED), а не печатать `[FAIL]` и продолжать.

**Причина бага (гипотеза):** используется **config с BOM** → `json.load` не читает → default → `issues=0`. Тест «ожидает» `issues > 0`, но не проверяет **строго**, только печатает `[FAIL]`.

**Что должно быть в тесте:**

```python
def test_t4_run_request_skip_ids(self):
    # ... подготовка AI_REQUEST с N issues ...
    stats, fixes = run_request(request_path, out_dir, cfg, skip_ids={1, 2})
    self.assertGreater(stats['issues'], 0, "issues должны быть (AI_REQUEST не пуст)")
    self.assertLess(stats['issues'], total_issues, "skip_ids должен уменьшить issues")
```

**Ожидание после фикса:** тест **проходит** после фикса BOM (issues не 0). Если BOM не исправлен — тест **падает** (FAILED).

### 3.3. Проверка

```powershell
cd F:\TO_DBI
python -m pytest SRC\tests\test_ds094_resume.py -v
```

Ожидание: 8/8 **PASSED** (после фикса BOM). Если BOM не исправлен — 7/8 PASSED, t4 FAILED.

## 4. Файлы

| # | Файл | Что менять |
|---|------|-----------|
| 1 | `tools\ai_local_worker_config.json` | Перезаписать без BOM (содержимое не менять) |
| 2 | `SRC\tests\test_ds094_resume.py` | Метод `test_t4_run_request_skip_ids` — добавить строгие `assert` |

## 5. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). Менять **только** 2 файла. Логику `run_request` не трогать. `validate_batch_response` не трогать.

## 6. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + разделы:

```
## Diff config
- BOM до: EF BB BF
- BOM после: <hex>
- json.load без warning: OK

## Diff test_ds094_resume.py
- test_t4: добавлены assert (было только print)

## Прогон тестов
- test_ds094_resume.py: 8/8 PASSED (было 7/8 с фиктивным t4)
- python -m pytest -v: 57 PASSED, 0 FAILED
```

## 7. Критерии успеха

- `ai_local_worker_config.json` без BOM.
- `json.load` в Python — без warning.
- `test_ds094_resume.py::t4` — **PASSED** (не FAIL).
- `python -m pytest -v` — **57 PASSED**, 0 FAILED.
- `python -m pytest -v` — **0 warning** про BOM.

## 8. Артефакты

- `tools\ai_local_worker_config.json` (изменён — без BOM)
- `SRC\tests\test_ds094_resume.py` (изменён — t4)
- `EXCHANGE\OUTBOX\DS_096a_report.md`