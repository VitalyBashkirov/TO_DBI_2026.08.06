# -*- coding: utf-8 -*-
"""DS_147b: AST/поведенческие тесты tools/validate_gen_plp.py."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GEN = PROJECT_ROOT / "tools" / "validate_gen_plp.py"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))


def _load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("validate_gen_plp", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ds147b_file_exists():
    assert GEN.exists(), f"нет файла: {GEN}"


def test_ds147b_bom_false():
    b = GEN.read_bytes()
    assert not b.startswith(b"\xef\xbb\xbf"), "BOM недопустим"


def test_ds147b_ast_parse():
    ast.parse(GEN.read_text(encoding="utf-8"))


def test_ds147b_re_rule_correct():
    mod = _load_module()
    pat = mod.RE_RULE.pattern
    assert "\\\\\\\\s" not in pat, f"двойной бэкслеш в RE_RULE: {pat!r}"
    m = mod.RE_RULE.match("-- Правило: plpcheck.SUBOPTIMAL_QUERY_WROWNUM")
    assert m is not None
    assert m.group(1) == "plpcheck.SUBOPTIMAL_QUERY_WROWNUM"


def test_ds147b_re_rule_no_match_other():
    mod = _load_module()
    assert mod.RE_RULE.match("-- Описание: что-то") is None


def test_ds147b_parse_csv():
    mod = _load_module()
    assert mod._parse_csv(None) is None
    assert mod._parse_csv("") is None
    assert mod._parse_csv(" , ") is None
    assert mod._parse_csv("a.B, a.C") == ["a.B", "a.C"]


def test_ds147b_collect_plp_dir(tmp_path):
    mod = _load_module()
    (tmp_path / "a.plp").write_text("x", encoding="utf-8")
    (tmp_path / "b.plp").write_text("x", encoding="utf-8")
    (tmp_path / "c.txt").write_text("x", encoding="utf-8")
    got = mod._collect_plp(str(tmp_path))
    assert len(got) == 2
    assert all(p.suffix == ".plp" for p in got)


def test_ds147b_collect_plp_file(tmp_path):
    mod = _load_module()
    p = tmp_path / "a.plp"
    lines = [
        "-- ===",
        "-- Правило: plpcheck.X",
        "-- Правило: plpcheck.Y",
        "PUBLIC PROCEDURE p IS",
        "BEGIN NULL; END;",
    ]
    p.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    got = mod._extract_rules_from_plp(p)
    assert got == ["plpcheck.X", "plpcheck.Y"]


def test_ds147b_no_plp(tmp_path):
    mod = _load_module()
    rc = mod.main(["-d", str(tmp_path)])
    assert rc == 1


def test_ds147b_parser_args():
    mod = _load_module()
    ns = mod._build_parser().parse_args(["-d", "DATA/generated_plp"])
    assert ns.dir == "DATA/generated_plp"
    assert ns.rules is None
    assert ns.out_log is None

def test_ds147b_extract_rules(tmp_path):
    mod = _load_module()
    p = tmp_path / "a.plp"
    lines = [
        "-- ===",
        "-- Правило: plpcheck.X",
        "-- Правило: plpcheck.Y",
        "PUBLIC PROCEDURE p IS",
        "BEGIN NULL; END;",
    ]
    p.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    got = mod._extract_rules_from_plp(p)
    assert got == ["plpcheck.X", "plpcheck.Y"]

