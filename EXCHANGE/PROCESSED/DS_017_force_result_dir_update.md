# DS 017: Принудительное обновление РК (убрать условие блокировки)

## Задача
Исправить метод `_auto_fill_result_dir()` в файле `F:\TO_DBI\SRC\gui_app.py` так, чтобы РК обновлялся **принудительно при каждом изменении ИК**, без проверки текущего значения.

## Проблема
В текущем коде (строки **1805–1830**) есть условие:

```python
# Проверяем текущее значение каталога результатов
current_result = self.result_dir_var.get()
if current_result:
    current_result = current_result.replace('/', BS).rstrip(BS)

# Обновляем только если каталог не указан или совпадает с текущим
if not current_result or current_result == result_str.rstrip(BS):
    self.result_dir_var.set(result_str)
    # ... остальной код
Это условие блокирует обновление, если в поле РК уже есть значение (даже если оно не совпадает с вычисленным).

Пример
Действие	ИК	Ожидаемый РК	Фактический РК
Ввод	F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1	F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1	F:\TO_DBI\PATCH_OUT\ (обрезано)
Причина: при первом вводе ИК поле РК уже содержит F:\TO_DBI\PATCH_OUT\, условие not current_result не срабатывает, и обновление не выполняется.

Решение
Убрать условие if not current_result or current_result == result_str.rstrip(BS): и всегда выполнять self.result_dir_var.set(result_str).

Исправленный код
Замените метод _auto_fill_result_dir (строки ~1789–1833) на:

python
def _auto_fill_result_dir(self, source_dir: Path):
    """Автоматическое формирование каталога результатов из исходного (DS 011).
    PATCH_IN + подкаталоги -> PATCH_OUT + те же подкаталоги (структура сохраняется)
    PATCH_OUT + подкаталоги -> PATCH_IN + те же подкаталоги
    """
    BS = chr(92)  # обратный слэш
    source_str = str(source_dir).replace('/', BS)
    
    # Сохраняем завершающий слэш (если был), работаем с путём без него
    trailing = BS if source_str.endswith(BS) else ''
    core = source_str.rstrip(BS).rstrip('/')
    
    if 'PATCH_IN' in core:
        # PATCH_IN\xxx -> PATCH_OUT\xxx (заменяем все вхождения PATCH_IN)
        result_str = core.replace('PATCH_IN', 'PATCH_OUT') + trailing
    elif 'PATCH_OUT' in core:
        # PATCH_OUT\xxx -> PATCH_IN\xxx (заменяем все вхождения PATCH_OUT)
        result_str = core.replace('PATCH_OUT', 'PATCH_IN') + trailing
    else:
        return None
    
    result_path = Path(result_str.rstrip(BS))
    
    # ============================================================
    # ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ РК (убрано условие блокировки)
    # ============================================================
    self.result_dir_var.set(result_str)
    
    # DS 014: проверка, что значение не было перезаписано другим кодом
    actual = self.result_dir_var.get()
    if actual != result_str:
        self.log(f"❌ ЗНАЧЕНИЕ БЫЛО ПЕРЕЗАПИСАНО! Ожидалось: '{result_str}', Получено: '{actual}'")
        self.log("📌 Ищите другой код, который меняет result_dir_var")
        # Принудительная установка через Entry (запасной механизм)
        if self.result_entry is not None:
            try:
                self.result_entry.delete(0, tk.END)
                self.result_entry.insert(0, result_str)
                self.result_dir_var.set(result_str)
                self.log(f"🔧 РК установлен принудительно через Entry: '{self.result_dir_var.get()}'")
            except Exception as e:
                self.log(f"Ошибка принудительной установки РК: {e}", 'error')
    
    return result_path
Что изменилось
Было	Стало
Обновление РК только если поле пустое или совпадает	Обновление РК всегда при наличии PATCH_IN/PATCH_OUT
Условие if not current_result or current_result == result_str.rstrip(BS):	Убрано
РК мог не обновиться при повторном вводе	РК обновляется при каждом изменении ИК
Тестовые сценарии
#	ИК	Ожидаемый РК
1	F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1	F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1
2	F:\PROJECT\PATCH_IN\src\main\	F:\PROJECT\PATCH_OUT\src\main\
3	F:\DATA\PATCH_IN\	F:\DATA\PATCH_OUT\
4	F:\PATCH_IN\project\PATCH_IN\file.txt	F:\PATCH_OUT\project\PATCH_OUT\file.txt
5	(изменение ИК с уже заполненным РК)	РК обновляется корректно
Ожидаемый результат
□ РК обновляется при каждом изменении ИК
□ При вводе F:\TO_DBI\PATCH_IN\patch_REPS_EXP_115_1 РК становится F:\TO_DBI\PATCH_OUT\patch_REPS_EXP_115_1
□ Все тестовые сценарии проходят
Формат ответа
json
{
  "task_id": "DS_017",
  "status": "success",
  "changes": [
    "Убрано условие `if not current_result or current_result == result_str.rstrip(BS):` в методе _auto_fill_result_dir()",
    "РК теперь обновляется принудительно при каждом изменении ИК",
    "Сохранена проверка перезаписи (DS 014)"
  ],
  "test_results": {
    "scenario_1": "PASSED",
    "scenario_2": "PASSED",
    "scenario_3": "PASSED",
    "scenario_4": "PASSED",
    "scenario_5": "PASSED"
  },
  "instructions": "Замените метод _auto_fill_result_dir() в gui_app.py на исправленный код и перезапустите АРМ"
}
Дополнительная информация
Файл: F:\TO_DBI\SRC\gui_app.py

Метод: _auto_fill_result_dir (строки ~1789–1833)

Причина проблемы: условие if not current_result or current_result == result_str.rstrip(BS) блокировало обновление РК, если поле уже содержало значение

Исправление: убрано условие, РК обновляется всегда

text

---

## ✅ Файл готов!

**Путь:** `F:\TO_DBI\EXCHANGE\INBOX\DS_017_force_result_dir_update.md`

Теперь вы можете выполнить команду `DS` в Koda. После получения ответа примените изменения и перезапустите АРМ. 🚀