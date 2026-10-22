# -*- coding: utf-8 -*-
"""DS_179: тесты _check_plp_suboptimal_wrownum (plpcheck.SUBOPTIMAL_QUERY_WROWNUM)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analyzer.scanner import PLPlusScanner  # noqa: E402


def _make_scanner():
    return PLPlusScanner.__new__(PLPlusScanner)


def test_positive_exit_in_for_loop():
    lines = [
        "procedure p is",
        "  v_dBeg number;",
        "begin",
        "  for (select u(u.DATE_BEGIN : C_D1) in ::[RKO] where u.ACCOUNT = p_acc_id) loop",
        "    v_dBeg := u.C_D1;",
        "    exit;",
        "  end loop;",
        "end;",
    ]
    sc = _make_scanner()
    issues = sc._check_plp_suboptimal_wrownum(lines)
    assert len(issues) == 1, issues
    line_num, msg, bad_code, b_start, b_end = issues[0]
    assert line_num == 4
    assert b_start == 4
    assert b_end >= 7
    assert "for" in bad_code.lower()


def test_negative_with_fetch():
    lines = [
        "  for (select u(u.DATE_BEGIN : C_D1) in ::[RKO] where u.ACCOUNT = p_acc_id fetch 1) loop",
        "    v_dBeg := u.C_D1;",
        "    exit;",
        "  end loop;",
    ]
    sc = _make_scanner()
    assert sc._check_plp_suboptimal_wrownum(lines) == []


def test_negative_with_rownum():
    lines = [
        "  for (select u(u.DATE_BEGIN : C_D1) in ::[RKO] where u.ACCOUNT = p_acc_id and rownum = 1) loop",
        "    v_dBeg := u.C_D1;",
        "    exit;",
        "  end loop;",
    ]
    sc = _make_scanner()
    assert sc._check_plp_suboptimal_wrownum(lines) == []


def test_negative_with_offset():
    lines = [
        "  for (select u(u.DATE_BEGIN : C_D1) in ::[RKO] where u.ACCOUNT = p_acc_id offset 0 rows) loop",
        "    v_dBeg := u.C_D1;",
        "    exit;",
        "  end loop;",
    ]
    sc = _make_scanner()
    assert sc._check_plp_suboptimal_wrownum(lines) == []


def test_negative_without_exit():
    lines = [
        "  for (select u(u.DATE_BEGIN : C_D1) in ::[RKO] where u.ACCOUNT = p_acc_id) loop",
        "    v_dBeg := u.C_D1;",
        "  end loop;",
    ]
    sc = _make_scanner()
    assert sc._check_plp_suboptimal_wrownum(lines) == []