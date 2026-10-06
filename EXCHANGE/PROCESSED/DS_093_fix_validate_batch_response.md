# DS_093 — Fix `validate_batch_response`: разрешить under-return

**Дата:** 05.10.2026
**Автор:** DeepSeek
**Исполнитель:** KODA
**Тип:** реализация
**Приоритет:** высокий
**Зависит от:** DS_091
**Блокирует:** DS_096 (git)

**См.:** `DS_STANDARD.md`, `DS_CONTEXT.md`, `DS_FILES.md`.

## 1. Цель

Разрешить **under-return** (модель вернула меньше фиксов, чем issues в batch). Over-return (больше) — оставить невалидным.

**Обоснование:** при batch_size=10 модель часто возвращает 6–8 (under-return) → сейчас invalid → fallback 2×5. Under-return приемлем — фиксы по остальным issues вернутся в следующем батче. Over-return (6 при batch 5) — галлюцинация, отсекаем.

Подтверждено: `DS_090_report.md` §6 п.2 — «batch 10 → invalid (модель возвращает 6 вместо 5)».

## 2. Файл

`tools\ai_local_worker.py`, функция `validate_batch_response` (строка 328).

## 3. Текущий код

```python
def validate_batch_response(parsed, batch):
    """DS_085 §2.1: валидация ответа батча.

    Валиден, если:
      - parsed — непустой список;
      - len(parsed) == len(batch);
      ...
    Иначе — invalid_json (count < len, count > len, пустой JSON, line mismatch).
    """
    if not isinstance(parsed, list) or not parsed:
        return False
    if len(parsed) != len(batch):          # ← МЕНЯТЬ
        return False
    batch_lines = set(iss['line'] for iss in batch)
    for item in parsed:
        if not isinstance(item, dict):
            return False
        line = item.get('line')
        if line is not None and line not in batch_lines:
            return False
    return True
```

## 4. Что менять

| # | Что | Было | Стало |
|---|-----|------|-------|
| 1 | Условие count | `if len(parsed) != len(batch):` | `if len(parsed) > len(batch):` |
| 2 | Докстринг | «len(parsed) == len(batch)» | «len(parsed) <= len(batch); under-return разрешён (DS_093)» |
| 3 | Комментарий | «count < len, count > len → invalid» | «count > len → invalid (over-return); count < len — OK (DS_093)» |

Больше **ничего** не менять.

## 5. Тесты

Новый `SRC\tests\test_ds093_validate.py`. Без `sys.stdout = ...` на уровне модуля.

| # | Что | Ожидание |
|---|-----|----------|
| t1 | `parsed = []` | False |
| t2 | `parsed = None` | False |
| t3 | `len(parsed) < len(batch)` | **True** (было False) |
| t4 | `len(parsed) == len(batch)` | True |
| t5 | `len(parsed) > len(batch)` | False |
| t6 | `line` не из batch | False |
| t7 | `item` не dict | False |
| t8 | `line` отсутствует | True (line не требуется) |

## 6. Ограничения

Стандартные (`DS_STANDARD.md` → раздел 2). Менять **только** `validate_batch_response` + её докстринг. `send_batch`, `run_fallback` — не трогать.

## 7. Отчёт

Стандартный (`DS_STANDARD.md` → раздел 3) + раздел:

```
## Diff (до/после)
- строка X: было `...` → стало `...`

## Прогон тестов
- test_ds093_validate.py: N/8 PASSED
- test_ds089b.py: 15/15 PASSED (регресс)
- test_ds089a.py: 13/13 PASSED (регресс)
```

## 8. Критерии успеха

- `!=` заменено на `>`.
- t1..t8 PASSED.
- Регресс `test_ds089b.py` — 15/15.
- Fallback 2×5 не сломан.

## 9. Артефакты

- `tools\ai_local_worker.py` (изменён)
- `SRC\tests\test_ds093_validate.py` (новый)
- `EXCHANGE\OUTBOX\DS_093_report.md`