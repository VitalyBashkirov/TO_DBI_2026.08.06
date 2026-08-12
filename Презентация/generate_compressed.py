#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Генератор сжатой версии презентации АРМ «Адаптация под DBI».
Сжатие: 32 таблицы → ~17, формулы удалены, стиль сохранён.
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement
from lxml import etree
import os

# ─── Константы ───────────────────────────────────────────────────────
COLOR_FISTASH = 'C5E1A5'       # фисташковый
COLOR_BLUE = '1A3A5C'          # тёмно-синий
COLOR_WHITE = 'FFFFFF'         # белый
COLOR_BLACK = '000000'         # чёрный
COLOR_GRAY = 'CCCCCC'          # границы
COLOR_LIGHT_GRAY = 'F2F2F2'    # фон ключевых тезисов
COLOR_GREEN = '2E7D32'         # зелёный для ключевых цифр
COLOR_RED = 'C62828'           # красный для ❌
FONT_TITLE = 'Arial'
FONT_BODY = 'Arial'

PAGE_WIDTH = Cm(21.0)     # книжная
PAGE_HEIGHT = Cm(29.7)
MARGIN = Cm(2.54)

BASE_DIR = r'F:\TO_DBI\Презентация'
OUTPUT = os.path.join(BASE_DIR, 'ИАР.Презентация_АРМ_Адаптация_под_DBI_v3.docx')

# ─── Утилиты ─────────────────────────────────────────────────────────

def set_page_dims(section):
    """Устанавливает книжную ориентацию (Portrait)."""
    section.page_width = PAGE_WIDTH
    section.page_height = PAGE_HEIGHT
    section.top_margin = MARGIN
    section.bottom_margin = MARGIN
    section.left_margin = MARGIN
    section.right_margin = MARGIN

def set_cell_shading(cell, color_hex):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color_hex)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)

def set_cell_font(cell, size=10, bold=False, color=None, bg=None, align=None):
    for p in cell.paragraphs:
        p.alignment = align or WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = Pt(12)
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.name = FONT_BODY
            if color:
                run.font.color.rgb = RGBColor(*[int(color[i:i+2], 16) for i in (0, 2, 4)])
    if bg:
        set_cell_shading(cell, bg)

def set_header_cell(cell, text, size=10):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.name = FONT_BODY
    run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    set_cell_shading(cell, COLOR_FISTASH)

