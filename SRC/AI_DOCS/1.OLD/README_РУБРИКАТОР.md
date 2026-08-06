# 📋 Рубрикатор маркировок PLPlus → DBI (v03)

## 🎯 Назначение

Рубрикатор — это централизованное хранилище требований к миграции кода с Oracle (PLPlus) на PostgreSQL (DBI). Он обеспечивает:

- **Единый источник истины** для всех правил маркировки
- **Версионирование** требований и изменений
- **Аудит** всех корректировок
- **Автоматизацию** через интеграцию с `code_fixer.py`
- **Поддержку PDF и TXT форматов** документации (v03)

---

## 📁 Структура файлов

```
SRC/AI_DOCS/
├── rubricator_markers.json    # Основная версия (JSON)
├── rubricator_markers.csv     # Excel-версия (для редактирования)
├── rubricator_loader.py       # Python-модуль загрузки
├── create_excel_rubricator.py # Генератор Excel-файла
├── README_РУБРИКАТОР.md       # Эта документация
└── docs_index.md              # Индекс документации (v03)
```

---

## 📊 Лист 1: MARKERS (Маркировка исправлений)

### Колонки

| Поле | Тип | Обязательное | Описание | Пример |
|------|-----|--------------|----------|--------|
| **ID** | string | ✅ | Уникальный идентификатор | `M001` |
| **Документ** | string | ✅ | Ссылка на документ (ID со 2-го листа) | `DOC_TDS_PDF` |
| **Строки** | string | ✅ | Диапазон строк в документации | `строки с 32 по 48` |
| **Маркер** | string | ✅ | Идентификатор правила | `тдс20240828.п.1` |
| **Формат маркировки** | string | ✅ | Полный формат комментария | `-- тдс20240828.п.1 строки с XXXX по YYYY. ...` |
| **Описание** | string | ✅ | Краткое описание изменения | `SYSDATE -> SYSTEM.OP_DATE` |
| **Статус** | enum | ✅ | `active` / `draft` / `deprecated` | `active` |
| **Версия** | string | ✅ | Версия правила | `v1.0` |
| **Дата_обновления** | date | ✅ | Последнее изменение | `2026-04-15` |
| **Примечания** | string | ❌ | Доп. информация | `Обязательная обработка PDF` |

### Пример записи

```json
{
  "id": "M007",
  "document_id": "DOC_TDS_PDF",
  "line_range": "строки с XX по YY",
  "marker": "тдс20240828.п.1",
  "format": "-- тдс20240828.п.1 строки с XXXX по YYYY. SYSDATE -> SYSTEM.OP_DATE",
  "description": "Замена SYSDATE на SYSTEM.OP_DATE (ТДС 2024-08-28)",
  "status": "active",
  "version": "v1.0",
  "updated": "2026-04-15",
  "notes": "Обязательная обработка: тдс20240828.Требования для совместимости кода с DBI.pdf"
}
```

---

## 🔄 Формат маркировки в коде

### Шаблон

```plp
-- {marker} строки с XXXX по YYYY. {description}
--OLD {YYYY-MM-DD HH:MM}:
-- {original_code}
{new_code}
```

### Примеры

```plp
-- v50.2.1 строки с 32 по 48. NativeID: NUMBER -> VARCHAR2(100)
--OLD 2026-04-15 10:30:
-- dp  number:=0;
dp VARCHAR2(100):=0;

-- тдс20240828.п.1 строки с XX по YY. SYSDATE -> SYSTEM.OP_DATE
--OLD 2026-04-15 10:31:
-- created := SYSDATE;
created := SYSTEM.OP_DATE;

-- тклоик20240828.КОДИРОВАНИЕ.п.3 строки с XX по YY. VARCHAR -> VARCHAR2
--OLD 2026-04-15 10:32:
-- name  VARCHAR(100);
name  VARCHAR2(100);
```

---

## 📊 Лист 2: DOCUMENTATION (Источники документации)

### Колонки

| Поле | Тип | Обязательное | Описание | Пример |
|------|-----|--------------|----------|--------|
| **ID** | string | ✅ | Уникальный идентификатор | `DOC_TDS_PDF` |
| **Маркер** | string | ✅ | Префикс для правил | `тдс20240828` |
| **Файл** | string | ✅ | Имя файла документации | `тдс20240828.Требования для совместимости кода с DBI.pdf` |
| **Путь** | string | ✅ | Относительный путь | `DATA/CFT Platform IDE Documentation/` |
| **Формат** | string | ✅ | Тип файла | `pdf` / `txt` / `docx` |
| **Версия** | string | ✅ | Версия документа | `v1.0` |
| **Статус** | enum | ✅ | `active` / `deprecated` | `active` |
| **Приоритет** | string | ❌ | Приоритет обработки | `high` |
| **Дата_актуализации** | date | ✅ | Последняя проверка | `2026-04-13` |
| **Автор** | string | ❌ | Ответственный | `NLP-Core-Team` |
| **Примечания** | string | ❌ | Доп. информация | `Обязательная обработка` |

