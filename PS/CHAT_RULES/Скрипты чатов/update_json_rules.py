#!/usr/bin/env python3
"""Корректное обновление JSON рубрикатора с экранированием regex"""
import json

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

rules = data['rules']

# BAD_PREFIX
rules['PlpCheck.STYLE.BAD_PREFIX.п.4.3'] = {
    "code": "PlpCheck.STYLE.BAD_PREFIX.п.4.3",
    "short_description": "Некорректный префикс переменной",
    "documentation_text": "Запрещены префиксы: dp, dbg, debug, bad, badprefix, tmp, temp, var, data, info, z_, x_, test, dummy.\n\nФормат: {назначение}{тип}{Смысл}\n- Назначение: v_ = локальная, p_ = параметр, cn_ = константа, cur_ = курсор, ret_ = возвращаемое значение\n- Тип: i = integer, n = number, v = varchar2/string, d = date, b = boolean, lr = ref/rowtype, lrec = record, tb = table\n- Смысл: CamelCase с заглавной буквы\n\nПримеры:\n- dp integer → v_iDp\n- tmp_data date → v_dData\n- bad_var number → v_nVar\n- name varchar2 → v_vName",
    "plplus_materials_note": "Проверка из PLPCheck — выявляет некорректные префиксы переменных.",
    "search_prompt": "Проанализируй объявления переменных и проверь префиксы на соответствие рекомендациям.",
    "regex_patterns": {
        "for_search": [
            {
                "pattern": "(?i)\\b(dp|dbg|debug|bad|badprefix|tmp|temp|var|data|info|z_|x_|test|dummy)\\w*\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)",
                "description": "Некорректный префикс переменной (ошибка)"
            },
            {
                "pattern": "(?i)\\b(id|name|code|type|status|date|count|num|val|desc|title)\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)",
                "description": "Короткое имя без префикса типа"
            }
        ],
        "for_ignore": [
            {
                "pattern": "^\\s*--.*",
                "description": "Игнорировать комментарии"
            }
        ]
    },
    "code_example_bad": "dp integer := 0;\nbad_var varchar2(100);\ntmp_data number;\nname varchar2(50);",
    "code_example_good": "v_iDp integer := 0;\nv_nBadVar varchar2(100);\nv_dData number;\nv_vName varchar2(50);",
    "fix_instruction": "Переименовать в формат {назначение}{тип}{Смысл}:\n1. Удалить плохой префикс (dp, tmp, bad, var)\n2. Добавить назначение: v_ (локальная)\n3. Добавить тип: i=integer, n=number, v=varchar2, d=date\n4. Добавить смысл в CamelCase\n\nПримеры:\n- dp integer → v_iDp\n- bad_var number → v_nVar\n- tmp_data date → v_dData\n- name varchar2 → v_vName",
    "fix_prompt": "Переименуй переменную в формат {назначение}{тип}{Смысл}.",
    "test_generation_prompt": "Сгенерируй тестовый PLPlus файл для проверки правила 'PlpCheck.STYLE.BAD_PREFIX.п.4.3'.",
    "examples": {
        "dp_to_v_iDp": {"bad": "dp integer := 0;", "good": "v_iDp integer := 0;"},
        "tmp_data": {"bad": "tmp_data date;", "good": "v_dData date;"},
        "bad_var": {"bad": "bad_var number;", "good": "v_nVar number;"},
        "name": {"bad": "name varchar2(50);", "good": "v_vName varchar2(50);"}
    },
    "priority": "HIGH",
    "priority_level": 1,
    "category": "STYLE",
    "subcategory": "STYLE.PREFIX",
    "source_files": ["PlpCheck"],
    "source_sections": ["п.4.3"],
    "tags": ["style", "prefix", "naming"],
    "ai_analysis_required": False
}

