# -*- coding: utf-8 -*-
"""
Единый хелпер лексического разбора комментариев и строковых литералов PL/Plus.
DS_056A: унификация _is_in_comment_or_string.

Ключевое архитектурное требование (раздел 2 задания):
  * is_in_comment_or_string        — ТОЛЬКО отвечает на вопрос, НЕ мутирует state.
  * advance_lexer_state            — обновляет state по всей строке (1 раз на строку).
  * is_line_fully_in_comment_or_string — обёртка (строка целиком), НЕ мутирует state.

Правила разбора (раздел 3.2):
  1. -- ...            — комментарий до конца строки (если не внутри '...' и /* */)
  2. /* ... */         — от /* до первого */ (Oracle: вложенность НЕ поддерживается)
  3. '...'             — от ' до '; '' внутри — экранирование, не закрывает литерал
  4. q'X...X'          — q-quoting (X ∈ [ { ( < или любой символ), регистр q не важен
  5. "..."             — двойные кавычки НЕ терминаторы строкового литерала
  6. &debug(...)       — при debug_mode=True переменные внутри '...' считаются кодом
  7. /*+ ... */        — hint: НЕ считается комментарием для целей поиска кода
  8. Многострочный '... — in_string_literal переносится между строками через advance
  9. CRLF              — \\r не должен ломать разбор (line.rstrip('\\r\\n'))
"""
from dataclasses import dataclass


# Парные терминаторы для q-quoting
_Q_PAIRS = {'[': ']', '{': '}', '(': ')', '<': '>'}


@dataclass
class LexerState:
    """Состояние лексического разбора, переносимое между строками."""
    in_block_comment: bool = False
    in_string_literal: bool = False


def _scan_line(line, in_block, in_str, answer_start):
    """
    Линейный разбор строки от начального состояния (in_block, in_str).

    Возвращает (final_block, final_str, covered, covered_in_str):
      final_block/final_str — состояние ПОСЛЕ разбора всей строки;
      covered — находился ли answer_start внутри комментария/строки
                (None для answer_start → не вычисляется);
      covered_in_str — если covered, то был ли охватитель именно строковым
                       литералом (для debug_mode).

    Функция ЧИСТАЯ: не трогает переданное состояние, только локальные копии.
    """
    i = 0
    n = len(line)
    covered = False
    covered_in_str = False

    while i < n:
        # Фиксируем охват позиции answer_start ДО обработки токена на i.
        if answer_start is not None and i == answer_start:
            if in_block or in_str:
                covered = True
                covered_in_str = in_str and not in_block

        if in_block:
            # Ищем закрывающий */
            if line[i] == '*' and i + 1 < n and line[i + 1] == '/':
                in_block = False
                i += 2
            else:
                i += 1
        elif in_str:
            # Ищем закрывающую ' (с учётом '' экранирования)
            if line[i] == "'":
                if i + 1 < n and line[i + 1] == "'":
                    i += 2
                else:
                    in_str = False
                    i += 1
            else:
                i += 1
        else:
            ch = line[i]

            if ch == '-' and i + 1 < n and line[i + 1] == '-':
                # Однострочный комментарий — до конца строки.
                if answer_start is not None and answer_start >= i:
                    covered = True
                    covered_in_str = False
                # Комментарий заканчивается на конце строки — state не меняется.
                return in_block, in_str, covered, covered_in_str

            elif ch == '/' and i + 1 < n and line[i + 1] == '*':
                if i + 2 < n and line[i + 2] == '+':
                    # Hint /*+ ... */ — НЕ комментарий. Пропускаем до */.
                    close = line.find('*/', i + 3)
                    i = (close + 2) if close != -1 else (i + 3)
                else:
                    in_block = True
                    i += 2

            elif ch == "'":
                # q-quoting: q' или Q' перед текущей ' (q — не часть идентификатора).
                if i >= 1 and line[i - 1] in ('q', 'Q') and (i < 2 or not (line[i - 2].isalnum() or line[i - 2] == '_')):
                    if i + 1 < n:
                        open_delim = line[i + 1]
                        close_delim = _Q_PAIRS.get(open_delim, open_delim)
                        terminator = close_delim + "'"
                        end_pos = line.find(terminator, i + 2)
                        if end_pos != -1:
                            # q-литерал закрыт на этой строке — пропускаем целиком.
                            if answer_start is not None and (i - 1) <= answer_start < (end_pos + 2):
                                covered = True
                                covered_in_str = True
                            i = end_pos + 2
                        else:
                            # Незакрытый q-литерал — переходим в строку.
                            if answer_start is not None and answer_start >= (i - 1):
                                covered = True
                                covered_in_str = True
                            in_str = True
                            i += 2
                    else:
                        in_str = True
                        i += 1
                else:
                    # Обычный строковый литерал.
                    in_str = True
                    i += 1
            else:
                i += 1

    # answer_start за пределами строки — охвачен, если строка завершилась в
    # комментарии/строке (состояние переноса).
    if answer_start is not None and answer_start >= n:
        if in_block or in_str:
            covered = True
            covered_in_str = in_str and not in_block

    return in_block, in_str, covered, covered_in_str


