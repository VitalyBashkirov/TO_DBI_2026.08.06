# DS 026: Убрать "Было → Стало" из отчёта

## Задача
Изменить формат отчёта в `scanner.py` — убрать блоки **"Было :"** и **"Станет:"** из Markdown-отчёта.

## Причина
Этот формат не соответствует дистрибутивному PlpCheck-отчёту и не нужен для анализа.

## Исправление

### Файл: `F:\TO_DBI\SRC\analyzer\scanner.py`

### Метод `generate_report()` — найти блок:

```python
for issue in issues:
    f.write(f"### Строка {issue.line_number}\n\n")
    f.write(f"**Проблема:** {issue.issue_type} - {issue.description}\n\n")
    f.write(f"```plp\n{issue.original_code}\n```\n\n")
    
    f.write(f"**Было  :** `{issue.original_code}`\n")
    f.write(f"**Станет:** `{issue.rubricator_example_fixed}`\n\n")
    f.write("---\n\n")
Заменить на:
python
for issue in issues:
    f.write(f"### Строка {issue.line_number}\n\n")
    f.write(f"**Проблема:** {issue.issue_type} - {issue.description}\n\n")
    f.write(f"```plp\n{issue.original_code}\n```\n\n")
    if issue.rubricator_example_fixed:
        f.write(f"**Исправление:** `{issue.rubricator_example_fixed}`\n\n")
    f.write("---\n\n")
Ожидаемый результат
Было (неправильно):
markdown
### Строка 1

**Проблема:** plpcheck.METH_PARAM_AND_VAR_NAMES - Параметры и переменные

```plp
class HOOK_BANK;
Было : class HOOK_BANK;
Станет: P_PAR in [STRING_10]

text

### Стало (правильно):
```markdown
### Строка 1

**Проблема:** plpcheck.METH_PARAM_AND_VAR_NAMES - Параметры и переменные

```plp
class HOOK_BANK;
Исправление: P_PAR in [STRING_10]

text

## Формат ответа
```json
{
  "task_id": "DS_026",
  "status": "success",
  "changes": [
    "Убраны блоки 'Было :' и 'Станет:' из отчёта",
    "Добавлен блок 'Исправление:' если есть пример исправления"
  ]
}
Инструкция
Замените блок в generate_report()

Перезапустите АРМ

Проверьте новый отчёт

text

---

## 📋 Сводка

| Задание | Что делает | Где применяется |
|---------|------------|-----------------|
| **DS 025** | HTML-отчёт в стиле PlpCheck | `scanner.py` |
| **DS 026** | Убирает "Было → Стало" | `scanner.py` |

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda (обработает оба задания)
2. **Примените изменения** в `scanner.py`
3. **Перезапустите АРМ**
4. **Проверьте** новый отчёт

---

**-= Задания DS 025 и DS 026 готовы к выполнению =-** 🚀