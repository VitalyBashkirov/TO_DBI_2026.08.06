# DS 023: Фильтрация паттернов в scanner.py

## Задача
Исправить `_load_patterns_from_rubricator()` так, чтобы загружались **только правила из selected_rules**.

## Проблема
При выборе только `PlpCheck` в логе:
[INFO] Загружено 342 паттернов из JSON-рубрикатора

text

Должно быть:
[INFO] Загружено 152 паттернов из JSON-рубрикатора

text

## Причина
В методе `_load_patterns_from_rubricator()` после фильтрации по `selected_rules` загружаются **все паттерны** из `rubricator_prompts`, а не только те, что прошли фильтр.

## Исправление

### Файл: `F:\TO_DBI\SRC\analyzer\scanner.py`

**Найти метод `_load_patterns_from_rubricator()`.**

**В блоке:**
```python
if self.rubricator_prompts and self.rubricator_prompts.loaded:
    all_rules = self.rubricator_prompts.get_all_rules()
    
    for rule_info in all_rules:
        rule_key = rule_info['code']
        # ... фильтрация
        # ЗАГРУЖАЮТСЯ ВСЕ ПАТТЕРНЫ, ПРОШЕДШИЕ ФИЛЬТР
Нужно убедиться, что фильтрация работает правильно.

Проверка фильтрации
Добавьте в _load_patterns_from_rubricator():

python
if self.rubricator_prompts and self.rubricator_prompts.loaded:
    all_rules = self.rubricator_prompts.get_all_rules()
    
    loaded_count = 0
    for rule_info in all_rules:
        rule_key = rule_info['code']
        rule_data = self.rubricator_prompts.get_rule(rule_key)
        if not rule_data:
            continue
        
        file_code = rule_key.split('.')[0]
        
        # Фильтрация по выбранным файлам
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
                continue  # ← ПРОПУСКАЕМ ПРАВИЛО
        
        # ТОЛЬКО ЕСЛИ ПРАВИЛО ПРОШЛО ФИЛЬТР — ЗАГРУЖАЕМ ПАТТЕРНЫ
        loaded_count += 1
        # ... загрузка паттернов
    
    print(f"[INFO] Загружено {loaded_count} паттернов из JSON-рубрикатора")
Ожидаемый результат
□ При выборе только PlpCheck загружается 152 паттерна
□ При выборе v53 загружается 106 паттернов
□ При выборе всех файлов загружается 342 паттерна
Формат ответа
json
{
  "task_id": "DS_023",
  "status": "success",
  "changes": [
    "Исправлена фильтрация паттернов в _load_patterns_from_rubricator()"
  ],
  "test_results": {
    "only_plpcheck": "PASSED (152 паттерна)",
    "only_v53": "PASSED (106 паттернов)",
    "all_files": "PASSED (342 паттерна)"
  }
}
Инструкция
Исправьте _load_patterns_from_rubricator()

Перезапустите АРМ

Выберите только PlpCheck

Нажмите «Сканировать»

В логе должно быть [INFO] Загружено 152 паттернов

В отчёте должны быть только plpcheck.* правила

text

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `scanner.py`
3. **Перезапустите АРМ**
4. **Проверьте** — выберите только `PlpCheck` и нажмите «Сканировать»

---

**-= Задание DS 023 создано =-** 🚀