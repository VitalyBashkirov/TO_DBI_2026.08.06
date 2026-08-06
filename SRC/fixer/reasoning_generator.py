#!/usr/bin/env python3
"""
Генератор рассуждений для исправления кода
На основе подробного описания из рубрикатора создаёт обоснование необходимости исправления
"""
from typing import Optional


class ReasoningGenerator:
    """Генератор рассуждений для исправления проблемных конструкций"""
    
    def __init__(self):
        pass
    
    def generate_reasoning(self, 
                          original_code: str,
                          rubricator_code: str,
                          short_description: str,
                          full_description: str,
                          example_code: str,
                          example_fixed: str) -> dict:
        """
        Генерация рассуждения о необходимости исправления
        
        Возвращает словарь:
        {
            'reasoning': 'Обоснование необходимости исправления',
            'suggested_fix': 'Предлагаемое исправление',
            'confidence': 'Уверенность в исправлении (high/medium/low)'
        }
        """
        # Базовое рассуждение на основе описания
        reasoning = self._build_reasoning(
            original_code, rubricator_code, short_description, full_description
        )
        
        # Определение уверенности
        confidence = self._assess_confidence(original_code, example_code, example_fixed)
        
        # Предлагаемое исправление
        suggested_fix = self._suggest_fix(original_code, example_code, example_fixed)
        
        return {
            'reasoning': reasoning,
            'suggested_fix': suggested_fix,
            'confidence': confidence,
            'rubricator_code': rubricator_code,
            'short_description': short_description
        }
    
    def _build_reasoning(self, original_code: str, rubricator_code: str, 
                         short_description: str, full_description: str) -> str:
        """Построение обоснования необходимости исправления"""
        reasoning = []
        
        # 1. Констатация проблемы
        reasoning.append(f"Найдена проблемная конструкция в коде:")
        reasoning.append(f"  Код: {rubricator_code}")
        reasoning.append(f"  Описание: {short_description}")
        reasoning.append("")
        
        # 2. Обоснование на основе полного описания
        reasoning.append(f"Обоснование:")
        reasoning.append(f"  {full_description}")
        reasoning.append("")
        
        # 3. Анализ найденного кода
        reasoning.append(f"Анализ найденного кода:")
        if len(original_code) > 100:
            reasoning.append(f"  {original_code[:100]}...")
        else:
            reasoning.append(f"  {original_code}")
        reasoning.append("")
        
        # 4. Вывод о необходимости исправления
        reasoning.append(f"Вывод:")
        reasoning.append(f"  Требуется исправление для совместимости с PostgreSQL/DBI.")
        
        return '\n'.join(reasoning)
    
    def _assess_confidence(self, original_code: str, example_code: str, 
                          example_fixed: str) -> str:
        """Оценка уверенности в исправлении"""
        # Если есть пример из рубрикатора и он похож на найденный код
        if example_code and original_code:
            # Простая оценка по длине совпадений
            common_words = set(original_code.lower().split()) & set(example_code.lower().split())
            if len(common_words) > 3:
                return 'high'
            elif len(common_words) > 1:
                return 'medium'
        return 'low'
    
    def _suggest_fix(self, original_code: str, example_code: str, 
                     example_fixed: str) -> str:
        """Предложение исправления"""
        if example_fixed and example_code:
            # Если есть готовый пример исправления
            return f"Заменить конструкцию аналогично примеру:\n" \
                   f"  Было: {example_code}\n" \
                   f"  Стало: {example_fixed}\n" \
                   f"Применить аналогичное преобразование к вашему коду."
        elif original_code:
            # Если нет примера, предложить общее исправление
            return f"Необходимо переписать конструкцию согласно требованиям DBI.\n" \
                   f"Текущий код требует ручной корректировки."
        return ''


def main():
    """Тестирование генератора рассуждений"""
    generator = ReasoningGenerator()
    
    result = generator.generate_reasoning(
        original_code='select * from t1, t2 where t1.id = t2.id(+)',
        rubricator_code='v50.SQL.OUTERJOIN.п.1.1',
        short_description='Замена (+) на LEFT/RIGHT JOIN',
        full_description='В Oracle используется оператор (+) для внешнего соединения. '
                        'В PostgreSQL и ANSI SQL его нет. Заменить на явные LEFT JOIN или RIGHT JOIN.',
        example_code='select * from t1, t2 where t1.id = t2.id(+)',
        example_fixed='select * from t1 left join t2 on t1.id = t2.id'
    )
    
    print("=== Генератор рассуждений ===\n")
    print(result['reasoning'])
    print("\n" + "="*60 + "\n")
    print(f"Уверенность: {result['confidence']}")
    print("\nПредлагаемое исправление:")
    print(result['suggested_fix'])


if __name__ == '__main__':
    main()
