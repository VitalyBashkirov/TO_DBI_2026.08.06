# DS 010: История изменений Каталога результатов

## Задача
Добавить логирование всех изменений РК с возможностью просмотра истории.

## Требования

### 1. Файл истории
Создать `F:\TO_DBI\EXCHANGE\result_dir_history.json`:

```json
{
  "history": [
    {
      "timestamp": "2026-09-05T12:00:00",
      "source_dir": "F:\\PROJECT\\PATCH_IN\\",
      "result_dir": "F:\\PROJECT\\PATCH_OUT\\",
      "action": "auto_update|manual",
      "user": "user_name"
    }
  ]
}
```

### 2. Метод log_result_dir_change()
```python
import json
from datetime import datetime

def log_result_dir_change(self, source_dir, result_dir, action="auto_update"):
    """Логирование изменения РК"""
    history_file = r"F:\TO_DBI\EXCHANGE\result_dir_history.json"
    
    # Загрузка существующей истории
    history = {"history": []}
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    # Добавление записи
    history["history"].append({
        "timestamp": datetime.now().isoformat(),
        "source_dir": source_dir,
        "result_dir": result_dir,
        "action": action,
        "user": os.getenv("USERNAME", "unknown")
    })
    
    # Ограничение истории (последние 100 записей)
    if len(history["history"]) > 100:
        history["history"] = history["history"][-100:]
    
    # Сохранение
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    self.log(f"📝 Изменение РК зафиксировано: {result_dir}")
```

### 3. Кнопка «История РК»
Добавить кнопку для просмотра истории:

```python
def show_result_dir_history(self):
    """Показать историю изменений РК"""
    history_file = r"F:\TO_DBI\EXCHANGE\result_dir_history.json"
    
    if not os.path.exists(history_file):
        self.log("📭 История РК пуста")
        return
    
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    if not history["history"]:
        self.log("📭 История РК пуста")
        return
    
    self.log("=" * 60)
    self.log("📋 ИСТОРИЯ ИЗМЕНЕНИЙ РК")
    self.log("=" * 60)
    
    for i, entry in enumerate(history["history"][-10:], 1):
        self.log(f"\n{i}. [{entry['timestamp']}]")
        self.log(f"   ИК: {entry['source_dir']}")
        self.log(f"   РК: {entry['result_dir']}")
        self.log(f"   Действие: {entry['action']}")
        self.log(f"   Пользователь: {entry['user']}")
```

### 4. Интеграция с on_source_dir_change()
```python
def on_source_dir_change(self, *args):
    source_dir = self.source_dir_var.get()
    if source_dir and "PATCH_IN" in source_dir:
        old_result = self.result_dir_var.get()
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
        
        # Логируем только если РК изменился
        if result_dir != old_result:
            self.log_result_dir_change(source_dir, result_dir)
            self.log(f"🔄 Автоматически обновлён РК: {result_dir}")
```

## Ожидаемый результат
- [ ] История сохраняется в result_dir_history.json
- [ ] Кнопка «История РК» отображает последние 10 записей
- [ ] Изменения логируются автоматически

## Формат ответа
```json
{
  "task_id": "DS_010",
  "status": "success",
  "changes": [
    "Добавлен файл result_dir_history.json",
    "Добавлен метод log_result_dir_change()",
    "Добавлена кнопка «История РК»",
    "Обновлён метод on_source_dir_change()"
  ],
  "history_file": "F:\\TO_DBI\\EXCHANGE\\result_dir_history.json"
}
```
