# SQL Parser - Автоматическое исправление PLPlus кода

## Описание
Модуль `sql_parser.py` обеспечивает автоматическое исправление проблемных конструкций PLPlus на основе правил из файла `5.RUBRICATOR_PARSER_SQL.json`.

## Основные функции

### `apply_fix(line: str, rule_code: str) -> Optional[str]`
Применяет исправление к строке кода на основе правила из рубрикатора.

**Параметры:**
- `line` - Исходная строка кода
- `rule_code` - Код правила (например, `'v50.SQL.OUTERJOIN.п.1.1'`)

**Возвращает:**
- Исправленную строку или `None`, если исправление не удалось

**Примеры:**
```python
from analyzer.sql_parser import apply_fix

# Oracle outer join
result = apply_fix('t1.id = t2.id(+)', 'v50.SQL.OUTERJOIN.п.1.1')
# Результат: 'left join t2 on t1.id = t2.id'

# ROWNUM
result = apply_fix('where rownum = 1', 'v50.SQL.ROWNUM.п.1.2')
# Результат: 'fetch first 1 rows only'

# DATE тип
result = apply_fix('DateTimeEnd date', 'v50.STOR.DATE.п.2.2')
# Результат: 'DateTimeEnd date_time'
```

### `apply_transform(match: re.Match, transform_template: str, named_mapping: Dict) -> str`
Применяет шаблон transform к найденному совпадению.

**Поддерживаемые плейсхолдеры:**
- `{1}, {2}, ...` - Группы захвата по номеру
- `{left_table}, {right_table}, {left_column}, {right_column}` - Именованные для JOIN
- `{limit}` - Для ROWNUM
- `{var_name}, {param_name}` - Для DATE
- `{alias}, {table}` - Для коллекций

## Интеграция с CodeFixer

Модуль интегрирован в `code_fixer.py`:

```python
from fixer.code_fixer import PLPlusFixer

fixer = PLPlusFixer(config)
# В методе apply_fix() сначала вызывается sql_parser, затем fallback
result, modified = fixer.apply_fix(line, issue, log_level)
```

## Алгоритм работы

1. **Загрузка конфигурации** - Кэшируется при первом вызове из `5.RUBRICATOR_PARSER_SQL.json`
2. **Поиск правила** - Находит правило по `rule_code`
3. **Перебор паттернов** - В порядке приоритета
4. **Поиск совпадений** - Через регулярные выражения
5. **Применение transform** - Подстановка групп захвата в шаблон
6. **Fallback** - Если паттерн hybrid и не хватает контекста, возвращается инструкция

## Типы правил

### Regex-правила
Полностью автоматическое исправление:
- `oracle_outer_plus_right` - Oracle `(+)` → `LEFT JOIN`
- `rownum_equal` - `ROWNUM = N` → `FETCH FIRST N ROWS ONLY`

### Гибридные правила
Требуют контекста или ручной доработки:
- `plplus_ref_param_true` - PLPlus ссылки с `(true)`
- `plplus_collection_true` - Коллекции с `(true)`

Для гибридных паттернов с незаполненными плейсхолдерами возвращается инструкция:
```
ac%id = gj.[ACCOUNT](true)  -- ВАЖНО: преобразовать в LEFT JOIN...
```

## Логирование

Включите DEBUG логирование для отладки:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Пример лога:
```
2026-05-03 20:03:18,256 [DEBUG] [PARSER] Конфигурация загружена: 5.RUBRICATOR_PARSER_SQL.json (версия 1.0.0)
2026-05-03 20:03:18,257 [DEBUG] [PARSER] Применён паттерн 'oracle_outer_plus_right' для v50.SQL.OUTERJOIN.п.1.1
2026-05-03 20:03:18,257 [DEBUG]   Было: t1.id = t2.id(+)
2026-05-03 20:03:18,257 [DEBUG]   Стало: left join t2 on t1.id = t2.id
```

## Тестирование

```bash
cd F:\TO_DBI
python SRC/analyzer/sql_parser.py
```

## Файлы

- `SRC/analyzer/sql_parser.py` - Основной модуль
- `DATA/Рубрикатор/5.RUBRICATOR_PARSER_SQL.json` - Конфигурация правил
- `SRC/fixer/code_fixer.py` - Интеграция с фиксером

## Версии

- **v1.0.0** - Первоначальная реализация с поддержкой regex и гибридных паттернов
