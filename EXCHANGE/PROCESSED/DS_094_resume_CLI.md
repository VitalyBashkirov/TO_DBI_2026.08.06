# DS_094 — Resume (`--resume` / `--skip-ids`) в CLI

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** высокий
**Зависит от:** DS_091
**Блокирует:** DS_096 (git)

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

## 1. Цель

Реализовать resume в `tools\ai_local_worker.py`: пропустить issues, уже обработанные в предыдущем прогоне. Симметрично GUI resume (DS_089b).

## 2. Текущее состояние

`ai_local_worker.py` **не содержит** `--resume`, `--skip-ids`, `load_processed_ids`, `save_processed_ids`. Подтверждено DS_091.

## 3. Что добавить

| # | Что | Где | Описание |
|---|-----|-----|----------|
| 1 | `--resume` (flag) | после `--skip-rule` (~839) | Читать `*.processed.json` из out-dir |
| 2 | `--skip-ids FILE` | после `--resume` | JSON со списком id |
| 3 | `load_processed_ids(out_dir)` | новая функция | Читает `*.processed.json`, возвращает `set(id)` |
| 4 | `save_processed_ids(out_dir, request_name, ids)` | новая функция | Пишет `*.processed.json` |
| 5 | Параметр `skip_ids` в `run_request` | `650` | `if skip_ids: issues = [i for i in issues if i['id'] not in skip_ids]` |
| 6 | `--resume` → `skip_ids = load_processed_ids(out_dir)` | в `main` | Автозагрузка |
| 7 | Запись `processed.json` после `run_request` | в `main` | Сохранить обработанные id |

## 4. Схема `processed.json`

```json
{
  "request": "AI_REQUEST_20260930_PSH_DEP_PRIV_GO.md",
  "processed_ids": ["id1", "id2", ...],
  "timestamp": "2026-10-05T12:00:00",
  "model": "deepseek-coder:6.7b"
}
```

Имя файла: `<request_stem>.processed.json` в `--out-dir`.

## 5. Тесты

Новый `SRC\tests\test_ds094_resume.py`. Без `sys.stdout = ...` на уровне модуля.

| # | Что | Ожидание |
|---|-----|----------|
| t1 | `load_processed_ids` — файла нет | пустой set |
| t2 | `load_processed_ids` — файл есть | set с id |
| t3 | `save_processed_ids` — пишет JSON | файл создан, JSON валиден |
| t4 | `run_request` с `skip_ids` | issues отфильтрованы, `stats['issues']` меньше |
| t5 | CLI `--skip-ids FILE` | парсится, передаётся в `run_request` |
| t6 | CLI `--resume` | автозагрузка из out-dir |
| t7 | Повторный прогон с `--resume` | issues не обработаны повторно |
| t8 | `--resume` без out-dir | ошибка/предупреждение |

## 6. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). Менять **только** `ai_local_worker.py`. CLI-контракт (существующие аргументы) не ломать. `--skip-rule`, `--filter-type`, `--limit`, `--fallback-size`, `--no-fallback` — работают как раньше.

## 7. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + разделы:

```
## Схема processed.json
<пример>

## CLI-контракт (новые аргументы)
| Аргумент | Тип | Назначение |
|----------|-----|------------|
| --resume | flag | ... |
| --skip-ids | path | ... |

## Прогон тестов
- test_ds094_resume.py: N/8 PASSED
- test_ds089b.py: 15/15 (регресс)
```

## 8. Критерии успеха

- t1..t8 PASSED.
- `--resume` работает end-to-end.
- `processed.json` пишется после прогона.
- Регресс `test_ds089b.py` — 15/15.
- Существующие CLI-аргументы работают.

## 9. Артефакты

- `tools\ai_local_worker.py` (изменён)
- `SRC\tests\test_ds094_resume.py` (новый)
- `EXCHANGE\OUTBOX\DS_094_report.md`