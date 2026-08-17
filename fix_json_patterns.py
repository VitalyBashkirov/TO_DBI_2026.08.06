import json
import re

# Читаем файл
with open('F:/TO_DBI/DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим все pattern значения и исправляем escape-последовательности
def fix_pattern(match):
    pattern = match.group(0)
    # Заменяем \b, \s, \w на \\b, \\s, \\w
    pattern = pattern.replace('\\b', '\\\\b')
    pattern = pattern.replace('\\s', '\\\\s')
    pattern = pattern.replace('\\w', '\\\\w')
    pattern = pattern.replace('\\d', '\\\\d')
    pattern = pattern.replace('\\D', '\\\\D')
    pattern = pattern.replace('\\W', '\\\\W')
    pattern = pattern.replace('\\S', '\\\\S')
    return pattern

# Ищем все строковые значения pattern
content = re.sub(r'"pattern":\s*"[^"]*"', fix_pattern, content)

# Записываем обратно
with open('F:/TO_DBI/DATA/Рубрикатор/4.RUBRICATOR_PROMPTS.json', 'w', encoding='utf-8') as f:
    f.write(content)

print("Исправлены escape-последовательности в pattern")

# Проверяем валидность JSON
try:
    data = json.loads(content)
    rules = data.get('rules', {})
    style_rules = [k for k in rules.keys() if 'STYLE' in k]
    print(f"JSON валиден. Всего правил: {len(rules)}")
    print(f"STYLE правила: {style_rules}")
except json.JSONDecodeError as e:
    print(f"Ошибка JSON: {e}")
