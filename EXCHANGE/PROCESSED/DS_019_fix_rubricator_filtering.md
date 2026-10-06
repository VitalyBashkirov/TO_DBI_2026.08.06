# DS 019: Исправление фильтрации рубрикатора — использовать только выбранные файлы

## Задача
Исправить логику сканирования так, чтобы использовались **только правила из выбранных файлов рубрикатора**, а не все правила из загруженного рубрикатора.

## Проблема
При выборе только `PlpCheck` сканирование использует правила из **всех** файлов рубрикатора (v53, тдс20240828, тклоик20240828, PlpCheck).

Это происходит потому, что `selected_rules` содержит **коды файлов** (`v50`, `PlpCheck`, ...), но сканеру передаются **все правила** из `self.rubricator_prompts`, а не только из выбранных файлов.

## Требования

### 1. Исправить сбор правил в `_run_scan` и `_run_fix`

**Текущий код (неправильный):**
```python
selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
Нужно: собрать все правила, которые относятся к выбранным файлам рубрикатора.

2. Логика маппинга
Код файла	Какие правила включать
v50	Все правила, начинающиеся с v50.
PlpCheck	Все правила, начинающиеся с plpcheck.
тдс20240828	Все правила, начинающиеся с тдс20240828.
тклоик20240828	Все правила, начинающиеся с тклоик20240828.
3. Исправленный код
python
def _get_rules_for_selected_files(self):
    """Получить список правил для выбранных файлов рубрикатора"""
    selected_files = [code for code, var in self.selected_rules.items() if var.get()]
    
    if not self.rubricator_prompts or not self.rubricator_prompts.loaded:
        return selected_files  # fallback
    
    all_rules = self.rubricator_prompts.get_all_rules()
    matched_rules = []
    
    for file_code in selected_files:
        if file_code == 'PlpCheck':
            # PlpCheck правила
            for rule in all_rules:
                if rule['code'].startswith('plpcheck.'):
                    matched_rules.append(rule['code'])
        elif file_code == 'v50':
            # v53 правила
            for rule in all_rules:
                if rule['code'].startswith('v53.') or rule['code'].startswith('v50.'):
                    matched_rules.append(rule['code'])
        elif file_code == 'тдс20240828':
            # тдс правила
            for rule in all_rules:
                if rule['code'].startswith('тдс20240828.'):
                    matched_rules.append(rule['code'])
        elif file_code == 'тклоик20240828':
            # тклоик правила
            for rule in all_rules:
                if rule['code'].startswith('тклоик20240828.'):
                    matched_rules.append(rule['code'])
        else:
            # fallback: ищем правила, содержащие код файла
            for rule in all_rules:
                if file_code in rule['code']:
                    matched_rules.append(rule['code'])
    
    return sorted(set(matched_rules))
4. Использовать в _run_scan и _run_fix
Заменить:

python
selected_rules = [code for code, var in self.selected_rules.items() if var.get()]
На:

python
selected_rules = self._get_rules_for_selected_files()
5. Логирование выбранных правил
Добавить в лог:

text
[12:00:00] ВЫБРАННЫЕ ФАЙЛЫ РУБРИКАТОРА:
[12:00:00]   [+] PlpCheck
[12:00:00] 
[12:00:00] ИСПОЛЬЗУЕМЫЕ ПРАВИЛА (16):
[12:00:00]   [+] plpcheck.ACCESS_STATIC
[12:00:00]   [+] plpcheck.BAD_PREFIX
[12:00:00]   [+] plpcheck.CODE_IN_COMMENT
[12:00:00]   ... (только PlpCheck правила)
6. Обновить _update_buttons_state
Проверка на any_rule_selected уже есть, но нужно убедиться, что кнопки блокируются, если не выбран ни один файл.

Ожидаемый результат
□ При выборе только PlpCheck сканируются только PlpCheck правила
□ При выборе PlpCheck + v50 сканируются оба набора правил
□ Лог показывает только выбранные правила
□ Лог сгруппирован как у дистрибутивного PlpCheck
Формат ответа
json
{
  "task_id": "DS_019",
  "status": "success",
  "changes": [
    "Добавлен метод _get_rules_for_selected_files()",
    "Обновлены _run_scan и _run_fix для использования только выбранных файлов",
    "Обновлено логирование — выводятся только выбранные правила"
  ],
  "test_results": {
    "only_plpcheck": "PASSED",
    "plpcheck_and_v50": "PASSED",
    "no_rules_selected": "PASSED"
  }
}
Пример дистрибутивного PlpCheck лога
text
[12:00:00] ============================================================
[12:00:00] НАЧАЛО СКАНИРОВАНИЯ (PlpCheck)
[12:00:00] ============================================================

[12:00:00] ВЫБРАННЫЕ ФАЙЛЫ РУБРИКАТОРА:
[12:00:00]   [+] PlpCheck

[12:00:00] ИСПОЛЬЗУЕМЫЕ ПРАВИЛА (16):
[12:00:00]   [+] plpcheck.ACCESS_STATIC
[12:00:00]   [+] plpcheck.ALIAS_COLUMN_VIEW
[12:00:00]   [+] plpcheck.BAD_PREFIX
[12:00:00]   [+] plpcheck.CODE_IN_COMMENT
[12:00:00]   [+] plpcheck.CONTINUE_EXIT_OFF_THE_LOOP
[12:00:00]   [+] plpcheck.EDIT_HOTKEY
[12:00:00]   [+] plpcheck.ENDLESS_CYCLE
[12:00:00]   [+] plpcheck.FIXME_NOT_ALLOWED
[12:00:00]   [+] plpcheck.FORM_SIZE
[12:00:00]   [+] plpcheck.FUNCRETURNKEYWORD
[12:00:00]   [+] plpcheck.FUNCTIONS_IN_BODY_OR_VALIDATE
[12:00:00]   [+] plpcheck.GETOBJECTINIFELSESECTION
[12:00:00]   [+] plpcheck.GLOBAL_VAR
[12:00:00]   [+] plpcheck.GOTO
[12:00:00]   [+] plpcheck.IF_EXIT_TO_EXIT_WHEN
[12:00:00]   [+] plpcheck.NOT_MENTIONED

[12:00:01] [ПАРСЕР SQL] Начало сканирования и анализа...
[12:00:01]   Источник: F:\TO_DBI\PATCH_IN\
[12:00:01]   Правила: 16

[12:05:30] [ПАРСЕР SQL] Завершено:
[12:05:30]   Найдено файлов: 42
[12:05:30]   Найдено проблем: 127

[12:05:30] [2/3] Результаты сканирования:
[12:05:30]   Найдено *.plp файлов: 42
[12:05:30]   Проблемных конструкций: 127

[12:05:30] [3/3] Проблемы по типам:
[12:05:30]   plpcheck.BAD_PREFIX: 23
[12:05:30]   plpcheck.GOTO: 12
[12:05:30]   plpcheck.NOT_MENTIONED: 369
[12:05:30]   ...

[12:05:30] Отчёт сохранён: F:\TO_DBI\logs\scan_report_PlpCheck_20260905_120530.md
[12:05:30] ============================================================
[12:05:30] СКАНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО
[12:05:30] ============================================================
Дополнительно
После применения изменений проверьте, что:

Выбор PlpCheck + v50 даёт правила из обоих наборов

Выбор всех файлов даёт все правила (как сейчас)

Кнопки блокируются, если не выбран ни один файл

Лог чистый и понятный

text

---

## ✅ Файл создан!

**Путь:** `F:\TO_DBI\EXCHANGE\INBOX\DS_019_fix_rubricator_filtering.md`

---

## 🚀 Что делать

1. **Выполните** `DS` в Koda
2. **Примените изменения** в `gui_app.py`
3. **Перезапустите АРМ**
4. **Проверьте**, выбрав только `PlpCheck`
5. **Проверьте лог** — должны быть только PlpCheck правила

---

## 📋 Сравнение

| Было | Стало |
|------|-------|
| Выбраны все правила из всех рубрикаторов | Выбраны только правила из выбранных файлов |
| Лог показывает все правила | Лог показывает только выбранные правила |
| При выборе PlpCheck используются v53, тдс, тклоик | При выборе PlpCheck используются только plpcheck.* правила |

---

**-= Задание DS 019 готово к выполнению =-** 🚀