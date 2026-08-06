# Исправление правила v50.SQL.OUTERJOIN.п.1.1

## Что исправлено

Добавлены паттерны для автоматического удаления `(true)` из конструкций PLPlus и добавления инструкции по преобразованию в LEFT JOIN.

### Паттерны в `SRC/fixer/code_fixer.py`:

```python
'v50.SQL.OUTERJOIN.п.1.1': [
    # Oracle (+) → LEFT JOIN
    (r'\(\+\)', 'LEFT JOIN', True, 'v50.SQL.OUTERJOIN.п.1.1'),
    # [REF](true) → инструкция по LEFT JOIN
    (r'(\w+)%?(\w+)\s*=\s*(\w+)\s*\.\s*\[(\w+)\]\s*\(true\)', 
     r'--<ВАЖНО: преобразовать в LEFT JOIN: left join [TABLE] \3 on \1=\3.\4>', 
     False, 'v50.SQL.OUTERJOIN.п.1.1'),
    # [TABLE](true) → удаление (true)
    (r'(\w+)\s*\.\s*\[(\w+)\]\s*\(true\)', 
     r'\1.\2 --<ВАЖНО: добавить LEFT JOIN вручную>', 
     False, 'v50.SQL.OUTERJOIN.п.1.1'),
    # collection(true) → удаление (true)
    (r'(\w+)\s*\.\s*(\w+)\s*\(true\)', 
     r'\1.\2 --<ВАЖНО: добавить LEFT JOIN вручную>', 
     False, 'v50.SQL.OUTERJOIN.п.1.1'),
    # &collection(true) → удаление (true)
    (r'&collection\s*\(true\)', 
     r'&collection --<ВАЖНО: добавить LEFT JOIN вручную>', 
     False, 'v50.SQL.OUTERJOIN.п.1.1'),
]
```

## Результат

### Пример 1: `ac%id = gj.[ACCOUNT](true)`

**Было:**
```sql
where ac%id = gj.[ACCOUNT](true)
```

**Станет:**
```sql
--(*)v50.SQL.OUTERJOIN.п.1.1 - [ПРОМПТ] ...
--OLD 2026-05-02 ...
-- ac%id = gj.[ACCOUNT](true)
--<ВАЖНО: преобразовать в LEFT JOIN: left join [TABLE] gj on ac=gj.ACCOUNT>
```

### Пример 2: `gj.[IN_FILE_HISTORY] = st.collection_id(true)`

**Было:**
```sql
gj.[IN_FILE_HISTORY] = st.collection_id(true)
```

**Станет:**
```sql
gj.[IN_FILE_HISTORY] = st.collection_id --<ВАЖНО: добавить LEFT JOIN вручную>
```

## Почему не полное автоматическое преобразование

Полное преобразование в `LEFT JOIN` требует:
1. Знания названия таблицы (не только алиаса)
2. Анализа контекста запроса (WHERE, JOIN условия)
3. Перестройки структуры запроса

Это невозможно сделать через regex-замены. Фиксер удаляет `(true)` и добавляет инструкцию для ручного исправления.

## Как запустить исправление

1. Откройте АРМ: `python SRC/gui_app.py`
2. Укажите исходный каталог: `F:\TO_DBI\PATCH_IN\patch_RV`
3. Отметьте правило `v50` в рубрикаторе
4. Нажмите **Сканировать (F5)**
5. Нажмите **Исправить код (F6)**
6. Проверьте результаты в `F:\TO_DBI\PATCH_OUT\patch_RV\patch_RV_v<дата>\`

## Ручное исправление

После автоматического исправления вручную замените:

```sql
--<ВАЖНО: преобразовать в LEFT JOIN: left join [TABLE] gj on ac=gj.ACCOUNT>
```

На:

```sql
left join [GNI_JOUR] gj on ac%id = gj.[ACCOUNT]
```

(Замените `[GNI_JOUR]` на реальное название таблицы из контекста)
