#!/usr/bin/env python3
"""
Утилиты для работы с кодировками
Поддержка UTF-8 и Windows-1251 (ANSI)
"""
import codecs
from pathlib import Path
from typing import Tuple, Optional


def detect_encoding(file_path: Path, sample_size: int = 8192) -> Tuple[str, str]:
    """
    Автоматическое определение кодировки файла
    
    Args:
        file_path: Путь к файлу
        sample_size: Размер образца для анализа (по умолчанию 8KB)
    
    Returns:
        Tuple (кодировка, сообщение)
        Кодировка: 'utf-8', 'cp1251', или 'unknown'
    """
    try:
        # Пробуем прочитать файл в бинарном режиме
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        # Проверка на BOM
        if sample.startswith(codecs.BOM_UTF8):
            return 'utf-8-sig', 'UTF-8 с BOM'
        elif sample.startswith(codecs.BOM_UTF16_LE):
            return 'utf-16-le', 'UTF-16 LE'
        elif sample.startswith(codecs.BOM_UTF16_BE):
            return 'utf-16-be', 'UTF-16 BE'
        
        # Пробуем UTF-8
        try:
            sample.decode('utf-8')
            return 'utf-8', 'UTF-8 без BOM'
        except UnicodeDecodeError:
            pass
        
        # Пробуем UTF-8 с игнорированием ошибок
        try:
            decoded = sample.decode('utf-8', errors='strict')
            # Если дошли сюда - файл в UTF-8
            return 'utf-8', 'UTF-8'
        except UnicodeDecodeError:
            pass
        
        # Пробуем Windows-1251 (ANSI)
        try:
            decoded = sample.decode('cp1251')
            # Проверяем на наличие характерных для CP1251 байтов
            # Если байты в диапазоне 0x80-0xFF, скорее всего это CP1251
            high_bytes = sum(1 for b in sample if 0x80 <= b <= 0xFF)
            if high_bytes > 0:
                return 'cp1251', 'Windows-1251 (ANSI)'
            return 'cp1251', 'Windows-1251 (ANSI)'
        except UnicodeDecodeError:
            pass
        
        # Пробуем с игнорированием ошибок
        try:
            sample.decode('cp1251', errors='ignore')
            return 'cp1251', 'Windows-1251 (ANSI) с пропусками'
        except:
            pass
        
        # Если ничего не подошло - пробуем latin-1 как fallback
        return 'latin-1', 'Latin-1 (fallback)'
    
    except Exception as e:
        return 'unknown', f'Ошибка определения: {e}'


def read_file_with_encoding(file_path: Path, preferred_encoding: str = None) -> Tuple[str, str]:
    """
    Чтение файла с автоматическим определением или указанием кодировки
    
    Args:
        file_path: Путь к файлу
        preferred_encoding: Предпочтительная кодировка (если None - автоопределение)
    
    Returns:
        Tuple (содержимое файла, кодировка)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    # Определяем кодировку
    if preferred_encoding:
        encoding = preferred_encoding
        encoding_desc = f'Указанная: {encoding}'
    else:
        encoding, encoding_desc = detect_encoding(file_path)
    
    # Читаем файл с определённой кодировкой
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        return content, encoding
    except Exception as e:
        # Fallback: пробуем с errors='replace'
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
            return content, encoding
        except Exception as e2:
            raise RuntimeError(f"Не удалось прочитать файл {file_path}: {e2}")


def write_file_with_encoding(file_path: Path, content: str, encoding: str = 'utf-8') -> None:
    """
    Запись файла с указанием кодировки
    
    Args:
        file_path: Путь к файлу
        content: Содержимое для записи
        encoding: Кодировка (по умолчанию UTF-8)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)


def convert_file_encoding(source_path: Path, target_path: Path, 
                          source_encoding: str = None, 
                          target_encoding: str = 'utf-8') -> Tuple[bool, str]:
    """
    Конвертация файла из одной кодировки в другую
    
    Args:
        source_path: Исходный файл
        target_path: Целевой файл
        source_encoding: Кодировка источника (автоопределение если None)
        target_encoding: Кодировка цели (по умолчанию UTF-8)
    
    Returns:
        Tuple (успешно, сообщение)
    """
    try:
        # Читаем исходный файл
        content, used_encoding = read_file_with_encoding(source_path, source_encoding)
        
        # Записываем в целевую кодировку
        write_file_with_encoding(target_path, content, target_encoding)
        
        return True, f'Конвертировано: {used_encoding} -> {target_encoding}'
    
    except Exception as e:
        return False, f'Ошибка конвертации: {e}'


class EncodingAwareFileReader:
    """Класс для чтения файлов с учётом кодировки"""
    
    def __init__(self, preferred_encoding: str = None):
        """
        Args:
            preferred_encoding: Предпочтительная кодировка (автоопределение если None)
        """
        self.preferred_encoding = preferred_encoding
        self.last_encoding = None
        self.encoding_stats = {
            'utf-8': 0,
            'cp1251': 0,
            'other': 0
        }
    
    def read(self, file_path: Path) -> str:
        """Чтение файла"""
        content, encoding = read_file_with_encoding(file_path, self.preferred_encoding)
        self.last_encoding = encoding
        self.encoding_stats[encoding if encoding in self.encoding_stats else 'other'] += 1
        return content
    
    def read_lines(self, file_path: Path) -> list:
        """Чтение файла по строкам"""
        content = self.read(file_path)
        return content.splitlines(keepends=True)
    
    def get_stats(self) -> dict:
        """Получить статистику по кодировкам"""
        total = sum(self.encoding_stats.values())
        return {
            'total_files': total,
            'utf-8': self.encoding_stats['utf-8'],
            'cp1251': self.encoding_stats['cp1251'],
            'other': self.encoding_stats['other'],
            'last_encoding': self.last_encoding
        }


def main():
    """Тестирование"""
    test_file = Path('PATCH_IN/patch_WORK/test.plp')
    
    if test_file.exists():
        print(f"Тестовый файл: {test_file}")
        
        # Автоопределение
        encoding, desc = detect_encoding(test_file)
        print(f"Определённая кодировка: {encoding} ({desc})")
        
        # Чтение
        content, used = read_file_with_encoding(test_file)
        print(f"Прочитано с кодировкой: {used}")
        print(f"Строк: {len(content.splitlines())}")
    else:
        print(f"Тестовый файл не найден: {test_file}")


if __name__ == '__main__':
    main()
