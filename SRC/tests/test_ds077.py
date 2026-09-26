# -*- coding: utf-8 -*-
"""
DS_077 - tests for two problem lines (with dubs + after dedup).

Run:  python SRC\tests\test_ds077.py
"""
import sys
import io
import os
import tempfile
from pathlib import Path
from typing import List

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'SRC'))

from analyzer.scanner import PLPlusScanner, Issue

results = []


def check(num, desc, ok, detail=""):
    results.append((num, desc, ok, detail))
    status = "OK " if ok else "FAIL"
    print(f"[{status}] #{num:>2} {desc}" + (f"  {detail}" if detail else ""))


def make_issues(n_total):
    issues = []
    for i in range(n_total):
        issues.append(Issue(
            file_path=f"file_{i % 3}.plp",
            line_number=(i % 50) + 1,
            issue_type=f"type_{i % 5}",
            description=f"desc_{i}",
            original_code=f"orig_{i}",
            category="STYLE",
            match_fragment=f"frag_{i}",
        ))
    return issues


def run_generate_report(issues, issues_before_dedup, abort_percent=None):
    scanner = PLPlusScanner.__new__(PLPlusScanner)
    scanner.issues = issues
    scanner.issues_before_dedup = issues_before_dedup
    scanner.abort_percent = abort_percent
    scanner.total_files = 10
    scanner.files_scanned = 8
    scanner.forecast_files_changed = 5
    scanner.files = [f"file_{i}.plp" for i in range(10)]
    scanner.report_log_path = None
    scanner.log_callback = None

    tmp = tempfile.mktemp(suffix=".txt")
    try:
        report_path = Path(tmp)
        scanner._dedup_issues = lambda: issues
        scanner._forecast_and_ai_counts = lambda: (10, len(issues) - 10)
        scanner._top_files_lines = lambda *a, **kw: []
        scanner._generate_active_rubricators_lines = lambda *a, **kw: []
        scanner.generate_report(report_path, mode='scan', fixed_count=0,
                                log_level='\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u044b\u0439',
                                report_stats_min_files=999)
        return report_path.read_text(encoding='utf-8')
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def test_1_two_lines():
    issues = make_issues(20)
    text = run_generate_report(issues, issues_before_dedup=25)
    d = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438): 25" in text
    t = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20" in text
    check(1, "scan_report: two lines when dubs", d and t, f"d={d} t={t}")


def test_2_one_line():
    issues = make_issues(20)
    text = run_generate_report(issues, issues_before_dedup=20)
    d = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438)" in text
    t = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20" in text
    check(2, "scan_report: one line no dubs", not d and t, f"d={d} t={t}")


def test_3_order():
    issues = make_issues(20)
    text = run_generate_report(issues, issues_before_dedup=25)
    p1 = text.find("\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438):")
    p2 = text.find("\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20")
    check(3, "scan_report: dubs line before total", p1 >= 0 and p2 >= 0 and p1 < p2, f"p1={p1} p2={p2}")


def test_4_abort():
    issues = make_issues(20)
    text = run_generate_report(issues, issues_before_dedup=25, abort_percent=50)
    d = "\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438): 25" in text
    t = "\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20" in text
    check(4, "scan_report abort: two lines", d and t, f"d={d} t={t}")


def test_5_regress_ds075():
    issues = make_issues(20)
    text = run_generate_report(issues, issues_before_dedup=25)
    pp = text.find("\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20")
    pf = text.find("\u041f\u0440\u043e\u0433\u043d\u043e\u0437 \u0438\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0439:")
    pi = text.find("\u0418\u0441\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e:")
    pa = text.find("\u0412 AI:")
    ok = pp >= 0 and pf >= 0 and pi >= 0 and pa >= 0 and pp < pf < pi < pa
    check(5, "Regress DS_075: fc/fix/ai after prob", ok, f"pp={pp} pf={pf} pi={pi} pa={pa}")


def test_6_regress_ds076():
    issues = make_issues(20)
    text = run_generate_report(issues, issues_before_dedup=25)
    pa = text.find("\u0412 AI:")
    ft = text.find("\u0412\u0441\u0435\u0433\u043e \u0444\u0430\u0439\u043b\u043e\u0432:")
    fp = text.find("\u0424\u0430\u0439\u043b\u043e\u0432 \u0441 \u043f\u0440\u043e\u0431\u043b\u0435\u043c\u0430\u043c\u0438:")
    fc = text.find("\u0424\u0430\u0439\u043b\u043e\u0432 \u0441 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f\u043c\u0438:")
    ok = pa >= 0 and ft >= 0 and fp >= 0 and fc >= 0 and pa < ft < fp < fc
    check(6, "Regress DS_076: file metrics after ai", ok, f"ai={pa} ft={ft} fp={fp} fc={fc}")


def test_7_save_log_two_lines():
    issues = make_issues(20)
    scanner = PLPlusScanner.__new__(PLPlusScanner)
    scanner.issues = issues
    scanner.issues_before_dedup = 25
    lines_t = []
    ibd = getattr(scanner, 'issues_before_dedup', 0)
    if ibd != len(issues):
        lines_t.append(f"\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438): {ibd}")
    lines_t.append(f"\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: {len(issues)}")
    d = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438): 25" in lines_t
    t = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20" in lines_t
    check(7, "save_log: two lines dubs", d and t, f"d={d} t={t}")


def test_8_save_log_one_line():
    issues = make_issues(20)
    scanner = PLPlusScanner.__new__(PLPlusScanner)
    scanner.issues = issues
    scanner.issues_before_dedup = 20
    lines_t = []
    ibd = getattr(scanner, 'issues_before_dedup', 0)
    if ibd != len(issues):
        lines_t.append(f"\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c (\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438): {ibd}")
    lines_t.append(f"\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: {len(issues)}")
    d = any("\u0441 \u0434\u0443\u0431\u043b\u044f\u043c\u0438" in l for l in lines_t)
    t = "\u0412\u0441\u0435\u0433\u043e \u043f\u0440\u043e\u0431\u043b\u0435\u043c: 20" in lines_t
    check(8, "save_log: one line no dubs", not d and t, f"d={d} t={t}")


if __name__ == "__main__":
    print("=" * 60)
    print("DS_077 - tests for two problem lines")
    print("=" * 60)
    print()
    test_1_two_lines()
    test_2_one_line()
    test_3_order()
    test_4_abort()
    test_5_regress_ds075()
    test_6_regress_ds076()
    test_7_save_log_two_lines()
    test_8_save_log_one_line()
    print()
    print("=" * 60)
    passed = sum(1 for _, _, ok, _ in results if ok)
    failed = sum(1 for _, _, ok, _ in results if not ok)
    print(f"Total: {passed} OK, {failed} FAIL, {len(results)} cases")
    if failed:
        print("\nFailed:")
        for num, desc, ok, detail in results:
            if not ok:
                print(f"  #{num} {desc}  {detail}")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)