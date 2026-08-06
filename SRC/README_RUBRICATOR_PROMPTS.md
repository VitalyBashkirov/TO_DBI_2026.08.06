# Работа с рубрикатором 4.RUBRICATOR_PROMPTS.json

## Описание

Файл `4.RUBRICATOR_PROMPTS.json` содержит расширенные инструкции для AI-ассистента KODA по поиску и исправлению проблемных конструкций PL/Plus кода.

## Структура файла

```json
{
  "version": "2.2.0",
  "based_on": "документация...",
  "rules": {
    "v50.SQL.OUTERJOIN.п.1.1": {
      "code": "код правила",
      "short_description": "краткое описание",
      "documentation_text": "полное описание из документации",
      "search_prompt": "инструкция для поиска проблем",
      "fix_prompt": "инструкция для исправления",
      "test_generation_prompt": "инструкция для генерации тестов",
      "regex_patterns": {
        "for_search": [...],
        "for_ignore": [...]
      },
      "examples": {
        "simple_case": {"bad": "...", "good": "..."}
      },
      "fix_instruction": "пошаговая инструкция",
      "priority": "high|normal|low",
      "category": "тип категории"
    }
  }
}
```

## Режимы работы

### Режим 1: Сканирование (по коду правила)

**Когда вызывается:** Пользователь запрашивает проверку файла или вводит код правила

**Алгоритм:**
1. Проверить, отключена ли работа с этим кодом (поле `disabled`)
2. Найти правило в `4.RUBRICATOR_PROMPTS.json`
3. Применить `regex_patterns.for_search` для поиска проблем
4. Использовать `search_prompt` для контекстного анализа
5. Игнорировать строки по `regex_patterns.for_ignore`
6. Выдать результат: найденные строки с типом проблемы

**Пример использования:**
```python
from rubricator_prompts import RubricatorPrompts

prompts = RubricatorPrompts(Path('DATA/Рубрикатор'))
prompts.load()

# Поиск проблем в файле
results = prompts.search_code_in_file(
    file_path=Path('test.plp'),
    code='v50.SQL.OUTERJOIN.п.1.1',
    log_callback=print
)
```

### Режим 2: Исправление кода

**Когда вызывается:** Требуется исправление найденных проблем

**Алгоритм:**
1. Определить тип проблемы по найденному паттерну
2. Выполнить `fix_prompt` — следовать инструкции
3. Применить преобразование из `examples`
4. Проверить синтаксис для DBI

**Пример использования:**
```python
# Получение инструкции по исправлению
fix_prompt = prompts.get_fix_prompt('v50.SQL.OUTERJOIN.п.1.1')
examples = prompts.get_examples('v50.SQL.OUTERJOIN.п.1.1')
```

### Режим 3: Генерация тестовых .plp файлов

**Когда вызывается:** Пользователь нажимает кнопку **«Генерация тестовых .plp файлов»**

**Каталог для сохранения:** `F:\TO_DBI\DATA\Тестовые файлы`

**Алгоритм:**
1. Проверить существование каталога — создать если отсутствует
2. Найти правило по коду в `4.RUBRICATOR_PROMPTS.json`
3. Извлечь `test_generation_prompt`
4. Сгенерировать тестовый PLPlus файл:
   - Расширение: `.plp`
   - Содержит ВСЕ типы проблемных конструкций из `regex_patterns.for_search`
   - Содержит корректные конструкции (для проверки ложных срабатываний)
   - Комментарии с пояснениями
5. Сохранить файл: `test_<код_правила>_<ГГГГММДД>.plp`

**Пример использования:**
```python
# Генерация тестового файла
file_path = prompts.generate_test_file(
    code='v50.SQL.OUTERJOIN.п.1.1',
    output_dir=Path('DATA/Тестовые файлы'),
    log_callback=print
)
print(f"Создан файл: {file_path}")
```

## Регулярные выражения

### Паттерны для поиска (`for_search`)

Каждый паттерн содержит:
- `pattern`: регулярное выражение
- `description`: описание что ищет
- `flags`: флаги (например, 'i' для case-insensitive)

**Пример:**
```json
{
  "pattern": "(\\w+)\\.(\\w+)\\s*=\\s*(\\w+)\\.(\\w+)\\(\\+\\)",
  "description": "Синтаксис Oracle (+), слева вправо",
  "flags": "i"
}
```

### Паттерны для игнорирования (`for_ignore`)

Строки, подпадающие под эти паттерны, исключаются из результатов:
- Комментарии (`--`)
- Строковые литералы (`'...'`)
- Уже исправленный код (ANSI JOIN)

**Пример:**
```json
{
  "pattern": "^\\s*--.*(\\(\\+\\)|&collection\\(true\\))",
  "description": "Комментарии"
}
```

## Примеры "было/стало"

Формат в `examples`:
```json
{
  "simple_case": {
    "bad": "select * from t1, t2 where t1.id = t2.id(+)",
    "good": "select * from t1 left join t2 on t1.id = t2.id"
  }
}
```

## Интеграция в GUI

Модуль `rubricator_prompts.py` интегрирован в `gui_app.py`:

1. **Загрузка при старте:** В методе `_populate_rules_tree()`
2. **Генерация тестов:** В методе `_run_test_generation()`
3. **Получение правил:** Доступно через `self.rubricator_prompts.get_rule(code)`

## Добавление новых правил

1. Откройте `4.RUBRICATOR_PROMPTS.json`
2. Добавьте новое правило в объект `rules`:
```json
"v50.NEW.CATEGORY.п.1": {
  "code": "v50.NEW.CATEGORY.п.1",
  "short_description": "Описание",
  "search_prompt": "...",
  "fix_prompt": "...",
  "test_generation_prompt": "...",
  "regex_patterns": {
    "for_search": [...],
    "for_ignore": [...]
  },
  "examples": {...},
  "fix_instruction": "...",
  "priority": "high",
  "category": "SQL"
}
```
3. Сохраните файл
4. Перезапустите приложение

## Проверка работы

```bash
cd F:\TO_DBI\SRC
python rubricator_prompts.py
```

Ожидаемый вывод:
```
Загружен расширенный рубрикатор: 4.RUBRICATOR_PROMPTS.json (версия 2.2.0)

Доступные правила:
  v50.SQL.OUTERJOIN.п.1.1: Замена (+) на LEFT/RIGHT JOIN
```

## Версии

| Версия | Дата | Изменения |
|--------|------|-----------|
| 2.2.0 | 2026 Q2 | Текущая версия |
| 2.1.0 | 2026 Q1 | Добавлены тестовые промпты |
| 2.0.0 | 2025 Q4 | Первоначальная версия |
