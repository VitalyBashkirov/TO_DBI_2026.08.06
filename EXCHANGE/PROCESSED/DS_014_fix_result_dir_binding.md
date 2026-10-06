# DS 014: Исправление привязки РК к полю ввода

## Задача
Найти и исправить причину, почему `self.result_dir_var.set()` не обновляет поле ввода РК.

## Диагностика
При вычислении РК:
- `replace()` даёт правильный результат: `F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1`
- Альтернативный результат правильный: `F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1`
- `self.result_dir_var.set()` вызывается
- НО в поле ввода РК отображается: `F:\TO_DBI\PATCH_OUT\`

## Возможные причины

### 1. Поле ввода НЕ связано с result_dir_var
В `gui_app.py` должно быть:
```python
self.result_dir_var = tk.StringVar()
self.result_entry = tk.Entry(
    self.main_frame,
    textvariable=self.result_dir_var,  # ← ЭТО ОБЯЗАТЕЛЬНО!
    width=60
)
2. Есть второй метод, перезаписывающий РК
Поискать в коде:

self.result_dir_var.set(

self.result_entry.insert(

self.result_entry.delete(

result_dir_var.set(

result_entry.config(text=

3. Событие после изменения
Проверить привязки событий:

bind('<FocusOut>')

bind('<KeyRelease>')

trace_add('write') у result_dir_var

Требования
1. Найти и показать код создания поля РК
Показать фрагмент gui_app.py с созданием result_entry.

2. Проверить наличие textvariable
Если textvariable отсутствует — исправить.

3. Добавить проверку в on_source_dir_change
python
def on_source_dir_change(self, *args):
    source_dir = self.source_dir_var.get().strip()
    if source_dir and "PATCH_IN" in source_dir:
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
        
        # === ДОБАВИТЬ ПРОВЕРКУ ===
        actual_value = self.result_dir_var.get()
        self.log(f"🔍 Установлено значение: '{result_dir}'")
        self.log(f"🔍 Фактическое значение: '{actual_value}'")
        if result_dir != actual_value:
            self.log("❌ ЗНАЧЕНИЕ БЫЛО ПЕРЕЗАПИСАНО!")
            self.log("📌 Ищите другой код, который меняет result_dir_var")
4. Принудительная установка через Entry (если нужно)
Если textvariable не работает, использовать прямой доступ:

python
self.result_entry.delete(0, tk.END)
self.result_entry.insert(0, result_dir)
Ожидаемый результат
□ Поле РК обновляется корректно
□ В Журнале видно, если значение перезаписывается
Формат ответа
json
{
  "task_id": "DS_014",
  "status": "success",
  "current_binding": "код создания result_entry",
  "fixed_binding": "исправленный код",
  "changes": [
    "Добавлена/исправлена привязка textvariable",
    "Добавлена проверка в on_source_dir_change",
    "Добавлена принудительная установка через Entry"
  ]
}
🚀 Выполнение
Файл DS_014_fix_result_dir_binding.md создан в INBOX

Выполните команду: DS

Исправления будут применены к gui_app.py

text

---

## 📋 Резюме

| Проблема | Решение |
|----------|---------|
| Вычисление правильное, но поле не обновляется | Проверить `textvariable` у `result_entry` |
| Поле обновляется, но потом перезаписывается | Найти другой код, меняющий `result_dir_var` |
| Ничего не помогает | Использовать прямой доступ через `result_entry.delete/insert` |

---

## 🔧 Немедленное исправление (вручную)

1. **Откройте** `F:\TO_DBI\SRC\gui_app.py`

2. **Найдите** создание `result_entry` (поиск: `result_entry = tk.Entry`)

3. **Проверьте**, есть ли там `textvariable=self.result_dir_var`

4. **Если нет** — добавьте:
   ```python
   self.result_entry = tk.Entry(
       self.main_frame,
       textvariable=self.result_dir_var,  # ← ДОБАВИТЬ
       width=60
   )
В методе on_source_dir_change после set() добавьте принудительную установку:

python
self.result_dir_var.set(result_dir)
self.result_entry.delete(0, tk.END)
self.result_entry.insert(0, result_dir)
-= Задание DS 014 готово к выполнению =- 🚀