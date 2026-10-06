# DS 012: Исправление формирования РК (гарантированное)

## Задача
Полностью переписать метод `on_source_dir_change()` в `F:\TO_DBI\SRC\gui_app.py` так, чтобы при замене `PATCH_IN` → `PATCH_OUT` сохранялась вся структура подкаталогов после `PATCH_IN`.

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

## Причина
В текущем коде используется обрезка пути вместо полной замены:
- ❌ `source_dir[:patch_index] + "PATCH_OUT"` — теряется хвост
- ✅ `source_dir.replace("PATCH_IN", "PATCH_OUT")` — сохраняется хвост

## Требования

### 1. Найти и показать текущий код
Найти в `gui_app.py` метод `on_source_dir_change()` и показать его полное содержимое.

### 2. Заменить на исправленный код
```python
def on_source_dir_change(self, *args):
    """
    Автоматическое обновление Каталога результатов при изменении Исходного каталога.
    Заменяет PATCH_IN на PATCH_OUT с сохранением всей структуры подкаталогов.
    """
    source_dir = self.source_dir_var.get().strip()
    
    if not source_dir:
        return
    
    if "PATCH_IN" in source_dir:
        # Заменяем ВСЕ вхождения PATCH_IN на PATCH_OUT
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
        self.log(f"🔄 РК обновлён: {result_dir}")
    else:
        self.log("ℹ️ В ИК отсутствует 'PATCH_IN'. РК не изменён.")
3. Проверить, что метод вызывается
Убедиться, что в __init__ или create_widgets есть привязка:

python
self.source_dir_var.trace_add('write', self.on_source_dir_change)
4. Добавить резервный метод (если нужно)
Если основной метод не срабатывает, добавить альтернативный:

python
def update_result_dir_from_source(self, source_dir):
    """Резервный метод обновления РК"""
    if source_dir and "PATCH_IN" in source_dir:
        return source_dir.replace("PATCH_IN", "PATCH_OUT")
    return source_dir
Тестовые сценарии
ИК	Ожидаемый РК
F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1	F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1
F:\PROJECT\PATCH_IN\src\main\	F:\PROJECT\PATCH_OUT\src\main\
F:\DATA\PATCH_IN\	F:\DATA\PATCH_OUT\
F:\PATCH_IN\project\PATCH_IN\file.txt	F:\PATCH_OUT\project\PATCH_OUT\file.txt
Ожидаемый результат
□ Метод on_source_dir_change() полностью переписан
□ При вводе ИК с PATCH_IN РК получает полный путь
□ Все тестовые сценарии проходят
Формат ответа
json
{
  "task_id": "DS_012",
  "status": "success",
  "current_code": "текущий код метода",
  "fixed_code": "исправленный код метода",
  "changes": [
    "Метод on_source_dir_change() переписан с использованием replace()",
    "Добавлена проверка на пустую строку",
    "Добавлено логирование"
  ],
  "test_results": {
    "scenario_1": "PASSED",
    "scenario_2": "PASSED",
    "scenario_3": "PASSED",
    "scenario_4": "PASSED"
  },
  "instructions": "Скопируйте fixed_code и замените им текущий метод в gui_app.py"
}
Дополнительно
Если в файле есть другие методы, которые могут влиять на РК (например, update_result_dir, set_result_dir), показать их и при необходимости исправить.

text

---

## ✅ Файл создан!

**Путь:** `F:\TO_DBI\EXCHANGE\INBOX\DS_012_fix_result_dir_final.md`

---

## 🚀 Что делать дальше

1. **Выполните команду** в Koda:
DS

text

2. **Дождитесь ответа** в `OUTBOX\DS_012_response.json`

3. **Примените исправления** из ответа

4. **Протестируйте**:
ИК: F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1
РК: F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1 ✅

text

---

## 📋 Текущие задания в INBOX

| Файл | Задание | Статус |
|------|---------|--------|
| `DS_008_validate_directories.md` | Валидация ИК и РК | ⏳ Ожидает |
| `DS_009_directory_status_indicator.md` | Индикация статуса | ⏳ Ожидает |
| `DS_010_result_dir_history.md` | История РК | ⏳ Ожидает |
| `DS_011_fix_result_dir_path.md` | Исправление РК (первая версия) | ⏳ Ожидает |
| `DS_012_fix_result_dir_final.md` | Исправление РК (гарантированное) | ⏳ Ожидает |

---

**-= Задание DS 012 готово к выполнению =-** 🚀