# PREFIX_TYPE
rules['PlpCheck.STYLE.PREFIX_TYPE.п.4.4'] = {
    "code": "PlpCheck.STYLE.PREFIX_TYPE.п.4.4",
    "short_description": "Наименование переменной не содержит префикс типа",
    "documentation_text": "Все переменные должны иметь префикс типа в формате {назначение}{тип}{Смысл}:\n- Назначение: v_ = локальная, p_ = параметр, cn_ = константа, cur_ = курсор, ret_ = возвращаемое значение\n- Тип: i = integer, n = number, v = varchar2/string, d = date, b = boolean, lr = ref/rowtype, lrec = record, tb = table\n- Смысл: CamelCase с заглавной буквы\n\nПримеры:\n- dp integer → v_iDp (v_=локальная, i=integer, Dp=смысл)\n- name varchar2 → v_vName (v_=локальная, v=varchar2, Name=смысл)\n- count number → v_nCount (v_=локальная, n=number, Count=смысл)\n- user_id number → v_nUserId (v_=локальная, n=number, UserId=смысл)",
    "plplus_materials_note": "Имена переменных без префикса типа нарушают соглашения PLPlus.",
    "search_prompt": "Проанализируй объявления переменных и проверь, что их имена содержат префикс типа в формате {назначение}{тип}{Смысл}.",
    "regex_patterns": {
        "for_search": [
            {
                "pattern": "(?i)\\b[a-z][a-z0-9_]*\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)\\b",
                "description": "Переменная без префикса типа (требуется проверка)"
            }
        ],
        "for_ignore": [
            {
                "pattern": "(?i)\\b(v_|p_|cn_|cur_|ret_)[invdblr][a-z0-9_]*\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)",
                "description": "Игнорировать переменные с корректным префиксом назначения+типа"
            },
            {
                "pattern": "^\\s*--",
                "description": "Игнорировать комментарии"
            }
        ]
    },
    "code_example_bad": "dp integer := 0;\nid number;\nname varchar2(100);\nuser_id number;",
    "code_example_good": "v_iDp integer := 0;\nv_nId number;\nv_vName varchar2(100);\nv_nUserId number;",
    "fix_instruction": "Переименовать в формат {назначение}{тип}{Смысл}:\n1. Назначение: v_ (локальная переменная)\n2. Тип: i=integer, n=number, v=varchar2, d=date, b=boolean, lr=ref, lrec=record, tb=table\n3. Смысл: оставшаяся часть имени в CamelCase с заглавной буквы\n\nПримеры:\n- dp integer → v_iDp\n- name varchar2(100) → v_vName\n- count number → v_nCount\n- user_id number → v_nUserId\n- fmt24 date → v_dFmt24",
    "fix_prompt": "Переименуй переменную в формат {назначение}{тип}{Смысл}: v_ + префикс типа + CamelCase смысла.",
    "test_generation_prompt": "Сгенерируй тестовый PLPlus файл для проверки правила 'PlpCheck.STYLE.PREFIX_TYPE.п.4.4'.",
    "examples": {
        "integer": {"bad": "dp integer := 0;", "good": "v_iDp integer := 0;"},
        "varchar2": {"bad": "name varchar2(100);", "good": "v_vName varchar2(100);"},
        "number": {"bad": "count number := 10;", "good": "v_nCount number := 10;"},
        "with_underscore": {"bad": "user_id number;", "good": "v_nUserId number;"}
    },
    "priority": "HIGH",
    "priority_level": 1,
    "category": "STYLE",
    "subcategory": "STYLE.PREFIX",
    "source_files": ["PlpCheck"],
    "source_sections": ["п.4.4"],
    "tags": ["style", "prefix", "naming", "types"],
    "ai_analysis_required": False
}

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'w', encoding='utf-8-sig') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON обновлён успешно!")
print(f"Правило BAD_PREFIX: {len(rules['PlpCheck.STYLE.BAD_PREFIX.п.4.3']['regex_patterns']['for_search'])} паттернов")
print(f"Правило PREFIX_TYPE: {len(rules['PlpCheck.STYLE.PREFIX_TYPE.п.4.4']['regex_patterns']['for_search'])} паттернов")
