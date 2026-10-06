## 🔍 Лог не поменялся — разбираемся

Это значит, что либо задание **DS 019** не применилось, либо в коде есть **другая логика**, которая переопределяет фильтрацию правил.

---

## 🐛 Вторая возможная причина

Посмотрите на логику в `_run_scan` (строки ~2300-2350):

```python
# Определение выбранных правил
selected_rules = [code for code, var in self.selected_rules.items() if var.get()]

# Фильтрация PlpCheck правил в зависимости от флага на форме
if not self.plpcheck_enabled_var.get():
    selected_rules = [r for r in selected_rules if r != 'PlpCheck']
```

**Проблема:** даже если `selected_rules` содержит только `['PlpCheck']`, в сканер передаётся **все правила из `self.rubricator_prompts`**, а не только те, что соответствуют `PlpCheck`.

---

## ✅ Решение — прямое исправление

### Шаг 1: Найдите в `gui_app.py` метод `_run_scan`

Поищите строку:
```python
selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
```

### Шаг 2: Замените блок кода

**Было:**
```python
# Определение выбранных правил
selected_rules = [code for code, var in self.selected_rules.items() if var.get()]

# Фильтрация PlpCheck правил в зависимости от флага на форме
if not self.plpcheck_enabled_var.get():
    selected_rules = [r for r in selected_rules if r != 'PlpCheck']
```

**Стало:**
```python
# Определение выбранных файлов рубрикатора
selected_files = [code for code, var in self.selected_rules.items() if var.get()]

# Фильтрация PlpCheck
if not self.plpcheck_enabled_var.get():
    selected_files = [r for r in selected_files if r != 'PlpCheck']

# Сбор правил из выбранных файлов
selected_rules = []
if self.rubricator_prompts and self.rubricator_prompts.loaded:
    all_rules = self.rubricator_prompts.get_all_rules()
    for file_code in selected_files:
        for rule in all_rules:
            rule_code = rule.get('code', '')
            if file_code == 'PlpCheck' and rule_code.startswith('plpcheck.'):
                selected_rules.append(rule_code)
            elif file_code == 'v50' and (rule_code.startswith('v53.') or rule_code.startswith('v50.')):
                selected_rules.append(rule_code)
            elif file_code == 'тдс20240828' and rule_code.startswith('тдс20240828.'):
                selected_rules.append(rule_code)
            elif file_code == 'тклоик20240828' and rule_code.startswith('тклоик20240828.'):
                selected_rules.append(rule_code)
            elif file_code not in ['PlpCheck', 'v50', 'тдс20240828', 'тклоик20240828']:
                # fallback
                if file_code in rule_code:
                    selected_rules.append(rule_code)
    selected_rules = sorted(set(selected_rules))
else:
    # fallback — используем коды файлов как есть
    selected_rules = selected_files
```

### Шаг 3: Обновить логирование

Замените:
```python
self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
for rule in selected_rules:
    self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
```

**На:**
```python
self.root.after(0, lambda: self.log(f"\nВЫБРАННЫЕ ФАЙЛЫ РУБРИКАТОРА:", 'highlight'))
for file_code in selected_files:
    self.root.after(0, lambda f=file_code: self.log(f"  [+] {f}", 'highlight'))

self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
for rule in selected_rules[:20]:
    self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
if len(selected_rules) > 20:
    self.root.after(0, lambda: self.log(f"  ... и ещё {len(selected_rules) - 20} правил", 'info'))
```

---

## 📄 Создаю финальное задание DS 020

**Файл:** `F:\TO_DBI\EXCHANGE\INBOX\DS_020_force_fix_rubricator_filtering.md`

```markdown
# DS 020: Принудительное исправление фильтрации рубрикатора

## Задача
Исправить фильтрацию правил в `_run_scan` и `_run_fix` — использовать ТОЛЬКО правила из выбранных файлов рубрикатора.

## Прямое исправление

### 1. Найти в `gui_app.py` блок кода (строки ~2310-2320):

```python
# Определение выбранных правил
selected_rules = [code for code, var in self.selected_rules.items() if var.get()]

# Фильтрация PlpCheck правил в зависимости от флага на форме
if not self.plpcheck_enabled_var.get():
    selected_rules = [r for r in selected_rules if r != 'PlpCheck']
```

### 2. Заменить на:

```python
# Определение выбранных файлов рубрикатора
selected_files = [code for code, var in self.selected_rules.items() if var.get()]

# Фильтрация PlpCheck
if not self.plpcheck_enabled_var.get():
    selected_files = [r for r in selected_files if r != 'PlpCheck']

# Сбор правил из выбранных файлов
selected_rules = []
if self.rubricator_prompts and self.rubricator_prompts.loaded:
    all_rules = self.rubricator_prompts.get_all_rules()
    for file_code in selected_files:
        for rule in all_rules:
            rule_code = rule.get('code', '')
            if file_code == 'PlpCheck' and rule_code.startswith('plpcheck.'):
                selected_rules.append(rule_code)
            elif file_code == 'v50' and (rule_code.startswith('v53.') or rule_code.startswith('v50.')):
                selected_rules.append(rule_code)
            elif file_code == 'тдс20240828' and rule_code.startswith('тдс20240828.'):
                selected_rules.append(rule_code)
            elif file_code == 'тклоик20240828' and rule_code.startswith('тклоик20240828.'):
                selected_rules.append(rule_code)
            elif file_code not in ['PlpCheck', 'v50', 'тдс20240828', 'тклоик20240828']:
                if file_code in rule_code:
                    selected_rules.append(rule_code)
    selected_rules = sorted(set(selected_rules))
else:
    # fallback
    selected_rules = selected_files
```

### 3. Обновить логирование (строки ~2350-2360)

**Было:**
```python
self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
for rule in selected_rules:
    self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
```

**Стало:**
```python
self.root.after(0, lambda: self.log(f"\nВЫБРАННЫЕ ФАЙЛЫ РУБРИКАТОРА:", 'highlight'))
for file_code in selected_files:
    self.root.after(0, lambda f=file_code: self.log(f"  [+] {f}", 'highlight'))

self.root.after(0, lambda: self.log(f"\nИСПОЛЬЗУЕМЫЕ ПРАВИЛА ({len(selected_rules)}):", 'info'))
for rule in selected_rules[:30]:
    self.root.after(0, lambda r=rule: self.log(f"  [+] {r}", 'info'))
if len(selected_rules) > 30:
    self.root.after(0, lambda: self.log(f"  ... и ещё {len(selected_rules) - 30} правил", 'info'))
```

### 4. Повторить для `_run_fix` (аналогичный блок кода)

## Ожидаемый результат
- [ ] При выборе только `PlpCheck` — сканируются только `plpcheck.*` правила
- [ ] Лог показывает выбранные файлы и правила
- [ ] Лог чистый и группированный

## Формат ответа
```json
{
  "task_id": "DS_020",
  "status": "success",
  "changes": [
    "Обновлена логика сбора правил в _run_scan",
    "Обновлена логика сбора правил в _run_fix",
    "Обновлено логирование выбранных правил"
  ]
}
```
```

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** вручную (если Koda не справится)
3. **Перезапустите АРМ**
4. **Проверьте** — выберите только `PlpCheck` и нажмите «Сканировать»
5. **Проверьте лог** — должны быть только `plpcheck.*` правила

---

## 📋 Если после DS 020 всё ещё не работает

Пришлите мне:
1. Содержимое `DS_020_response.json`
2. Или фрагмент лога после сканирования

Я помогу разобраться! 🔍