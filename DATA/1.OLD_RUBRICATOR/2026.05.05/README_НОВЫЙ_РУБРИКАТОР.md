# Новый рубрикатор 4.RUBRICATOR_PROMPTS.json и 5.RUBRICATOR_PARSER_SQL.json

## Что нового?

Раньше вы работали только со статическими правилами из `3.RUBRICATOR_FIXES.md`.  
Теперь у вас есть два конфигурационных файла:

1. **`4.RUBRICATOR_PROMPTS.json`** — Промпты для AI-ассистента KODA
2. **`5.RUBRICATOR_PARSER_SQL.json`** — Алгоритмические правила для SQL-парсера

## Преимущества нового подхода

### 4.RUBRICATOR_PROMPTS.json (AI-ассистент)
1. **Регулярные выражения** — точный поиск проблемных конструкций
2. **Промпты для AI** — детальные инструкции для поиска и исправления
3. **Примеры "было/стало"** — наглядные преобразования кода
4. **Генерация тестов** — автоматическое создание тестовых файлов
5. **Приоритеты правил** — high/normal/low для важности исправлений

### 5.RUBRICATOR_PARSER_SQL.json (Алгоритмический парсер)
1. **Гибридный подход** — regex для простых случаев, алгоритмический парсер для сложных
2. **Быстрые преобразования** — через `re.sub()` для типовых конструкций
3. **Fallback инструкции** — когда автоматическое преобразование невозможно
4. **Алгоритмические подсказки** — для разработчика парсера

## Гибридный подход

| transform_type | Описание | Пример |
|---------------|----------|--------|
| `regex` | Быстрое преобразование через `re.sub()` | `t1.id = t2.id(+)` → `left join t2 on t1.id = t2.id` |
| `hybrid` | Алгоритмический парсер с анализом контекста | `ac%id = gj.[ACCOUNT](true)` → требует таблицы |
| `ignore` | Пропустить без изменений | `TO_DATE(...)` — не менять |

## Сравнение файлов

| Файл | Назначение | Кто использует | Формат |
|------|-----------|----------------|--------|
| `4.RUBRICATOR_PROMPTS.json` | Промпты для AI | KODA (AI-ассистент) | JSON с regex + промптами |
| `5.RUBRICATOR_PARSER_SQL.json` | Правила для SQL-парсера | sql_parser.py (алгоритмический) | JSON с regex + алгоритмами |

## Как использовать

### В GUI приложении

1. **Автоматическая загрузка** — при запуске приложения рубрикатор загружается автоматически
2. **Генерация тестов** — кнопка «Генерация тестовых .plp-файлов» использует новый рубрикатор
3. **Пропуск при отсутствии** — если правило нет в новом рубрикаторе, используется старый алгоритм

### В коде (4.RUBRICATOR_PROMPTS.json)
```python
from rubricator_prompts import RubricatorPrompts
from pathlib import Path

# Инициализация
prompts = RubricatorPrompts(Path('DATA/Рубрикатор'))
prompts.load()

# Получение правила
rule = prompts.get_rule('v50.SQL.OUTERJOIN.п.1.1')

# Поиск проблем в файле
results = prompts.search_code_in_file(Path('test.plp'), 'v50.SQL.OUTERJOIN.п.1.1')

# Генерация тестового файла
file_path = prompts.generate_test_file(
    'v50.SQL.OUTERJOIN.п.1.1',
    Path('DATA/Тестовые файлы')
)
```

### В коде (5.RUBRICATOR_PARSER_SQL.json)
```python
from sql_parser import SQLParser

# Инициализация
parser = SQLParser('DATA/Рубрикатор/5.RUBRICATOR_PARSER_SQL.json')

# Преобразование строки
line = "ac%id = gj.[ACCOUNT](true)"
rule_code = "v50.SQL.OUTERJOIN.п.1.1"

result = parser.parse_and_transform(line, rule_code)
if result.transform_type == 'regex':
    # Быстрое преобразование
    fixed_line = result.fixed_code
elif result.transform_type == 'hybrid':
    # Алгоритмический парсер
    if result.success:
        fixed_line = result.fixed_code
    else:
        fixed_line = result.fallback_instruction  # Инструкция для AI
```

