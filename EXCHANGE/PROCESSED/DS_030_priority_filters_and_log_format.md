# DS 030: Информация о фильтрах по приоритету и улучшение формата лога

## Задача
1. Добавить в Журнал выполнения при загрузке АРМ информацию о фильтрах по приоритету
2. Подсветить строки лога цветом
3. Удалить дублирующиеся строки

---

## Часть 1: Информация о фильтрах по приоритету при загрузке

### Файл: `F:\TO_DBI\SRC\gui_app.py`

### В методе `_log_rubricator_status()` добавить информацию о фильтрах:

```python
def _log_rubricator_status(self):
    """Вывод информации о загруженных рубрикаторах и фильтрах в Журнал выполнения"""
    self.log("=" * 60, 'info')
    self.log("ЗАГРУЖЕНЫ РУБРИКАТОРЫ:", 'highlight')
    self.log("=" * 60, 'info')
    
    total_rules = 0
    for code, var in self.selected_rules.items():
        status = "включён" if var.get() else "отключён"
        name = self.rubricator_files.get(code, code)
        self.log(f"  [{'+' if var.get() else '-'}] {code} ({status})", 'info')
        if self.rubricator_prompts and self.rubricator_prompts.loaded:
            rules = [r for r in self.rubricator_prompts.get_all_rules() if r['code'].startswith(code.lower())]
            if rules:
                total_rules += len(rules)
                self.log(f"      Правил: {len(rules)}", 'debug')
    
    self.log("=" * 60, 'info')
    if self.rubricator_prompts and self.rubricator_prompts.loaded:
        self.log(f"Всего правил: {total_rules}", 'info')
    self.log("=" * 60, 'info')
    
    # ========== ИНФОРМАЦИЯ О ФИЛЬТРАХ ПО ПРИОРИТЕТУ ==========
    selected_priorities = [p for p, var in self.priority_vars.items() if var.get()]
    
    if selected_priorities:
        self.log("=" * 60, 'info')
        self.log("ФИЛЬТРЫ ПО ПРИОРИТЕТУ:", 'highlight')
        self.log("=" * 60, 'info')
        for prio in selected_priorities:
            self.log(f"  ★ {prio}", 'highlight')
        
        # Показываем количество правил по каждому приоритету
        from rubricator_priority_mapping import PRIORITY_RULES
        for prio in selected_priorities:
            if prio in PRIORITY_RULES:
                count = len(PRIORITY_RULES[prio])
                self.log(f"     Правил в {prio}: {count}", 'info')
        
        self.log("=" * 60, 'info')
    else:
        self.log("=" * 60, 'info')
        self.log("ФИЛЬТРЫ ПО ПРИОРИТЕТУ: не выбраны (используются все правила)", 'info')
        self.log("=" * 60, 'info')
Часть 2: Подсветка строк лога цветом и удаление дубликатов
Файл: F:\TO_DBI\SRC\analyzer\scanner.py
Метод generate_report() — добавить обработку дубликатов:
python
def generate_report(self, output_path: Path):
    """Генерация отчёта в формате дистрибутивного PlpCheck-лога с цветом и без дубликатов"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not self.issues:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Проблем не найдено.\n")
        return
    
    # Сбор всех проблем с метаданными
    lines = []
    
    for issue in self.issues:
        class_name, method_name, section = self._parse_file_metadata(issue.file_path)
        
        # Формируем строку: {КЛАСС}.{МЕТОД}.{СЕКЦИЯ}:{СТРОКА} {ТИП}: {ОПИСАНИЕ} | ПЛАН: {ПЛАН}
        plan = self._get_plan(issue)
        line = f"{class_name}.{method_name}.{section}:{issue.line_number} {issue.issue_type}: {issue.description} | ПЛАН: {plan}"
        lines.append(line)
    
    # Сортировка по классу, методу, строке
    lines.sort()
    
    # Удаление дубликатов (сохраняем порядок)
    unique_lines = []
    seen = set()
    for line in lines:
        if line not in seen:
            unique_lines.append(line)
            seen.add(line)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("PlpCheck Отчёт\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Всего проблем: {len(lines)}\n")
        f.write(f"Уникальных проблем: {len(unique_lines)}\n")
        f.write(f"Всего файлов: {len(set(i.file_path for i in self.issues))}\n\n")
        f.write("\n".join(unique_lines))
Добавить метод _get_plan() для формирования ПЛАНА:
python
def _get_plan(self, issue) -> str:
    """Формирование плана исправления"""
    issue_type = issue.issue_type
    
    if 'bad_prefix' in issue_type:
        return "Переименовать с правильным префиксом"
    if 'not_mentioned' in issue_type:
        return "Удалить объявление (переменная не используется)"
    if 'code_in_comment' in issue_type:
        return "Удалить закомментированный код"
    if 'wrong_method_syntax' in issue_type:
        return "Исправить на ::[RUNTIME].[STDIO]"
    if 'prefix_type_in_var_name' in issue_type:
        return "Добавить префикс типа"
    if 'syntax_error' in issue_type:
        return "Исправить синтаксическую ошибку"
    if 'pure_sql_dblink' in issue_type:
        return "Заменить на прикладную таблицу"
    if 'pure_udf' in issue_type:
        return "Вынести UDF в процедурный код"
    if 'outer_join' in issue_type:
        return "Заменить на ANSI JOIN"
    if 'rownum' in issue_type:
        return "Заменить на FETCH"
    if 'connectby' in issue_type or 'CONNECT_BY' in issue_type:
        return "Заменить на WITH RECURSIVE"
    if 'nvl' in issue_type.lower():
        return "Заменить на COALESCE"
    if 'decode' in issue_type.lower():
        return "Заменить на CASE"
    
    return "Исправить по описанию"
Цветовая подсветка в выводе:
В gui_app.py при отображении строк лога использовать теги:

python
# В методе, который выводит строки лога
def display_log_line(self, line: str):
    """Вывод строки лога с цветовой подсветкой"""
    # Подсветка номера строки (зелёный)
    # Подсветка типа правила (жёлтый/оранжевый)
    # Подсветка ПЛАНА (синий)
    
    # Пример использования тегов:
    # self.log_text.insert(tk.END, f"{class_name}.{method_name}.{section}:", 'class_method')
    # self.log_text.insert(tk.END, f"{line_number} ", 'line_number')
    # self.log_text.insert(tk.END, f"{issue_type}: ", 'issue_type')
    # self.log_text.insert(tk.END, f"{description} | ", 'description')
    # self.log_text.insert(tk.END, f"ПЛАН: {plan}", 'plan')
    
    # Регистрация тегов (в __init__):
    # self.log_text.tag_configure('class_method', foreground='#0066cc')
    # self.log_text.tag_configure('line_number', foreground='#008000', font=('Consolas', 9, 'bold'))
    # self.log_text.tag_configure('issue_type', foreground='#cc6600')
    # self.log_text.tag_configure('description', foreground='#000000')
    # self.log_text.tag_configure('plan', foreground='#cc0000', font=('Consolas', 9, 'bold'))
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
[XX:XX:XX] ============================================================
[XX:XX:XX] ФИЛЬТРЫ ПО ПРИОРИТЕТУ:
[XX:XX:XX] ============================================================
[XX:XX:XX]   ★ HIGH
[XX:XX:XX]      Правил в HIGH: 45
[XX:XX:XX]   ★ MEDIUM
[XX:XX:XX]      Правил в MEDIUM: 30
[XX:XX:XX]   ★ LOW
[XX:XX:XX]      Правил в LOW: 20
[XX:XX:XX] ============================================================
2. Отчёт с цветной подсветкой и без дубликатов:
text
PlpCheck Отчёт
Дата: 2026-09-06 12:47:29
Всего проблем: 323
Уникальных проблем: 150
Всего файлов: 1

HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 plpcheck.METH_PARAM_AND_VAR_NAMES: Параметры и переменные | ПЛАН: Исправить по описанию
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 plpcheck.SYNTAX_ERROR: Весь код | ПЛАН: Исправить синтаксическую ошибку
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 plpcheck.VARIABLE_SAME_NAME: Имена | ПЛАН: Исправить по описанию
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 plpcheck.WRONG_LOCAL_PREFIX: Локальные объекты | ПЛАН: Исправить по описанию
HOOK_BANK.REPS_EXP_115_1.PRIVATE:3 plpcheck.NO_RECURSION_COMMENT: Вызов функции/процедуры | ПЛАН: Исправить по описанию
HOOK_BANK.REPS_EXP_115_1.PRIVATE:3 plpcheck.PURE_SQL_DBLINK: DBLink | ПЛАН: Заменить на прикладную таблицу
HOOK_BANK.REPS_EXP_115_1.PRIVATE:3 plpcheck.PURE_UDF: Вызов функции | ПЛАН: Вынести UDF в процедурный код
...
3. Дубликаты удалены:
text
# Было (дубликаты):
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 SYNTAX_ERROR: Весь код | ПЛАН: Исправить синтаксическую ошибку
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 SYNTAX_ERROR: Весь код | ПЛАН: Исправить синтаксическую ошибку

# Стало (один раз):
HOOK_BANK.REPS_EXP_115_1.PRIVATE:1 SYNTAX_ERROR: Весь код | ПЛАН: Исправить синтаксическую ошибку
Формат ответа
json
{
  "task_id": "DS_030",
  "status": "success",
  "changes": [
    "Добавлена информация о фильтрах по приоритету при загрузке",
    "Добавлена цветовая подсветка строк лога",
    "Добавлено удаление дублирующихся строк в отчёте"
  ]
}
Инструкция
Примените изменения в gui_app.py и scanner.py

Перезапустите АРМ

Проверьте Журнал — должны быть рубрикаторы и фильтры

Проверьте отчёт — без дубликатов, с цветом

text

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `gui_app.py` и `scanner.py`
3. **Перезапустите АРМ**
4. **Проверьте**:
   - Журнал при загрузке — рубрикаторы + фильтры
   - Отчёт — без дубликатов, с цветом

---

**-= Задание DS 030 создано =-** 🚀