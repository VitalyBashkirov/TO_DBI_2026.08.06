# DS 024: Исправление фильтрации по приоритетам

## Задача
Исправить работу фильтрации по приоритетам (HIGH/MEDIUM/LOW) в `gui_app.py` и добавить защиту от пустого `selected_rules` в `scanner.py`.

## Проблема
1. При выборе HIGH/MEDIUM/LOW и только PlpCheck в логе:
[ПРИОРИТЕТ] Фильтрация по приоритетам: HIGH, MEDIUM, LOW
Всего правил из приоритетов: 164
Используемых правил: 0

text
Из-за этого `selected_rules` становится пустым, и сканер загружает ВСЕ правила.

2. В `scanner.py` нет проверки на пустой `selected_rules`, поэтому загружаются все правила.

## Исправления

### 1. В `gui_app.py` (методы `_run_scan` и `_run_fix`)

**Найти блок:**
```python
if selected_priorities:
 from rubricator_priority_mapping import PRIORITY_RULES
 priority_rules = set()
 for prio in selected_priorities:
     if prio in PRIORITY_RULES:
         priority_rules.update(PRIORITY_RULES[prio])
 priority_rules = sorted(priority_rules)
 selected_rules = [r for r in selected_rules if r in priority_rules]
Заменить на:

python
if selected_priorities:
    from rubricator_priority_mapping import PRIORITY_RULES
    priority_rules = set()
    for prio in selected_priorities:
        if prio in PRIORITY_RULES:
            priority_rules.update(PRIORITY_RULES[prio])
    priority_rules = sorted(priority_rules)
    
    # Фильтруем только если есть приоритеты
    if priority_rules:
        filtered_rules = [r for r in selected_rules if r in priority_rules]
        if filtered_rules:
            selected_rules = filtered_rules
        else:
            self.log(f"⚠️ Для выбранных файлов нет правил с приоритетами {selected_priorities}. Используются все правила.", 'warning')
            # selected_rules остаётся без изменений
    else:
        self.log("⚠️ Нет правил в PRIORITY_RULES. Используются все правила.", 'warning')
2. В scanner.py (метод _load_patterns_from_rubricator)
Добавить в начало метода:

python
def _load_patterns_from_rubricator(self) -> Dict:
    patterns = {}
    ignore_patterns_map = {}
    self._rubricator_rules = {}
    
    if not self.rubricator_prompts or not self.rubricator_prompts.loaded:
        return patterns
    
    all_rules = self.rubricator_prompts.get_all_rules()
    
    # Если selected_rules пустой — загружаем ВСЕ правила (обратная совместимость)
    # и выводим предупреждение
    if not self.selected_rules:
        print("[WARN] selected_rules пуст! Загружаются все правила.")
        # Загружаем все правила
        for rule_info in all_rules:
            # ... загрузка всех правил без фильтрации
            pass
        return patterns
    
    # ... существующий код фильтрации
Ожидаемый результат
□ При выборе только PlpCheck и HIGH/MEDIUM/LOW загружаются только PlpCheck правила с соответствующим приоритетом
□ Если в PRIORITY_RULES нет правил для выбранных файлов — загружаются все правила из выбранных файлов
□ В логе нет Используемых правил: 0
Формат ответа
json
{
  "task_id": "DS_024",
  "status": "success",
  "changes": [
    "Исправлена фильтрация по приоритетам в gui_app.py",
    "Добавлена проверка на пустой selected_rules в scanner.py"
  ],
  "test_results": {
    "plpcheck_and_priorities": "PASSED",
    "empty_selected_rules": "PASSED"
  }
}
Инструкция
Примените изменения в gui_app.py и scanner.py

Перезапустите АРМ

Выберите только PlpCheck и приоритеты HIGH/MEDIUM/LOW

Нажмите «Сканировать»

В отчёте должны быть только plpcheck.* правила

text

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения**
3. **Перезапустите АРМ**
4. **Проверьте** — выберите только `PlpCheck` + приоритеты

---

**-= Задание DS 024 создано =-** 🚀