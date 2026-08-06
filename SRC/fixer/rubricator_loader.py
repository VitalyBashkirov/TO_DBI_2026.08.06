#!/usr/bin/env python3
"""
Рубрикатор маркировок для адаптации PLPlus кода под DBI
Загрузка и управление требованиями из JSON/CSV
"""
import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class RubricatorLoader:
    """Загрузчик рубрикатора маркировок"""
    
    def __init__(self, rubricator_path: Optional[Path] = None):
        """
        Инициализация загрузчика рубрикатора
        
        Args:
            rubricator_path: Путь к файлу рубрикатора (JSON или CSV)
        """
        if rubricator_path is None:
            rubricator_path = Path(__file__).parent.parent / 'AI_DOCS' / 'rubricator_markers.json'
        
        self.rubricator_path = rubricator_path
        self.data: Dict = {}
        self.markers: Dict[str, Dict] = {}
        self.documents: Dict[str, Dict] = {}
        self.pdf_cache: Dict[str, str] = {}  # Кэш извлечённого текста из PDF
        self.load()
    
    def load(self):
        """Загрузка рубрикатора из файла"""
        if not self.rubricator_path.exists():
            raise FileNotFoundError(f"Рубрикатор не найден: {self.rubricator_path}")
        
        ext = self.rubricator_path.suffix.lower()
        
        if ext == '.json':
            self._load_json()
        elif ext == '.csv':
            self._load_csv()
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}. Используйте .json или .csv")
        
        self._parse_markers()
        self._parse_documents()
    
    def _load_json(self):
        """Загрузка из JSON"""
        with open(self.rubricator_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def _load_csv(self):
        """Загрузка из CSV (только markers)"""
        self.data = {
            'markers': [],
            'documents': [],
            'format_rules': {
                'marker_template': '-- {marker} строки с XXXX по YYYY. {description}',
                'old_template': '--OLD {YYYY-MM-DD HH:MM}:',
                'max_description_length': 120
            }
        }
        
        with open(self.rubricator_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.data['markers'].append(row)
    
    def _parse_markers(self):
        """Парсинг маркеров"""
        for marker in self.data.get('markers', []):
            key = marker.get('marker') or marker.get('Маркер')
            if key:
                self.markers[key] = marker
    
    def _parse_documents(self):
        """Парсинг документов"""
        for doc in self.data.get('documents', []):
            key = doc.get('id') or doc.get('ID')
            if key:
                self.documents[key] = doc
    
    def get_marker(self, marker_id: str) -> Optional[Dict]:
        """
        Получение информации о маркере
        
        Args:
            marker_id: Идентификатор маркера (например, 'v50.2.1')
        
        Returns:
            Словарь с информацией о маркере или None
        """
        return self.markers.get(marker_id)
    
    def get_active_markers(self) -> List[Dict]:
        """Получение списка активных маркеров"""
        return [m for m in self.markers.values() if m.get('status') == 'active']
    
    def get_marker_format(self, marker_id: str) -> str:
        """
        Получение формата маркировки для маркера
        
        Args:
            marker_id: Идентификатор маркера
        
        Returns:
            Строка формата маркировки
        """
        marker = self.get_marker(marker_id)
        if marker:
            return marker.get('format', '')
        return ''
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Получение информации о документе
        
        Args:
            doc_id: Идентификатор документа
        
        Returns:
            Словарь с информацией о документе или None
        """
        return self.documents.get(doc_id)
    
    def get_active_documents(self) -> List[Dict]:
        """Получение списка активных документов"""
        return [d for d in self.documents.values() if d.get('status') == 'active']
    
    def get_required_pdf_documents(self) -> List[Dict]:
        """
        Получение списка PDF документов, требующих обязательной обработки
        
        Returns:
            Список документов с форматом pdf и priority high
        """
        return [
            d for d in self.get_active_documents()
            if d.get('format') == 'pdf' and d.get('priority') == 'high'
        ]
    
    def extract_pdf_text(self, doc_id: str) -> Optional[str]:
        """
        Извлечение текста из PDF документа
        
        Args:
            doc_id: Идентификатор документа
        
        Returns:
            Извлечённый текст или None
        """
        if doc_id in self.pdf_cache:
            return self.pdf_cache[doc_id]
        
        doc = self.get_document(doc_id)
        if not doc:
            return None
        
        pdf_path = Path(doc.get('path', '')) / doc.get('filename', '')
        
        if not pdf_path.exists():
            print(f"⚠️  PDF файл не найден: {pdf_path}")
            return None
        
        try:
            # Пытаемся использовать pdfplumber или PyPDF2
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = '\n'.join([page.extract_text() or '' for page in pdf.pages])
            except ImportError:
                try:
                    import PyPDF2
                    with open(pdf_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = '\n'.join([page.extract_text() or '' for page in reader.pages])
                except ImportError:
                    print("⚠️  Установите pdfplumber или PyPDF2 для обработки PDF")
                    return None
            
            self.pdf_cache[doc_id] = text
            return text
        except Exception as e:
            print(f"⚠️  Ошибка извлечения текста из PDF: {e}")
            return None
    
    def get_fix_rules(self) -> Dict:
        """Получение правил для code_fixer.py"""
        rules = {}
        for marker in self.get_active_markers():
            marker_id = marker.get('marker')
            if marker_id:
                rules[marker_id] = {
                    'format': marker.get('format', ''),
                    'description': marker.get('description', ''),
                    'line_range': marker.get('line_range', '')
                }
        return rules
    
    def update_marker(self, marker_id: str, updates: Dict):
        """
        Обновление маркера
        
        Args:
            marker_id: Идентификатор маркера
            updates: Словарь обновлений
        """
        if marker_id in self.markers:
            self.markers[marker_id].update(updates)
            self.markers[marker_id]['updated'] = datetime.now().strftime('%Y-%m-%d')
    
    def save(self, path: Optional[Path] = None):
        """
        Сохранение рубрикатора
        
        Args:
            path: Путь для сохранения (по умолчанию - исходный файл)
        """
        if path is None:
            path = self.rubricator_path
        
        ext = path.suffix.lower()
        
        if ext == '.json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        elif ext == '.csv':
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['ID', 'Документ', 'Стр.', 'Абз.', 'Маркер', 
                             'Формат маркировки', 'Описание', 'Статус', 
                             'Версия', 'Дата_обновления', 'Примечания']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for marker in self.data.get('markers', []):
                    writer.writerow(marker)
        
        # Обновляем журнал изменений
        self._add_audit_log('updated', f"Сохранение рубрикатора: {path}")
    
    def _add_audit_log(self, action: str, changes: str):
        """Добавление записи в журнал изменений"""
        if 'audit_log' not in self.data:
            self.data['audit_log'] = []
        
        self.data['audit_log'].append({
            'date': datetime.now().isoformat(),
            'action': action,
            'author': 'NLP-Core-Team',
            'changes': changes
        })

    def print_pdf_processing_status(self):
        """Вывод статуса обработки PDF документов"""
        pdf_docs = self.get_required_pdf_documents()

        print("\n=== PDF Документы для обязательной обработки ===")
        if not pdf_docs:
            print("  Нет PDF документов для обработки")
            return
        
        for doc in pdf_docs:
            filename = doc.get('filename', 'unknown')
            doc_id = doc.get('id', 'unknown')
            status = "[OK] Загружен" if doc_id in self.pdf_cache else "[--] Не обработан"
            print(f"  {status} | {filename}")


def main():
    """Демонстрация работы рубрикатора"""
    rubricator = RubricatorLoader()
    
    print("=== Рубрикатор маркировок PLPlus -> DBI (v03) ===\n")
    
    print("Активные маркеры:")
    for marker in rubricator.get_active_markers():
        print(f"  {marker.get('marker'):30} | {marker.get('description')[:50]}")
    
    print("\nАктивные документы:")
    for doc in rubricator.get_active_documents():
        fmt = doc.get('format', 'unknown')
        print(f"  [{fmt.upper():4}] {doc.get('id'):20} | {doc.get('filename')[:40]}")
    
    rubricator.print_pdf_processing_status()
    
    print("\nПравила для code_fixer.py:")
    rules = rubricator.get_fix_rules()
    for marker_id, rule in rules.items():
        print(f"  {marker_id}: {rule.get('format')}")


if __name__ == '__main__':
    main()
