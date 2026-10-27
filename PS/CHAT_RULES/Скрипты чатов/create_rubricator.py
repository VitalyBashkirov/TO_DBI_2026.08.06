#!/usr/bin/env python3
"""Создание JSON рубрикатора с PlpCheck-правилами"""
import json

data = {
    'version': '5.0.1',
    'based_on': 'Рекомендации по адаптации кода на PLPlus для работы с DBI приложением v50.docx',
    'last_updated': '2026-08-18',
    'total_rules': 0,
    'ai_analysis_enabled': True,
    'rules': {}
}

rules = data['rules']

# BAD_PREFIX
rules['PlpCheck.STYLE.BAD_PREFIX.п.4.3'] = {
    'code': 'PlpCheck.STYLE.BAD_PREFIX.п.4.3',
    'short_description': 'Некорректный префикс переменной',
    'documentation_text': 'Запрещены префиксы: dp, dbg, debug, bad, badprefix, tmp, temp, var, data, info, z_, x_, test, dummy.',
    'regex_patterns': {
        'for_search': [
            {'pattern': '(?i)\\b(dp|dbg|debug|bad|badprefix|tmp|temp|var|data|info|z_|x_|test|dummy)\\w*\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)', 'description': 'Некорректный префикс'},
            {'pattern': '(?i)\\b(id|name|code|type|status|date|count|num|val|desc|title)\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)', 'description': 'Короткое имя без префикса типа'}
        ],
        'for_ignore': [{'pattern': '^\\s*--.*', 'description': 'Комментарии'}]
    },
    'code_example_bad': 'dp integer := 0;',
    'code_example_good': 'v_iDp integer := 0;',
    'fix_instruction': 'Переименовать в формат {назначение}{тип}{Смысл}.',
    'priority': 'HIGH', 'priority_level': 1, 'category': 'STYLE', 'subcategory': 'STYLE.PREFIX',
    'tags': ['style', 'prefix', 'naming'], 'ai_analysis_required': False
}

# PREFIX_TYPE
rules['PlpCheck.STYLE.PREFIX_TYPE.п.4.4'] = {
    'code': 'PlpCheck.STYLE.PREFIX_TYPE.п.4.4',
    'short_description': 'Наименование переменной не содержит префикс типа',
    'documentation_text': 'Все переменные должны иметь префикс типа в формате {назначение}{тип}{Смысл}.',
    'regex_patterns': {
        'for_search': [
            {'pattern': '(?i)\\b[a-z][a-z0-9_]*\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)\\b', 'description': 'Переменная без префикса типа (требуется проверка)'}
        ],
        'for_ignore': [
            {'pattern': '(?i)\\b(v_|p_|cn_|cur_|ret_)[invdblr][a-z0-9_]*\\s+(varchar2|string|number|date|boolean|ref|rowtype|integer|binary_integer|pls_integer|char|varchar|clob|blob|long|long\\s*raw|raw|bfile|timestamp|date_time)', 'description': 'Игнорировать переменные с корректным префиксом назначения+типа'},
            {'pattern': '^\\s*--', 'description': 'Игнорировать комментарии'}
        ]
    },
    'code_example_bad': 'dp integer := 0;',
    'code_example_good': 'v_iDp integer := 0;',
    'fix_instruction': 'Добавить {назначение}{тип}: dp integer -> v_iDp.',
    'priority': 'HIGH', 'priority_level': 1, 'category': 'STYLE', 'subcategory': 'STYLE.PREFIX',
    'tags': ['style', 'prefix', 'naming', 'types'], 'ai_analysis_required': False
}

# NOT_MENTIONED
rules['PlpCheck.STYLE.NOT_MENTIONED'] = {
    'code': 'PlpCheck.STYLE.NOT_MENTIONED',
    'short_description': 'Переменная объявлена, но нигде не используется',
    'documentation_text': 'Объявленные, но неиспользуемые переменные увеличивают размер кода и вносят путаницу.',
    'regex_patterns': {
        'for_search': [
            {'pattern': '^\\s+(\\w+)\\s+(string|number|integer|varchar2|date|ref|rowtype|boolean)\\s*(?:\\([^)]*\\))?\\s*(?::=|;)', 'description': 'Объявление переменной'}
        ],
        'for_ignore': [{'pattern': '^\\s*--', 'description': 'Комментарии'}]
    },
    'code_example_bad': 'tmp_data number;',
    'code_example_good': 'v_nTmpData number;',
    'fix_instruction': 'Удалить неиспользуемую переменную.',
    'priority': 'MEDIUM', 'priority_level': 2, 'category': 'STYLE', 'subcategory': 'STYLE.VARIABLES',
    'tags': ['style', 'unused', 'variables'], 'ai_analysis_required': False
}