def is_in_comment_or_string(
    line: str,
    match_start: int,
    match_end: int,
    state: LexerState,
    debug_mode: bool = False,
) -> bool:
    """
    Возвращает True, если позиция [match_start, match_end) находится
    в комментарии или строковом литерале.

    ВАЖНО: НЕ мутирует `state`. Может вызываться многократно для одной
    строки — по одному разу на каждое regex-совпадение.

    debug_mode=True — для строк, содержащих &debug(...): переменные внутри
    строковых литералов считаются кодом (возвращаем False для позиции,
    охваченной именно строковым литералом).
    """
    line = line.rstrip('\r\n')
    _, _, covered, covered_in_str = _scan_line(
        line, state.in_block_comment, state.in_string_literal, match_start
    )
    if covered and covered_in_str and debug_mode:
        # &debug: литералы в такой строке считаются кодом.
        return False
    return covered


def advance_lexer_state(line: str, state: LexerState) -> None:
    """
    Обновляет `state` (in_block_comment, in_string_literal) по результатам
    разбора ВСЕЙ строки.

    Вызывается РОВНО ОДИН РАЗ на строку — после того, как для неё отработали
    все вызовы is_in_comment_or_string. НЕ зависит от match_start/match_end.
    """
    line = line.rstrip('\r\n')
    final_block, final_str, _, _ = _scan_line(
        line, state.in_block_comment, state.in_string_literal, None
    )
    state.in_block_comment = final_block
    state.in_string_literal = final_str


def is_line_fully_in_comment_or_string(line: str, state: LexerState) -> bool:
    """
    Упрощённая обёртка (работает со строкой целиком).

    НЕ мутирует `state`. Возвращает True, если вся строка (значимая её часть)
    находится внутри комментария или строкового литерала, начавшегося РАНЕЕ
    либо на этой же строке, — то есть в строке НЕТ кода вне комментариев/строк.
    """
    line = line.rstrip('\r\n')
    in_block = state.in_block_comment
    in_str = state.in_string_literal

    has_code = False
    i = 0
    n = len(line)

    while i < n:
        if in_block:
            if line[i] == '*' and i + 1 < n and line[i + 1] == '/':
                in_block = False
                i += 2
            else:
                i += 1
        elif in_str:
            if line[i] == "'":
                if i + 1 < n and line[i + 1] == "'":
                    i += 2
                else:
                    in_str = False
                    i += 1
            else:
                i += 1
        else:
            ch = line[i]
            if ch == '-' and i + 1 < n and line[i + 1] == '-':
                # Остаток — комментарий. Кодом считается только то, что ДО '--'.
                if line[:i].strip():
                    has_code = True
                break
            elif ch == '/' and i + 1 < n and line[i + 1] == '*':
                if i + 2 < n and line[i + 2] == '+':
                    # Hint — не комментарий: до и после него возможен код.
                    close = line.find('*/', i + 3)
                    if close != -1:
                        if line[:i].strip() or line[close + 2:].strip():
                            has_code = True
                        i = close + 2
                    else:
                        i += 3
                else:
                    # Начало блока: код — только до '/*'.
                    if line[:i].strip():
                        has_code = True
                    in_block = True
                    i += 2
            elif ch == "'":
                # Литерал: код — только до открывающей кавычки.
                if line[:i].strip():
                    has_code = True
                # q-quoting
                if i >= 1 and line[i - 1] in ('q', 'Q') and (i < 2 or not (line[i - 2].isalnum() or line[i - 2] == '_')):
                    if i + 1 < n:
                        open_delim = line[i + 1]
                        close_delim = _Q_PAIRS.get(open_delim, open_delim)
                        terminator = close_delim + "'"
                        end_pos = line.find(terminator, i + 2)
                        if end_pos != -1:
                            if line[end_pos + 2:].strip():
                                has_code = True
                            i = end_pos + 2
                        else:
                            in_str = True
                            i += 2
                    else:
                        in_str = True
                        i += 1
                else:
                    in_str = True
                    i += 1
            else:
                if ch not in (' ', '\t', '\r'):
                    has_code = True
                i += 1

    return not has_code
