# DS 011: Исправление формирования Каталога результатов

## Задача
Исправить метод `on_source_dir_change()` так, чтобы при замене `PATCH_IN` → `PATCH_OUT` сохранялась вся структура подкаталогов после `PATCH_IN`.

## Проблема
**Сейчас:**
ИК: F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1
РК: F:\TO_DBI\PATCH_OUT\

text

**Должно быть:**
ИК: F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1
РК: F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1

text

## Требования

### 1. Исправить метод on_source_dir_change() в файле `F:\TO_DBI\SRC\gui_app.py`

**Текущий код (неправильный):**
```python
def on_source_dir_change(self, *args):
    source_dir = self.source_dir_var.get()
    if source_dir and "PATCH_IN" in source_dir:
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
Исправленный код:

python
def on_source_dir_change(self, *args):
    """
    Автоматическое обновление Каталога результатов при изменении Исходного каталога.
    Заменяет PATCH_IN на PATCH_OUT с сохранением всей структуры подкаталогов.
    """
    source_dir = self.source_dir_var.get().strip()
    
    if not source_dir:
        return
    
    if "PATCH_IN" in source_dir:
        # Заменяем PATCH_IN на PATCH_OUT с сохранением подкаталогов
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
        self.log(f"🔄 РК обновлён: {result_dir}")
    else:
        self.log("ℹ️ В ИК отсутствует 'PATCH_IN'. РК не изменён.")
2. Тестовые сценарии
ИК	Ожидаемый РК
F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1	F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1
F:\PROJECT\PATCH_IN\src\main\	F:\PROJECT\PATCH_OUT\src\main\
F:\DATA\PATCH_IN\	F:\DATA\PATCH_OUT\
F:\PATCH_IN\project\PATCH_IN\	F:\PATCH_OUT\project\PATCH_OUT\
Ожидаемый результат
□ РК сохраняет полный путь с подкаталогами
□ Все тестовые сценарии проходят
Формат ответа
json
{
  "task_id": "DS_011",
  "status": "success",
  "changes": [
    "Исправлен метод on_source_dir_change()"
  ],
  "test_results": {
    "scenario_1": "PASSED",
    "scenario_2": "PASSED",
    "scenario_3": "PASSED",
    "scenario_4": "PASSED"
  }
}
🚀 Выполнение
Файл DS_011_fix_result_dir_path.md создан в INBOX

Выполните команду: DS

Исправление будет применено к gui_app.py

📝 Итоговый полный код метода
python
def on_source_dir_change(self, *args):
    """
    Автоматическое обновление Каталога результатов при изменении Исходного каталога.
    Заменяет PATCH_IN на PATCH_OUT с сохранением всей структуры подкаталогов.
    """
    source_dir = self.source_dir_var.get().strip()
    
    if not source_dir:
        return
    
    if "PATCH_IN" in source_dir:
        # Заменяем PATCH_IN на PATCH_OUT с сохранением подкаталогов
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
        self.log(f"🔄 РК обновлён: {result_dir}")
    else:
        self.log("ℹ️ В ИК отсутствует 'PATCH_IN'. РК не изменён.")
text

---

## ✅ Файл создан!

Теперь:

1. **Проверьте** в проводнике:
F:\TO_DBI\EXCHANGE\INBOX\DS_011_fix_result_dir_path.md

text

2. **Выполните команду** в Koda:
DS

text

3. **Дождитесь ответа** в `OUTBOX\`

---

## 📋 Текущие задания в INBOX

| Файл | Задание | Статус |
|------|---------|--------|
| `DS_008_validate_directories.md` | Валидация ИК и РК | ⏳ Ожидает |
| `DS_009_directory_status_indicator.md` | Индикация статуса | ⏳ Ожидает |
| `DS_010_result_dir_history.md` | История РК | ⏳ Ожидает |
| `DS_011_fix_result_dir_path.md` | Исправление РК | ⏳ Ожидает |

---

**-= Задание DS 011 готово к выполнению =-** 🚀