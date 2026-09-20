from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import re
from pathlib import Path

# DS_056A: единый хелпер лексического разбора
from analyzer.lexer_state import (
    LexerState,
    advance_lexer_state,
    is_line_fully_in_comment_or_string,
)


@dataclass
class VariableDeclaration:
    """Модель объявления переменной"""
    name: str
    var_type: str
    line_number: int
    is_parameter: bool = False
    is_constant: bool = False
    is_cursor: bool = False
    is_global: bool = False
    prefix_purpose: str = ""
    prefix_type: str = ""
    meaning: str = ""
    references: List[int] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []


class VariableParser:
    """Парсит PLPlus код и находит все объявления переменных"""
    
    TYPE_TO_PREFIX = {
        'integer': 'i', 'number': 'n', 'numeric': 'n', 'decimal': 'n',
        'bigint': 'n', 'smallint': 'n', 'pls_integer': 'n', 'binary_integer': 'n',
        'varchar2': 'v', 'varchar': 'v', 'string': 'v', 'char': 'v',
        'date': 'd', 'date_time': 'd', 'timestamp': 'd',
        'boolean': 'b',
        'ref': 'r', 'rowtype': 'r',
        'record': 'rec', 'table': 'tb', 'varray': 'tb',
        'clob': 'v', 'blob': 'v', 'long': 'v', 'raw': 'v'
    }
    
    KNOWN_TYPES = list(TYPE_TO_PREFIX.keys())
    
    def parse_variables(self, code: str) -> List[VariableDeclaration]:
        """Находит все объявления переменных в PLPlus коде"""
        variables = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self._is_comment_or_string(line):
                continue
            
            var = self._parse_declaration(line, line_num, code)
            if var:
                variables.append(var)
        
        return variables
    
    def _is_comment_or_string(self, line: str) -> bool:
        stripped = line.strip()
        if stripped.startswith(('--', '/*')):
            return True
        if re.match(r"^'.*'$", stripped):
            return True
        return False
    
    def _parse_declaration(self, line: str, line_num: int, full_code: str = '') -> Optional[VariableDeclaration]:
        """Парсит строку на наличие объявления переменной"""
        stripped = line.strip()
        
        # Пропускаем служебные строки
        if not stripped or stripped.startswith(('--', '/*', 'pragma', '@', 'begin', 'end', 'is')):
            return None
        if stripped.lower().startswith(('procedure', 'function', 'method')):
            return None
        
        # Ищем известный тип в строке
        found_type = None
        for type_name in self.KNOWN_TYPES:
            if type_name in stripped.lower():
                found_type = type_name
                break
        
        if not found_type:
            return None
        
        # Извлекаем имя переменной
        name = self._extract_name(stripped, found_type)
        if not name:
            return None
        
        # Определяем скоуп с учётом контекста
        scope = self._determine_scope(stripped, full_code, line_num)
        
        # Определяем префиксы
        prefix_purpose = self._get_purpose_prefix(name, scope)
        prefix_type = self.TYPE_TO_PREFIX.get(found_type, 'v')
        meaning = self._clean_meaning(name)
        
        return VariableDeclaration(
            name=name,
            var_type=found_type,
            line_number=line_num,
            is_parameter=(scope == 'parameter'),
            is_constant=(scope == 'constant'),
            is_cursor=(scope == 'cursor'),
            is_global=(scope == 'global'),
            prefix_purpose=prefix_purpose,
            prefix_type=prefix_type,
            meaning=meaning
        )
    
    def _extract_name(self, line: str, found_type: str) -> Optional[str]:
        """Извлекает имя переменной из строки"""
        type_pos = line.lower().find(found_type)
        if type_pos == -1:
            return None
        
        before_type = line[:type_pos].strip()
        if not before_type:
            return None
        
        words = before_type.split()
        if not words:
            return None
        
        name = words[-1]
        if name.lower() in ('var', 'const', 'public', 'in', 'out'):
            if len(words) > 1:
                name = words[-2]
            else:
                return None
        
        return name
    
    def _determine_scope(self, line: str, full_code: str = '', line_num: int = 0) -> str:
        """Определяет скоуп переменной с учётом контекста"""
        lower = line.lower()
        
        # Проверяем, находится ли строка внутри списка параметров процедуры
        if full_code and self._is_in_parameter_list(full_code, line_num):
            return 'parameter'
        
        if 'in' in lower or 'out' in lower:
            return 'parameter'
        if 'const' in lower:
            return 'constant'
        if 'cursor' in lower:
            return 'cursor'
        if lower.startswith('public'):
            return 'global'
        return 'local'
    
    def _is_in_parameter_list(self, code: str, line_num: int) -> bool:
        """Проверяет, находится ли строка внутри списка параметров процедуры"""
        lines = code.split('\n')
        if line_num > len(lines):
            return False
        
        current_line = lines[line_num - 1].strip()
        print(f"[DEBUG] Проверка строки {line_num}: '{current_line}'")
        
        # Идём вверх, ищем объявление procedure/function/method
        for i in range(line_num - 1, max(0, line_num - 15), -1):
            line = lines[i].strip()
            print(f"[DEBUG]   Строка {i+1}: '{line}'")
            # Ищем объявление с открывающей скобкой
            match = re.search(
                r'(procedure|function|method|operation)\s+\w+\s*\(', 
                line, 
                re.IGNORECASE
            )
            if match:
                print(f"[DEBUG]   Найдено объявление в строке {i+1}")
                # Проверяем скобки
                bracket_count = 0
                for j in range(i, line_num):
                    bracket_count += lines[j].count('(')
                    bracket_count -= lines[j].count(')')
                    print(f"[DEBUG]     Строка {j+1}: скобки = {bracket_count}")
                    if bracket_count == 0 and j > i:
                        print(f"[DEBUG]     Скобки закрыты, возвращаем False")
                        return False
                print(f"[DEBUG]   Скобки открыты, возвращаем True")
                return bracket_count > 0
        
        print(f"[DEBUG] Объявление не найдено, возвращаем False")
        return False
    
    def _get_purpose_prefix(self, name: str, scope: str) -> str:
        """Определяет префикс назначения"""
        prefixes = ['v_', 'p_', 'cn_', 'cur_', 'gv_', 'gcn_', 'gcur_', 'ret_']
        for prefix in prefixes:
            if name.startswith(prefix):
                return prefix
        
        scope_map = {
            'parameter': 'p_',
            'constant': 'cn_',
            'cursor': 'cur_',
            'global': 'gv_',
        }
        return scope_map.get(scope, 'v_')
    
    def _clean_meaning(self, name: str) -> str:
        """Очищает смысловую часть от префиксов"""
        meaning = name
        
        for prefix in ['v_', 'p_', 'cn_', 'cur_', 'gv_', 'gcn_', 'gcur_', 'ret_']:
            if meaning.startswith(prefix):
                meaning = meaning[len(prefix):]
                break
        
        for prefix in ['n', 'v', 'd', 'b', 'r', 'rec', 'tb', 'i']:
            if meaning.startswith(prefix) and len(meaning) > len(prefix):
                if meaning[len(prefix)].isupper():
                    meaning = meaning[len(prefix):]
                    break
        
        if '_' in meaning and meaning.isupper():
            meaning = ''.join(word.capitalize() for word in meaning.split('_'))
        
        if meaning:
            meaning = meaning[0].upper() + meaning[1:]
        
        return meaning or name


