#!/usr/bin/env python3
"""
Генерация Excel-версии рубрикатора из JSON
"""
import json
from pathlib import Path
from datetime import datetime


def create_excel_rubricator():
    """Создание Excel-файла рубрикатора"""
    
    json_path = Path(__file__).parent / 'rubricator_markers.json'
    excel_path = Path(__file__).parent / 'rubricator_markers.xlsx'
    
    # Проверка наличия openpyxl
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
    except ImportError:
        print("⚠️  openpyxl не найден. Установите: pip install openpyxl")
        print("Используется CSV-версия вместо Excel")
        return False
    
    # Загрузка JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создание книги
    wb = Workbook()
    
    # === ЛИСТ 1: MARKERS ===
    ws_markers = wb.active
    ws_markers.title = 'MARKERS'
    
    # Заголовки
    markers_headers = [
        'ID', 'Документ', 'Стр.', 'Абз.', 'Маркер',
        'Формат маркировки', 'Описание', 'Статус',
        'Версия', 'Дата_обновления', 'Примечания'
    ]
    
    # Стилизация заголовков
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4472C4', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    for col, header in enumerate(markers_headers, 1):
        cell = ws_markers.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # Данные
    for row_idx, marker in enumerate(data.get('markers', []), 2):
        ws_markers.cell(row=row_idx, column=1, value=marker.get('id', ''))
        ws_markers.cell(row=row_idx, column=2, value=marker.get('document_id', ''))
        ws_markers.cell(row=row_idx, column=3, value=marker.get('page_paragraph', '').split(',')[0].replace('Стр.', '').strip())
        ws_markers.cell(row=row_idx, column=4, value=marker.get('page_paragraph', '').split(',')[1].replace('П.', '').strip() if ',' in marker.get('page_paragraph', '') else '')
        ws_markers.cell(row=row_idx, column=5, value=marker.get('marker', ''))
        ws_markers.cell(row=row_idx, column=6, value=marker.get('format', ''))
        ws_markers.cell(row=row_idx, column=7, value=marker.get('description', ''))
        ws_markers.cell(row=row_idx, column=8, value=marker.get('status', ''))
        ws_markers.cell(row=row_idx, column=9, value=marker.get('version', ''))
        ws_markers.cell(row=row_idx, column=10, value=marker.get('updated', ''))
        ws_markers.cell(row=row_idx, column=11, value=marker.get('notes', ''))
    
    # Автоширина колонок
    ws_markers.column_dimensions['A'].width = 8
    ws_markers.column_dimensions['B'].width = 15
    ws_markers.column_dimensions['C'].width = 8
    ws_markers.column_dimensions['D'].width = 8
    ws_markers.column_dimensions['E'].width = 15
    ws_markers.column_dimensions['F'].width = 70
    ws_markers.column_dimensions['G'].width = 50
    ws_markers.column_dimensions['H'].width = 12
    ws_markers.column_dimensions['I'].width = 10
    ws_markers.column_dimensions['J'].width = 15
    ws_markers.column_dimensions['K'].width = 40
    
    # === ЛИСТ 2: DOCUMENTATION ===
    ws_docs = wb.create_sheet('DOCUMENTATION')
    
    docs_headers = [
        'ID', 'Маркер', 'Файл', 'Путь', 'Версия',
        'Статус', 'Дата_актуализации', 'Автор', 'Примечания'
    ]
    
    for col, header in enumerate(docs_headers, 1):
        cell = ws_docs.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    for row_idx, doc in enumerate(data.get('documents', []), 2):
        ws_docs.cell(row=row_idx, column=1, value=doc.get('id', ''))
        ws_docs.cell(row=row_idx, column=2, value=doc.get('marker', ''))
        ws_docs.cell(row=row_idx, column=3, value=doc.get('filename', ''))
        ws_docs.cell(row=row_idx, column=4, value=doc.get('path', ''))
        ws_docs.cell(row=row_idx, column=5, value=doc.get('version', ''))
        ws_docs.cell(row=row_idx, column=6, value=doc.get('status', ''))
        ws_docs.cell(row=row_idx, column=7, value=doc.get('updated', ''))
        ws_docs.cell(row=row_idx, column=8, value=doc.get('author', ''))
        ws_docs.cell(row=row_idx, column=9, value=doc.get('notes', ''))
    
    ws_docs.column_dimensions['A'].width = 12
    ws_docs.column_dimensions['B'].width = 15
    ws_docs.column_dimensions['C'].width = 50
    ws_docs.column_dimensions['D'].width = 40
    ws_docs.column_dimensions['E'].width = 10
    ws_docs.column_dimensions['F'].width = 12
    ws_docs.column_dimensions['G'].width = 15
    ws_docs.column_dimensions['H'].width = 20
    ws_docs.column_dimensions['I'].width = 30
    
    # === ЛИСТ 3: ИНСТРУКЦИЯ ===
    ws_help = wb.create_sheet('ИНСТРУКЦИЯ')
    
    help_text = [
        ['РУБРИКАТОР МАРКИРОВОК PLPlus → DBI'],
        [''],
        ['НАЗНАЧЕНИЕ:'],
        ['Этот файл содержит правила маркировки изменений кода при миграции с Oracle на PostgreSQL.'],
        [''],
        ['ЛИСТ 1 - MARKERS:'],
        ['  - Содержит правила маркировки исправлений'],
        ['  - Каждая строка = одно правило'],
        ['  - Статус: active (действующее), draft (черновик), deprecated (устаревшее)'],
        [''],
        ['ЛИСТ 2 - DOCUMENTATION:'],
        ['  - Содержит источники документации'],
        ['  - Ссылки из лист 1 на этот лист через ID'],
        ['  - Статус: active (действующая), deprecated (устаревшая)'],
        [''],
        ['ЛИСТ 3 - ИНСТРУКЦИЯ:'],
        ['  - Эта страница'],
        [''],
        ['ПРАВИЛА РЕДАКТИРОВАНИЯ:'],
        ['1. Не удаляйте существующие строки без согласования'],
        ['2. Новые правила создавайте со статусом "draft"'],
        ['3. После проверки переводите в "active"'],
        ['4. Фиксируйте изменения в примечаниях'],
        ['5. Сохраняйте версию рубрикатора в JSON после правок'],
        [''],
        ['ФОРМАТ МАРКИРОВКИ В КОДЕ:'],
        ['-- {маркер} Стр.X,П.Y. {описание}'],
        ['--OLD YYYY-MM-DD HH:MM:'],
        ['-- оригинальный_код'],
        ['новый_код'],
        [''],
        ['ПРИМЕР:'],
        ['-- v50.2.1 Стр.8,П.1. NativeID: NUMBER -> VARCHAR2(100)'],
        ['--OLD 2026-04-13 12:36:'],
        ['-- dp  number:=0;'],
        ['dp VARCHAR2(100):=0;'],
        [''],
        ['КОНТАКТЫ: NLP-Core-Team'],
        [f'Создано: {datetime.now().strftime("%Y-%m-%d %H:%M")}']
    ]
    
    for row_idx, row_data in enumerate(help_text, 1):
        ws_help.cell(row=row_idx, column=1, value=row_data[0] if row_data else '')
    
    ws_help.column_dimensions['A'].width = 80
    
    # Сохранение
    wb.save(excel_path)
    print(f"✅ Excel-файл создан: {excel_path}")
    return True


if __name__ == '__main__':
    create_excel_rubricator()
