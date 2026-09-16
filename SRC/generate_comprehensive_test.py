#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор сводного тестового файла (в стиле TestDeepSeek_full.plp)

Создаёт один файл, содержащий ВСЕ 47 правил рубрикатора v3.0.0:
  - Заголовок со списком всех правил
  - Для каждого правила: метаданные из 3.RUBRICATOR_FIXES.md и 4.RUBRICATOR_PROMPTS.json
  - Блок кода: [-] неправильный код → [+] исправленный код
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Добавляем SRC в путь
sys.path.insert(0, str(Path(__file__).parent))

from fixer.markdown_rubricator_loader_v3 import MarkdownRubricatorLoaderV3


def escape_for_comment(text: str) -> str:
    """Экранирование текста для комментариев -- """
    return text.replace('\n', '\n--   ')


def get_code_example_bad_text(rule) -> str:
    """Получить текст примеров плохого кода"""
    bad_examples = rule.code_example_bad if rule.code_example_bad else []
    # Берём первый (основной) пример
    return bad_examples[0] if bad_examples else ''


def get_code_example_bad_extra(rule) -> List[str]:
    """Получить дополнительные примеры плохого кода"""
    bad_examples = rule.code_example_bad if rule.code_example_bad else []
    return bad_examples[1:] if len(bad_examples) > 1 else []


def get_code_example_good_text(rule) -> str:
    """Получить текст примера хорошего кода"""
    return rule.code_example_good if rule.code_example_good else ''


def get_rule_short_desc(code: str) -> str:
    """Извлекает короткое описание из кода правила.
    
    Например: v50.SQL.OUTERJOIN.п.1.1 -> 'Замена (+) на LEFT/RIGHT JOIN'
    Берём из category/subcategory как fallback.
    """
    # Формат: v{version}.{category}.{subcategory}.{пункт}.{подпункт}
    parts = code.split('.')
    if len(parts) >= 3:
        # category = parts[1], subcategory = parts[2]
        return f"{parts[1]}.{parts[2]}"
    return code


def get_rule_number(code: str, all_rules: Dict) -> int:
    """Возвращает номер правила в отсортированном списке"""
    sorted_codes = sorted(all_rules.keys())
    try:
        return sorted_codes.index(code) + 1
    except ValueError:
        return 0


def format_code_block(code_lines: str, label: str, indent: int = 0) -> str:
    """Форматирует блок кода с [-] или [+]"""
    lines = []
    prefix = ' ' * indent
    if code_lines:
        lines.append(f'{prefix}-- {label}:')
        for line in code_lines.strip().split('\n'):
            lines.append(f'{prefix}-- {line}')
    else:
        lines.append(f'{prefix}-- {label}: (нет примера)')
    return '\n'.join(lines)


def generate_header(rules: Dict[str, Any], version: str, total: int) -> str:
    """Генерирует заголовок файла со списком всех правил"""
    lines = []
    lines.append('-- ============================================================================')
    lines.append(f'-- СВОДНЫЙ ТЕСТОВЫЙ ФАЙЛ: ВСЕ ПРАВИЛА v{version} ({total} правил)')
    lines.append(f'-- Дата генерации: {datetime.now().strftime("%Y-%m-%d")}')
    lines.append(f'-- Описание: Тестовые файлы для всех правил PLPlus адаптации')
    lines.append('-- ============================================================================')
    lines.append('-- Сп�сок всех правил (HIGH, ' + str(total) + ' шт.):')
    lines.append('-- ============================================================================')
    
    sorted_codes = sorted(rules.keys())
    for i, code in enumerate(sorted_codes, 1):
        rule = rules[code]
        short_desc = rule.short_description[:50] if rule.short_description else '...'
        # Формат: 1.  v50.SQL.OUTERJOIN.п.1.1      - Замена (+) на LEFT/RIGHT JOIN
        desc_padded = short_desc.ljust(55)
        lines.append(f'-- {i:2d}.  {code:45s} - {desc_padded}')
    
    lines.append('-- ============================================================================')
    lines.append('')
    return '\n'.join(lines)


