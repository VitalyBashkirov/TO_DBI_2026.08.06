# DS 013: Отладка вычисления РК с выводом в Журнал

## Задача
Добавить детальное логирование в метод `on_source_dir_change()` для отладки вычисления РК.

## Текущая проблема
При вводе:
ИК: F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1

text
Получается:
РК: F:\TO_DBI\PATCH_OUT\

text
А должно быть:
РК: F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1

text

## Требования

### 1. Найти метод on_source_dir_change()
В файле `F:\TO_DBI\SRC\gui_app.py` найти метод:

```python
def on_source_dir_change(self, *args):
    ...
2. Добавить детальное логирование
Исправленный код с логированием:

python
def on_source_dir_change(self, *args):
    """
    Автоматическое обновление Каталога результатов при изменении Исходного каталога.
    Заменяет PATCH_IN на PATCH_OUT с сохранением всей структуры подкаталогов.
    """
    # === ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ===
    self.log("=" * 60)
    self.log("🔍 ВЫЧИСЛЕНИЕ РК")
    self.log("=" * 60)
    
    # 1. Получаем значение ИК
    source_dir = self.source_dir_var.get().strip()
    self.log(f"📁 ИК (исходный): '{source_dir}'")
    self.log(f"📏 Длина ИК: {len(source_dir)}")
    
    if not source_dir:
        self.log("⚠️ ИК пуст, РК не изменяется")
        return
    
    # 2. Проверяем наличие PATCH_IN
    has_patch_in = "PATCH_IN" in source_dir
    self.log(f"🔎 Найдено 'PATCH_IN': {has_patch_in}")
    
    if has_patch_in:
        # 3. Находим позицию PATCH_IN
        patch_index = source_dir.find("PATCH_IN")
        self.log(f"📍 Позиция 'PATCH_IN': {patch_index}")
        
        # 4. Показываем части пути
        before = source_dir[:patch_index]
        after = source_dir[patch_index + len("PATCH_IN"):]
        self.log(f"📂 До 'PATCH_IN': '{before}'")
        self.log(f"📂 После 'PATCH_IN': '{after}'")
        
        # 5. Выполняем замену
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.log(f"🔄 Результат replace(): '{result_dir}'")
        
        # 6. Альтернативный способ (для проверки)
        alt_result = before + "PATCH_OUT" + after
        self.log(f"🔄 Альтернативный результат: '{alt_result}'")
        
        # 7. Устанавливаем РК
        self.result_dir_var.set(result_dir)
        self.log(f"✅ РК установлен: '{result_dir}'")
        
        # 8. Проверяем, что установилось
        actual_result = self.result_dir_var.get()
        self.log(f"🔍 Фактическое значение РК: '{actual_result}'")
        
        # 9. Сравниваем ожидание и реальность
        if result_dir == actual_result:
            self.log("✅ РК установлен корректно")
        else:
            self.log(f"❌ РАСХОЖДЕНИЕ! Ожидалось: '{result_dir}', Получено: '{actual_result}'")
        
        # 10. Вывод в журнал изменений (как просили)
        self.log(f"📝 ВЫЧИСЛЕННЫЙ РК: {result_dir}")
        
    else:
        self.log("ℹ️ В ИК отсутствует 'PATCH_IN'. РК не изменён.")
    
    self.log("=" * 60)
    self.log("🔍 КОНЕЦ ВЫЧИСЛЕНИЯ РК")
    self.log("=" * 60)
3. Что должно появиться в Журнале
При вводе ИК F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1 в Журнале должно быть:

text
============================================================
🔍 ВЫЧИСЛЕНИЕ РК
============================================================
📁 ИК (исходный): 'F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1'
📏 Длина ИК: 43
🔎 Найдено 'PATCH_IN': True
📍 Позиция 'PATCH_IN': 12
📂 До 'PATCH_IN': 'F:\TO_DBI\'
📂 После 'PATCH_IN': '\patch_REPS_EXP_115_1'
🔄 Результат replace(): 'F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1'
🔄 Альтернативный результат: 'F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1'
✅ РК установлен: 'F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1'
🔍 Фактическое значение РК: 'F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1'
✅ РК установлен корректно
📝 ВЫЧИСЛЕННЫЙ РК: F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1
============================================================
🔍 КОНЕЦ ВЫЧИСЛЕНИЯ РК
============================================================
Ожидаемый результат
□ При каждом изменении ИК в Журнал выводится детальная информация
□ Видно, какая часть кода работает не так
□ Можно определить, где теряется хвост пути
Формат ответа
json
{
  "task_id": "DS_013",
  "status": "success",
  "changes": [
    "В метод on_source_dir_change() добавлено детальное логирование",
    "Добавлен вывод вычисленного РК в Журнал"
  ],
  "log_output": "ожидаемый вывод в Журнале",
  "instructions": "Замените метод on_source_dir_change() на код с логированием"
}
Дополнительно
Если метод on_source_dir_change() вообще не вызывается, проверить привязку:

python
# В __init__ или create_widgets должно быть:
self.source_dir_var.trace_add('write', self.on_source_dir_change)
Если привязки нет — добавить её.

text

---

## 🚀 Что делать дальше

1. **Файл создан:** `F:\TO_DBI\EXCHANGE\INBOX\DS_013_debug_result_dir.md`

2. **Выполните команду** в Koda:
DS

text

3. **Получите ответ** в `OUTBOX\DS_013_response.json`

4. **Примените изменения** в `gui_app.py`

5. **Протестируйте** и посмотрите, что появится в Журнале

---

## 📋 Текущие задания в INBOX

| Файл | Задание | Приоритет |
|------|---------|-----------|
| `DS_008_validate_directories.md` | Валидация ИК и РК | HIGH |
| `DS_009_directory_status_indicator.md` | Индикация статуса | MEDIUM |
| `DS_010_result_dir_history.md` | История РК | LOW |
| `DS_011_fix_result_dir_path.md` | Исправление РК (v1) | HIGH |
| `DS_012_fix_result_dir_final.md` | Исправление РК (v2) | HIGH |
| `DS_013_debug_result_dir.md` | Отладка РК | HIGH |

---

## 📝 Примечание

**Где искать код вычисления ИК в `gui_app.py`:**

1. Откройте `F:\TO_DBI\SRC\gui_app.py`
2. Найдите `def on_source_dir_change`
3. Если такого метода нет — значит проблема в другом месте
4. Если есть — его нужно заменить на код с логированием

**-= Задание DS 013 готово к выполнению =-** 🚀