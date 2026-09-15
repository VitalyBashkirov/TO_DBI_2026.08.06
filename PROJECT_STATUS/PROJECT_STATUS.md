# Проект TO_DBI — Статус и документация

**Дата:** 05.09.2026
**Версия:** 2.0
**Статус:** Активная разработка

---

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Структура проекта](#структура-проекта)
3. [Архитектура и протокол DS](#архитектура-и-протокол-ds)
4. [Текущий статус](#текущий-статус)
5. [Рубрикаторы](#рубрикаторы)
6. [Правила PlpCheck (краткий обзор)](#правила-plpcheck-краткий-обзор)
7. [Интеграция с АРМ](#интеграция-с-арм)
8. [Активные задачи](#активные-задачи)
9. [Шаблоны заданий DS](#шаблоны-заданий-ds)
10. [Примеры выполненных задач](#примеры-выполненных-задач)
11. [Планы и улучшения](#планы-и-улучшения)
12. [Логи и история](#логи-и-история)
13. [Контакты](#контакты)

---

## Обзор проекта

### Назначение
**АРМ «Адаптация под DBI»** — инструмент для автоматической миграции PL/Plus кода с Oracle-совместимого синтаксиса на архитектуру DBI (PostgreSQL).

### Ключевые компоненты
| Компонент | Путь | Назначение |
|-----------|------|------------|
| **АРМ** | `F:\TO_DBI\SRC\gui_app.py` | Графический интерфейс для сканирования и анализа кода |
| **Koda** | `F:\TO_DBI\AGENTS\koda_agent.prompt` | AI-агент для адаптации кода |
| **EXCHANGE** | `F:\TO_DBI\EXCHANGE\` | Файловый обмен между АРМ и Koda |
| **Рубрикаторы** | `F:\TO_DBI\4*.json` | Наборы правил для анализа (v53, тдс20240828, тклоик20240828, PlpCheck) |

### Технологический стек
- **Язык:** Python (GUI: Tkinter)
- **AI:** DeepSeek API (через Koda)
- **Файловый обмен:** JSON / Markdown
- **Кодировка:** UTF-8 (файлы), Windows-1251 (логи)
- **Целевая БД:** PostgreSQL (DBI)

---

## Структура проекта
F:\TO_DBI
├── SRC
│ └── gui_app.py # Основной код АРМ
├── AGENTS
│ └── koda_agent.prompt # Промпт Koda
├── EXCHANGE
│ ├── INBOX\ # Входящие задания (Markdown/JSON)
│ ├── OUTBOX\ # Ответы от Koda (JSON/Markdown)
│ ├── PROCESSED\ # История выполненных заданий
│ └── bot.log # Лог-файл (Windows-1251)
├── TESTDATA\ # Тестовые файлы PL/Plus
├── PROMPTS\ # Шаблоны промптов
├── FIXED\ # Исправленный код (результат)
├── 4a.RUBRICATOR_PROMPT_v53.json
├── 4b.RUBRICATOR_PROMPT_тдс20240828.json
├── 4c.RUBRICATOR_PROMPT_тклоик20240828.json
├── 4d.RUBRICATOR_PROMPT_PlpCheck.json
├── PROJECT_STATUS.md # Этот файл
└── CHANGELOG.md # Журнал изменений кода

text

---

## Архитектура и протокол DS

### Протокол DS (Data/Task Exchange)

**DS — это НЕ DeepSeek API**, а файловый протокол обмена задачами между АРМ и Koda.

#### Схема работы
Пользователь → АРМ → INBOX/ → Koda → DeepSeek API → OUTBOX/ → АРМ → Пользователь

text

#### Директории обмена
F:\TO_DBI\EXCHANGE
├── INBOX\ # Задания на выполнение (Markdown/JSON)
├── OUTBOX\ # Результаты выполнения (JSON/Markdown)
└── PROCESSED\ # История выполненных заданий

text

#### Команды DS
| Команда | Действие |
|---------|----------|
| `DS` | Обработать все файлы из INBOX по очереди |
| `DS <файл>` | Обработать конкретный файл из INBOX |
| `DS --help` | Показать справку |

#### Жизненный цикл задания
1. **Создание** — файл помещается в `INBOX/` (вручную или через АРМ)
2. **Чтение** — Koda читает файл (проверка блокировки, ожидание 10-15 сек)
3. **Выполнение** — Koda отправляет промпт в DeepSeek API
4. **Результат** — Ответ сохраняется в `OUTBOX/`
5. **Архивация** — Файл задания переносится в `PROCESSED/`

#### Форматы файлов

**Входящее задание (INBOX):**
```markdown
# DS: <название задачи>

## Задача
<описание>

## Требования
<список>

## Ожидаемый результат
<формат ответа>
Исходящий ответ (OUTBOX):

json
{
  "task_id": "DS_XXX",
  "status": "success|error|processing",
  "summary": { ... },
  "issues": [ ... ],
  "recommendations": [ ... ]
}
Логирование
Файл: F:\TO_DBI\EXCHANGE\bot.log

Формат: [ДД.ММ.ГГГГ ЧЧ:ММ:СС] <сообщение>

Кодировка: Windows-1251

Текущий статус
Выполненные задачи (PROCESSED)
Задача	Дата	Описание	Статус
DS 001	20.08.2026	Первичный анализ кода	✅ Выполнен
DS 002	20.08.2026	Утверждение плана адаптации	✅ Выполнен
DS 003	21.08.2026	Добавлен звуковой сигнал (победные ноты / ноты сожаления)	✅ Выполнен
DS 004	22.08.2026	Интеграция АРМ с Koda через файловый обмен	✅ Выполнен
DS 005	21.08.2026	Обновление промпта Koda	✅ Выполнен
DS 006	21.08.2026	Полный анализ кода по рубрикатору PlpCheck	✅ Выполнен
 DS 007	21.08.2026	Автоматическая подстановка Каталога результатов	✅ Выполнен
 DS 044	06.10.2026	Удалён раздел «Исключения из проверки» (gui_app.py, settings.json)	✅ Выполнен (PASS=15 FAIL=0)
 DS 045	06.10.2026	Аудит кода DS_036–DS_044 — замечаний нет, изменений нет	✅ Выполнен (PASS=10 FAIL=0)
 DS 046	07.10.2026	Регрессия 14 тестов: PASS=904 FAIL=0, изменений источников нет	✅ Выполнен (готов к финальной проверке)
 Текущая очередь (INBOX)
text
📭 INBOX пуст — все задания обработаны.
Статистика по коду (на 05.09.2026)
Проанализировано файлов: 599

HIGH-проблем: 381

WHEN OTHERS без ROLLBACK/RAISE: 369

NativeID: 12

MEDIUM-проблем: ~200 (оценка)

LOW-проблем: ~150 (оценка)

Рубрикаторы
Список рубрикаторов
Файл	Правил	Описание
4a.RUBRICATOR_PROMPT_v53.json	~100	Базовые правила адаптации
4b.RUBRICATOR_PROMPT_тдс20240828.json	~90	Правила ТДС
4c.RUBRICATOR_PROMPT_тклоик20240828.json	43	Правила ТКЛОИК
4d.RUBRICATOR_PROMPT_PlpCheck.json	93	Правила плагина PLPCheck
ИТОГО:	~332	
Структура правила
json
{
  "code": "plpcheck.ACCESS_STATIC",
  "short_description": "Обращение к статическому экземпляру",
  "documentation_text": "...",
  "regex_patterns": {
    "for_search": [{"pattern": "...", "description": "..."}],
    "for_ignore": [{"pattern": "...", "description": "..."}]
  },
  "code_example_bad": "...",
  "code_example_good": "...",
  "fix_instruction": "...",
  "priority": "HIGH|MEDIUM|LOW",
  "priority_level": 1|2|3,
  "category": "DBI|DEV|WEB",
  "subcategory": "...",
  "tags": ["..."]
}
Приоритеты исправлений
Уровень	Приоритет	Описание	Примеры
HIGH	1	Критично для DBI, блокирует миграцию	CONNECT BY, ROWNUM, WHEN OTHERS
MEDIUM	2	Важно, влияет на производительность	NVL, отсутствие ALL, NULL
LOW	3	Стилистические, косметические	Префиксы, GOTO, FIXME
Критические замены Oracle → PostgreSQL
Oracle	PostgreSQL
ROWNUM	FETCH FIRST n ROWS ONLY
CONNECT BY	WITH RECURSIVE
MINUS	EXCEPT
(+)	LEFT JOIN / RIGHT JOIN
NVL(a,b)	COALESCE(a,b)
DECODE	CASE
SYSDATE	CURRENT_TIMESTAMP
USER	::[RUNTIME].[STDLIB].userid
ROWID	%id
JSON_OBJECT_T	::[RUNTIME].[LIB_JSON]
XMLType	Использовать JSON
Правила PlpCheck (краткий обзор)
Категории правил (93 шт.)
Категория	Количество	Примеры правил
DBI (критические)	~45	CONNECTBY2WITH, ROWNUM, OBLIGATORY_IN_OTHERS, JSON_TYPES, PURE_SQL_VIEW_IN_CONDITION
DEV (стиль)	~30	BAD_PREFIX, GOTO, NOT_MENTIONED, THIS_IN_DEFAULT, WRONG_LOCAL_PREFIX
WEB	~10	HOT_KEY_PROHIBITED, EXCEL_WORD_LIBS_WEB, WEB_NOT_IMPLEMENTED, REPORT_METHODS_WEB
SQL/Pure SQL	~8	PURE_SQL_VIEW_IN_CONDITION, QUOTING, PURE_SQL_FUNCTION_UNSUPPORTED
Топ-10 критических правил (HIGH)
#	Правило	Описание	Исправление
1	CONNECTBY2WITH	Использование CONNECT BY	WITH RECURSIVE
2	ROWNUM	Использование ROWNUM	FETCH FIRST n ROWS ONLY
3	OBLIGATORY_IN_OTHERS	WHEN OTHERS без ROLLBACK/RAISE	Добавить ROLLBACK/RAISE
4	JSON_TYPES	JSON_OBJECT_T, PLJSON	::[RUNTIME].[LIB_JSON]
5	PURE_SQL_VIEW_IN_CONDITION	VW_CRIT, v$, dba_*	Использовать прикладные таблицы
6	OUTER_JOIN	Внешние соединения через (+)	LEFT/RIGHT JOIN
7	NVL_IN_SELECT	NVL с подзапросом	COALESCE
8	DIRECT_COMPARISON_WITH_NULL	Сравнение с NULL	IS NULL / IS NOT NULL
9	PURE_SQL_DBLINK	Использование DBLink	Убрать DBLink
10	UPDATE_DELETE_BY_SUBQUERY	UPDATE/DELETE по подзапросу	Переписать без подзапроса
Интеграция с АРМ
Кнопки управления (gui_app.py)
Кнопка	Метод	Функция
🔍 Сканировать	run_scan()	Запуск сканирования кода
📤 Отправить в Koda	send_to_koda()	Выгрузка результатов в INBOX
📥 Получить ответ	receive_from_koda()	Загрузка ответа из OUTBOX
📂 Сканировать EXCHANGE	scan_exchange()	Просмотр состояния обмена
🗑 Очистить лог	clear_log()	Очистка журнала изменений
Автоматизация РК (DS 007)
Правило: При изменении Исходного каталога (ИК) автоматически вычисляется Каталог результатов (РК):

text
РК = ИК.replace("\PATCH_IN\", "\PATCH_OUT\")
Статус: ✅ Реализовано в gui_app.py

Метод on_source_dir_change
python
def on_source_dir_change(self, *args):
    """Автоматическое обновление Каталога результатов при изменении Исходного каталога"""
    source_dir = self.source_dir_var.get()
    if source_dir and "PATCH_IN" in source_dir:
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
        self.log(f"🔄 Автоматически обновлён РК: {result_dir}")
    else:
        self.log("ℹ️ В ИК отсутствует PATCH_IN. РК не изменён.")
Активные задачи
1. Тестирование интеграции с Koda (приоритет: HIGH)
□ Проверить работу кнопки «Отправить в Koda»
□ Проверить работу кнопки «Получить ответ»
□ Проверить обработку очереди INBOX
□ Проверить логирование в bot.log
2. Массовое исправление HIGH-проблем (приоритет: HIGH)
□ Исправить 369 случаев WHEN OTHERS без ROLLBACK/RAISE
□ Исправить 12 случаев NativeID
□ Создать CHANGELOG.md с описанием изменений
3. Полный анализ по рубрикатору PlpCheck (приоритет: MEDIUM)
□ Запустить сканирование всех файлов
□ Сгенерировать отчёт по всем 93 правилам
□ Классифицировать проблемы по категориям
4. Улучшение АРМ (приоритет: LOW)
□ Добавить индикацию статуса полей (зелёный/красный)
□ Добавить прогресс-бар для сканирования
□ Добавить экспорт отчёта в PDF
Шаблоны заданий DS
Шаблон 1: Анализ файла
markdown
# DS: Анализ файла

## Задача
Проанализировать файл `F:\TO_DBI\TESTDATA\sample.plp` по рубрикатору PlpCheck.

## Требования
- Вернуть JSON с найденными проблемами
- Указать severity (HIGH/MEDIUM/LOW)
- Предложить исправления

## Ожидаемый результат
```json
{
  "task_id": "DS_XXX",
  "status": "success",
  "issues": [...]
}
text

### Шаблон 2: Исправление конкретной проблемы
```markdown
# DS: Исправление CONNECT BY

## Задача
Найти все файлы в `F:\TO_DBI\TESTDATA\` с CONNECT BY.
Заменить на WITH RECURSIVE.
Вернуть список изменённых файлов.

## Формат ответа
```json
{
  "task_id": "DS_XXX",
  "status": "success",
  "files_changed": [...],
  "changes": [...]
}
text

### Шаблон 3: Полный анализ проекта
```markdown
# DS: Полный анализ проекта

## Задача
Выполнить полный анализ кода проекта по рубрикатору PlpCheck.

## Область сканирования
`F:\TO_DBI\TESTDATA\*.plp`

## Ожидаемый результат
- JSON с полной статистикой
- Список всех проблем с приоритетами
- Рекомендации по исправлению
Примеры выполненных задач
Пример: DS 007 — Автоподстановка РК
Задача:

markdown
# DS 007: Автоматическая подстановка Каталога результатов

## Задача
При изменении Исходного каталога автоматически вычислять Каталог результатов.

## Формула
РК = ИК.replace("\PATCH_IN\", "\PATCH_OUT\")
Результат:

json
{
  "task_id": "DS_007",
  "status": "success",
  "summary": {
    "changes": [
      "Добавлен метод on_source_dir_change",
      "Обновлён метод run_scan",
      "Добавлена привязка события к полю ИК"
    ]
  },
  "test_results": {
    "scenario_1": "PASSED",
    "scenario_2": "PASSED",
    "scenario_3": "PASSED"
  }
}
Реализация:

python
def on_source_dir_change(self, *args):
    source_dir = self.source_dir_var.get()
    if source_dir and "PATCH_IN" in source_dir:
        result_dir = source_dir.replace("PATCH_IN", "PATCH_OUT")
        self.result_dir_var.set(result_dir)
Планы и улучшения
Ближайшие планы
✅ Завершить интеграцию с Koda (DS 004)

✅ Добавить автоматическую подстановку РК (DS 007)

🔄 Протестировать полный цикл работы АРМ

📋 Создать документацию по использованию

Среднесрочные планы
Автоматическое исправление HIGH-проблем

Интеграция с системой контроля версий (Git)

Параллельная обработка файлов

Долгосрочные планы
Полная автоматизация миграции

Поддержка других СУБД (не только PostgreSQL)

Веб-интерфейс для АРМ

Логи и история
Структура логов
text
[21.08.2026 14:30:15] 🔍 Сканирование запущено
[21.08.2026 14:30:16] 📁 ИК: F:\PROJECT\PATCH_IN\
[21.08.2026 14:30:16] 📁 РК: F:\PROJECT\PATCH_OUT\
[21.08.2026 14:30:45] ✅ Сканирование завершено. Найдено 42 проблемы.
[21.08.2026 14:31:00] 📤 Отправка в Koda: koda_task_20260821_143100.md
[21.08.2026 14:32:15] 📥 Получен ответ: response_20260821_143215.json
История задач (PROCESSED)
Все выполненные задания хранятся в F:\TO_DBI\EXCHANGE\PROCESSED\ с временными метками.

Файлы для архивации
Файл	Назначение
bot.log	Лог всех операций
CHANGELOG.md	История изменений кода
PROJECT_STATUS.md	Этот файл — статус проекта
Контакты
Проект: TO_DBI (Адаптация под DBI)

Версия рубрикатора: 5.3.0

Версия документации: 2.0

Последнее обновление: 05.09.2026

Автор: Команда разработки АРМ «Адаптация под DBI»

Лог-файл: F:\TO_DBI\EXCHANGE\bot.log

-= Проект TO_DBI успешно инициализирован =-

text

---

## ✅ Итог

Теперь у вас есть **полный обновлённый `PROJECT_STATUS.md`** с:

1. ✅ Структурой проекта
2. ✅ Кратким обзором правил PlpCheck (93 шт.)
3. ✅ Топ-10 критических правил
4. ✅ Примером выполненной задачи DS 007
5. ✅ Всеми разделами из предыдущей версии

**Просто скопируйте содержимое и сохраните как `F:\TO_DBI\PROJECT_STATUS.md`** — файл готов к использованию! 🚀