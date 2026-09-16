#!/usr/bin/env python3
"""Добавление PlpCheck-правил в рубрикатор"""
import json
import re

# Читаем текущий JSON
with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print(f'Всего правил до обновления: {len(data.get("rules", {}))}')

rules = data['rules']

# NOT_MENTIONED
rules['PlpCheck.STYLE.NOT_MENTIONED'] = {
    "code": "PlpCheck.STYLE.NOT_MENTIONED",
    "short_description": "Переменная объявлена, но нигде не используется",
    "documentation_text": "Объявленные, но неиспользуемые переменные увеличивают размер кода и вносят путаницу. Все объявленные переменные должны использоваться в коде.",
    "regex_patterns": {
        "for_search": [
            {"pattern": "^\\s+(\\w+)\\s+(string|number|integer|varchar2|date|ref|rowtype|boolean)\\s*(?:\\([^)]*\\))?\\s*(?::=|;)", "description": "Объявление переменной"}
        ],
        "for_ignore": [
            {"pattern": "^\\s*--", "description": "Комментарии"}
        ]
    },
    "code_example_bad": "tmp_data number;\n-- tmp_data не используется",
    "code_example_good": "v_nTmpData number;\n-- v_nTmpData используется",
    "fix_instruction": "Удалить неиспользуемую переменную или начать использовать её в коде.",
    "priority": "MEDIUM", "priority_level": 2, "category": "STYLE", "subcategory": "STYLE.VARIABLES",
    "tags": ["style", "unused", "variables"], "ai_analysis_required": False
}

# CODE_IN_COMMENT
rules['PlpCheck.STYLE.CODE_IN_COMMENT'] = {
    "code": "PlpCheck.STYLE.CODE_IN_COMMENT",
    "short_description": "Закомментированный код",
    "documentation_text": "Закомментированный код должен быть удалён из проекта. Используйте системы контроля версий для хранения истории изменений.",
    "regex_patterns": {
        "for_search": [
            {"pattern": "^\\s*--.*\\b(if|then|else|end|if|return|:=|select|from|where)\\b", "description": "Закомментированный код"}
        ],
        "for_ignore": []
    },
    "code_example_bad": "--if lrecBrInfo.f_BIC is not null then null;",
    "code_example_good": "",
    "fix_instruction": "Удалить закомментированный код.",
    "priority": "LOW", "priority_level": 3, "category": "STYLE", "subcategory": "STYLE.COMMENTS",
    "tags": ["style", "commented", "code"], "ai_analysis_required": False
}

# PREFIX_BAD
rules['PlpCheck.STYLE.PREFIX_BAD.п.4.3'] = {
    "code": "PlpCheck.STYLE.PREFIX_BAD.п.4.3",
    "short_description": "Переменная с запрещённым префиксом",
    "documentation_text": "Запрещены префиксы: dp, dbg, debug, bad, badprefix, tmp, temp, var, data, info, z_, x_, test, dummy, fmt, lv. Локальные переменные должны начинаться с v_.",
    "regex_patterns": {
        "for_search": [
            {"pattern": "(?i)\\b(dp|dbg|debug|bad|badprefix|tmp|temp|var|data|info|z_|x_|test|dummy|fmt|fmt24|fmtHMS|lv|v1|v2|v3)\\w*\\s+(integer|string|number|date|boolean|ref|rowtype|varchar2)", "description": "Переменная с запрещённым префиксом"}
        ],
        "for_ignore": [
            {"pattern": "^\\s*--", "description": "Комментарии"}
        ]
    },
    "code_example_bad": "dp integer:=0;",
    "code_example_good": "v_iDp integer:=0;",
    "fix_instruction": "Переименовать переменную: dp integer -> v_iDp (v_=локальная, i=integer, Dp=смысл).",
    "priority": "HIGH", "priority_level": 1, "category": "STYLE", "subcategory": "STYLE.PREFIX",
    "tags": ["style", "prefix", "naming"], "ai_analysis_required": False
}

# PREFIX_TYPE_IN_VAR
rules['PlpCheck.STYLE.PREFIX_TYPE_IN_VAR.п.4.4'] = {
    "code": "PlpCheck.STYLE.PREFIX_TYPE_IN_VAR.п.4.4",
    "short_description": "Переменная не содержит префикс типа в имени",
    "documentation_text": "Локальные переменные должны начинаться с v_ (или p_ для параметров), за которым следует префикс типа (i=integer, n=number, v=varchar2, d=date, b=boolean, lr=ref).",
    "regex_patterns": {
        "for_search": [
            {"pattern": "^\\s+(\\w+)\\s+(string|number|integer|varchar2|date|ref|rowtype|boolean)\\b", "description": "Объявление переменной без префикса типа"}
        ],
        "for_ignore": [
            {"pattern": "(?i)^(\\s+)?(v_|p_|cn_|cur_|ret_)[invdblr]", "description": "Переменные с корректным префиксом"}
        ]
    },
    "code_example_bad": "lrBranch ref [BRANCH];",
    "code_example_good": "v_lrBranch ref [BRANCH];",
    "fix_instruction": "Добавить префикс типа: lrBranch ref -> v_lrBranch ref (v_=локальная, lr=ref, Branch=смысл).",
    "priority": "HIGH", "priority_level": 1, "category": "STYLE", "subcategory": "STYLE.PREFIX",
    "tags": ["style", "prefix", "type", "naming"], "ai_analysis_required": False
}

# Сохраняем
with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'w', encoding='utf-8-sig') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Проверяем
with open('DATA/Рубрикатор v5/4.RUBRICATOR_PROMPT v5.json', 'r', encoding='utf-8-sig') as f:
    checked = json.load(f)

print(f'Добавлено новых правил: 4')
print(f'Всего правил теперь: {len(checked.get("rules", {}))}')
print(f'JSON валиден!')
