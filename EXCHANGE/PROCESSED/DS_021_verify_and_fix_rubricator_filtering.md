# DS 021: Проверка и принудительное исправление фильтрации рубрикатора

## Задача
Проверить, что изменения DS 020 применены корректно, и если нет — применить их принудительно.

## Текущая проблема
При выборе только `PlpCheck` в рубрикаторе сканирование использует правила из **всех** рубрикаторов (`v53`, `тдс20240828`, `тклоик20240828`, `PlpCheck`).

## Диагностика
Из отчёта видно, что используются:
- `v53.STOR.SPEC_CHARS.п.2.10` — 308 раз
- `тклоик20240828.NAMING_UNDERSCORE.стр.2` — 72 раза
- `тклоик20240828.CASE.стр.8` — 23 раза
- ... и другие не-PLP правил

## Что проверить

### 1. Проверить наличие метода `_get_rules_for_selected_files`
В `gui_app.py` должен быть метод:

```python
def _get_rules_for_selected_files(self, selected_files=None):
    """Получить список правил для выбранных файлов рубрикатора"""
    if selected_files is None:
        selected_files = [code for code, var in self.selected_rules.items() if var.get()]
    
    if not self.rubricator_prompts or not self.rubricator_prompts.loaded:
        return selected_files
    
    all_rules = self.rubricator_prompts.get_all_rules()
    matched_rules = []
    
    for file_code in selected_files:
        for rule in all_rules:
            rule_code = rule.get('code', '')
            if file_code == 'PlpCheck' and rule_code.startswith('plpcheck.'):
                matched_rules.append(rule_code)
            elif file_code == 'v50' and (rule_code.startswith('v53.') or rule_code.startswith('v50.')):
                matched_rules.append(rule_code)
            elif file_code == 'тдс20240828' and rule_code.startswith('тдс20240828.'):
                matched_rules.append(rule_code)
            elif file_code == 'тклоик20240828' and rule_code.startswith('тклоик20240828.'):
                matched_rules.append(rule_code)
            elif file_code not in ['PlpCheck', 'v50', 'тдс20240828', 'тклоик20240828']:
                if file_code in rule_code:
                    matched_rules.append(rule_code)
    
    return sorted(set(matched_rules))
2. Проверить _run_scan и _run_fix
В обоих методах должен быть код:

python
selected_files = [code for code, var in self.selected_rules.items() if var.get()]

if not self.plpcheck_enabled_var.get():
    selected_files = [r for r in selected_files if r != 'PlpCheck']

selected_rules = self._get_rules_for_selected_files(selected_files)
3. Если изменений нет — применить их
Ожидаемый результат
□ При выборе только PlpCheck — сканируются только plpcheck.* правила
□ В отчёте нет правил из других рубрикаторов
□ Лог показывает выбранные файлы и правила
Формат ответа
json
{
  "task_id": "DS_021",
  "status": "success",
  "diagnosis": "Описание текущего состояния",
  "changes": "Что было изменено",
  "test_results": {
    "method_exists": "PASSED/FAILED",
    "run_scan_updated": "PASSED/FAILED",
    "run_fix_updated": "PASSED/FAILED",
    "only_plpcheck": "PASSED/FAILED"
  }
}
text

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Проверьте** `DS_021_result.json`
3. **Примените изменения** вручную, если нужно
4. **Перезапустите АРМ**
5. **Проверьте** — выберите только `PlpCheck` и нажмите «Сканировать»
6. **Проверьте отчёт** — должны быть только `plpcheck.*` правила

---

**-= Задание DS 021 создано и готово к выполнению =-** 🚀