# CODE_IN_COMMENT
rules['PlpCheck.STYLE.CODE_IN_COMMENT'] = {
    'code': 'PlpCheck.STYLE.CODE_IN_COMMENT',
    'short_description': 'Закомментированный код',
    'documentation_text': 'Закомментированный код должен быть удалён из проекта.',
    'regex_patterns': {
        'for_search': [
            {'pattern': '^\\s*--.*\\b(if|then|else|end|if|return|:=|select|from|where)\\b', 'description': 'Закомментированный код'}
        ],
        'for_ignore': []
    },
    'code_example_bad': '--if lrecBrInfo.f_BIC is not null then null;',
    'code_example_good': '',
    'fix_instruction': 'Удалить закомментированный код.',
    'priority': 'LOW', 'priority_level': 3, 'category': 'STYLE', 'subcategory': 'STYLE.COMMENTS',
    'tags': ['style', 'commented', 'code'], 'ai_analysis_required': False
}

# PREFIX_BAD
rules['PlpCheck.STYLE.PREFIX_BAD.п.4.3'] = {
    'code': 'PlpCheck.STYLE.PREFIX_BAD.п.4.3',
    'short_description': 'Переменная с запрещённым префиксом',
    'documentation_text': 'Запрещены префиксы: dp, dbg, debug, bad, badprefix, tmp, temp, var, data, info, z_, x_, test, dummy, fmt, lv.',
    'regex_patterns': {
        'for_search': [
            {'pattern': '(?i)\\b(dp|dbg|debug|bad|badprefix|tmp|temp|var|data|info|z_|x_|test|dummy|fmt|fmt24|fmtHMS|lv|v1|v2|v3)\\w*\\s+(integer|string|number|date|boolean|ref|rowtype|varchar2)', 'description': 'Переменная с запрещённым префиксом'}
        ],
        'for_ignore': [{'pattern': '^\\s*--', 'description': 'Комментарии'}]
    },
    'code_example_bad': 'dp integer:=0;',
    'code_example_good': 'v_iDp integer:=0;',
    'fix_instruction': 'Переименовать: dp integer -> v_iDp.',
    'priority': 'HIGH', 'priority_level': 1, 'category': 'STYLE', 'subcategory': 'STYLE.PREFIX',
    'tags': ['style', 'prefix', 'naming'], 'ai_analysis_required': False
}

# PREFIX_TYPE_IN_VAR
rules['PlpCheck.STYLE.PREFIX_TYPE_IN_VAR.п.4.4'] = {
    'code': 'PlpCheck.STYLE.PREFIX_TYPE_IN_VAR.п.4.4',
    'short_description': 'Переменная не содержит префикс типа в имени',
    'documentation_text': 'Локальные переменные должны начинаться с v_ (или p_ для параметров), за которым следует префикс типа.',
    'regex_patterns': {
        'for_search': [
            {'pattern': '^\\s+(\\w+)\\s+(string|number|integer|varchar2|date|ref|rowtype|boolean)\\b', 'description': 'Объявление переменной без префикса типа'}
        ],
        'for_ignore': [{'pattern': '(?i)^(\\s+)?(v_|p_|cn_|cur_|ret_)[invdblr]', 'description': 'Переменные с корректным префиксом'}]
    },
    'code_example_bad': 'lrBranch ref [BRANCH];',
    'code_example_good': 'v_lrBranch ref [BRANCH];',
    'fix_instruction': 'Добавить префикс типа: lrBranch ref -> v_lrBranch ref.',
    'priority': 'HIGH', 'priority_level': 1, 'category': 'STYLE', 'subcategory': 'STYLE.PREFIX',
    'tags': ['style', 'prefix', 'type', 'naming'], 'ai_analysis_required': False
}

data['total_rules'] = len(data['rules'])

with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'w', encoding='utf-8-sig') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'JSON создан! Всего правил: {len(data["rules"])}')

# Проверяем
with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
    checked = json.load(f)
print(f'JSON валиден!')