## Структура правила (4.RUBRICATOR_PROMPTS.json)

```json
{
  "code": "v50.SQL.OUTERJOIN.п.1.1",
  "short_description": "Замена (+) на LEFT/RIGHT JOIN",
  "search_prompt": "Ищите в PLPlus коде следующие проблемные конструкции...",
  "fix_prompt": "Вы AI-ассистент по исправлению PLPlus кода...",
  "test_generation_prompt": "Вы AI-ассистент по генерации тестовых файлов...",
  "regex_patterns": {
    "for_search": [...],
    "for_ignore": [...]
  },
  "examples": {
    "simple_case": {
      "bad": "select * from t1, t2 where t1.id = t2.id(+)",
      "good": "select * from t1 left join t2 on t1.id = t2.id"
    }
  },
  "fix_instruction": "Последовательность шагов для исправления...",
  "priority": "high",
  "category": "SQL"
}
```

## Поля правила

| Поле | Описание |
|------|----------|
| `code` | Уникальный идентификатор правила |
| `short_description` | Краткое описание для отображения |
| `search_prompt` | Инструкция для AI по поиску проблем |
| `fix_prompt` | Инструкция для AI по исправлению |
| `test_generation_prompt` | Инструкция для генерации тестов |
| `regex_patterns.for_search` | Паттерны для поиска проблем |
| `regex_patterns.for_ignore` | Паттерны для исключения (комментарии, строки) |
| `examples` | Примеры "было/стало" |
| `fix_instruction` | Пошаговая инструкция |
| `priority` | Приоритет: high/normal/low |
| `category` | Категория: SQL/Типы_данных/Транзакции и т.д. |

## Добавление новых правил

1. Откройте `4.RUBRICATOR_PROMPTS.json`
2. Добавьте новое правило в секцию `rules`
3. Укажите все обязательные поля
4. Сохраните файл в UTF-8
5. Перезапустите приложение

## Пример правила

Полный пример правила для замены синтаксиса Oracle (+) на ANSI JOIN смотрите в файле `4.RUBRICATOR_PROMPTS.json` (правило `v50.SQL.OUTERJOIN.п.1.1`).

## Совместимость

- **Обратная совместимость:** Если правило отсутствует в новом рубрикаторе, используется старый алгоритм из `3.RUBRICATOR_FIXES.md`
- **Параллельная работа:** Оба рубрикатора работают одновременно
- **Плавный переход:** Можно постепенно мигрировать правила из старого формата в новый

## Отладка

Для проверки загрузки рубрикатора:
```bash
cd F:\TO_DBI\SRC
python rubricator_prompts.py
```

Вывод:
```
Загружен расширенный рубрикатор: 4.RUBRICATOR_PROMPTS.json (версия 2.2.0)

Доступные правила:
  v50.SQL.OUTERJOIN.п.1.1: Замена (+) на LEFT/RIGHT JOIN (SQL, high)
```

## Контакты

Вопросы и предложения по новому рубрикатору направляйте в NLP-Core-Team.

## Статус разработки

- **4.RUBRICATOR_PROMPTS.json** — ✅ Готов к использованию
- **5.RUBRICATOR_PARSER_SQL.json** — ✅ Готов к использованию (содержит все правила с hybrid_mode)
- **sql_parser.py** — 🚧 В разработке (будет использован для алгоритмических преобразований)

## Примечание

Файл `5.RUBRICATOR_PARSER_SQL.json` уже содержит все необходимые правила для гибридного парсера:
- Все правила из `4.RUBRICATOR_PROMPTS.json` отражены
- Для каждого паттерна есть примеры `example_in` и `example_out`
- Гибридные паттерны содержат `algorithmic_hint` и `fallback_instruction`
- Файл валиден (проверен через JSON parser)
