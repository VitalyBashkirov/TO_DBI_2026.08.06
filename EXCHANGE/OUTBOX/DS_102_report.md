# DS_102 — Отчёт: GUI → CLI resume-интеграция

**Дата:** 07.10.2026
**Статус:** Выполнено

---

## 1. Разведка: текущий argv Popen ai_local_worker

**Файл:** `SRC\gui_app.py`, строка 5746–5750 (до правки):

```python
proc = subprocess.Popen(
    [sys.executable, str(tools / 'ai_local_worker.py'),
     '--in-dir', str(ai_in), '--out-dir', str(ai_out)],
    cwd=str(root), stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT)
```

`--resume` НЕ передавался.

Popen для `rule_based_fixer.py` (строка 5733) — не трогался (детерминированный фиксер, идемпотентен).

---

## 2. Правка: было/стало

**Было:**
```python
'--in-dir', str(ai_in), '--out-dir', str(ai_out)],
```

**Стало:**
```python
'--in-dir', str(ai_in), '--out-dir', str(ai_out),
 '--resume'],
```

Добавлен единственный аргумент `'--resume'` в конец argv.

---

## 3. Уточнение поведения

| Сценарий | Поведение |
|----------|-----------|
| `<request>.processed.json` существует в `ai_out` | `load_processed_ids()` возвращает множество id; `ai_local_worker` пропускает обработанные issues |
| `.processed.json` НЕТ | `load_processed_ids()` возвращает пустое множество; прогон как обычно |
| После успешного прогона | `save_processed_ids()` сохраняет `.processed.json` в `ai_out` |

Логика в `ai_local_worker.py` (строки ~974–979):
```python
skip_ids = set()
if args.resume:
    skip_ids |= load_processed_ids(out)
if skip_ids:
    log(f'resume: {len(skip_ids)} id уже обработано (пропускаю)')
```

GUI не мешает: `.processed.json` лежит в `EXCHANGE\AI_OUT`, читается при повторном нажатии «3. В Ai».

---

## 4. Тест

**Файл:** `SRC\tests\test_ds102_gui_resume.py` (новый)

| Тест | Что проверяет |
|------|---------------|
| `test_t1_argv_contains_resume` | `'--resume'` в argv при Popen для ai_local_worker |
| `test_t2_processed_json_skip` | При существующем `.processed.json` — `skip_ids` непустой |
| `test_t3_no_processed_json_empty_skip` | Без `.processed.json` — `skip_ids` пустой |

Существующие тесты:
- `test_ds092_e2e.py` — покрывает scan/fix abort/resume (skip_files), но НЕ проверяет argv Popen.
- `test_ds094_resume.py` — покрывает CLI `--resume`/`--skip-ids` парсинг и повторный прогон, но НЕ GUI argv.

Новый тест DS_102 заполняет этот пробел.

---

## 5. Регресс

```
python -m pytest SRC/tests/ -v
60 PASSED
```

(57 существующих + 3 новых DS_102)

---

## 6. Артефакты

| Файл | Действие |
|------|----------|
| `SRC\gui_app.py` | Правка Popen (+`'--resume'`) |
| `SRC\tests\test_ds102_gui_resume.py` | Новый тест (3 теста) |
| `EXCHANGE\OUTBOX\DS_102_report.md` | Отчёт |

---

## 7. Вывод

GUI resume-интеграция работает. Открытая проблема №3 закрыта: «GUI не передаёт `--resume` / `--skip-ids` в CLI». Повторный прогон через GUI не дублирует уже обработанные issues.

---

## 8. Расхождения

Нет.
