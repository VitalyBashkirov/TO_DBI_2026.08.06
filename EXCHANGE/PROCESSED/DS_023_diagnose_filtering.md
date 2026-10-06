# DS 023: Диагностика фильтрации рубрикатора

## Задача
Добавить отладочный вывод в `scanner.py` и `gui_app.py` для диагностики фильтрации правил.

## Требования

### 1. В `scanner.py` метод `_load_patterns_from_rubricator()`

Добавить вывод:
```python
print(f"[DEBUG] selected_rules: {self.selected_rules}")
print(f"[DEBUG] rule_key: {rule_key}, file_code: {file_code}, file_code_lower: {file_code_lower}")
print(f"[DEBUG] allowed_prefixes: {allowed_prefixes}")
if file_code_lower not in allowed_prefixes:
    print(f"[DEBUG] ПРОПУЩЕНО: {rule_key}")
else:
    print(f"[DEBUG] ЗАГРУЖЕНО: {rule_key}")
2. В scanner.py метод scan_file()
Добавить вывод:

python
print(f"[DEBUG] scan_file: {file_path.name}, selected_rules: {self.selected_rules}")
3. В gui_app.py метод _run_scan()
Добавить вывод в лог:

python
self.log(f"[DEBUG] selected_files: {selected_files}", 'info')
self.log(f"[DEBUG] selected_rules (передано в сканер): {selected_rules}", 'info')
4. В scanner.py метод scan_directory()
Добавить вывод общего количества загруженных паттернов:

python
print(f"[DEBUG] Всего загружено паттернов: {len(self.PATTERNS)}")
Ожидаемый результат
□ В консоли видно, какие правила загружаются и пропускаются
□ В логе АРМ видно, какие правила переданы в сканер
□ Можно определить, где происходит сбой фильтрации
Формат ответа
json
{
  "task_id": "DS_023",
  "status": "success",
  "changes": [
    "Добавлен отладочный вывод в scanner.py",
    "Добавлен отладочный вывод в gui_app.py"
  ],
  "diagnosis": "Описание найденной проблемы"
}
text

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения**
3. **Перезапустите АРМ**
4. **Выберите только `PlpCheck`**
5. **Нажмите «Сканировать»**
6. **Посмотрите консоль** — там будут отладочные сообщения
7. **Пришлите мне**:
   - Отладочный вывод из консоли
   - Лог из АРМ
   - Отчёт

---

**-= Задание DS 023 создано =-** 🚀

