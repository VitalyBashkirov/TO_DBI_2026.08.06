#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для формирования промптов для KODA
Содержит шаблоны промптов для различных сценариев исправления PLPlus кода
"""


class KodaPrompts:
    """Генератор промптов для KODA"""
    
    @staticmethod
    def generate_full_fix_prompt(code: str, rules: list = None) -> str:
        """
        Генерация полного промпта для исправления кода
        
        Args:
            code: исходный код PLPlus
            rules: список правил для применения
            
        Returns:
            str: полный промпт для KODA
        """
        base_prompt = """Ты — AI-ассистент для адаптации PLPlus кода под DBI (PostgreSQL). Исправляй код согласно рубрикатору v5.0.1.

ИСХОДНЫЙ КОД ДЛЯ ИСПРАВЛЕНИЯ:
{code}

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:

## 1. ОБНОВЛЕНИЕ ССЫЛОК НА ПЕРЕИМЕНОВАННЫЕ ПЕРЕМЕННЫЕ (САМОЕ ВАЖНОЕ!)
После переименования переменной ОБЯЗАТЕЛЬНО найди и обнови ВСЕ её использования в теле метода:
- P_PARAM → v_rParam (и все v_rParam.[FIELD], &debug('...||P_PARAM...')
- P_FILE_XML → v_vP_FILE_XML (и все Set_Par(..., P_FILE_XML), replace(P_FILE_XML...)
- P_FILE_ZIP → v_vP_FILE_ZIP (и все Set_Par(..., P_FILE_ZIP), P_FILE_NAME := P_FILE_ZIP)
- lrecBrInfo → v_recBrInfo (и все &debug(...||lrecBrInfo...)
- fmt → v_vFmt (и все to_char(..., fmt))

ПРАВИЛО: Если переменная переименована, найди ВСЕ строки, где она используется, и замени на новое имя.

## 2. СИНТАКСИС КЛАССА
- class HOOK_BANK; → class ::[HOOK_BANK];

## 3. КОМБИНИРОВАННЫЕ ПРЕФИКСЫ
Формат: [[назначение]][[тип]][[Смысл]]
- Назначение: v_ (локальная), p_ (параметр)
- Тип: i (integer), v (varchar2/string), r (ref), rec (record)
- Смысл: CamelCase с заглавной буквы

Конкретные исправления:
- dp integer → v_iDp integer
- dp1 integer → v_iDp1 integer
- fmt string(10) → v_vFmt string(10)
- lrBranch ref [BRANCH] → v_rBranch ref [BRANCH]
- lrecBrInfo → v_recBrInfo
- P_PARAM ref [REPS_PARAMS] → v_rParam ref [REPS_PARAMS]
- v_vVDateRep → v_vDateRep (убрать лишнюю V)
- lvRepPeriod → v_vRepPeriod (убрать лишний Lv)
- P_FILE_XML [STRING_1000] → v_vP_FILE_XML [STRING_1000]
- P_FILE_ZIP [STRING_1000] → v_vP_FILE_ZIP [STRING_1000]

## 4. ФУНКЦИЯ iif
- Параметры должны иметь префикс p_
- v1 → p_bCondition
- v2 → p_vTrueValue
- v3 → p_vFalseValue
- if v1 then return v2; else return v3; → if p_bCondition then return p_vTrueValue; else return p_vFalseValue;

## 5. ОБРАЩЕНИЕ К МЕТОДАМ
- [str].get_str_par(...) → ::[RUNTIME].[STR].get_str_par(...)

## 6. НЕИСПОЛЬЗУЕМЫЕ ПЕРЕМЕННЫЕ (УДАЛИТЬ!)
Переменные, которые объявлены, но нигде не используются в теле метода — УДАЛИТЬ:
- v_lrLrBranch (не используется)
- v_vVDateRep (не используется)
- v_vLvRepPeriod (не используется)

## 7. ЗАКОММЕНТИРОВАННЫЙ КОД (УДАЛИТЬ!)
- Блоки /** / ... /**/ — удалить
- Строки с --if, --end if — удалить

## 8. УПРАВЛЯЮЩИЕ ПЕРЕМЕННЫЕ В &debug
- &debug('...', dp) → &debug('...', v_iDp)
- &debug('...', dp1) → &debug('...', v_iDp1)
"""
        
        return base_prompt.format(code=code)
    
    @staticmethod
    def generate_clean_output_instruction() -> str:
        """
        Генерация инструкции для чистого вывода
        
        Returns:
            str: инструкция для KODA
        """
        return """

ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ К ВЫВОДУ:
1. Верни ТОЛЬКО исправленный код без каких-либо пояснений, комментариев-маркеров, блоков --OLD, маркеров <<< и >>>
2. НЕ добавляй в код комментарии вида --(*)PlpCheck.STYLE.*
3. НЕ добавляй блоки --OLD <дата> -- <старый код>
4. Все пояснения, список изменений, обоснования, предупреждения запиши в ЖУРНАЛ (отдельный блок)
5. ЖУРНАЛ должен содержать: что было изменено, почему, какое правило применено

ФОРМАТ ЖУРНАЛА:
### Журнал изменений
| № | Строка | Правило | Было | Стало | Обоснование |
|---|--------|---------|------|-------|-------------|

### Удаленный код
| № | Строка | Удаленный код | Причина |
|---|--------|---------------|---------|

### Статистика
- Всего изменений: N
- HIGH: N
- MEDIUM: N
- LOW: N
"""


# Глобальный экземпляр для удобства
koda_prompts = KodaPrompts()