def generate_rule_section(rule_code: str, rule, rule_num: int, examples: Dict) -> str:
    """Генерирует секцию для одного правила"""
    lines = []
    
    # Заголовок секции
    short_desc = rule.short_description[:60] if rule.short_description else '...'
    lines.append('-- ============================================================================')
    lines.append(f'-- {rule_num:2d}: {rule_code} - {short_desc}')
    lines.append('-- ============================================================================')
    
    # --- 3.RUBRICATOR_FIXES.md metadata ---
    lines.append('-- 3.RUBRICATOR_FIXES.md:')
    lines.append(f'--   Короткое описание: {rule.short_description}')
    lines.append(f'--   Подробное описание: {rule.documentation_text}')
    
    # Примеры
    bad_main = get_code_example_bad_text(rule)
    if bad_main:
        lines.append(f'--   Пример кода (плохой): {bad_main}')
    extra_bads = get_code_example_bad_extra(rule)
    for idx, bad in enumerate(extra_bads, 2):
        lines.append(f'--   Пример кода {idx} (плохой): {bad}')
    
    # Хорошие примеры из JSON
    good_from_json = ''
    if examples:
        # Сначала ищем simple, затем simple_case, затем любой другой
        good_from_json = examples.get('simple', {}).get('good', '')
        if not good_from_json:
            good_from_json = examples.get('simple_case', {}).get('good', '')
        if not good_from_json:
            # Ищем в любом примере
            for ex_name, ex_data in examples.items():
                if ex_data.get('good'):
                    good_from_json = ex_data['good']
                    break
    good = get_code_example_good_text(rule) or good_from_json
    
    if good:
        lines.append(f'--   Пример кода (исправленный): {good}')
    
    # Теги (извлекаем из категории/подкатегории)
    parts = rule_code.split('.')
    tags = ', '.join(parts) if len(parts) >= 2 else rule.priority
    lines.append(f'--   Теги: {tags}')
    
    # --- 4.RUBRICATOR_PROMPTS.json metadata ---
    lines.append('-- 4.RUBRICATOR_PROMPTS.json (расширенный):')
    lines.append(f'--   documentation_text: {rule.documentation_text}')
    lines.append(f'--   plplus_materials_note: {rule.plplus_materials_note}')
    lines.append(f'--   search_prompt: {rule.search_prompt}')
    
    # regex_patterns
    patterns_str = []
    for p in rule.regex_patterns_search:
        desc = p.get('description', p.get('pattern', ''))
        patterns_str.append(f'({len(patterns_str)+1}) {desc}')
    if patterns_str:
        lines.append(f'--   regex_patterns.for_search: {"; ".join(patterns_str)}')
    
    # code_example_bad
    if bad_main:
        lines.append(f'--   code_example_bad: {bad_main}')
    for idx, bad in enumerate(extra_bads, 2):
        lines.append(f'--   code_example_bad{idx}: {bad}')
    
    if rule.fix_instruction:
        lines.append(f'--   fix_instruction: {rule.fix_instruction}')
    
    # test_generation_prompt
    lines.append(f'--   test_generation_prompt: Сгенерировать тестовый PLPlus файл для проверки правила \'{rule_code}\' с проблемными конструкциями.')
    
    # examples из JSON
    lines.append(f'--   examples.simple.bad: {bad_main if bad_main else "(нет примера)"}')
    lines.append(f'--   examples.simple.good: {good if good else "(нет примера)"}')
    
    # Дополнительные примеры из JSON
    if examples:
        for ex_name in ['simple_case', 'parametrized_collection', 'parametrized_ref', 'with_order', 'between']:
            if ex_name in examples:
                ex = examples[ex_name]
                ex_bad = ex.get('bad', ex.get('bad2', ''))
                ex_good = ex.get('good', '')
                lines.append(f'--   examples.{ex_name}.bad: {ex_bad}')
                lines.append(f'--   examples.{ex_name}.good: {ex_good}')
    
    lines.append(f'--   priority: {rule.priority}')
    lines.append(f'--   category: {rule.category}')
    lines.append(f'--   subcategory: {rule.subcategory}')
    lines.append(f'--   source_files: v50.docx')
    lines.append(f'--   source_sections: {rule_code.split(".")[-1] if len(rule_code.split(".")) > 2 else "N/A"}')
    
    lines.append('-- ============================================================================')
    
    # --- Блок кода PROCEDURE ---
    proc_name = rule_code.replace('.', '_').replace('(', '').replace(')', '').replace(',', '')
    # Транслитерация кириллицы в латиницу для имени процедуры
    _CYR_TO_LAT = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    proc_name = ''.join(_CYR_TO_LAT.get(ch, ch) for ch in proc_name)
    lines.append(f'PROCEDURE {proc_name} IS')
    
    # Объявление переменных (если есть примеры)
    if bad_main:
        lines.append(f'\t-- Объявления переменных из примеров')
    
    lines.append('BEGIN')
    
    # [-] Неправильный код
    lines.append('\t-- [-] Неправильный код')
    if bad_main:
        lines.append('\t-- begin pl/sql')
        for line in bad_main.strip().split('\n'):
            lines.append(f'\t\t{line.strip()}')
        if extra_bads:
            for extra in extra_bads:
                lines.append(f'\t\t-- Дополнительный пример:')
                for line in extra.strip().split('\n'):
                    lines.append(f'\t\t{line.strip()}')
        lines.append('\t-- end pl/sql')
    else:
        lines.append('\t\t-- (нет примера плохого кода)')
    
    lines.append('')
    
    # [+] Исправленный код
    lines.append('\t-- [+] Исправленный код')
    if good:
        lines.append('\t-- begin pl/sql')
        for line in good.strip().split('\n'):
            lines.append(f'\t\t{line.strip()}')
        lines.append('\t-- end pl/sql')
    elif rule.fix_instruction:
        # Если нет good примера, но есть инструкция — показываем инструкцию
        lines.append('\t-- begin pl/sql')
        lines.append(f'\t\t-- Исправление: {rule.fix_instruction}')
        lines.append('\t-- end pl/sql')
    else:
        lines.append('\t\t-- (нет примера исправленного кода)')
    
    lines.append('END;')
    lines.append('')
    lines.append('')
    
    return '\n'.join(lines)


