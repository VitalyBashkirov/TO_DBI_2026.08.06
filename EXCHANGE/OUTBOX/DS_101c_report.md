# DS_101c — Отчёт: Фикс мок-сервера Ollama

**Дата:** 07.10.2026
**Статус:** Выполнено

---

## 1. Изменения в mock_ollama_invalid.py

**Файл:** `tools\mock_ollama_invalid.py` (7 000 B, 209 строк, UTF-8 без BOM, mtime 07.10.2026 03:44:31)

### Суть бага

Мок использовал regex `\bline\s+(\d+)\s*,` на всём user content.
В build_prompt есть блок EXAMPLE со строкой
`"Issue: line 32, code: IS_EOD_NEW ..."`, из-за чего мок возвращал
N+1 элементов. `validate_batch_response` считал `len(parsed) >
len(batch)` → invalid.

### Решение (Вариант B)

Добавлены/изменены функции:

1. **`_extract_count(content)`** — новый. Regex
   `exactly\s+(\d+)\s+elements` извлекает явное число N из
   инструкции промпта. Возвращает int или None.

2. **`_extract_lines(content)`** — изменена. Теперь сканирует
   только секцию ПОСЛЕ `"ISSUES:"` (case-sensitive). Блок EXAMPLE
   с `line 32,` игнорируется. Если `ISSUES:` не найден —
   сканирует весь content (обратная совместимость).

3. **`_make_fix_array(n, lines)`** — принимает явный `n`.
   - lines > n → обрезка до n.
   - lines < n → дополнение `last+1, last+2, ...`.
   - lines пуст → `range(1, n+1)`.

4. **`do_POST`** — вызывает `_extract_count`, затем
   `_make_fix_array(n, lines)`. Если `exactly N elements` не найден
   — fallback: `_extract_lines` (после `ISSUES:`), `n = len(lines)`.

### Приоритет извлечения N

1. `exactly N elements` — основной.
2. `len(_extract_lines)` — fallback (секция после `ISSUES:`).
3. `default_count` — последний резерв.

---

## 2. py_compile

```
python -m py_compile tools\mock_ollama_invalid.py
```

Результат: RC 0.

---

## 3. Тест batch=3 с EXAMPLE

Промпт содержит EXAMPLE (`line 32,`) + 3 issues +
`"exactly 3 elements"`.

**R1** (невалидный): `not a valid json at all` ✓

**R2** (валидный):
```json
[{"line":1,"after":"mock fixed line",...},
 {"line":2,...},
 {"line":3,...}]
```

Длина массива: **3**. line 32 отсутствует. ✓

---

## 4. Тест batch=10

Промпт с EXAMPLE + 10 issues + `"exactly 10 elements"`.

**R2:** массив из **10** элементов.

Содержит line 32: **нет**. ✓

---

## 5. Тест batch=5 (fallback sub)

Промпт с EXAMPLE + 5 issues + `"exactly 5 elements"`.

**R2:** массив из **5** элементов.

Lines: 1,2,3,4,5. Содержит line 32: **нет**. ✓

---

## 6. Итог

Мок-сервер `tools\mock_ollama_invalid.py` исправлен. Теперь
всегда возвращает ровно N элементов (N из инструкции промпта).
EXAMPLE-блок не влияет на размер ответа. Готов к повторному
прогону DS_101b.
