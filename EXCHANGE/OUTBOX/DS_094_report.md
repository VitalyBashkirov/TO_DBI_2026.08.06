# DS_094 - Отчёт

## 1. Что сделано
- Добавлены функции `load_processed_ids(out_dir)` и `save_processed_ids(out_dir, request_name, ids, model)`
- Добавлен параметр `skip_ids` в `run_request` - фильтрация issues по id
- Добавлены CLI-аргументы `--resume` (flag) и `--skip-ids FILE`
- В `main()`: --resume -> load_processed_ids, --skip-ids -> чтение JSON
- После каждого run_request: сохранение processed.json
- Создан тест test_ds094_resume.py (8 кейсов)

## 2. Изменённые файлы
- tools\ai_local_worker.py - load/save_processed_ids, skip_ids, CLI
- SRC\tests\test_ds094_resume.py - новый файл (8 тестов)

## Схема processed.json
```json
{
  "request": "AI_REQUEST_test.md",
  "processed_ids": [1, 2, 3],
  "timestamp": "2026-10-05T12:00:00",
  "model": "deepseek-coder:6.7b"
}
```

## CLI-контракт (новые аргументы)
| Аргумент | Тип | Назначение |
|----------|-----|------------|
| --resume | flag | Читать *.processed.json из --out-dir |
| --skip-ids | path | JSON со списком id для пропуска |

## 3. Результат тестов
- test_ds094_resume.py: 8/8 PASSED
- test_ds089b.py: 15/15 PASSED (регресс)
- python -m pytest -v: 57 PASSED, 0 FAILED

## 4. Расхождения
- нет

## 5. Артефакты
- tools\ai_local_worker.py (изменён)
- SRC\tests\test_ds094_resume.py (новый)
- EXCHANGE\OUTBOX\DS_094_report.md