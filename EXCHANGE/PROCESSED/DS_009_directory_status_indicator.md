# DS 009: Индикация статуса каталогов

## Задача
Добавить в АРМ визуальную индикацию статуса ИК и РК с помощью цветовых меток и иконок.

## Требования

### 1. Добавить метки статуса
Рядом с полями ИК и РК добавить текстовые метки со статусом:

```python
# В __init__ или create_widgets
self.source_status_label = tk.Label(self.main_frame, text="", font=("Segoe UI", 9))
self.source_status_label.pack(side=tk.RIGHT, padx=5)

self.result_status_label = tk.Label(self.main_frame, text="", font=("Segoe UI", 9))
self.result_status_label.pack(side=tk.RIGHT, padx=5)
```

### 2. Метод update_status_indicators()
```python
def update_status_indicators(self):
    """Обновление индикаторов статуса каталогов"""
    
    def get_status_text(path, is_source=True):
        if not path:
            return "⚠️ не указан", "#ffc107"  # жёлтый
        
        if is_source:
            if not os.path.exists(path):
                return "❌ не существует", "#dc3545"  # красный
            elif not os.access(path, os.R_OK):
                return "🔒 нет доступа", "#dc3545"  # красный
            else:
                return "✅ доступен", "#28a745"  # зелёный
        else:
            if not os.path.exists(path):
                return "📁 будет создан", "#ffc107"  # жёлтый
            elif not os.access(path, os.W_OK):
                return "🔒 нет доступа", "#dc3545"  # красный
            else:
                return "✅ доступен", "#28a745"  # зелёный
    
    # Обновление ИК
    source_dir = self.source_dir_var.get()
    text, color = get_status_text(source_dir, True)
    self.source_status_label.config(text=text, fg=color)
    
    # Обновление РК
    result_dir = self.result_dir_var.get()
    if not result_dir:
        result_dir = source_dir  # если РК не указан, используем ИК
    text, color = get_status_text(result_dir, False)
    self.result_status_label.config(text=text, fg=color)
```

### 3. Привязка к событиям
```python
# При создании полей
self.source_dir_var.trace_add('write', lambda *args: self.update_status_indicators())
self.result_dir_var.trace_add('write', lambda *args: self.update_status_indicators())

# При запуске АРМ
self.update_status_indicators()
```

## Ожидаемый результат
- [ ] Метки статуса отображаются рядом с полями
- [ ] Цвет меняется в зависимости от состояния
- [ ] Обновляется при изменении путей

## Формат ответа
```json
{
  "task_id": "DS_009",
  "status": "success",
  "changes": [
    "Добавлены метки статуса",
    "Добавлен метод update_status_indicators()",
    "Настроена привязка событий"
  ],
  "status_colors": {
    "green": "доступен",
    "yellow": "не указан / будет создан",
    "red": "не существует / нет доступа"
  }
}
```
