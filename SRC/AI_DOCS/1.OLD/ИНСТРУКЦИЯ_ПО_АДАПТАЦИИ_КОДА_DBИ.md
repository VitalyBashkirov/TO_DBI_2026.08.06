# Инструкция по адаптации кода под DBI для Kode

## Оглавление

1. [Что нужно знать перед началом](#1-что-нужно-знать-перед-началом)
2. [SQL/DML — самые частые изменения](#2-sqldml--самые-частые-изменения)
3. [Хранение данных](#3-хранение-данных)
4. [Процедурный код](#4-процедурный-код)
5. [Интеграции](#5-интеграции)
6. [Кэширование](#6-кэширование)
7. [Чек-лист разработчика](#7-чек-лист-разработчика)
8. [Где брать актуальную информацию](#8-где-брать-актуальную-информацию)
9. [Памятка для быстрого поиска проблем](#9-памятка-для-быстрого-поиска-проблем)

---

## 1. Что нужно знать перед началом

### Основные принципы DBI

| Принцип | Значение |
|---------|----------|
| **Единая кодоваяая база** | Один код для Oracle и PostgreSQL |
| **ANSI SQL стандарт** | Отказ от Oracle-специфичных конструкций |
| **Двухфазная архитектура** | Ядро (Kernel) + Прикладной уровень (Runtime) |
| **Кэширование** | Многоуровневая система кэширования Hibernate |
| **Безопасность** | Централизованное управление правами доступа |

### Цветовая маркировка в документации

| Цвет | Значение | Действие |
|------|----------|----------|
| 🔵 **Синий** | Критичные изменения | Обязательно к исполнению |
| 🟣 **Фиолетовый** | Рекомендации по оптимизации | Желательно выполнить |
| 🟠 **Оранжевый** | Особенности реализации | Изучить и учесть |
| ⚪ **Серый** | Справочная информация | Для ознакомления |

---

## 2. SQL/DML — самые частые изменения

### 2.1. Outer Join: `(+)` → `LEFT/RIGHT JOIN`

**❌ Было (Oracle):**
```sql
SELECT t1.name, t2.value
FROM table1 t1, table2 t2
WHERE t1.id = t2.id(+)
```

**✅ Стало (ANSI SQL / DBI):**
```sql
SELECT t1.name, t2.value
FROM table1 t1
LEFT JOIN table2 t2 ON t1.id = t2.id
```

**❌ Было (Oracle right join):**
```sql
SELECT t1.name, t2.value
FROM table1 t1, table2 t2
WHERE t1.id(+) = t2.id
```

**✅ Стало (ANSI SQL / DBI):**
```sql
SELECT t1.name, t2.value
FROM table1 t1
RIGHT JOIN table2 t2 ON t1.id = t2.id
```

---

### 2.2. Ограничение выборки: `ROWNUM` → `FETCH FIRST`

**❌ Было (Oracle):**
```sql
SELECT * FROM (
    SELECT * FROM clients ORDER BY created_date DESC
) WHERE ROWNUM <= 10
```

**✅ Стало (ANSI SQL / DBI):**
```sql
SELECT * FROM clients
ORDER BY created_date DESC
FETCH FIRST 10 ROWS ONLY
```

**❌ Было (Oracle ROWNUM = 1):**
```sql
SELECT * FROM clients WHERE ROWNUM = 1
```

**✅ Стало (ANSI SQL / DBI):**
```sql
SELECT * FROM clients
FETCH FIRST 1 ROW ONLY
```

---

### 2.3. `DECODE` → `CASE`

**❌ Было (Oracle):**
```sql
SELECT DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown') AS status_name
FROM clients
```

**✅ Стало (ANSI SQL / DBI):**
```sql
SELECT CASE status
    WHEN 'A' THEN 'Active'
    WHEN 'I' THEN 'Inactive'
    ELSE 'Unknown'
END AS status_name
FROM clients
```

**❌ Было (Oracle с условием):**
```sql
SELECT DECODE(SIGN(amount - 1000), 1, 'Large', 'Small') AS size_type
FROM transactions
```

**✅ Стало (ANSI SQL / DBI):**
```sql
SELECT CASE
    WHEN amount > 1000 THEN 'Large'
    ELSE 'Small'
END AS size_type
FROM transactions
```

---

### 2.4. Иерархические запросы: `CONNECT BY` → `WITH RECURSIVE`

**❌ Было (Oracle):**
```sql
SELECT employee_id, manager_id, LEVEL
FROM employees
START WITH manager_id IS NULL
CONNECT BY PRIOR employee_id = manager_id
```

**✅ Стало (ANSI SQL / DBI):**
```sql
WITH RECURSIVE emp_hierarchy AS (
    SELECT employee_id, manager_id, 1 AS level_num
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.employee_id, e.manager_id, eh.level_num + 1
    FROM employees e
    INNER JOIN emp_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT employee_id, manager_id, level_num AS level
FROM emp_hierarchy
```

---

### 2.5. UDF в SQL: где запрещено, где можно

| Контекст | Статус | Примечание |
|----------|--------|------------|
| SELECT список | ✅ Разрешено | С ограничениями на производительность |
| WHERE условие | ⚠️ Ограничено | Может блокировать использование индексов |
| JOIN условие | ❌ Запрещено | Не поддерживается оптимизатором |
| GROUP BY | ⚠️ Ограничено | Только детерминированные функции |
| ORDER BY | ✅ Разрешено | Может влиять на производительность |

**❌ Было (UDF в JOIN):**
```sql
SELECT * FROM t1, t2
WHERE t1.id = get_id_from_name(t2.name)
```

**✅ Стало (через подзапрос):**
```sql
SELECT t1.*, t2.*
FROM t1
INNER JOIN (
    SELECT id, name FROM t2 WHERE get_id_from_name(name) IS NOT NULL
) t2 ON t1.id = t2.id
```

---

### 2.6. Системные представления Oracle

| Oracle представление | Статус в DBI | Альтернатива |
|---------------------|--------------|--------------|
| `DUAL` | ❌ Запрещено | `SELECT ... FROM SYSTEM.DUAL` или без FROM |
| `USER_TABLES` | ❌ Запрещено | `STDLIB.GET_TABLE_INFO()` |
| `ALL_TAB_COLUMNS` | ❌ Запрещено | `STDLIB.GET_COLUMN_INFO()` |
| `USER_SEQUENCES` | ❌ Запрещено | `STDLIB.GET_SEQUENCE_INFO()` |
| `V$SESSION` | ❌ Запрещено | `RUNTIME.SESSION_MGR` |
| `USER_OBJECTS` | ❌ Запрещено | `STDLIB.GET_OBJECT_INFO()` |
| `SYSDATE` | ❌ Запрещено | `SYSTEM.OP_DATE` |
| `USER` | ❌ Запрещено | `STDLIB.USERID` |
| `SYSTIMESTAMP` | ❌ Запрещено | `SYSTEM.OP_TIMESTAMP` |

---

## 3. Хранение данных

### 3.1. Тип `DATE` → `DATE_TIME` для PostgreSQL

**Особенности:**
- Oracle `DATE` хранит дату и время (7 байт)
- PostgreSQL `DATE` хранит только дату (4 байта)
- PostgreSQL `TIMESTAMP` хранит дату и время (8 байт)
- DBI использует `DATE_TIME` для совместимости

**❌ Было (Oracle):**
```plp
created_date DATE := SYSDATE;
```

**✅ Стало (DBI):**
```plp
created_date DATE_TIME := SYSTEM.OP_DATE;
```

**Правило:** Все поля типа `DATE` в Oracle, содержащие время, должны быть объявлены как `DATE_TIME` в DBI.

---

### 3.2. Временные таблицы

**Проблема:** Временные таблицы Oracle (`GLOBAL TEMPORARY TABLES`) не поддерживаются в PostgreSQL в том же виде.

**Решение:** Использовать альтернативы:

| Oracle | DBI Альтернатива |
|--------|------------------|
| `GLOBAL TEMPORARY TABLE` | `VARRAY` / Коллекции |
| `INSERT INTO temp_table` | `RUNTIME.TEMP_STORAGE` |
| `ON COMMIT PRESERVE ROWS` | Локальные переменные |

**Пример с `init_temp_table`:**

**❌ Было (Oracle):**
```plp
CREATE GLOBAL TEMPORARY TABLE temp_calc (
    id NUMBER,
    value NUMBER
) ON COMMIT PRESERVE ROWS;

INSERT INTO temp_calc SELECT id, value FROM source;
```

**✅ Стало (DBI):**
```plp
TYPE temp_calc_type IS VARRAY(10000) OF RECORD (
    id NUMBER,
    value NUMBER
);

temp_data temp_calc_type := temp_calc_type();
```

---

### 3.3. Уникальные индексы с NULL

**Различие Oracle/PostgreSQL:**

| СУБД | Поведение с NULL |
|------|------------------|
| Oracle | NULL ≠ NULL, можно несколько NULL |
| PostgreSQL | NULL = NULL, только один NULL |

**❌ Было (Oracle):**
```sql
CREATE UNIQUE INDEX idx_unique_email ON clients(email);
-- В Oracle: несколько записей с email = NULL
```

**✅ Стало (DBI):**
```sql
-- Вариант 1: Частичный индекс
CREATE UNIQUE INDEX idx_unique_email ON clients(email)
WHERE email IS NOT NULL;

-- Вариант 2: Функциональный индекс
CREATE UNIQUE INDEX idx_unique_email ON clients(COALESCE(email, id));
```

---

### 3.4. Размер BTREE индекса

**Ограничение:** Максимальный размер BTREE индекса в PostgreSQL — 2704 байта (зависит от `page_size`).

**Проблема:** Индексы на строковые поля большой длины могут превышать лимит.

**Решения:**

| Способ | Когда применять | Пример |
|--------|-----------------|--------|
| Хэш-индекс | Для точных совпадений | `CREATE INDEX idx_hash ON t USING HASH (long_field)` |
| Частичный индекс | Для частых запросов с условием | `CREATE INDEX idx_partial ON t (field) WHERE field IS NOT NULL` |
| Индекс по префиксу | Для поиска по началу строки | `CREATE INDEX idx_prefix ON t (SUBSTRING(field, 1, 100))` |
| GiST индекс | Для полнотекстового поиска | `CREATE INDEX idx_gist ON t USING GIST (text_field)` |

---

## 4. Процедурный код

### 4.1. Замена Oracle пакетов

| Oracle компонент | DBI Альтернатива | Примечание |
|-----------------|------------------|------------|
| `PACKAGE` | `ENTITY` / `TYPE` | Группировка по бизнес-объектам |
| `PACKAGE BODY` | `.plp` файлы | Реализация в отдельных файлах |
| `PACKAGE VARIABLE` | `GLOBAL` переменные | Через `RUNTIME.GLOBAL` |
| `PACKAGE FUNCTION` | `FUNCTION` в ENTITY | Экспорт через интерфейс |
| `PACKAGE PROCEDURE` | `PROCEDURE` в ENTITY | Экспорт через интерфейс |

---

### 4.2. `EXECUTE IMMEDIATE`: правила

**Правило 1: Экранирование параметров**

**❌ Было (риск SQL-инъекции):**
```plp
sql_text := 'SELECT * FROM clients WHERE id = ' || p_id;
EXECUTE IMMEDIATE sql_text;
```

**✅ Стало (с параметрами):**
```plp
sql_text := 'SELECT * FROM clients WHERE id = :1';
EXECUTE IMMEDIATE sql_text USING p_id;
```

**Правило 2: Сброс кэша**

```plp
-- После DDL операций
EXECUTE IMMEDIATE 'ALTER SESSION SET SQL_CACHE = NONE';
```

**Правило 3: Обработка ошибок**

```plp
BEGIN
    EXECUTE IMMEDIATE sql_text USING p_id;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
```

---

### 4.3. `WHEN OTHERS`: обязательный rollback или raise

**❌ Было (Oracle — подавление ошибок):**
```plp
BEGIN
    INSERT INTO audit_log VALUES (...);
    UPDATE accounts SET balance = balance - 100 WHERE id = p_id;
EXCEPTION
    WHEN OTHERS THEN
        NULL; -- Ошибка игнорируется!
END;
```

**✅ Стало (DBI — правильная обработка):**
```plp
BEGIN
    INSERT INTO audit_log VALUES (...);
    UPDATE accounts SET balance = balance - 100 WHERE id = p_id;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE; -- Передаём ошибку выше
END;
```

**Или с логированием:**
```plp
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RUNTIME.LOG_ERROR(SQLERRM);
        RAISE;
```

---

### 4.4. Bulk операции

**Поддерживаются:**

| Операция | Oracle | DBI PostgreSQL | Примечание |
|----------|--------|----------------|------------|
| `BULK COLLECT` | ✅ | ✅ | Ограничение: 10000 строк за раз |
| `FORALL` | ✅ | ✅ | Пакетная вставка/обновление |
| `SAVE EXCEPTIONS` | ✅ | ⚠️ | Частичная поддержка |

**Пример `FORALL`:**

```plp
TYPE t_id_table IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
l_ids t_id_table;

-- Заполнение массива
FOR i IN 1..l_ids.COUNT LOOP
    l_ids(i) := i;
END LOOP;

-- Пакетная вставка
FORALL i IN 1..l_ids.COUNT
    INSERT INTO target_table (id) VALUES (l_ids(i));
```

**Ограничение:** Избегать `BULK COLLECT` без `LIMIT` для больших объёмов данных.

---

## 5. Интеграции

### 5.1. Замена Database Link на REST/SOAP

| Задача | Oracle | DBI Альтернатива | Приложение | Версия |
|--------|--------|------------------|------------|--------|
| Запрос к удалённой БД | `DBLINK` | `RUNTIME.HTTP_MGR` | HTTP-клиент | v50+ |
| Вызов удалённой процедуры | `RPC over DBLINK` | `SOAP/REST` | Web-сервис | v50+ |
| Репликация данных | `Materialized View` | `ETL / CDC` | Integration Hub | v51+ |
| Обмен файлами | `UTL_FILE` | `RUNTIME.FILE_MGR` | File-сервис | v50+ |
| Отправка email | `UTL_MAIL` | `RUNTIME.SMTP_MAIL` | SMTP-сервис | v50+ |

**Пример вызова REST:**

```plp
-- ❌ Было (DBLINK)
SELECT * FROM remote_table@DBLINK_NAME;

-- ✅ Стало (REST)
l_response := RUNTIME.HTTP_MGR.GET(
    p_url => 'https://api.example.com/data',
    p_headers => http_headers
);
```

---

### 5.2. Очереди

| Компонент | Oracle | DBI Альтернатива |
|-----------|--------|------------------|
| Очереди сообщений | `Oracle AQ` | `Apache ActiveMQ` |
| Управление очередями | `DBMS_AQ` | `[RUNTIME].[AQ_LIB]` |
| Подписка | `AQ$SUBSCRIBERS` | `RUNTIME.AQ_SUBSCRIBE` |
| Публикация | `DBMS_AQ.ENQUEUE` | `RUNTIME.AQ_PUBLISH` |

**Пример работы с очередью:**

```plp
-- Публикация сообщения
RUNTIME.AQ_PUBLISH(
    p_queue_name => 'NOTIFY_QUEUE',
    p_message => l_message,
    p_priority => 1
);

-- Подписка и получение
l_message := RUNTIME.AQ_SUBSCRIBE(
    p_queue_name => 'NOTIFY_QUEUE',
    p_wait_time => 5
);
```

---

## 6. Кэширование

### 6.1. Уровни кэша Hibernate

| Уровень | Где хранится | Размер | Время жизни |
|---------|--------------|--------|-------------|
| **L1 (Session)** | В сессии пользователя | Ограничен сессией | До конца сессии |
| **L2 (SessionFactory)** | Общий для приложения | Настраиваемый (MB/GB) | До перезапуска / инвалидации |
| **Query Cache** | Кэш запросов | Ограниченный | До изменения данных |

---

### 6.2. Разыменование ссылки = обращение к кэшу

**Пример:**

```plp
-- ✅ Правильно: использование кэша
l_client := client_ref;  -- Объект из кэша
l_name := l_client.name; -- Быстрое обращение

-- ❌ Неправильно: лишний запрос
SELECT name INTO l_name FROM clients WHERE id = p_id;
```

---

### 6.3. Совет: получать поля сразу в курсоре

**❌ Было (N+1 проблема):**
```plp
FOR l_client IN (SELECT id FROM clients) LOOP
    l_name := get_client_name(l_client.id); -- Запрос на каждую итерацию
END LOOP;
```

**✅ Стало (один запрос):**
```plp
FOR l_client IN (
    SELECT id, name FROM clients
) LOOP
    l_name := l_client.name; -- Из кэша курсора
END LOOP;
```

---

### 6.4. Настройка кэша 2 уровня (пример XML)

```xml
<!-- hibernate.cfg.xml -->
<property name="hibernate.cache.use_second_level_cache">true</property>
<property name="hibernate.cache.region.factory_class">
    org.hibernate.cache.ehcache.EhCacheRegionFactory
</property>
<property name="hibernate.cache.use_query_cache">true</property>

<!-- Настройка регионов -->
<cache region="clients" usage="read-write"/>
```

---

## 7. Чек-лист разработчика

### SQL запросы

- [ ] Все `(+)` заменены на `LEFT/RIGHT JOIN`
- [ ] `ROWNUM` заменён на `FETCH FIRST`
- [ ] `DECODE` заменён на `CASE`
- [ ] `CONNECT BY` заменён на `WITH RECURSIVE`
- [ ] Нет UDF в условиях `JOIN`
- [ ] Нет ссылок на системные представления Oracle
- [ ] `SYSDATE` заменён на `SYSTEM.OP_DATE`
- [ ] `USER` заменён на `STDLIB.USERID`

### Хранение

- [ ] Тип `DATE` заменён на `DATE_TIME` где нужно
- [ ] Временные таблицы заменены на `VARRAY`
- [ ] Уникальные индексы с NULL проверены
- [ ] Размер индексов не превышает 2704 байта

### Процедурный код

- [ ] Пакеты Oracle перенесены в `ENTITY`
- [ ] `EXECUTE IMMEDIATE` использует параметры
- [ ] Все `WHEN OTHERS` содержат `ROLLBACK` и `RAISE`
- [ ] `BULK COLLECT` использует `LIMIT`
- [ ] Нет подавления ошибок через `NULL`

### Интеграции

- [ ] `DBLINK` заменён на REST/SOAP
- [ ] `UTL_FILE` заменён на `RUNTIME.FILE_MGR`
- [ ] `UTL_MAIL` заменён на `RUNTIME.SMTP_MAIL`
- [ ] `UTL_HTTP` заменён на `RUNTIME.HTTP_MGR`
- [ ] Очереди используют `RUNTIME.AQ_LIB`

### Кэш

- [ ] Избегается проблема N+1
- [ ] Используется кэш L1/L2
- [ ] Настроена инвалидация кэша
- [ ] Критичные запросы помечены для кэширования

---

## 8. Где брать актуальную информацию

| Источник | Что там | Актуальность |
|----------|---------|--------------|
| `DATA/CFT Platform IDE Documentation/Рекомендации...v50.txt` | Основные правила миграции | ✅ Актуально |
| `тдс20240828.Требования для совместимости кода с DBI.pdf` | Требования ТДС | ✅ Обязательно |
| `тклоик20240828.Требования к локальным объектам.pdf` | Требования КЛОИК | ✅ Обязательно |
| `SRC/AI_DOCS/rubricator_markers.json` | Рубрикатор правил | ✅ Актуально |
| `RUNTIME` пакет | Библиотеки времени выполнения | ✅ Актуально |
| `STDLIB` пакет | Стандартная библиотека | ✅ Актуально |
| `SYSTEM` пакет | Системные функции | ✅ Актуально |

---

## 9. Памятка для быстрого поиска проблем

| Если ищете... | Искать в коде | Что делать |
|---------------|---------------|------------|
| Старые join | `(+), WHERE t1, t2` | Заменить на `LEFT/RIGHT JOIN` |
| Ограничение строк | `ROWNUM, TOP` | Заменить на `FETCH FIRST` |
| Условный выбор | `DECODE` | Заменить на `CASE` |
| Иерархия | `CONNECT BY, START WITH` | Заменить на `WITH RECURSIVE` |
| Дата/время | `SYSDATE, DATE` | Заменить на `SYSTEM.OP_DATE, DATE_TIME` |
| Пользователь | `USER, UID` | Заменить на `STDLIB.USERID` |
| Динамический SQL | `EXECUTE IMMEDIATE` | Добавить `USING`, экранирование |
| Обработка ошибок | `WHEN OTHERS THEN NULL` | Добавить `ROLLBACK; RAISE;` |
| Удалённый доступ | `@DBLINK, DBLINK` | Заменить на REST/SOAP |
| Файлы | `UTL_FILE` | Заменить на `RUNTIME.FILE_MGR` |
| HTTP | `UTL_HTTP` | Заменить на `RUNTIME.HTTP_MGR` |
| Почта | `UTL_MAIL` | Заменить на `RUNTIME.SMTP_MAIL` |
| Очереди | `DBMS_AQ` | Заменить на `RUNTIME.AQ_LIB` |
| Временные таблицы | `GLOBAL TEMPORARY TABLE` | Заменить на `VARRAY` |
| Системные объекты | `USER_*, ALL_*, V$*` | Заменить на `STDLIB.*, RUNTIME.*` |

---

## Приложения

### A. Маркировка исправлений в коде

```plp
-- v50.2.1 строки с 32 по 48. NativeID: NUMBER -> VARCHAR2(100)
--OLD 2026-04-15 10:30:
-- dp  number:=0;
dp VARCHAR2(100):=0;

-- тдс20240828.п.1 строки с 25 по 42. SYSDATE -> SYSTEM.OP_DATE
--OLD 2026-04-15 10:31:
-- created := SYSDATE;
created := SYSTEM.OP_DATE;

-- тклоик20240828.КОДИРОВАНИЕ.п.3 строки с 15 по 20. VARCHAR -> VARCHAR2
--OLD 2026-04-15 10:32:
-- name  VARCHAR(100);
name  VARCHAR2(100);
```

### B. Контакты поддержки

| Вопрос | Куда обращаться |
|--------|-----------------|
| Технические вопросы | NLP-Core-Team |
| Документация | `SRC/AI_DOCS/README_РУБРИКАТОР.md` |
| Рубрикатор правил | `SRC/AI_DOCS/rubricator_markers.json` |

---

**Версия инструкции:** v1.0  
**Дата создания:** 2026-04-15  
**Автор:** NLP-Core-Team
