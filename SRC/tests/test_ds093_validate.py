# -*- coding: utf-8 -*-
"""DS_093 - testy validate_batch_response: under-return razreshen.

t1..t8 - 8 keysov (sm. DS_093 S5).
Zapusk:  python SRC/tests/test_ds093_validate.py
"""
import sys
import os

if __name__ == '__main__':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'tools')
sys.path.insert(0, TOOLS)

from ai_local_worker import validate_batch_response

results = []


def check(num, desc, got, expected):
    ok = (got == expected)
    results.append((num, desc, ok, got, expected))
    status = "OK " if ok else "FAIL"
    print(f"[{status}] #{num:>2} {desc}  got={got} expected={expected}")


def test_t1_empty_list():
    check(1, "parsed = [] -> False",
          validate_batch_response([], [{'line': 1}, {'line': 2}]), False)


def test_t2_none():
    check(2, "parsed = None -> False",
          validate_batch_response(None, [{'line': 1}]), False)


def test_t3_under_return():
    batch = [{'line': 1}, {'line': 2}, {'line': 3}]
    parsed = [{'line': 1, 'after': 'x'}]
    check(3, "under-return: len(parsed) < len(batch) -> True",
          validate_batch_response(parsed, batch), True)


def test_t4_exact_match():
    batch = [{'line': 1}, {'line': 2}]
    parsed = [{'line': 1, 'after': 'x'}, {'line': 2, 'after': 'y'}]
    check(4, "len(parsed) == len(batch) -> True",
          validate_batch_response(parsed, batch), True)


def test_t5_over_return():
    batch = [{'line': 1}, {'line': 2}]
    parsed = [{'line': 1, 'after': 'x'}, {'line': 2, 'after': 'y'}, {'line': 3, 'after': 'z'}]
    check(5, "over-return: len(parsed) > len(batch) -> False",
          validate_batch_response(parsed, batch), False)


def test_t6_line_not_in_batch():
    batch = [{'line': 1}, {'line': 2}]
    parsed = [{'line': 99, 'after': 'x'}]
    check(6, "line ne iz batch -> False",
          validate_batch_response(parsed, batch), False)


def test_t7_item_not_dict():
    batch = [{'line': 1}, {'line': 2}]
    parsed = ['not_a_dict']
    check(7, "item ne dict -> False",
          validate_batch_response(parsed, batch), False)


def test_t8_line_absent():
    batch = [{'line': 1}, {'line': 2}]
    parsed = [{'after': 'x', 'confidence': 0.9}]
    check(8, "line otsutstvuet -> True (line ne trebuetsya)",
          validate_batch_response(parsed, batch), True)


def main():
    for fn in (test_t1_empty_list, test_t2_none, test_t3_under_return,
               test_t4_exact_match, test_t5_over_return, test_t6_line_not_in_batch,
               test_t7_item_not_dict, test_t8_line_absent):
        fn()
    passed = sum(1 for _, _, ok, _, _ in results if ok)
    total = len(results)
    print("-" * 60)
    print(f"ITOG: {passed}/{total} PASSED")
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())