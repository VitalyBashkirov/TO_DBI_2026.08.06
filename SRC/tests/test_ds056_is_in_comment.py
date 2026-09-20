# -*- coding: utf-8 -*-
"""
DS_056A — тесты единого хелпера лексического разбора is_in_comment_or_string.

Кейсы 1–15 из раздела 5 задания DS_056A.
Тест 15 — обязательная проверка идемпотентности (is_in_comment_or_string НЕ
мутирует state).

Запуск:  python SRC\\tests\\test_ds056_is_in_comment.py
"""
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..' , 'SRC'))

from analyzer.lexer_state import (
    LexerState,
    is_in_comment_or_string,
    advance_lexer_state,
    is_line_fully_in_comment_or_string,
)

results = []


def check(num, desc, got, expected):
    ok = (got == expected)
    results.append((num, desc, ok, got, expected))
    status = "OK " if ok else "FAIL"
    print(f"[{status}] #{num:>2} {desc}  got={got} expected={expected}")


# --- Кейс 1: многострочный /* ... v := 1 ... */ (3 строки) ---
# По DS_056 (кейс 1) и алгоритму (раздел 3.2, п.2) средняя строка ВНУТРИ /* */ —
# В комментарии. (В таблице раздела 5 формулировка «не в комментарии» — см. отчёт.)
def case_1():
    lines = ["/* start comment", "   v := 1;", "*/"]
    st = LexerState()
    # строка 0: открыть комментарий
    advance_lexer_state(lines[0], st)
    assert st.in_block_comment is True, "после '/*' должны быть в блочном комментарии"
    # строка 1: v := 1 — позиция 'v'
    pos = lines[1].find('v')
    got = is_in_comment_or_string(lines[1], pos, pos + 1, st)
    check(1, "многострочный /* */ — средняя строка в комментарии", got, True)
    advance_lexer_state(lines[1], st)
    # строка 2: */ — закрыть
    advance_lexer_state(lines[2], st)
    assert st.in_block_comment is False, "после '*/' должны выйти из комментария"


# --- Кейс 2: &debug('P_PARAM' || P_PARAM), debug_mode=True ---
def case_2():
    line = "&debug('P_PARAM' || P_PARAM)"
    st = LexerState()
    pos = line.find('P_PARAM')  # первый P_PARAM — внутри '...'
    got_debug = is_in_comment_or_string(line, pos, pos + 7, st, debug_mode=True)
    check(2, "&debug: литерал в debug_mode = код (не строка)", got_debug, False)
    # вне debug_mode тот же символ — в строке
    got_nodebug = is_in_comment_or_string(line, pos, pos + 7, st, debug_mode=False)
    assert got_nodebug is True, "вне debug_mode символ внутри '...' = в строке"


# --- Кейс 3: -- &debug("x") — в комментарии ---
def case_3():
    line = '-- &debug("x")'
    st = LexerState()
    pos = line.find('&')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(3, "-- &debug(\"x\") — в комментарии", got, True)


# --- Кейс 4: /* &debug("x") */ — в комментарии ---
def case_4():
    line = '/* &debug("x") */'
    st = LexerState()
    pos = line.find('&')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(4, "/* &debug(\"x\") */ — в комментарии", got, True)


# --- Кейс 5: '&debug("x")' — в строке (вне debug_mode) ---
def case_5():
    line = 'v := \'&debug("x")\';'
    st = LexerState()
    pos = line.find('&')
    got = is_in_comment_or_string(line, pos, pos + 1, st, debug_mode=False)
    check(5, "'&debug(\"x\")' — в строке (вне debug_mode)", got, True)


# --- Кейс 6: v := 'it''s'; w := 1; — w не в строке ---
def case_6():
    line = "v := 'it''s'; w := 1;"
    st = LexerState()
    pos = line.find('w')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(6, "'it''s' — w после закрытого литерала не в строке", got, False)


