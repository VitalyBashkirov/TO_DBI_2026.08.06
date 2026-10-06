# DS 008: Валидация Исходного каталога и Каталога результатов

## Задача
Добавить в АРМ валидацию путей ИК и РК с проверкой существования и доступности.

## Требования

### 1. Метод validate_directories()
Добавить в `gui_app.py` метод:

```python
def validate_directories(self):
    """Проверка существования и доступности ИК и РК"""
    source_dir = self.source_dir_var.get().strip()
    result_dir = self.result_dir_var.get().strip()
    
    errors = []
    warnings = []
    
    # Проверка ИК
    if not source_dir:
        errors.append("Исходный каталог не указан")
    elif not os.path.exists(source_dir):
        errors.append(f"Исходный каталог не существует: {source_dir}")
    elif not os.access(source_dir, os.R_OK):
        errors.append(f"Нет доступа на чтение к ИК: {source_dir}")
    
    # Проверка РК
    if result_dir:
        if not os.path.exists(result_dir):
            warnings.append(f"РК не существует, будет создан: {result_dir}")
        elif not os.access(result_dir, os.W_OK):
            errors.append(f"Нет доступа на запись в РК: {result_dir}")
    else:
        warnings.append("РК не указан, будет использован ИК")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
```

### 2. Интеграция в run_scan()
Перед запуском сканирования вызывать валидацию:

```python
def run_scan(self):
    """Запуск сканирования с валидацией"""
    validation = self.validate_directories()
    
    if not validation["valid"]:
        for error in validation["errors"]:
            self.log(f"❌ {error}", level="error")
        return
    
    for warning in validation["warnings"]:
        self.log(f"⚠️ {warning}", level="warning")
    
    # ... остальной код сканирования
```

### 3. Визуальная индикация
Добавить изменение цвета полей при валидации:

```python
def update_field_colors(self):
    """Обновление цвета полей ввода на основе валидации"""
    validation = self.validate_directories()
    
    # ИК
    if validation["valid"] and os.path.exists(self.source_dir_var.get()):
        self.source_entry.config(bg="#d4edda")  # зелёный
    elif validation["errors"]:
        self.source_entry.config(bg="#f8d7da")  # красный
    else:
        self.source_entry.config(bg="#fff3cd")  # жёлтый
    
    # РК
    result_dir = self.result_dir_var.get()
    if result_dir and os.path.exists(result_dir):
        self.result_entry.config(bg="#d4edda")  # зелёный
    elif result_dir:
        self.result_entry.config(bg="#fff3cd")  # жёлтый (будет создан)
    else:
        self.result_entry.config(bg="#f8d7da")  # красный (не указан)
```

## Ожидаемый результат
- [ ] Метод validate_directories() добавлен
- [ ] Валидация интегрирована в run_scan()
- [ ] Поля ИК/РК меняют цвет при изменении

## Формат ответа
```json
{
  "task_id": "DS_008",
  "status": "success",
  "changes": [
    "Добавлен метод validate_directories()",
    "Обновлён метод run_scan()",
    "Добавлена визуальная индикация полей"
  ],
  "test_results": {
    "empty_source": "PASSED",
    "non_existent_source": "PASSED",
    "valid_paths": "PASSED"
  }
}
```
