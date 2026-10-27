#!/usr/bin/env python3
"""
Анализ: почему ARH не находит PlpCheck проблемы в REPS_EXP_115_1.plp
"""
import re

# Читаем файл
with open('PATCH_IN/patch_REPS_EXP_115_1/src/ENTITY/HOOK_BANK/REPS_EXP_115_1.plp', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=" * 100)
print("АНАЛИЗ ПРОБЛЕМ PlpCheck В ФАЙЛЕ REPS_EXP_115_1.PLp")
print("=" * 100)

# 1. bad_prefix - переменные с плохими префиксами
print("\n1. bad_prefix (переменные с плохими префиксами):")
print("-" * 80)
bad_prefixes = ['dp', 'dbg', 'debug', 'bad', 'badprefix', 'tmp', 'temp', 'var', 'data', 'info', 'z_', 'x_', 'test', 'dummy']
for i, line in enumerate(lines, 1):
    for bp in bad_prefixes:
        if re.search(rf'\b{bp}\w*\s+(integer|string|number|date|boolean|ref|rowtype|varchar2)', line, re.IGNORECASE):
            print(f"  Строка {i}: {line.strip()}")
            print(f"    -> Префикс '{bp}' запрещён. Нужно: v_i{bp.capitalize()}")

# 2. not_mentioned - переменные, которые объявлены, но нигде не используются
print("\n2. not_mentioned (объявлены, но не используются):")
print("-" * 80)
full_code = ''.join(lines)
declared_vars = {}
for i, line in enumerate(lines, 1):
    # Ищем объявления переменных
    match = re.search(r'\b(\w+)\s+(?:string|number|integer|varchar2|date|ref|rowtype|boolean|timestamp)\s*(?:\([^)]*\))?\s*(?::=|;)', line, re.IGNORECASE)
    if match and not line.strip().startswith('--'):
        var_name = match.group(1)
        # Исключаем параметры методов и системные
        if var_name not in ['P_ADDS', 'P_FILE_NAME', 'P_SOURCE_FILE_NAME', 'P_PARAM', 'class', 'method', 'execute', 'begin', 'if', 'then', 'else', 'end', 'return', 'function', 'is', 'pragma', 'include', 'macro', 'ref', 'string', 'number', 'integer', 'varchar2', 'date', 'boolean', 'timestamp']:
            # Проверяем, используется ли переменная дальше
            var_pattern = re.compile(rf'\b{var_name}\b')
            # Считаем вхождения (исключаем объявление)
            count = 0
            for j, l in enumerate(lines, 1):
                if j != i:
                    count += len(var_pattern.findall(l))
            if count == 0:
                print(f"  Строка {i}: {line.strip()}")
                print(f"    -> Переменная '{var_name}' нигде не используется!")

# 3. prefix_type_in_var_name - переменные без префикса типа
print("\n3. prefix_type_in_var_name (нет префикса типа в имени):")
print("-" * 80)
# Проверяем локальные переменные (не параметры in/out)
for i, line in enumerate(lines, 1):
    # Ищем объявления локальных переменных (не параметры)
    match = re.search(r'^\s+(\w+)\s+(string|number|integer|varchar2|date|ref|rowtype|boolean)\b', line, re.IGNORECASE)
    if match and not line.strip().startswith('--') and not line.strip().startswith('@'):
        var_name = match.group(1)
        var_type = match.group(2).lower()
        # Проверяем, есть ли префикс типа
        if not re.match(r'^[vp][invdblr]', var_name, re.IGNORECASE):
            print(f"  Строка {i}: {line.strip()}")
            print(f"    -> Нет префикса типа. Нужно: v_{var_type[0]}{var_name[0].upper()}{var_name[1:]}")

# 4. wrong_method_syntax - неправильный вызов метода
print("\n4. wrong_method_syntax (неправильный вызов метода):")
print("-" * 80)
for i, line in enumerate(lines, 1):
    # Ищем вызовы типа [word].method()
    match = re.search(r'\[(\w+)\]\.(\w+)\s*\(', line)
    if match and match.group(1).lower() not in ['runtime']:
        print(f"  Строка {i}: {line.strip()}")
        print(f"    -> [str].get_str_par() -> должно быть ::[RUNTIME].[STR].get_str_par()")

# 5. code_in_comment - закомментированный код
print("\n5. code_in_comment (закомментированный код):")
print("-" * 80)
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('--') and len(stripped) > 10:
        # Проверяем, что это не просто комментарий, а закомментированный код
        if re.search(r'\b(if|then|else|end|if|return|:=|select|from|where)\b', stripped, re.IGNORECASE):
            print(f"  Строка {i}: {stripped[:100]}")
            print(f"    -> Закомментированный код. Нужно удалить.")

print("\n" + "=" * 100)
print("ВЫВОД: ARH не находит эти проблемы, потому что:")
print("  1. Правила PlpCheck.STYLE.BAD_PREFIX.п.4.3 и PREFIX_TYPE.п.4.4 есть, но")
print("     они не покрывают все случаи (dp, fmt, fmt24, v1, lrBranch)")
print("  2. Правило PlpCheck.STYLE.NOT_MENTIONED (неиспользуемые переменные) ОТСУТСТВУЕТ")
print("  3. Правило PlpCheck.STYLE.WRONG_METHOD.п.4.14 есть, но паттерн не ловит [str].method()")
print("  4. Правило PlpCheck.STYLE.CODE_IN_COMMENT (закомментированный код) ОТСУТСТВУЕТ")
print("=" * 100)
