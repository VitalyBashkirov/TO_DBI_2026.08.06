# DS 025: PlpCheck-отчёт в формате HTML (как дистрибутивный)

## Задача
Изменить формат генерируемого отчёта в `scanner.py` с Markdown на HTML-таблицу, аналогичную дистрибутивному PlpCheck-отчёту (`report_all.html`).

## Требуемый формат

### 1. Структура HTML
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PlpCheck Отчёт</title>
    <style>
        /* Стили для таблицы, заголовков, подсветки строк */
    </style>
</head>
<body>
    <h1>PlpCheck Отчёт</h1>
    <h2>Статистика</h2>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Класс</th>
                <th>Метод</th>
                <th>Секция</th>
                <th>Строка</th>
                <th>Тип</th>
                <th>Уровень</th>
                <th>Описание</th>
            </tr>
        </thead>
        <tbody>
            <!-- Строки проблем -->
        </tbody>
    </table>
</body>
</html>
2. Данные для каждой строки
Колонка	Источник
#	Порядковый номер проблемы
Класс	Имя класса из файла (парсинг class NAME;)
Метод	Имя метода из файла (парсинг method NAME is)
Секция	PRIVATE / EXECUTE / VALIDATE / PUBLIC
Строка	Номер строки
Тип	issue.issue_type (например, bad_prefix, not_mentioned)
Уровень	ERROR_STYLE / WARNING_STYLE / INFO_STYLE
Описание	issue.description
3. Парсинг класса и метода из файла
python
def _parse_class_and_method(self, file_path: str) -> Tuple[str, str]:
    """Парсинг имени класса и метода из файла"""
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
    except Exception:
        pass
    
    return class_name, method_name, section
4. Определение уровня
python
def _get_severity_level(self, issue_type: str) -> str:
    """Определение уровня на основе типа проблемы"""
    # HIGH-правила → ERROR_STYLE
    high_rules = [
        'CONNECTBY2WITH', 'ROWNUM', 'OBLIGATORY_IN_OTHERS',
        'JSON_TYPES', 'OUTER_JOIN', 'NVL_IN_SELECT',
        'DIRECT_COMPARISON_WITH_NULL', 'PURE_SQL_DBLINK',
        'UPDATE_DELETE_BY_SUBQUERY'
    ]
    # MEDIUM → WARNING_STYLE
    # LOW → INFO_STYLE
    for rule in high_rules:
        if rule in issue_type:
            return 'ERROR_STYLE'
    return 'WARNING_STYLE'
5. Сортировка
Сортировка строк:

По имени класса (алфавитно)

По имени метода (алфавитно)

По номеру строки (по возрастанию)

6. Сохранение
Формат: .html

Путь: F:\TO_DBI\logs\plpcheck_report_<timestamp>.html

Плюс сохранять текущий .md для обратной совместимости (опционально)

Ожидаемый результат
Файл plpcheck_report_20260906_004422.html с таблицей:

#	Класс	Метод	Секция	Строка	Тип	Уровень	Описание
1	HOOK_BANK	REPS_EXP_115_1	PRIVATE	10	bad_prefix	WARNING_STYLE	Не корректный префикс, пожалуйста переименуйте в "v_Dp"
2	HOOK_BANK	REPS_EXP_115_1	PRIVATE	11	bad_prefix	WARNING_STYLE	Не корректный префикс, пожалуйста переименуйте в "v_Dp1"
...	...	...	...	...	...	...	...
Формат ответа
json
{
  "task_id": "DS_025",
  "status": "success",
  "changes": [
    "Метод generate_report() переписан для генерации HTML",
    "Добавлены методы _parse_class_and_method(), _get_severity_level()",
    "Добавлена сортировка по классу, методу, строке"
  ],
  "test_results": {
    "html_generation": "PASSED",
    "class_parsing": "PASSED",
    "method_parsing": "PASSED",
    "sorting": "PASSED"
  }
}
Инструкция
Замените метод generate_report в scanner.py на новый

Перезапустите АРМ

Выполните сканирование

Откройте plpcheck_report_*.html в браузере

text

---Ы

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `scanner.py`
3. **Перезапустите АРМ**
4. **Выполните сканирование**
5. **Откройте** `plpcheck_report_*.html`

---

**-= Задание DS 025 создано =-** 🚀