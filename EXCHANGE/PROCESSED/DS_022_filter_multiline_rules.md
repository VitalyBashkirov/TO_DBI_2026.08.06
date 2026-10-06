## Задача
Добавить фильтрацию многострочных правил по `selected_rules`.

## Проблема
Многострочные правила (WHEN OTHERS, NativeID, ID_SIZE, NOT_MENTIONED, VARCHAR_SIZE, NO_INTEGER_FOR_ID) хардкодом добавлены в `scanner.py` и не фильтруются по выбранным файлам рубрикатора.

При выборе только `PlpCheck` они всё равно появляются в отчёте.

## Исправление

### Файл: `F:\TO_DBI\SRC\analyzer\scanner.py`

### 1. Добавить метод `_is_rule_selected()`

```python
def _is_rule_selected(self, rule_code: str) -> bool:
    """Проверка, выбран ли файл рубрикатора для данного правила"""
    if not self.selected_rules:
        return True
    
    parts = rule_code.split('.')
    if len(parts) < 2:
        return False
    
    rule_prefix = parts[0].lower()
    
    prefix_to_file = {
        'v53': 'v53',
        'v50': 'v53',
        'plpcheck': 'PlpCheck',
        'тдс20240828': 'тдс20240828',
        'тклоик20240828': 'тклоик20240828',
    }
    
    file_code = prefix_to_file.get(rule_prefix, rule_prefix)
    return file_code in self.selected_rules
2. Обернуть каждый многострочный блок в проверку
python
# 1. WHEN OTHERS без ROLLBACK/RAISE
if self._is_rule_selected('тдс20240828.TRANS_ABORTED.стр.29') or \
   self._is_rule_selected('v53.PROC.WHENOTHERS.п.3.5'):
    multiline_issues = self._check_multiline_when_others(self.lines)
    # ... остальной код

# 2. NativeID
if self._is_rule_selected('v53.PROC.NATIVEID.п.3.26'):
    nativeid_issues = self._check_multiline_nativeid(self.lines)
    # ... остальной код

# 3. ID_SIZE
if self._is_rule_selected('v53.PROC.ID_SIZE.п.3.27'):
    id_size_issues = self._check_multiline_id_size(self.lines)
    # ... остальной код

# 4. NOT_MENTIONED
if self._is_rule_selected('PlpCheck.STYLE.NOT_MENTIONED'):
    not_mentioned_issues = self._check_multiline_not_mentioned(self.lines)
    # ... остальной код

# 5. VARCHAR_SIZE
if self._is_rule_selected('тклоик20240828.VARCHAR_SIZE.стр.4'):
    varchar_size_issues = self._check_multiline_varchar_size(self.lines)
    # ... остальной код

# 6. NO_INTEGER_FOR_ID
if self._is_rule_selected('тклоик20240828.NO_INTEGER_FOR_ID.стр.4'):
    integer_id_issues = self._check_multiline_integer_id(self.lines)
    # ... остальной код
Ожидаемый результат
□ При выборе только PlpCheck — только plpcheck.* правила
□ При выборе v53 — только v53.* правила
□ При выборе всех файлов — все правила
Формат ответа
json
{
  "task_id": "DS_022",
  "status": "success",
  "changes": [
    "Добавлен метод _is_rule_selected()",
    "Добавлена фильтрация для всех многострочных правил"
  ],
  "test_results": {
    "only_plpcheck": "PASSED",
    "only_v53": "PASSED",
    "all_files": "PASSED"
  }
}
Инструкция
Добавьте метод _is_rule_selected() в класс PLPlusScanner

Оберните все вызовы многострочных правил в проверку

Перезапустите АРМ

Проверьте сканирование

text

---

## ✅ Файл создан!

**Путь:** `F:\TO_DBI\EXCHANGE\INBOX\DS_022_filter_multiline_rules.md`

Теперь выполните `DS` в Koda. 🚀