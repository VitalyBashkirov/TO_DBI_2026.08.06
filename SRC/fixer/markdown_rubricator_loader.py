#!/usr/bin/env python3
"""
Загрузчик рубрикатора из markdown файлов
Версия: v01
"""
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RubricatorFile:
    """Файл рубрикатора"""
    id: int
    enabled: bool  # Признак (+/-)
    code: str
    filename: str
    path: str


@dataclass
class RubricatorFix:
    """Исправление из рубрикатора"""
    id: int
    code: str  # КодФайла.КодКатегории.КодИсправл.Пункт
    points: str  # Пункт(ы)
    tags: List[str]  # Теги (через запятую)
    short_description: str
    full_description: str
    example_code: str  # Пример кода для корректировки
    example_fixed: str  # Пример исправленного кода
    enabled: bool = True  # Включено ли (зависит от файла)
    rubricator_line: str = ''  # Полное содержимое строки из рубрикатора


class MarkdownRubricatorLoader:
    """Загрузчик рубрикатора из markdown файлов"""
    
    def __init__(self, rubricator_dir: str = None):
        if rubricator_dir is None:
            rubricator_dir = Path(__file__).parent.parent.parent / 'DATA' / 'Рубрикатор'
        else:
            rubricator_dir = Path(rubricator_dir)
        
        self.rubricator_dir = Path(rubricator_dir)
        self.files: List[RubricatorFile] = []
        self.fixes: List[RubricatorFix] = []
        self.categories: List[dict] = []
        
        self._load_files()
        self._load_categories()
        self._load_fixes()
    
    def _load_files(self):
        """Загрузка 1.RUBRICATOR_FILES.md"""
        file_path = self.rubricator_dir / '1.RUBRICATOR_FILES.md'
        
        if not file_path.exists():
            print(f"[!] Файл не найден: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсинг таблицы
        lines = content.strip().split('\n')
        
        # Пропускаем заголовок и разделитель (первые 2 строки после заголовка)
        in_table = False
        for line in lines:
            line = line.strip()
            
            # Пропускаем пустые строки и заголовок
            if not line or line.startswith('#'):
                continue
            
            # Пропускаем разделительную строку
            if line.startswith('|---'):
                in_table = True
                continue
            
            if not in_table:
                continue
            
            # Разбираем строку таблицы
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) < 4:
                continue
            
            try:
                # Порядок столбцов: № | Признак | Код файла | Полное имя файла
                file_id = int(parts[0])
                enabled = parts[1].strip() == '+'
                code = parts[2].strip()
                filename = parts[3].strip().strip('`')
                
                # Извлекаем путь из имени файла
                path_match = re.search(r'`([^`]+)`', line)
                path = path_match.group(1) if path_match else filename
                
                self.files.append(RubricatorFile(
                    id=file_id,
                    enabled=enabled,
                    code=code,
                    filename=filename,
                    path=path
                ))
            except (ValueError, IndexError) as e:
                print(f"[!] Ошибка парсинга строки: {line} - {e}")
    
    def _load_categories(self):
        """Загрузка 2.RUBRICATOR_CATEGORIES.md"""
        file_path = self.rubricator_dir / '2.RUBRICATOR_CATEGORIES.md'
        
        if not file_path.exists():
            print(f"[!] Файл не найден: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсинг таблицы
        lines = content.strip().split('\n')
        
        in_table = False
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('|---'):
                in_table = True
                continue
            
            if not in_table:
                continue
            
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) < 3:
                continue
            
            try:
                # Порядок столбцов: № | Код категории | Описание категории
                cat_id = int(parts[0])
                code = parts[1].strip()
                description = parts[2].strip()
                
                self.categories.append({
                    'id': cat_id,
                    'code': code,
                    'description': description
                })
            except (ValueError, IndexError):
                pass
    
    def _load_fixes(self):
        """Загрузка 3.RUBRICATOR_FIXES.md"""
        file_path = self.rubricator_dir / '3.RUBRICATOR_FIXES.md'
        
        if not file_path.exists():
            print(f"[!] Файл не найден: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Определяем включённые коды файлов
        enabled_codes = {f.code for f in self.files if f.enabled}
        print(f"[DEBUG] Включённые коды файлов: {enabled_codes}")
        
        # Парсинг таблицы
        lines = content.strip().split('\n')
        
        in_table = False
        fix_count = 0
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('|---'):
                in_table = True
                continue
            
            if not in_table:
                continue
            
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) < 6:
                continue
            
            try:
                # Порядок столбцов: |N|++|Коды Файла.Категории.Исправления.Пункты/Строки|Пункт/Стр.|Теги|Короткое описание|...
                # Индексы:            [0, 1,  3,                                             4,         5,        6]
                fix_id = int(parts[0])
                plus_plus = parts[1].strip()  # Колонка "++"
                code = parts[2].strip()
                points = parts[3].strip()
                tags_str = parts[4].strip()
                short_desc = parts[5].strip() if len(parts) > 5 else ''
                full_desc = parts[6].strip() if len(parts) > 6 else ''
                
                # Проверяем 1-й символ колонки "++": '-' - не выполнять, '+' или ' ' - выполнять
                if plus_plus and plus_plus[0] == '-':
                    continue  # Пропускаем отключённые исправления
                
                # Проверяем, включён ли файл
                file_code = code.split('.')[0]  # v50, тдс20240828, тклоик20240828
                enabled = file_code in enabled_codes
                
                # Парсим теги (разделяем по запятой)
                tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []
                
                self.fixes.append(RubricatorFix(
                    id=fix_id,
                    code=code,
                    points=points,
                    tags=tags,
                    short_description=short_desc,
                    full_description=full_desc,
                    example_code='',  # Пустой пример (не загружается из старого рубрикатора)
                    example_fixed='',  # Пустой пример (не загружается из старого рубрикатора)
                    enabled=enabled
                ))
                fix_count += 1
            except (ValueError, IndexError) as e:
                print(f"[!] Ошибка парсинга строки: {line} - {e}")
        
        print(f"[DEBUG] Загружено исправлений: {fix_count}")
    
    def get_enabled_files(self) -> List[RubricatorFile]:
        """Получить список включённых файлов"""
        return [f for f in self.files if f.enabled]
    
    def get_disabled_files(self) -> List[RubricatorFile]:
        """Получить список отключённых файлов"""
        return [f for f in self.files if not f.enabled]
    
    def get_enabled_fixes(self) -> List[RubricatorFix]:
        """Получить список включённых исправлений"""
        return [f for f in self.fixes if f.enabled]
    
    def get_fixes_by_file_code(self, file_code: str) -> List[RubricatorFix]:
        """Получить исправления по коду файла"""
        return [f for f in self.fixes if f.code.startswith(file_code + '.')]
    
    def get_fixes_by_tags(self, tags: List[str]) -> List[RubricatorFix]:
        """Получить исправления по тегам"""
        if not tags:
            return []
        result = []
        for fix in self.fixes:
            if fix.enabled:
                for tag in tags:
                    if tag.lower() in [t.lower() for t in fix.tags]:
                        result.append(fix)
                        break
        return result

    def get_fix_by_code(self, code: str) -> Optional[RubricatorFix]:
        """Получить исправление по коду (первое совпадение)"""
        for fix in self.fixes:
            if fix.enabled and fix.code == code:
                return fix
        return None

    def get_all_tags(self) -> List[str]:
        """Получить список всех уникальных тегов"""
        tags = set()
        for fix in self.fixes:
            for tag in fix.tags:
                tags.add(tag.lower())
        return sorted(list(tags))
    
    def print_to_log(self, log_func) -> str:
        """
        Вывод рубрикатора в журнал
        Возвращает строку для логирования
        """
        lines = []
        lines.append("=" * 80)
        lines.append("РУБРИКАТОР (из DATA/Рубрикатор/)")
        lines.append("=" * 80)
        
        # Файлы рубрикатора
        lines.append("\n1. ФАЙЛЫ РУБРИКАТОРА:")
        lines.append("-" * 80)
        lines.append(f"{'№':<4} {'Вкл.':<6} {'Код':<15} {'Имя файла'}")
        lines.append("-" * 80)
        
        for file in self.files:
            status = "[+]" if file.enabled else "[-]"
            lines.append(f"{file.id:<4} {status:<6} {file.code:<15} {file.filename}")
        
        # Категории
        lines.append("\n2. КАТЕГОРИИ ИСПРАВЛЕНИЙ:")
        lines.append("-" * 80)
        for cat in self.categories:
            lines.append(f"  {cat['code']:<10} - {cat['description']}")
        
        # Исправления
        lines.append("\n3. ИСПРАВЛЕНИЯ (с учётом включения/отключения):")
        lines.append("-" * 80)
        lines.append(f"{'№':<4} {'Вкл.':<6} {'Код исправления':<35} {'Теги':<30} {'Описание'}")
        lines.append("-" * 80)
        
        for fix in self.fixes:
            status = "[+]" if fix.enabled else "[-]"
            code_short = fix.code[:33] + '..' if len(fix.code) > 35 else fix.code
            tags_str = ', '.join(fix.tags[:3]) if fix.tags else '-'
            tags_short = tags_str[:28] + '..' if len(tags_str) > 30 else tags_str
            desc_short = fix.short_description[:40] + '..' if len(fix.short_description) > 42 else fix.short_description
            lines.append(f"{fix.id:<4} {status:<6} {code_short:<35} {tags_short:<30} {desc_short}")
        
        # Статистика
        enabled_count = len(self.get_enabled_fixes())
        total_count = len(self.fixes)
        lines.append("\n" + "-" * 80)
        lines.append(f"ВСЕГО ИСПРАВЛЕНИЙ: {total_count}")
        lines.append(f"ВКЛЮЧЕНО: {enabled_count}")
        lines.append(f"ОТКЛЮЧЕНО: {total_count - enabled_count}")
        lines.append("=" * 80)
        
        result = '\n'.join(lines)
        
        # Вывод в журнал
        for line in lines:
            log_func(line)
        
        return result


def main():
    """Тестирование загрузчика"""
    loader = MarkdownRubricatorLoader()
    
    print("\n=== Загрузчик рубрикатора ===\n")
    
    # Вывод в stdout
    def print_log(msg):
        print(msg)
    
    loader.print_to_log(print_log)
    
    print(f"\nВключённые файлы: {len(loader.get_enabled_files())}")
    for f in loader.get_enabled_files():
        print(f"  - {f.code}: {f.filename}")
    
    print(f"\nВключённые исправления: {len(loader.get_enabled_fixes())}")
    for fix in loader.get_enabled_fixes()[:10]:  # Первые 10
        print(f"  - {fix.code}: {fix.short_description}")


if __name__ == '__main__':
    main()