---

## 🔄 Формат маркировки в коде

### Шаблон

```plp
-- {marker} Стр.X,П.Y. {description}
--OLD {YYYY-MM-DD HH:MM}:
-- {original_code}
{new_code}
```

### Примеры

```plp
-- v50.2.1 Стр.8,П.1. NativeID: NUMBER -> VARCHAR2(100)
--OLD 2026-04-13 12:36:
-- dp  number:=0;
dp VARCHAR2(100):=0;

-- тдс20240828.п.1 Стр.5,П.1. SYSDATE -> SYSTEM.OP_DATE
--OLD 2026-04-13 12:37:
-- created := SYSDATE;
created := SYSTEM.OP_DATE;

-- тклоик20240828.КОДИРОВАНИЕ.п.3 Стр.3,П.3. VARCHAR -> VARCHAR2
--OLD 2026-04-13 12:38:
-- name  VARCHAR(100);
name  VARCHAR2(100);
```

---

## 🛠️ Использование

### 1. Просмотр рубрикатора

```bash
cd F:\TO_DBI\SRC\fixer
python rubricator_loader.py
```

### 2. Редактирование в Excel

1. Откройте `rubricator_markers.csv` в Excel
2. Внесите изменения
3. Сохраните как CSV (UTF-8)
4. Запустите валидацию:

```python
from fixer.rubricator_loader import RubricatorLoader

rubricator = RubricatorLoader()
print(f"Загружено маркеров: {len(rubricator.get_active_markers())}")
```

### 3. Интеграция с code_fixer.py

```python
from fixer.code_fixer import PLPlusFixer

# Автоматическая загрузка рубрикатора
fixer = PLPlusFixer(config, iteration, use_rubricator=True)
```

### 4. Добавление нового правила

**В rubricator_markers.json:**

```json
{
  "id": "M011",
  "document_id": "DOC_V50",
  "page_paragraph": "Стр.20,П.4",
  "marker": "v50.4.0",
  "format": "-- v50.4.0 Стр.20,П.4. NEW_RULE -> NEW_IMPLEMENTATION",
  "description": "Описание нового правила",
  "status": "draft",
  "version": "v50.2",
  "updated": "2026-04-13",
  "notes": "Черновик - требует проверки"
}
```

**Затем перевести в active:**

```python
rubricator.update_marker('v50.4.0', {'status': 'active'})
rubricator.save()
```

---

## 📝 Журнал изменений (Audit Log)

Все изменения фиксируются в поле `audit_log`:

```json
{
  "date": "2026-04-13T15:30:00",
  "action": "updated",
  "author": "NLP-Core-Team",
  "changes": "Добавлено правило v50.4.0"
}
```

---

## ✅ Контроль качества

### Валидация перед применением

```python
def validate_rubricator(rubricator: RubricatorLoader) -> List[str]:
    """Проверка целостности рубрикатора"""
    errors = []
    
    # Проверка активных маркеров
    for marker in rubricator.get_active_markers():
        if not marker.get('format'):
            errors.append(f"Маркер {marker.get('marker')} не имеет формата")
        if len(marker.get('description', '')) > 120:
            errors.append(f"Маркер {marker.get('marker')}: описание > 120 символов")
    
    # Проверка ссылок на документы
    for marker in rubricator.get_active_markers():
        doc_id = marker.get('document_id')
        if doc_id and not rubricator.get_document(doc_id):
            errors.append(f"Маркер {marker.get('marker')}: документ {doc_id} не найден")
    
    return errors
```

---

## 📈 Статистика

| Показатель | Значение |
|------------|----------|
| Активных маркеров | 10 |
| Черновиков | 1 |
| Активных документов | 5 |
| PDF документов (обязательных) | 2 |
| TXT документов | 2 |
| Последнее обновление | 2026-04-15 10:00 |
| Версия рубрикатора | v03 |

---

## 🚀 Будущие улучшения

- [ ] Экспорт в Excel с автогенерацией форматирования
- [ ] Web-интерфейс для редактирования
- [ ] Интеграция с Git для отслеживания версий
- [ ] Автоматическая генерация документации
- [ ] Поддержка нескольких версий документации параллельно
- [ ] Автоматическое извлечение требований из PDF (v03)

---

## 📞 Контакты

**Вопросы по рубрикатору:** NLP-Core-Team  
**Версия:** v03  
**Дата создания:** 2026-04-13
