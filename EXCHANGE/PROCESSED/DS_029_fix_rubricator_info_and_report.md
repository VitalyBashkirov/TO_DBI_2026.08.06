# DS 029: Отображение рубрикаторов при загрузке и исправление формата отчёта

## Задача
1. Добавить в Журнал выполнения при загрузке АРМ информацию о загруженных рубрикаторах
2. Исправить формат отчёта на дистрибутивный PlpCheck-стиль (одна строка на проблему)

---

## Часть 1: Отображение рубрикаторов при загрузке

### Файл: `F:\TO_DBI\SRC\gui_app.py`

### Метод `__init__` — после загрузки рубрикаторов добавить:

```python
# После self._populate_rules_tree() или self._load_rubricator_files()
self._log_rubricator_status()
Добавить метод _log_rubricator_status():
python
def _log_rubricator_status(self):
    """Вывод информации о загруженных рубрикаторах в Журнал выполнения"""
    self.log("=" * 60, 'info')
    self.log("ЗАГРУЖЕНЫ РУБРИКАТОРЫ:", 'highlight')
    self.log("=" * 60, 'info')
    
    total_rules = 0
    for code, var in self.selected_rules.items():
        status = "включён" if var.get() else "отключён"
        name = self.rubricator_files.get(code, code)
        self.log(f"  [{'+' if var.get() else '-'}] {code} ({status})", 'info')
        # Подсчёт правил для каждого файла
        if self.rubricator_prompts and self.rubricator_prompts.loaded:
            rules = [r for r in self.rubricator_prompts.get_all_rules() if r['code'].startswith(code.lower())]
            if rules:
                total_rules += len(rules)
                self.log(f"      Правил: {len(rules)}", 'debug')
    
    self.log("=" * 60, 'info')
    if self.rubricator_prompts and self.rubricator_prompts.loaded:
        self.log(f"Всего правил: {total_rules}", 'info')
    self.log("=" * 60, 'info')
Часть 2: Исправление формата отчёта
Файл: F:\TO_DBI\SRC\analyzer\scanner.py
Метод generate_report() — полностью заменить на:
python
def generate_report(self, output_path: Path):
    """Генерация отчёта в формате дистрибутивного PlpCheck-лога"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not self.issues:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Проблем не найдено.\n")
        return
    
    # Сбор всех проблем с метаданными
    lines = []
    
    for issue in self.issues:
        # Парсим класс и метод из файла
        class_name, method_name, section = self._parse_file_metadata(issue.file_path)
        
        # Формируем строку: {КЛАСС}.{МЕТОД}.{СЕКЦИЯ}:{СТРОКА} {ТИП}: {ОПИСАНИЕ}
        line = f"{class_name}.{method_name}.{section}:{issue.line_number} {issue.issue_type}: {issue.description}"
        lines.append(line)
    
    # Сортировка по классу, методу, строке
    lines.sort()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"PlpCheck Отчёт\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Всего проблем: {len(lines)}\n")
        f.write(f"Всего файлов: {len(set(i.file_path for i in self.issues))}\n\n")
        f.write("\n".join(lines))
Добавить метод _parse_file_metadata():
python
def _parse_file_metadata(self, file_path: str) -> Tuple[str, str, str]:
    """Парсинг имени класса, метода и секции из файла"""
    class_name = "UNKNOWN"
    method_name = "UNKNOWN"
    section = "PRIVATE"
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            # Ищем класс
            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                class_name = class_match.group(1)
            # Ищем метод
            method_match = re.search(r'method\s+(\w+)\s+is', content)
            if method_match:
                method_name = method_match.group(1)
            # Ищем секцию (execute/validate)
            if re.search(r'execute\s+is', content):
                section = "EXECUTE"
            elif re.search(r'validate\s+is', content):
                section = "VALIDATE"
    except Exception:
        pass
    
    return class_name, method_name, section
Ожидаемый результат
1. При загрузке АРМ в Журнале выполнения:
text
[XX:XX:XX] ============================================================
[XX:XX:XX] ЗАГРУЖЕНЫ РУБРИКАТОРЫ:
[XX:XX:XX] ============================================================
[XX:XX:XX]   [+] v53 (включён)
[XX:XX:XX]   [+] PlpCheck (включён)
[XX:XX:XX]   [-] тдс20240828 (отключён)
[XX:XX:XX]   [-] тклоик20240828 (отключён)
[XX:XX:XX] ============================================================
[XX:XX:XX] Всего правил: 342
[XX:XX:XX] ============================================================
2. Отчёт в формате PlpCheck:
text
PlpCheck Отчёт
Дата: 2026-09-06 12:47:29
Всего проблем: 323
Всего файлов: 1

HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 METH_PARAM_AND_VAR_NAMES: Параметры и переменные
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 SYNTAX_ERROR: Весь код
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 SYNTAX_ERROR: Весь код
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 VARIABLE_SAME_NAME: Имена
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 VARIABLE_SAME_NAME: Имена
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 WRONG_LOCAL_PREFIX: Локальные объекты
HOOK_BANK.REPS_EXP_115_1.PRIVATE:2 SYNTAX_ERROR: Весь код
HOOK_BANK.REPS_EXP_115_1.PRIVATE:3 NO_RECURSION_COMMENT: Вызов функции/процедуры
HOOK_BANK.REPS_EXP_115_1.PRIVATE:3 PURE_SQL_DBLINK: DBLink
...
Формат ответа
json
{
  "task_id": "DS_029",
  "status": "success",
  "changes": [
    "Добавлен вывод рубрикаторов при загрузке АРМ",
    "Изменён формат отчёта на PlpCheck-стиль (одна строка на проблему)"
  ],
  "test_results": {
    "rubricator_info": "PASSED",
    "report_format": "PASSED"
  }
}
Инструкция
Примените изменения в gui_app.py и scanner.py

Перезапустите АРМ

Проверьте Журнал при загрузке — должны быть рубрикаторы

Выполните сканирование и проверьте отчёт — формат КЛАСС.МЕТОД.СЕКЦИЯ:СТРОКА ТИП: ОПИСАНИЕ

text

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `gui_app.py` и `scanner.py`
3. **Перезапустите АРМ**
4. **Проверьте**:
   - Журнал при загрузке — видны рубрикаторы
   - Отчёт — формат PlpCheck-стиля

---

**-= Задание DS 029 создано =-** 🚀