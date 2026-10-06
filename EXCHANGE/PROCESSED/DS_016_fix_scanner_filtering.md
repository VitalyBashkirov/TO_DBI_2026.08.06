# DS 016: Исправление фильтрации рубрикатора в scanner.py

## Задача
Исправить фильтрацию правил в `analyzer/scanner.py` — при выборе только `PlpCheck` должны загружаться только правила `plpcheck.*`.

## Проблема
В методе `_load_patterns_from_rubricator()` сравнивается `file_code = 'plpcheck'` (из правила) с `selected_rules = ['PlpCheck']` (с большой буквы).

Из-за регистрозависимого сравнения ни одно правило не проходит фильтр, и загружаются ВСЕ правила из всех рубрикаторов.

## Исправление

### Файл: `F:\TO_DBI\SRC\analyzer\scanner.py`

**Найти блок кода (строки ~170-190):**
```python
if self.selected_rules:
    file_to_prefixes = {
        'v53': ('v53', 'v50'),
        'v50': ('v53', 'v50'),
        'PlpCheck': ('plpcheck',),
        'тдс20240828': ('тдс20240828',),
        'тклоик20240828': ('тклоик20240828',),
    }
    allowed_prefixes = set()
    for fc in self.selected_rules:
        allowed_prefixes.update(file_to_prefixes.get(fc, (fc,)))
    if file_code not in allowed_prefixes:
        continue
Заменить на:

python
if self.selected_rules:
    file_code_lower = file_code.lower()
    file_to_prefixes = {
        'v53': ('v53', 'v50'),
        'v50': ('v53', 'v50'),
        'plpcheck': ('plpcheck',),
        'тдс20240828': ('тдс20240828',),
        'тклоик20240828': ('тклоик20240828',),
    }
    allowed_prefixes = set()
    for fc in self.selected_rules:
        fc_lower = fc.lower()
        allowed_prefixes.update(file_to_prefixes.get(fc_lower, (fc_lower,)))
    if file_code_lower not in allowed_prefixes:
        continue
Ожидаемый результат
□ При выборе только PlpCheck загружаются только plpcheck.* правила
□ При выборе v53 загружаются только v53.* и v50.* правила
□ При выборе всех файлов загружаются все правила
Формат ответа
json
{
  "task_id": "DS_016",
  "status": "success",
  "changes": [
    "Исправлена регистрозависимость в фильтрации правил",
    "Все сравнения приведены к нижнему регистру"
  ],
  "test_results": {
    "only_plpcheck": "PASSED",
    "only_v53": "PASSED",
    "all_files": "PASSED"
  }
}
Инструкция
Замените блок кода в scanner.py

Перезапустите АРМ

Проверьте: выберите только PlpCheck и нажмите «Сканировать»

В отчёте должны быть только plpcheck.* правила

text

---

## ✅ Файл создан!

**Путь:** `F:\TO_DBI\EXCHANGE\INBOX\DS_016_fix_scanner_filtering.md`

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `scanner.py`
3. **Перезапустите АРМ**
4. **Проверьте** — выберите только `PlpCheck` и нажмите «Сканировать»

---

## 📋 Сравнение

| Было | Стало |
|------|-------|
| `'plpcheck' in ['PlpCheck']` → **False** | `'plpcheck' in ['plpcheck']` → **True** |
| Все правила загружались | Только `plpcheck.*` правила |
| В отчёте v53 и тклоик20240828 | В отчёте только PlpCheck |

---

**-= Задание DS 016 готово к выполнению =-** 🚀