def set_data_cell(cell, text, size=10, bold=False, color=None, bg=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = Pt(12)
    run = p.add_run(str(text))
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = FONT_BODY
    if color:
        run.font.color.rgb = RGBColor(*[int(color[i:i+2], 16) for i in (0, 2, 4)])
    if bg:
        set_cell_shading(cell, bg)

def add_table(doc, headers, rows, col_widths_pct=None, col_aligns=None):
    """Создаёт таблицу с фисташковыми заголовками."""
    ncols = len(headers)
    nrows = len(rows)
    table = doc.add_table(rows=nrows + 1, cols=ncols)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Заголовки
    for i, h in enumerate(headers):
        set_header_cell(table.rows[0].cells[i], h)

    # Данные
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            align = (col_aligns or [WD_ALIGN_PARAGRAPH.LEFT])[c] if col_aligns else WD_ALIGN_PARAGRAPH.LEFT
            is_bold = False
            is_color = None
            # Авто-подсветка ключевых значений
            val_str = str(val)
            if any(k in val_str for k in ['>95%', '>130%', '>80%', '>70%', '<3', '<10', '<15', '184%', '131%', '3 часа', '309 FTE', '350 FTE', '6.57', '5.35', '446 000', '2.2', '1.7', '✔️']):
                is_bold = True
                is_color = COLOR_GREEN
            elif val_str.startswith('❌'):
                is_bold = True
                is_color = COLOR_RED
            set_data_cell(table.rows[r + 1].cells[c], val, bold=is_bold, color=is_color, align=align)

    # Ширина колонок
    if col_widths_pct:
        total = sum(col_widths_pct)
        for i, pct in enumerate(col_widths_pct):
            for row in table.rows:
                row.cells[i].width = PAGE_WIDTH * pct / total

    # Границы
    for row in table.rows:
        for cell in row.cells:
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
                el = OxmlElement(f'w:{edge}')
                el.set(qn('w:val'), 'single')
                el.set(qn('w:sz'), '4')
                el.set(qn('w:color'), COLOR_GRAY)
                el.set(qn('w:space'), '0')
                tcBorders.append(el)
            tcPr.append(tcBorders)

    return table

def add_key_thesis(doc, text):
    """Добавляет ключевой тезис (без рамки)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = Pt(14)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), COLOR_LIGHT_GRAY)
    shd.set(qn('w:val'), 'clear')
    pPr.append(shd)

    run = p.add_run('▸  ' + text)
    run.font.size = Pt(10)
    run.font.name = FONT_BODY
    run.font.bold = True
    run.font.color.rgb = RGBColor(*[int(COLOR_BLUE[i:i+2], 16) for i in (0, 2, 4)])

def add_heading_compact(doc, text, level=1):
    """Компактный заголовок."""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = FONT_TITLE
        run.font.color.rgb = RGBColor(*[int(COLOR_BLUE[i:i+2], 16) for i in (0, 2, 4)])
    h.paragraph_format.space_before = Pt(4)
    h.paragraph_format.space_after = Pt(2)
    return h

def add_section_text(doc, items, size=10):
    """Текстовый блок с пунктами."""
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = Pt(12)
        r = p.add_run(item)
        r.font.size = Pt(size)
        r.font.name = FONT_BODY

def add_image(doc, image_path, width_cm=7, height_cm=None, left=None):
    """Добавляет изображение в документ."""
    if not os.path.exists(image_path):
        return
    result = doc.add_picture(image_path, width=Cm(width_cm))
    if height_cm:
        result.height = Cm(height_cm)
    return result

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 1 — ТИТУЛЬНЫЙ ЛИСТ (книжная ориентация)
# ═════════════════════════════════════════════════════════════════════
def slide1_title(doc):
    section = doc.sections[0]
    set_page_dims(section)

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('БАНК «НАРОДНЫЙ»  |  ЦФТ  |  DBI')
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.name = FONT_TITLE
    r.font.color.rgb = RGBColor(*[int(COLOR_BLUE[i:i+2], 16) for i in (0, 2, 4)])

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('РАЗРАБОТКА АРМа\n«АДАПТАЦИЯ ПОД DBI»')
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.name = FONT_TITLE
    r.font.color.rgb = RGBColor(*[int(COLOR_BLUE[i:i+2], 16) for i in (0, 2, 4)])

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('для перехода АБС «ЦФТ-Банк»\nс Платформы 1 на 2MCA DBI')
    r.font.size = Pt(16)
    r.font.name = FONT_TITLE
    r.font.color.rgb = RGBColor(*[int(COLOR_BLUE[i:i+2], 16) for i in (0, 2, 4)])

    doc.add_paragraph()
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Автор: Башкиров В.Г.\nДата: 2026')
    r.font.size = Pt(14)
    r.font.name = FONT_TITLE

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 2 — ПРОБЛЕМА + ЦЕЛИ + АКТУАЛЬНОСТЬ (4 таблицы → 2)
# ═════════════════════════════════════════════════════════════════════
def slide2(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 2. Зачем нужен АРМ «Адаптация под DBI»?', level=1)

    # Таблица 1: Ключевые термины (сокращённый глоссарий)
    add_table(doc,
        ['Термин', 'Значение'],
        [
            ['ЦФТ', 'Центр Финансовых Технологий. Разработчик АБС и платформы 2MCA DBI'],
            ['DBI', 'Database Independent. Код работает на разных СУБД без переписывания'],
            ['АРМ', 'Автоматизированное Рабочее Место — инструмент адаптации кода'],
            ['Oracle → PostgreSQL', 'Миграция с платной СУБД на российскую (реестр ПО)'],
            ['КИИ', 'Критическая инфоинфраструктура — банки обязаны переходить на отечественное ПО'],
        ],
        col_widths_pct=[20, 80]
    )

    doc.add_paragraph()

    # Таблица 2: Задачи АРМа
    add_heading_compact(doc, 'Задачи АРМа', level=2)
    add_table(doc,
        ['Задача', 'Описание'],
        [
            ['Сканирование (F5)', 'Анализ кода на Oracle-зависимости: обычный и Deep-режимы'],
            ['Исправление (F6)', 'Автоматическое преобразование по 31+ правилам рубрикатора'],
            ['Тестирование', 'Генерация тестовых .plp файлов для проверки'],
            ['Архивация', 'Упаковка результата в ZIP с .pck для передачи'],
        ],
        col_widths_pct=[30, 70]
    )

    doc.add_paragraph()

    # Таблица 3: Актуальность + Опыт
    add_heading_compact(doc, 'Актуальность и рыночный опыт', level=2)
    add_table(doc,
        ['Фактор', 'Суть'],
        [
            ['Прекращение поддержки', 'С июля 2027 ЦФТ прекращает сопровождение Платформы 1 (30 лет работы)'],
            ['Закон / КИИ', 'Банки обязаны переходить на российское ПО'],
            ['Экономия', 'Отказ от дорогих лицензий Oracle'],
            ['Опыт Газпромбанк', 'Миграция за 3 часа в рабочие дни'],
        ],
        col_widths_pct=[30, 70]
    )

    doc.add_paragraph()

    # Три этапа — компактная таблица
    add_heading_compact(doc, 'Этапы перехода', level=2)
    add_table(doc,
        ['Этап', 'Содержание'],
        [
            ['1. Подготовка', 'Оптимизация БД, адаптация локальных объектов, переход на IDE DBI'],
            ['2. Переход на DBI Oracle', 'Нагрузочное и регрессионное тестирование'],
            ['3. Переход на DBI PostgreSQL', 'Миграция данных, тестирование, запуск'],
        ],
        col_widths_pct=[30, 70]
    )

    add_key_thesis(doc, 'Платформа 1 перестанет сопровождаться с июля 2027. Переход на DBI — необходимость. АРМ автоматизирует миграцию: сканирует, исправляет, тестирует и готовит пакет для PostgreSQL.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 3 — ИНСТРУМЕНТЫ И СРЕДА (5 таблиц → 2)
# ═════════════════════════════════════════════════════════════════════
def slide3(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 3. Инструменты и среда разработки', level=1)

    # Таблица: техстек (сокращённый)
    add_table(doc,
        ['Компонент', 'Инструмент', 'Назначение'],
        [
            ['Язык разработки', 'Python 3.8+', 'Логика сканирования и исправления кода'],
            ['GUI-фреймворк', 'Tkinter', 'Окна, кнопки, журнал выполнения'],
            ['Среда разработки', 'VS Code + KodaCode', 'Разработка с AI-агентом'],
            ['AI-модель', 'DeepSeek', 'Создание рубрикатора (31+ правил)'],
            ['Целевая СУБД', 'PostgreSQL', 'Российская СУБД, реестр ПО'],
        ],
        col_widths_pct=[25, 25, 50]
    )

    doc.add_paragraph()

    # Алгоритм работы (сжатый)
    add_heading_compact(doc, 'Алгоритм работы АРМа', level=2)
    algo = [
        '1. Настройка — указать PATCH_IN / PATCH_OUT / шаблон *.plp',
        '2. Выбор правил — открыть рубрикатор, отметить нужные (Ctrl+S)',
        '3. Сканирование (F5) — обход каталогов, выявление Oracle-зависимостей, отчёт в logs/',
        '4. Исправление (F6) — 5-этапный алгоритм: копирование → сканирование → исправления → логирование → статистика',
        '5. Архивация — ZIP + .pck для передачи в промышленную среду',
    ]
    add_section_text(doc, algo)

    doc.add_paragraph()

    # Компоненты + рубрикатор — одна таблица
    add_heading_compact(doc, 'Компоненты и рубрикатор', level=2)
    add_table(doc,
        ['Компонент', 'Описание'],
        [
            ['GUI-оболочка', 'Tkinter: пути, рубрикатор, панель управления, журнал'],
            ['Рубрикатор', '3 файла правил, созданных DeepSeek. Точность >95%'],
            ['Сканер', 'F5 — обычный, Ctrl+F5 — Deep режим'],
            ['Фиксер', 'F6 — автоматическое применение правил'],
            ['Генератор тестов', 'Создаёт тестовые .plp файлы'],
            ['Архиватор', 'ZIP + .pck'],
        ],
        col_widths_pct=[25, 75]
    )

    # Картинка VS CODE+KODA
    add_image(doc, os.path.join(BASE_DIR, 'VS CODE+KODA.jpg'), width_cm=8, height_cm=5.5)

    add_key_thesis(doc, 'Инструменты для разработки АРМа — бесплатные (Python, Tkinter, VS Code). DeepSeek через KodaCode автоматизировал создание рубрикатора с 31+ правилами. АРМ не требует покупки дополнительного коммерческого ПО.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 4 — ЭКОНОМИКА (8 таблиц → 3)
# ═════════════════════════════════════════════════════════════════════
def slide4(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 4. Экономика проекта и ROI', level=1)

    # Таблица 1: Исходные данные + расчёт (объединены)
    add_heading_compact(doc, 'Исходные данные и расчёт экономии', level=2)
    add_table(doc,
        ['Параметр', 'Значение', 'Обоснование'],
        [
            ['Сотрудников', '4 чел.', 'Команда адаптации'],
            ['Часов в день (1 чел.)', '2 ч.', 'Только адаптация, не вся смена'],
            ['Дней в месяце', '22', 'Производственный календарь'],
            ['Оклад (на руки)', '350 000 ₽', 'Рыночная ставка инженера'],
            ['Заменяемая доля', '70%', 'Реалистичный показатель'],
            ['Прямая экономия / мес', '~446 000 ₽', '0.7 FTE × 637 000 ₽'],
            ['Прямая экономия / год', '~5.35 млн ₽', '446 000 × 12'],
        ],
        col_widths_pct=[25, 20, 55]
    )

    doc.add_paragraph()

    # Таблица 2: Затраты (CapEx + OpEx объединены)
    add_heading_compact(doc, 'Затраты проекта (TCO)', level=2)
    add_table(doc,
        ['Статья', 'Сумма, ₽', 'Тип'],
        [
            ['Разработка АРМа', '420 000', 'CapEx'],
            ['Интеграция с ЦФТ', '210 000', 'CapEx'],
            ['Рубрикатор (DeepSeek)', '20 000', 'CapEx'],
            ['Обучение сотрудников', '20 000', 'CapEx'],
            ['Прочие CapEx', '20 000', 'CapEx'],
            ['Итого CapEx', '690 000', 'CapEx'],
            ['KodaCode Pro / мес', '4 790', 'OpEx'],
            ['Поддержка (0.2 FTE)', '110 000', 'OpEx'],
            ['Прочие OpEx', '20 000', 'OpEx'],
            ['Итого OpEx / мес', '~135 000', 'OpEx'],
        ],
        col_widths_pct=[40, 20, 15]
    )

    doc.add_paragraph()

    # Таблица 3: ROI (ключевая)
    add_heading_compact(doc, 'Ключевые метрики', level=2)
    add_table(doc,
        ['Сценарий', 'Эффект в год', 'Затраты в год', 'ROI', 'Окупаемость'],
        [
            ['Без Soft Benefits', '5.35 млн ₽', '2.31 млн ₽', '~131%', '2.2 мес.'],
            ['С Soft Benefits', '6.57 млн ₽', '2.31 млн ₽', '~184%', '1.7 мес.'],
        ],
        col_widths_pct=[20, 15, 15, 15, 15]
    )

    doc.add_paragraph()

    # Аналоги + стресс-тест — одна компактная таблица
    add_heading_compact(doc, 'Рыночные кейсы и стресс-тест', level=2)
    add_table(doc,
        ['Банк / Риск', 'Результат / Влияние'],
        [
            ['Газпромбанк', 'Миграция за 3 часа'],
            ['ВТБ', 'Эффект 309 FTE (600 млн ₽)'],
            ['Открытие', 'Эффект 350 FTE'],
            ['Интеграция дороже ×2', 'Окупаемость ~3.5 мес.'],
            ['Эффект упал до 70%', 'ROI ~85%'],
            ['Задержка +2 мес.', 'ROI ~120%'],
        ],
        col_widths_pct=[30, 70]
    )

    add_key_thesis(doc, 'АРМ «Адаптация под DBI» окупается за 2–3 месяца, обеспечивает ROI >130% в первый год и соответствует успешным практикам импортозамещения в банковском секторе.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 5 — УПРАВЛЕНИЕ ПРОЕКТОМ (5 таблиц → 2)
# ═════════════════════════════════════════════════════════════════════
def slide5(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 5. Управление проектом', level=1)

    # Таблица 1: Этапы
    add_heading_compact(doc, 'Этапы проекта', level=2)
    add_table(doc,
        ['Этап', 'Длит.', 'Результат'],
        [
            ['1. Инициация', '1 нед.', 'Утверждённый план'],
            ['2. Разработка MVP', '3 нед.', 'Сканер + рубрикатор + GUI'],
            ['3. Пилот', '1 нед.', 'Отчёт о пилоте'],
            ['4. Доработка', '1 нед.', 'Готовый АРМ v.04'],
            ['5. Внедрение', '2 нед.', 'Промышленная эксплуатация'],
        ],
        col_widths_pct=[30, 15, 55]
    )

    doc.add_paragraph()

    # KPI
    add_heading_compact(doc, 'KPI проекта', level=2)
    add_table(doc,
        ['Метрика', 'Цель'],
        [
            ['Снижение времени адаптации', '-70%'],
            ['Доля авто-исправленного кода', '>80%'],
            ['Точность рубрикатора', '>95%'],
            ['ROI первого года', '>130%'],
            ['Точка безубыточности', '<3 месяцев'],
        ],
        col_widths_pct=[40, 30]
    )

    doc.add_paragraph()

    # Стейкхолдеры + Риски — одна таблица
    add_heading_compact(doc, 'Стейкхолдеры и ключевые риски', level=2)
    add_table(doc,
        ['Стейкхолдер / Риск', 'Стратегия / Решение'],
        [
            ['IT-директор (спонсор)', 'Регулярные отчёты, демонстрация ROI'],
            ['Руководитель сопровождения', 'Вовлечение в пилот, обучение'],
            ['ЦФТ (вендор)', 'Консультации, согласование DBI'],
            ['Регулятор', 'Соблюдение сроков до июля 2027'],
            ['⚠️ Неполнота рубрикатора', 'Итеративное дополнение правил'],
            ['⚠️ Изменение требований DBI', 'Мониторинг обновлений ЦФТ'],
        ],
        col_widths_pct=[40, 60]
    )

    add_key_thesis(doc, 'Проект управляется по гибкой методологии с чёткими KPI, стоп-лимитом и активным вовлечением стейкхолдеров. ROI >130% и окупаемость <3 месяцев делают его инвестиционно привлекательным.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 6 — MVP (3 таблицы + 8 шагов → 2 таблицы + 5 шагов)
# ═════════════════════════════════════════════════════════════════════
def slide6(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 6. MVP и сценарий использования', level=1)

    # Таблица 1: План MVP (сжатый)
    add_heading_compact(doc, 'План создания MVP (~5 недель)', level=2)
    add_table(doc,
        ['Этап', 'Длит.', 'Результат', 'Критерий'],
        [
            ['1. Анализ + рубрикатор', '6 дн.', '3 файла .md, 31+ правил', 'Все категории DBI'],
            ['2. Сканер + фиксер', '9 дн.', 'F5/F6 с GUI-интеграцией', '5–10 сек/файл'],
            ['3. GUI-приложение', '4 дн.', 'Tkinter, settings.json', 'Настройки сохраняются'],
            ['4. Тестирование', '4 дн.', 'Стабильная версия', '1000 файлов без сбоев'],
            ['5. Пилот', '3 дн.', 'Обратная связь', 'Эффективность >70%'],
        ],
        col_widths_pct=[25, 10, 35, 30]
    )

    doc.add_paragraph()

    # Сценарий использования (5 шагов)
    add_heading_compact(doc, 'Сценарий использования', level=2)
    steps = [
        '1. Запуск: python SRC/gui_app.py → открыть GUI',
        '2. Настройка: указать PATCH_IN / PATCH_OUT / *.plp',
        '3. Сканирование (F5): обход файлов, отчёт за <10 мин',
        '4. Исправление (F6): авто-исправление по правилам, лог fix_log_*.md',
        '5. Архивация: ZIP + .pck → передача в среду DBI',
    ]
    add_section_text(doc, steps)

    doc.add_paragraph()

    # Таблица 2: Метрики + Матрица (объединены)
    add_heading_compact(doc, 'Метрики и интеграция в бизнес-процессы', level=2)
    add_table(doc,
        ['Процесс', 'Было', 'Стало'],
        [
            ['Адаптация кода', 'Ручной поиск (месяцы)', 'Авто-сканирование (минуты)'],
            ['Тестирование', 'Ручная проверка (дни)', 'Генерация тестов (секунды)'],
            ['Документирование', 'Ручные журналы', 'Авто-отчёты scan_report_*.md'],
            ['Архивация', 'Ручная упаковка', 'Один клик ZIP + .pck'],
        ],
        col_widths_pct=[25, 35, 40]
    )

    add_key_thesis(doc, 'MVP АРМа автоматизирует 70% рутины адаптации кода, сокращая время с месяцев до дней, и готов к пилотному внедрению через 5 недель.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 7 — БЕЗОПАСНОСТЬ (2 таблицы → 1)
# ═════════════════════════════════════════════════════════════════════
def slide7(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 7. Кибербезопасность', level=1)

    # Одна таблица: меры + Human-in-the-Loop
    add_table(doc,
        ['Мера / Принцип', 'Реализация в АРМе'],
        [
            ['Аутентификация', 'LDAP / Active Directory (доступ по ролям)'],
            ['Журналирование', 'Встроенное логирование (logs/, logs_Deep/)'],
            ['Изоляция окружения', 'PATCH_IN → PATCH_OUT, только тестовые полигоны'],
            ['Контроль версий', 'fix_log_*.md — отслеживание изменений'],
            ['Шифрование данных', 'SSL/TLS 1.3, ограниченный доступ к settings.json'],
            ['Human-in-the-Loop', 'Разработчик проверяет код перед архивацией'],
            ['Эскалация', 'АРМ помечает проблемные участки для ручного разбора'],
            ['Аудит действий', 'Полный лог: кто, когда и что изменил'],
        ],
        col_widths_pct=[30, 70]
    )

    add_key_thesis(doc, 'Безопасность встроена в архитектуру АРМа на всех уровнях: от ролевого доступа до логирования. Человек остаётся финальным контролёром в цикле безопасности.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 8 — МАСШТАБИРОВАНИЕ (таблица + текст → таблица + тезис)
# ═════════════════════════════════════════════════════════════════════
def slide8(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 8. Масштабирование ИИ-решения', level=1)

    # Текст — сжатый
    add_heading_compact(doc, 'Видение масштабирования', level=2)
    items = [
        'Текущее состояние: АРМ для автоматизации локального кода АБС «ЦФТ-Банк» (~3500 локальных операций)',
        'Цель: превратить АРМ в корпоративную ИИ-платформу для каждого программиста Банка',
        'Архитектура: трёхуровневая (СУБД → Технологическое ядро → Прикладной код)',
        'Контейнеризация: Docker + Kubernetes для горизонтального масштабирования',
        'ИИ-ядро: обучение моделей на исторических данных, интеграция с LLM',
        'Экономия: отказ от лицензий Oracle, отказ от Plp Check у каждого разработчика',
    ]
    add_section_text(doc, items)

    doc.add_paragraph()

    # Таблица плана
    add_heading_compact(doc, 'План внедрения', level=2)
    add_table(doc,
        ['Этап', 'Задачи', 'Сроки'],
        [
            ['1. Пилот', 'Запуск в «Народном банке», сбор метрик', 'Завершён'],
            ['2. Тиражирование', 'Адаптация для 4–5 программистов, доработка ИИ', '2026–2027'],
            ['3. Платформа', 'Веб-платформа с самообслуживанием для банков-партнёров', '2028'],
        ],
        col_widths_pct=[20, 45, 15]
    )

    doc.add_paragraph()

    # Картинка GitHub
    add_image(doc, os.path.join(BASE_DIR, 'GitHub_VitalyBashkirov.jpg'), width_cm=7, height_cm=5)

    add_key_thesis(doc, 'АРМ «Адаптация под DBI» — фундамент для масштабируемой ИИ-платформы, которая обеспечит технологический суверенитет и станет новым стандартом для DBI-миграций.')

    # Ссылки
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(4)
    r = p.add_run('GitHub: https://github.com/VitalyBashkirov/TO_DBI_2026.08.06')
    r.font.size = Pt(9)
    r.font.name = FONT_BODY
    r.font.color.rgb = RGBColor(0x1A, 0x73, 0xE8)

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 9 — СТРУКТУРА БД (2 таблицы + схемы → 1 таблица)
# ═════════════════════════════════════════════════════════════════════
def slide9(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 9. Структура БД и источники данных', level=1)

    # Архитектура — одна строка
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run('СУБД  →  Технологическое ядро DBI  →  Прикладной код (PL/Plus)')
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.name = FONT_TITLE
    r.font.color.rgb = RGBColor(*[int(COLOR_BLUE[i:i+2], 16) for i in (0, 2, 4)])

    doc.add_paragraph()

    # Данные + особенности — одна таблица
    add_heading_compact(doc, 'Источники данных', level=2)
    add_table(doc,
        ['Источник', 'Формат', 'Применение'],
        [
            ['PATCH_IN/xxx', '.plp', 'Входные данные для сканирования'],
            ['Документация DBI (v50.docx)', '.docx', 'Основа для рубрикатора'],
            ['Рубрикатор (3 файла)', '.md', 'Правила исправления кода'],
            ['PATCH_OUT/xxx', '.plp', 'Результат адаптации'],
            ['Logs', '.md', 'Отчёты и логи изменений'],
            ['Независимость от СУБД', '—', 'Структура в файловом репозитории, ANSI SQL'],
        ],
        col_widths_pct=[30, 15, 55]
    )

    doc.add_paragraph()

    # Движение данных — сжатое
    add_heading_compact(doc, 'Движение данных', level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run('PATCH_IN/*.plp  →  Сканирование (F5)  →  scan_report_*.md')
    r.font.size = Pt(10)
    r.font.name = FONT_BODY
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run('PATCH_IN/*.plp  →  Исправление (F6)  →  PATCH_OUT/*.plp + fix_log_*.md')
    r.font.size = Pt(10)
    r.font.name = FONT_BODY

    add_key_thesis(doc, 'Источник данных — локальный код банка на PL/Plus. Масштаб системы: 8 000 таблиц, 12 млн строк кода. Архитектура ЦФТ хранит структуру в файловом репозитории и разворачивает в любую ANSI SQL СУБД.')

# ═════════════════════════════════════════════════════════════════════
# СЛАЙД 10 — ВЫВОДЫ (2 таблицы + текст → 2 таблицы)
# ═════════════════════════════════════════════════════════════════════
def slide10(doc):
    section = doc.add_section()
    set_page_dims(section)

    add_heading_compact(doc, 'Слайд 10. Выводы: оптимальность стратегии', level=1)

    # Таблица 1: Критерии (обоснование сокращено)
    add_heading_compact(doc, 'Критерии оптимальности', level=2)
    add_table(doc,
        ['Критерий', 'Оценка', 'Обоснование'],
        [
            ['Регуляторные требования', '✔️ Выполнено', 'КИИ → отечественное ПО. PostgreSQL в реестре'],
            ['Минимизация переписывания', '✔️ Выполнено', 'Доработка ядра ЦФТ + адаптация прикладного кода'],
            ['Автоматизация рутины', '✔️ Выполнено', 'АРМ автоматизирует 70%, точность рубрикатора >95%'],
            ['Бесшовность миграции', '✔️ Выполнено', 'Платформа 1 → 2MCA DBI Oracle → PostgreSQL'],
            ['Экономическая эффективность', '✔️ Выполнено', 'ROI >130%, окупаемость <3 месяцев'],
        ],
        col_widths_pct=[30, 12, 58]
    )

    doc.add_paragraph()

    # Таблица 2: Сравнение стратегий
    add_heading_compact(doc, 'Сравнение со стратегиями', level=2)
    add_table(doc,
        ['Стратегия', 'Недостатки', 'Итог'],
        [
            ['Ручная адаптация', 'Месяцы работы, высокие риски', '❌ Неоптимально'],
            ['Полное переписывание', 'Трудозатраты с нуля, потеря функциональности', '❌ Невозможно'],
            ['АРМ «Адаптация под DBI»', 'Доработка при новых правилах', '✅ Оптимально'],
        ],
        col_widths_pct=[35, 35, 15]
    )

    doc.add_paragraph()

    add_key_thesis(doc, 'Стратегия оптимальна: соответствует методологии ЦФТ, подтверждена опытом Газпромбанка (3 часа), автоматизирует 70% рутины, ROI >130%, масштабируема на группу банков.')

# ═════════════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ═════════════════════════════════════════════════════════════════════
def main():
    doc = Document()

    # Слайд 1 — титульный (Portrait)
    slide1_title(doc)

    # Слайды 2–10 (Landscape)
    slide2(doc)
    slide3(doc)
    slide4(doc)
    slide5(doc)
    slide6(doc)
    slide7(doc)
    slide8(doc)
    slide9(doc)
    slide10(doc)

    doc.save(OUTPUT)
    print(f'OK Презентация сохранена: {OUTPUT}')
    print(f'  Таблиц в документе: {len(doc.tables)}')

if __name__ == '__main__':
    main()