# --- Кейс 7: v := q'[It's "test"]'; w := 1; — w не в строке ---
def case_7():
    line = "v := q'[It's \"test\"]'; w := 1;"
    st = LexerState()
    pos = line.find('w')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(7, "q'[It's \"test\"]' — w после q-литерала не в строке", got, False)


# --- Кейс 8: /* /* */ v := 1; */ — v не в комментарии (Oracle-семантика) ---
def case_8():
    line = "/* /* */ v := 1; */"
    st = LexerState()
    pos = line.find('v')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(8, "вложенные /* /* */ */ — v не в комментарии (Oracle)", got, False)


# --- Кейс 9: v := 1; -- trailing — trailing в комментарии ---
def case_9():
    line = "v := 1; -- trailing"
    st = LexerState()
    pos = line.find('trailing')
    got = is_in_comment_or_string(line, pos, pos + 8, st)
    check(9, "trailing после -- — в комментарии", got, True)


# --- Кейс 10: многострочный '... без закрытия + след. строка ---
def case_10():
    lines = ["v := 'DateTimeEnd := sysdate;", "w := 1;"]
    st = LexerState()
    advance_lexer_state(lines[0], st)
    assert st.in_string_literal is True, "незакрытая ' должна дать in_string_literal"
    pos = lines[1].find('w')
    got = is_in_comment_or_string(lines[1], pos, pos + 1, st)
    check(10, "многострочный '... — след. строка в строковом литерале", got, True)


# --- Кейс 11: v := q'{a''b}'; w := 1; — w не в строке ---
def case_11():
    line = "v := q'{a''b}'; w := 1;"
    st = LexerState()
    pos = line.find('w')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(11, "q'{a''b}' — w после q-литерала не в строке", got, False)


# --- Кейс 12: v := 'a"b'; w := 1; — w не в строке ---
def case_12():
    line = "v := 'a\"b'; w := 1;"
    st = LexerState()
    pos = line.find('w')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(12, "\"...\" не терминатор — w после 'a\"b' не в строке", got, False)


# --- Кейс 13: CRLF: v := 1; -- x\\r\\nw := 2; — w не в комментарии ---
def case_13():
    # \r в конце не должен ломать определение конца строки
    line1 = "v := 1; -- x\r\n"
    line2 = "w := 2;\r\n"
    st = LexerState()
    advance_lexer_state(line1, st)
    assert st.in_block_comment is False and st.in_string_literal is False, \
        "после строки с -- состояние переноса пустое"
    pos = line2.find('w')
    got = is_in_comment_or_string(line2, pos, pos + 1, st)
    check(13, "CRLF: w := 2; на след. строке не в комментарии", got, False)


# --- Кейс 14: /*+ hint */ v := 1; — v не в комментарии (hint) ---
def case_14():
    line = "/*+ hint */ v := 1;"
    st = LexerState()
    pos = line.find('v')
    got = is_in_comment_or_string(line, pos, pos + 1, st)
    check(14, "/*+ hint */ — v после хинта не в комментарии", got, False)


# --- Кейс 15: идемпотентность (is_in_comment_or_string НЕ мутирует state) ---
def case_15():
    line = "v := 1; -- x"
    st = LexerState()
    pos_v = line.find('v')
    pos_x = line.find('x')
    first = is_in_comment_or_string(line, pos_v, pos_v + 1, st)   # v — код
    second = is_in_comment_or_string(line, pos_x, pos_x + 1, st)  # x — комментарий
    ok = (first is False and second is True
          and st.in_block_comment is False and st.in_string_literal is False)
    check(15, "идемпотентность: state не мутируется, v=код, x=коммент",
          ok, True)


def main():
    for fn in (case_1, case_2, case_3, case_4, case_5, case_6, case_7,
               case_8, case_9, case_10, case_11, case_12, case_13,
               case_14, case_15):
        fn()

    passed = sum(1 for _, _, ok, _, _ in results if ok)
    total = len(results)
    print("-" * 60)
    print(f"ИТОГ: {passed}/{total} PASSED")
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