class DeterministicFixer:
    """Применяет детерминированные правки к PLPlus коду"""
    
    def __init__(self):
        self.parser = VariableParser()
    
    def fix_file(self, file_path: str) -> Dict:
        """Основной метод исправления файла"""
        if not Path(file_path).exists():
            return {'file': file_path, 'changes': [], 'modified': False, 'error': f'Файл не найден: {file_path}'}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        changes = []
        
        variables = self.parser.parse_variables(code)
        rename_map = self._build_rename_map(variables)
        
        for old_name, new_name in rename_map.items():
            code, count = self._rename_variable(code, old_name, new_name)
            if count > 0:
                changes.append({'old_name': old_name, 'new_name': new_name, 'count': count})
        
        code, deleted = self._remove_unused(code, variables, rename_map)
        if deleted:
            changes.append({'deleted': deleted, 'count': len(deleted)})
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return {
            'file': file_path,
            'changes': changes,
            'modified': len(changes) > 0
        }
    
    def _build_rename_map(self, variables: List[VariableDeclaration]) -> Dict[str, str]:
        rename_map = {}
        for var in variables:
            if self._is_correctly_named(var):
                continue
            new_name = self._build_new_name(var)
            if new_name and new_name != var.name:
                rename_map[var.name] = new_name
        return rename_map
    
    def _is_correctly_named(self, var: VariableDeclaration) -> bool:
        """Проверяет, правильно ли названа переменная"""
        if var.is_parameter:
            # Для параметров: должно быть p_{тип}{Смысл}
            expected_prefix = 'p_' + var.prefix_type
            # Проверяем, начинается ли имя с правильного префикса
            if var.name.startswith(expected_prefix):
                # Дополнительно проверяем, что после префикса идёт заглавная буква
                rest = var.name[len(expected_prefix):]
                if rest and rest[0].isupper():
                    return True
            return False
        
        # Для локальных: должно быть v_{тип}{Смысл}
        expected_prefix = 'v_' + var.prefix_type
        if var.name.startswith(expected_prefix):
            rest = var.name[len(expected_prefix):]
            if rest and rest[0].isupper():
                return True
        return False
    
    def _build_new_name(self, var: VariableDeclaration) -> str:
        purpose = var.prefix_purpose
        type_prefix = var.prefix_type
        meaning = var.meaning
        if not meaning:
            meaning = self._extract_meaning(var.name)
        if meaning:
            meaning = meaning[0].upper() + meaning[1:] if len(meaning) > 1 else meaning.upper()
        return f"{purpose}{type_prefix}{meaning}"
    
    def _extract_meaning(self, name: str) -> str:
        for prefix in ['v_', 'p_', 'cn_', 'cur_', 'gv_', 'gcn_', 'gcur_', 'ret_']:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        for prefix in ['n', 'v', 'd', 'b', 'r', 'rec', 'tb', 'i']:
            if name.startswith(prefix) and len(name) > len(prefix):
                if name[len(prefix)].isupper():
                    name = name[len(prefix):]
                    break
        return name
    
    def _rename_variable(self, code: str, old_name: str, new_name: str) -> Tuple[str, int]:
        lines = code.split('\n')
        count = 0
        state = LexerState()  # DS_056A: лексическое состояние переносим между строками
        for i, line in enumerate(lines):
            in_cmt = is_line_fully_in_comment_or_string(line, state)
            advance_lexer_state(line, state)  # ровно один раз на строку
            if in_cmt:
                continue
            new_line = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, line)
            if new_line != line:
                lines[i] = new_line
                count += len(re.findall(r'\b' + re.escape(old_name) + r'\b', line))
        return '\n'.join(lines), count
    
    def _is_in_comment_or_string(self, line: str) -> bool:
        """
        DS_056A: делегирование в единый хелпер (обёртка «строка целиком»).
        Используется как совместимый без-стейтовый вызов (без переноса состояния
        между строками). Для итераций по строкам см. _rename_variable /
        _is_variable_used — там состояние ведётся явно через LexerState.
        """
        return is_line_fully_in_comment_or_string(line, LexerState())
    
    def _remove_unused(self, code: str, variables: List[VariableDeclaration], rename_map: Dict[str, str]) -> Tuple[str, List]:
        lines = code.split('\n')
        deleted = []
        
        used_vars = set()
        for var in variables:
            new_name = rename_map.get(var.name, var.name)
            if self._is_variable_used(code, new_name, var.line_number):
                used_vars.add(var.name)
        
        new_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('--'):
                new_lines.append(line)
                continue
            
            is_unused_decl = False
            for var in variables:
                if var.name not in used_vars:
                    if re.search(r'\b' + re.escape(var.name) + r'\b\s*[;:=]', stripped):
                        is_unused_decl = True
                        deleted.append({'name': var.name, 'line': i + 1})
                        break
            
            if not is_unused_decl:
                new_lines.append(line)
        
        return '\n'.join(new_lines), deleted
    
    def _is_variable_used(self, code: str, var_name: str, decl_line: int) -> bool:
        lines = code.split('\n')
        state = LexerState()  # DS_056A: переносим лексическое состояние между строками
        for i, line in enumerate(lines):
            in_cmt = is_line_fully_in_comment_or_string(line, state)
            advance_lexer_state(line, state)  # ровно один раз на строку
            if i + 1 == decl_line:
                continue
            if re.search(r'\b' + re.escape(var_name) + r'\b', line):
                if not in_cmt:
                    return True
        return False