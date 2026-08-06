#!/usr/bin/env python3
"""
AI-анализатор сложных правил рубрикатора v3.3.0
Двухфазный анализ: быстрое сканирование + AI-анализ контекста
"""
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AIAnalysisResult:
    """Результат AI-анализа"""
    rule_code: str
    priority: int
    line_number: int
    original_code: str
    fixed_code: str
    reasoning: str
    steps_summary: str
    confidence: float  # 0.0-1.0


class PLPlusAIAnalyzer:
    """AI-анализатор для сложных правил миграции"""
    
    # Системные функции Oracle (не являются UDF)
    SYSTEM_FUNCTIONS = {
        'nvl', 'decode', 'case', 'coalesce', 'to_char', 'to_date', 'to_number',
        'substr', 'instr', 'length', 'trim', 'upper', 'lower', 'count', 'sum',
        'avg', 'min', 'max', 'sysdate', 'user', 'rownum', 'null', 'lengthb',
        'replace', 'translate', 'round', 'trunc', 'mod', 'power', 'sqrt',
        'sign', 'abs', 'ceil', 'floor', 'greatest', 'least', 'nvl2', 'nullif',
        'concat', 'chr', 'ascii', 'lpad', 'rpad', 'ltrim', 'rtrim', 'initcap',
        'instrb', 'substrb', 'to_timestamp', 'to_clob', 'to_blob', 'rawtohex',
        'hextoraw', 'dump', 'vsize', 'chartorowid', 'rowidtochar'
    }
    
    def __init__(self, rubricator_rules: Dict):
        self.rules = rubricator_rules
        self.ai_rules = {
            code: rule for code, rule in rubricator_rules.items()
            if rule.get('ai_analysis_required', False)
        }
    
    def analyze_file(self, file_path: Path, lines: List[str], 
                     found_issues: List[Dict]) -> List[AIAnalysisResult]:
        """
        Фаза 2: AI-анализ найденных потенциальных проблем
        
        Args:
            file_path: путь к файлу
            lines: строки файла
            found_issues: список найденных на Фазе1 проблем
            
        Returns:
            Список подтверждённых проблем с предложениями исправлений
        """
        results = []
        
        # Собираем контекст файла (объявления функций, переменных)
        file_context = self._extract_file_context(lines)
        
        for issue in found_issues:
            rule_code = issue.get('rule_code', '')
            if rule_code not in self.ai_rules:
                continue
            
            rule = self.ai_rules[rule_code]
            ai_instructions = rule.get('ai_analysis_instructions', {})
            
            # Определяем тип правила и вызываем соответствующий анализатор
            analyzer_method = self._get_analyzer(rule_code)
            if analyzer_method:
                result = analyzer_method(
                    rule_code=rule_code,
                    rule=rule,
                    ai_instructions=ai_instructions,
                    lines=lines,
                    issue=issue,
                    file_context=file_context
                )
                if result:
                    results.append(result)
        
        return results
    
    def _get_analyzer(self, rule_code: str):
        """Получить метод-анализатор для правила"""
        analyzers = {
            'v50.SQL.UDF.п.1.3': self._analyze_udf,
            'v50.SQL.SYSTABLES.п.1.10': self._analyze_systables,
            'v50.SQL.ORACLE_PKG.п.1.11': self._analyze_oracle_pkg,
            'v50.SQL.CONTEXT.п.1.23': self._analyze_context,
            'v50.PROC.NATIVEID.п.3.26': self._analyze_nativeid,
            'v50.PROC.ID_SIZE.п.3.27': self._analyze_id_size,
            'v50.SQL.REF_SELECT.п.1.27': self._analyze_ref_select,
            'v50.SQL.DML_JOIN.п.1.17': self._analyze_dml_join,
            'v50.SQL.TABLE_SELECT.п.1.13': self._analyze_table_select,
        }
        return analyzers.get(rule_code)
    
    def _extract_file_context(self, lines: List[str]) -> Dict:
        """Извлечь контекст файла: объявления функций, переменных"""
        context = {
            'functions': [],  # Объявленные функции
            'variables': {},  # Объявленные переменные с типами
            'packages': [],   # Используемые пакеты
        }
        
        for i, line in enumerate(lines, 1):
            # Объявление функции: FUNCTION name (...) RETURN ... IS
            func_match = re.search(
                r'\bFUNCTION\s+(\w+)\s*\((.*?)\)\s*RETURN\s+(\w+)',
                line, re.IGNORECASE
            )
            if func_match:
                context['functions'].append({
                    'name': func_match.group(1).upper(),
                    'params': func_match.group(2),
                    'return_type': func_match.group(3),
                    'line': i
                })
            
            # Объявление переменной: name TYPE;
            var_match = re.search(
                r'^(\w+)\s+(NUMBER|VARCHAR2?|STRING|DATE|BOOLEAN|REF\s+\w+)',
                line.strip(), re.IGNORECASE
            )
            if var_match:
                var_name = var_match.group(1).upper()
                var_type = var_match.group(2).upper()
                context['variables'][var_name] = {
                    'type': var_type,
                    'line': i
                }
        
        return context
    
    def _analyze_udf(self, rule_code: str, rule: Dict, 
                     ai_instructions: Dict, lines: List[str],
                     issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип A: UDF в WHERE/GROUP BY/ORDER BY
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        # Шаг 1: Извлечь все вызовы функций из строки
        func_calls = re.findall(r'\b(\w+)\s*\(', line)
        
        # Шаг 2: Исключить системные функции
        udf_calls = [
            f for f in func_calls 
            if f.upper() not in self.SYSTEM_FUNCTIONS
        ]
        
        if not udf_calls:
            return None
        
        # Шаг 3: Проверить, объявлена ли функция в файле
        declared_funcs = {f['name'] for f in file_context['functions']}
        
        # Шаг 4: Проверить контекст использования (WHERE/GROUP BY/ORDER BY/HAVING)
        forbidden_contexts = ['WHERE', 'GROUP BY', 'ORDER BY', 'HAVING']
        line_upper = line.upper()
        
        context_found = None
        for ctx in forbidden_contexts:
            if ctx in line_upper:
                context_found = ctx
                break
        
        if not context_found:
            return None
        
        # Шаг 5: Сформировать исправление
        func_name = udf_calls[0]
        is_user_defined = func_name.upper() in declared_funcs
        
        reasoning = (
            f"Функция '{func_name}' используется в контексте {context_found}. "
            f"{'Это пользовательская функция (UDF), объявленная в файле. ' if is_user_defined else ''}"
            f"UDF запрещены в WHERE/GROUP BY/ORDER BY/HAVING. "
            f"Необходимо перенести вызов в SELECT-лист."
        )
        
        # Пример исправления
        fixed = line
        if is_user_defined:
            fixed = (
                f"-- [AI] Перенесите вызов {func_name}() в SELECT-лист\n"
                f"-- Оригинал: {line.strip()}\n"
                f"-- Исправьте: SELECT id, {func_name}(...) AS val FROM ... WHERE val > ..."
            )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=fixed,
            reasoning=reasoning,
            steps_summary="UDF v zapreshennom kontekste -> perenos v SELECT-list",
            confidence=0.95 if is_user_defined else 0.7
        )
    
    def _analyze_systables(self, rule_code: str, rule: Dict,
                           ai_instructions: Dict, lines: List[str],
                           issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип B: Системные таблицы ТЯ
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        forbidden_tables = ai_instructions.get('forbidden_tables', [])
        line_upper = line.upper()
        
        found_table = None
        for table in forbidden_tables:
            if table.upper() in line_upper:
                found_table = table
                break
        
        if not found_table:
            return None
        
        replacements = ai_instructions.get('replacements', {})
        replacement = replacements.get(found_table, '::[METACLASS]')
        
        reasoning = (
            f"Обнаружена системная таблица '{found_table}' в запросе. "
            f"Системные таблицы ТЯ недоступны в DBI. "
            f"Рекомендуется заменить на '{replacement}'."
        )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=f"-- [AI] Замените {found_table} на {replacement}\n-- {line.strip()}",
            reasoning=reasoning,
            steps_summary="Sistemnaia tablitsa -> zamena na METACLASS",
            confidence=0.9
        )
    
    def _analyze_oracle_pkg(self, rule_code: str, rule: Dict,
                            ai_instructions: Dict, lines: List[str],
                            issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип C: Oracle пакеты
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        forbidden_packages = ai_instructions.get('forbidden_packages', [])
        line_upper = line.upper()
        
        found_pkg = None
        for pkg in forbidden_packages:
            if pkg.upper() in line_upper:
                found_pkg = pkg
                break
        
        if not found_pkg:
            return None
        
        reasoning = (
            f"Обнаружен вызов Oracle пакета '{found_pkg}'. "
            f"Oracle пакеты недоступны в PostgreSQL/DBI. "
            f"Необходимо заменить на аналог из PCORE_INTERFACE или удалить."
        )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=f"-- [AI] Удалите или замените вызов {found_pkg}\n-- {line.strip()}",
            reasoning=reasoning,
            steps_summary="Oracle paket -> udalenie/zamena",
            confidence=0.95
        )
    
    def _analyze_context(self, rule_code: str, rule: Dict,
                         ai_instructions: Dict, lines: List[str],
                         issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип D: SYS_CONTEXT
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        # Извлечь параметр SYS_CONTEXT
        match = re.search(
            r'SYS_CONTEXT\s*\(\s*[\'"](\w+)[\'"]\s*,\s*[\'"](\w+)[\'"]\s*\)',
            line, re.IGNORECASE
        )
        if not match:
            return None
        
        namespace = match.group(1).upper()
        parameter = match.group(2).upper()
        
        replacements = ai_instructions.get('replacements', {})
        key = f"{namespace}.{parameter}"
        replacement = replacements.get(key) or replacements.get(parameter)
        
        if not replacement:
            replacement = f"::[RUNTIME].[ENVIRONMENT].ClassStorage('ТБП').{parameter.lower()}"
        
        reasoning = (
            f"SYS_CONTEXT('{namespace}', '{parameter}') не поддерживается. "
            f"Замените на '{replacement}'."
        )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=f"-- [AI] Замените SYS_CONTEXT на {replacement}\n-- {line.strip()}",
            reasoning=reasoning,
            steps_summary="SYS_CONTEXT -> zamena na RUNTIME",
            confidence=0.95
        )
    
    def _analyze_nativeid(self, rule_code: str, rule: Dict,
                          ai_instructions: Dict, lines: List[str],
                          issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип E: NativeID - присваивание %id в NUMBER
        """
        line_num = issue['line_number']
        
        # Ищем объявление NUMBER переменной
        for i in range(max(0, line_num - 10), line_num):
            decl_match = re.search(
                r'^(\w+)\s+NUMBER\s*;',
                lines[i].strip(), re.IGNORECASE
            )
            if decl_match:
                var_name = decl_match.group(1)
                # Проверяем что переменная используется для %id
                for j in range(line_num - 1, min(len(lines), line_num + 5)):
                    if re.search(rf'{var_name}\s*:=\s*\w+%id', lines[j], re.IGNORECASE):
                        reasoning = (
                            f"Переменная '{var_name}' объявлена как NUMBER, "
                            f"но используется для хранения %id (строковый идентификатор). "
                            f"В DBI идентификаторы операций стали строками. "
                            f"Замените на VARCHAR2(100)."
                        )
                        return AIAnalysisResult(
                            rule_code=rule_code,
                            priority=rule.get('priority_level', 1),
                            line_number=i + 1,
                            original_code=lines[i].strip(),
                            fixed_code=f"{var_name} VARCHAR2(100); -- [AI] Было NUMBER, заменено для %id",
                            reasoning=reasoning,
                            steps_summary="NUMBER -> VARCHAR2(100) dlia %id",
                            confidence=0.95
                        )
        
        return None
    
    def _analyze_id_size(self, rule_code: str, rule: Dict,
                         ai_instructions: Dict, lines: List[str],
                         issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип F: Размер ID < 20 символов
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        match = re.search(
            r'(\w+)\s+(?:VARCHAR2|STRING)\s*\((\d+)\)\s*;',
            line, re.IGNORECASE
        )
        if not match:
            return None
        
        var_name = match.group(1)
        size = int(match.group(2))
        
        if size >= 20:
            return None
        
        # Проверяем что переменная используется для %id
        for j in range(line_num, min(len(lines), line_num + 10)):
            if re.search(rf'{var_name}\s*:=\s*\w+%id', lines[j], re.IGNORECASE):
                reasoning = (
                    f"Переменная '{var_name}' объявлена как VARCHAR2({size}), "
                    f"но используется для хранения %id. "
                    f"ID генерируется как bigint (до 19 цифр). "
                    f"Размер должен быть >= 20 символов."
                )
                return AIAnalysisResult(
                    rule_code=rule_code,
                    priority=rule.get('priority_level', 1),
                    line_number=line_num,
                    original_code=line.strip(),
                    fixed_code=f"{var_name} VARCHAR2(20); -- [AI] Было {size}, увеличено для %id",
                    reasoning=reasoning,
                    steps_summary="VARCHAR2(%s) -> VARCHAR2(20) dlia %%id" % size,
                    confidence=0.95
                )
        
        return None
    
    def _analyze_ref_select(self, rule_code: str, rule: Dict,
                            ai_instructions: Dict, lines: List[str],
                            issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип G: Выборка из ссылок (REF)
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        match = re.search(
            r'SELECT\s+.*\s+FROM\s+(\w+)',
            line, re.IGNORECASE
        )
        if not match:
            return None
        
        var_name = match.group(1).upper()
        var_info = file_context['variables'].get(var_name)
        
        if not var_info or 'REF' not in var_info['type']:
            return None
        
        reasoning = (
            f"SELECT из переменной '{var_name}' типа REF. "
            f"Выборка из ссылок требует анализа типа REF. "
            f"Проверьте корректность запроса для DBI."
        )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=f"-- [AI] Проверьте SELECT из REF переменной\n-- {line.strip()}",
            reasoning=reasoning,
            steps_summary="SELECT iz REF -> proverka korrektnosti",
            confidence=0.7
        )
    
    def _analyze_dml_join(self, rule_code: str, rule: Dict,
                          ai_instructions: Dict, lines: List[str],
                          issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип H: DML с JOIN
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        if not re.search(r'\b(UPDATE|DELETE)\b', line, re.IGNORECASE):
            return None
        
        if not re.search(r'\bJOIN\b|\bFROM\b.*,', line, re.IGNORECASE):
            return None
        
        reasoning = (
            f"Обнаружен UPDATE/DELETE с JOIN. "
            f"В PostgreSQL синтаксис DML с JOIN отличается от Oracle. "
            f"Необходимо преобразовать в подзапрос с EXISTS."
        )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=f"-- [AI] Преобразуйте UPDATE/DELETE с JOIN в подзапрос с EXISTS\n-- {line.strip()}",
            reasoning=reasoning,
            steps_summary="DML s JOIN -> podzapros s EXISTS",
            confidence=0.85
        )
    
    def _analyze_table_select(self, rule_code: str, rule: Dict,
                              ai_instructions: Dict, lines: List[str],
                              issue: Dict, file_context: Dict) -> Optional[AIAnalysisResult]:
        """
        Тип I: SELECT FROM TABLE()
        """
        line_num = issue['line_number']
        line = lines[line_num - 1]
        
        match = re.search(
            r'FROM\s+TABLE\s*\(\s*(\w+)\s*\)',
            line, re.IGNORECASE
        )
        if not match:
            return None
        
        collection_name = match.group(1)
        
        reasoning = (
            f"SELECT FROM TABLE({collection_name}). "
            f"Необходимо определить тип коллекции (скалярная/объектная). "
            f"Skaliarnaia kollektsiia -> ostavit kak est. "
            f"Obiektnaia kollektsiia -> trebuetsia analiz."
        )
        
        return AIAnalysisResult(
            rule_code=rule_code,
            priority=rule.get('priority_level', 1),
            line_number=line_num,
            original_code=line.strip(),
            fixed_code=f"-- [AI] Проверьте тип коллекции {collection_name}\n-- {line.strip()}",
            reasoning=reasoning,
            steps_summary="TABLE(collection) -> proverka tipa kollektsii",
            confidence=0.6
        )
