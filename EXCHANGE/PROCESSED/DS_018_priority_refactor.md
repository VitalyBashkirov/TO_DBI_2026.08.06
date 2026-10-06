# DS 018: Рефакторинг приоритетов — HIGH/MEDIUM/LOW вместо Приоритет 1/2/3/4

## Задача
Переработать интерфейс АРМ:
1. Убрать панель «Приоритеты» из бокса «2. Рубрикатор»
2. Увеличить высоту Treeview на 1 строку (чтобы все рубрикаторы были видны)
3. Добавить чекбоксы HIGH, MEDIUM, LOW в бокс «3. Опции сканирования и исправления. Логирование»

## Требования к изменениям

### 1. Удалить панель приоритетов из бокса 2

**Удалить код (строки ~562-570):**
```python
# Панель приоритетов справа от рубрикатора
priority_frame = ttk.Frame(rules_frame)
priority_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

self.priority_vars = {}
priorities = ['Приоритет 1', 'Приоритет 2', 'Приоритет 3', 'Приоритет 4']
for i, prio in enumerate(priorities):
    var = tk.BooleanVar(value=False)
    self.priority_vars[prio] = var
    ttk.Checkbutton(priority_frame, text=prio, variable=var, 
                  command=self._on_priority_change).grid(row=i, column=0, pady=2, sticky=tk.W)
Удалить метод _on_priority_change (строки ~575-595):

python
def _on_priority_change(self):
    ...
    self._filter_rules_tree(selected_priorities)
Удалить метод _filter_rules_tree (строки ~600-630):

python
def _filter_rules_tree(self, selected_priorities: list):
    ...
Удалить переменные:

self.priority_vars

self.priority_filter_active

self._saved_priorities

2. Увеличить высоту Treeview
Изменить строку 535:

python
# Было
self.rules_tree = ttk.Treeview(rules_frame, ..., height=3)

# Стало
self.rules_tree = ttk.Treeview(rules_frame, ..., height=4)
3. Добавить чекбоксы HIGH, MEDIUM, LOW в бокс 3
Добавить после строки с чекбоксом PlpCheck (~610-615):

python
# Чекбоксы приоритетов (HIGH/MEDIUM/LOW)
priority_frame = ttk.Frame(options_frame)
priority_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=(5,0))

ttk.Label(priority_frame, text="Фильтр по приоритету:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0,10))

self.priority_high_var = tk.BooleanVar(value=False)
self.priority_medium_var = tk.BooleanVar(value=False)
self.priority_low_var = tk.BooleanVar(value=False)

ttk.Checkbutton(priority_frame, text="HIGH", variable=self.priority_high_var,
                command=self._on_priority_filter_change).pack(side=tk.LEFT, padx=5)
ttk.Checkbutton(priority_frame, text="MEDIUM", variable=self.priority_medium_var,
                command=self._on_priority_filter_change).pack(side=tk.LEFT, padx=5)
ttk.Checkbutton(priority_frame, text="LOW", variable=self.priority_low_var,
                command=self._on_priority_filter_change).pack(side=tk.LEFT, padx=5)

# Метка для отображения выбранных приоритетов
self.priority_status_label = ttk.Label(priority_frame, text="", font=('Segoe UI', 9, 'italic'))
self.priority_status_label.pack(side=tk.LEFT, padx=(10,0))
4. Добавить метод фильтрации по приоритетам
python
def _on_priority_filter_change(self):
    """Обработка изменения чекбоксов HIGH/MEDIUM/LOW"""
    selected = []
    if self.priority_high_var.get():
        selected.append('HIGH')
    if self.priority_medium_var.get():
        selected.append('MEDIUM')
    if self.priority_low_var.get():
        selected.append('LOW')
    
    # Обновляем статус
    if selected:
        self.priority_status_label.config(text=f"Активны: {', '.join(selected)}", foreground='green')
    else:
        self.priority_status_label.config(text="Все приоритеты", foreground='gray')
    
    # Сохраняем для использования в сканировании
    self._selected_priorities = selected
    
    # Логируем
    self.log(f"Фильтр по приоритетам: {', '.join(selected) if selected else 'все'}", 'info')
5. Обновить методы сканирования и исправления
В _run_scan и _run_fix заменить использование self.priority_vars на self._selected_priorities:

python
# Было
selected_priorities = [p for p, var in self.priority_vars.items() if var.get()]

# Стало
selected_priorities = getattr(self, '_selected_priorities', [])
Маппинг для совместимости с PRIORITY_RULES:

python
# В начале _run_scan и _run_fix добавить:
priority_mapping = {
    'HIGH': 'Приоритет 1',
    'MEDIUM': 'Приоритет 2',
    'LOW': 'Приоритет 3'
}
selected_priorities = [priority_mapping.get(p, p) for p in getattr(self, '_selected_priorities', [])]
6. Обновить сохранение настроек
В save_settings добавить сохранение HIGH/MEDIUM/LOW:

python
settings = {
    ...
    'selected_priorities': getattr(self, '_selected_priorities', [])
}
В load_settings добавить загрузку:

python
saved_priorities = settings.get('selected_priorities', [])
self._selected_priorities = saved_priorities
# Установка чекбоксов
self.priority_high_var.set('HIGH' in saved_priorities)
self.priority_medium_var.set('MEDIUM' in saved_priorities)
self.priority_low_var.set('LOW' in saved_priorities)
self._on_priority_filter_change()
Ожидаемый результат
□ Панель «Приоритеты» удалена из бокса 2
□ Treeview показывает 4 строки (видны все рубрикаторы)
□ В боксе 3 появились чекбоксы HIGH, MEDIUM, LOW
□ При выборе HIGH/MEDIUM/LOW фильтруются правила
□ Настройки сохраняются и загружаются
Формат ответа
json
{
  "task_id": "DS_018",
  "status": "success",
  "changes": [
    "Удалена панель приоритетов из бокса 2",
    "Удалены методы _on_priority_change и _filter_rules_tree",
    "Удалены переменные self.priority_vars, self.priority_filter_active, self._saved_priorities",
    "Высота Treeview увеличена с 3 до 4 строк",
    "Добавлены чекбоксы HIGH, MEDIUM, LOW в бокс 3",
    "Добавлен метод _on_priority_filter_change",
    "Обновлены методы _run_scan и _run_fix для использования новых приоритетов",
    "Обновлены методы save_settings и load_settings"
  ],
  "test_results": {
    "treeview_height": "PASSED",
    "priority_filters": "PASSED",
    "settings_save_load": "PASSED"
  }
}
Дополнительно
После применения изменений удалите файл rubricator_priority_mapping.py, так как он больше не нужен.

text

---

## ✅ Файл создан!

**Путь:** `F:\TO_DBI\EXCHANGE\INBOX\DS_018_priority_refactor.md`

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `gui_app.py`
3. **Удалите** файл `rubricator_priority_mapping.py` (он больше не нужен)
4. **Перезапустите АРМ**
5. **Проверьте**, что в боксе 3 появились чекбоксы HIGH, MEDIUM, LOW

---

## 📋 Итоговый вид боксов

### Бокс 2 — Рубрикатор
+----------------------------------------------------------+
| 2. Рубрикатор. Выбор корректировок |
| +------------------------------------------------------+ |
| | Treeview (height=4, видны все рубрикаторы) | |
| | +------+--------+-----------------------------------+ | |
| | |Выбрано| Код | Полное имя файла | | |
| | |-------|--------|-----------------------------------| | |
| | | ✓ | v50 | Рекомендации по адаптации... | | |
| | | ✗ | PlpCheck| Правила PlpCheck (стиль кода) | | |
| | | ✓ | тдс... | Правила ТДС | | |
| | | ✓ | ткло...| Правила ТКЛОИК | | |
| | +------+--------+-----------------------------------+ | |
| +------------------------------------------------------+ |
+----------------------------------------------------------+

text

### Бокс 3 — Опции
+----------------------------------------------------------+
| 3. Опции сканирования и исправления. Логирование |
| ☐ Только модифицированные файлы |
| ☑ Сохранить структуру каталогов |
| Уровень логирования: [Минимальный ▼] |
| ☑ "Исправить код" — только пометить найденные теги |
| ☐ Добавлять PlpCheck-правила (стиль кода) |
| ☐ Верни только исправленный код без пояснений |
| ☑ Архивировать результат |
| |
| Фильтр по приоритету: [HIGH] [MEDIUM] [LOW] Все приоритеты |
+----------------------------------------------------------+

text

---

**-= Задание DS 018 готово к выполнению =-** 🚀