def generate_comprehensive_test(rubricator_dir: Path, output_file: Path) -> None:
    """Генерирует сводный тестовый файл"""
    print(f'\nГенератор сводного тестового файла')
    print(f'Каталог рубрикаторов: {rubricator_dir}')
    print(f'Выходной файл: {output_file}')
    print()
    
    # Загружаем рубрикатор v3.0.0
    loader = MarkdownRubricatorLoaderV3(rubricator_dir)
    rules = loader.rules
    
    if not rules:
        print('[!] Нет правил для генерации')
        return
    
    # Загружаем JSON для доступа к examples
    json_path = rubricator_dir / '4.RUBRICATOR_PROMPTS.json'
    json_data = {}
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            json_data = json.load(f)
    
    print(f'Загружено правил: {len(rules)}')
    print()
    
    # Генерируем содержимое
    content_lines = []
    
    # 1. Заголовок
    total = len(rules)
    version = loader.metadata.get('version', '3.0.0')
    content_lines.append(generate_header(rules, version, total))
    
    # 2. Секции для каждого правила
    sorted_codes = sorted(rules.keys())
    for i, code in enumerate(sorted_codes, 1):
        rule = rules[code]
        # Получаем примеры из JSON
        json_rule = json_data.get('rules', {}).get(code, {})
        examples = json_rule.get('examples', {})
        section = generate_rule_section(code, rule, i, examples)
        content_lines.append(section)
        if i % 10 == 0:
            print(f'  Обработано правил: {i}/{total}')
    
    # 3. Футер
    content_lines.append('-- ============================================================================')
    content_lines.append(f'-- КОНЕЦ ФАЙЛА: {total} правил v{version}')
    content_lines.append(f'-- Дата генерации: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    content_lines.append('-- ============================================================================')
    
    # Записываем файл
    output_file.parent.mkdir(parents=True, exist_ok=True)
    content = '\n'.join(content_lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'\n[OK] Сводный файл создан: {output_file}')
    print(f'[OK] Размер файла: {len(content):,} символов')
    print(f'[OK] Количество правил: {total}')
    
    # Статистика
    bad_with_examples = sum(1 for r in rules.values() if r.code_example_bad)
    
    # Считаем good примеры из JSON (проверяем все примеры)
    good_from_json_count = 0
    for code in rules.keys():
        json_rule = json_data.get('rules', {}).get(code, {})
        examples = json_rule.get('examples', {})
        good = ''
        if examples:
            good = examples.get('simple', {}).get('good', '')
            if not good:
                good = examples.get('simple_case', {}).get('good', '')
            if not good:
                for ex_name, ex_data in examples.items():
                    if ex_data.get('good'):
                        good = ex_data['good']
                        break
        if good:
            good_from_json_count += 1
    
    # Также считаем из code_example_good
    good_from_rule_count = sum(1 for r in rules.values() if r.code_example_good)
    
    print(f'[OK] Плохих примеров: {bad_with_examples}/{total}')
    print(f'[OK] Хороших примеров (из JSON): {good_from_json_count}/{total}')
    print(f'[OK] Хороших примеров (из правила): {good_from_rule_count}/{total}')


def main():
    project_root = Path(__file__).parent.parent
    rubricator_dir = project_root / 'DATA' / 'Рубрикатор'
    output_file = project_root / 'DATA' / 'Тестовые файлы' / 'test_comprehensive_v300.plp'
    
    generate_comprehensive_test(rubricator_dir, output_file)


if __name__ == '__main__':
    main()
