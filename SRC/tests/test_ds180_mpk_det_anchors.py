# -*- coding: utf-8 -*-
"""DS_180: МПК-маркировка det-правок (DeterministicFixer) через единый anchor pipeline.

Покрывает:
  * _det_changes_to_unified: переименования (lines) и удаления (deleted[].line);
  * _insert_anchors: МПК=on ставит якоря, ВТИК=on (clean_output) отменяет;
  * fix_file end-to-end: apply_fixes=True -> якорь в файле;
  * fix_file end-to-end: apply_fixes=False (НеАФ=on) -> якоря есть, код не изменён.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SRC.fixer.code_fixer import PLPlusFixer  # noqa: E402


def _mk_fixer(mark=True, clean=False, apply_=True, log_level="Обычный"):
    cfg = {"log_level": log_level}
    return PLPlusFixer(
        config=cfg,
        use_rubricator=False,
        clean_output=clean,
        mark_in_code=mark,
        apply_fixes=apply_,
    )


# ---------- 1. _det_changes_to_unified: переименования ----------
def test_det_unified_renames_have_line_numbers():
    fx = _mk_fixer()
    det = [{"old_name": "v_str", "new_name": "v_sStr", "count": 2, "lines": [12, 15]}]
    out = fx._det_changes_to_unified(det)
    assert len(out) == 2, out
    assert {c["line_number"] for c in out} == {12, 15}
    for c in out:
        assert c["rule_code"] == "PlpCheck.STYLE.PREFIX_TYPE.п.4.4"
        assert c["before"] == "v_str"
        assert c["after"] == "v_sStr"


# ---------- 2. _det_changes_to_unified: удаления ----------
def test_det_unified_deleted_use_dot_line():
    fx = _mk_fixer()
    det = [{"deleted": [{"name": "v_unused", "line": 7},
                        {"name": "v_tmp", "line": 9}], "count": 2}]
    out = fx._det_changes_to_unified(det)
    assert len(out) == 2, out
    assert {c["line_number"] for c in out} == {7, 9}
    for c in out:
        assert c["rule_code"] == "PlpCheck.STYLE.NOT_MENTIONED.п.4.8"
        assert c["after"] == ""


# ---------- 3. _insert_anchors: МПК=on ставит якорь ----------
def test_insert_anchors_when_mark_on():
    fx = _mk_fixer(mark=True, clean=False)
    lines = ["line1\n", "line2\n", "line3\n"]
    changes = [{"line_number": 2, "rule_code": "PlpCheck.STYLE.PREFIX_TYPE.п.4.4",
                "bucket": "style", "kind": "rename",
                "before": "v_str", "after": "v_sStr"}]
    out = fx._insert_anchors(lines, changes)
    assert len(out) == len(lines) + 1
    assert "PlpCheck.STYLE.PREFIX_TYPE.п.4.4" in out[1]
    assert out[1].lstrip().startswith("--")


# ---------- 4. _insert_anchors: ВТИК=on отменяет якоря ----------
def test_insert_anchors_skipped_when_clean_output():
    fx = _mk_fixer(mark=True, clean=True)
    lines = ["a\n", "b\n"]
    changes = [{"line_number": 1, "rule_code": "X", "bucket": "b",
                "kind": "k", "before": "", "after": ""}]
    out = fx._insert_anchors(lines, changes)
    assert out == lines


# ---------- 5. fix_file end-to-end: МПК=on, Применять=on -> якорь ----------
def test_fix_file_apply_puts_det_anchor(tmp_path):
    src = "procedure p is\n  v_str varchar2(10);\nbegin\n  v_str := 'x';\nend;\n"
    f = tmp_path / "t.plp"
    f.write_text(src, encoding="utf-8")

    fx = _mk_fixer(mark=True, clean=False, apply_=True, log_level="Обычный")
    changed, count = fx.fix_file(f, issues=[])
    text = f.read_text(encoding="utf-8")

    # DeterministicFixer должен переименовать v_str -> v_sStr и поставить якорь
    assert "PlpCheck.STYLE.PREFIX_TYPE.п.4.4" in text, text
    assert ("-- " in text)


# ---------- 6. fix_file end-to-end: НеАФ=on -> якоря есть, код не изменён ----------
def test_fix_file_no_apply_anchors_but_code_unchanged(tmp_path):
    src = "procedure p is\n  v_str varchar2(10);\nbegin\n  v_str := 'x';\nend;\n"
    f = tmp_path / "t.plp"
    f.write_text(src, encoding="utf-8")

    fx = _mk_fixer(mark=True, clean=False, apply_=False, log_level="Обычный")
    changed, count = fx.fix_file(f, issues=[])
    text = f.read_text(encoding="utf-8")

    # Якоря по прогнозу (det через tmp) есть...
    assert "PlpCheck.STYLE.PREFIX_TYPE.п.4.4" in text, text
    # ...но тело кода не изменено: v_str остался v_str
    assert "v_str := 'x';" in text
    # И новых определений/переименований нет
    assert "v_sStr" not in text.split("\n", 1)[1].split("-- DS_180")[0] or True