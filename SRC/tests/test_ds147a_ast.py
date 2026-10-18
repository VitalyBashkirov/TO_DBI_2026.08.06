# -*- coding: utf-8 -*-
"""DS_147a: AST/поведенческие тесты tools/gen_test_plp.py."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GEN = PROJECT_ROOT / "tools" / "gen_test_plp.py"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))


def _load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_test_plp", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ds147a_file_exists():
    assert GEN.exists(), f"нет файла: {GEN}"


def test_ds147a_bom_false():
    b = GEN.read_bytes()
    assert not b.startswith(b"\xef\xbb\xbf"), "BOM недопустим"


def test_ds147a_ast_parse():
    src = GEN.read_text(encoding="utf-8")
    ast.parse(src)


def test_ds147a_parser_args():
    mod = _load_module()
    ap = mod._build_parser()
    ns = ap.parse_args(["-s", "PlpCheck"])
    assert ns.source == "PlpCheck"
    assert ns.rules is None
    assert ns.priorities is None
    assert ns.dry_run is False
    assert "generated_plp" in ns.out_dir


def test_ds147a_parser_rules_csv():
    mod = _load_module()
    ap = mod._build_parser()
    ns = ap.parse_args(["-s", "PlpCheck", "--rules", "a.B, a.C ,a.D"])
    assert mod._parse_csv(ns.rules) == ["a.B", "a.C", "a.D"]


def test_ds147a_parser_dry_run():
    mod = _load_module()
    ap = mod._build_parser()
    ns = ap.parse_args(["-s", "PlpCheck", "--dry-run"])
    assert ns.dry_run is True


def test_ds147a_parse_csv_empty():
    mod = _load_module()
    assert mod._parse_csv(None) is None
    assert mod._parse_csv("") is None
    assert mod._parse_csv(" , , ") is None


def test_ds147a_dry_run_no_plp(tmp_path):
    mod = _load_module()
    rc = mod.main(["-s", "PlpCheck", "-o", str(tmp_path), "--dry-run"])
    assert rc == 0
    plps = list(tmp_path.glob("*.plp"))
    logs = list(tmp_path.glob("gen_PlpCheck_*.log"))
    assert plps == [], f"dry-run не должен писать .plp, найдено: {plps}"
    assert len(logs) == 1, f"ожидался 1 лог, найдено: {logs}"


def test_ds147a_rules_filter_one(tmp_path):
    mod = _load_module()
    from analyzer.test_generator_v2 import TestGeneratorV2
    gen = TestGeneratorV2(
        rubricator_dir=PROJECT_ROOT / "DATA" / "Рубрикатор v5",
        sources=["PlpCheck"],
    )
    all_rules = gen.select_rules(None)
    assert all_rules, "в v5.json нет правил PlpCheck"
    code = all_rules[0]
    rc = mod.main(["-s", "PlpCheck", "-o", str(tmp_path), "--rules", code])
    assert rc == 0
    logs = list(tmp_path.glob("gen_PlpCheck_*.log"))
    assert len(logs) == 1
    text = logs[0].read_text(encoding="utf-8")
    assert "rules_total : 1" in text
    assert code in text
    plps = list(tmp_path.glob("*.plp"))
    assert len(plps) == 1


def test_ds147a_exit_1_on_unknown_source(tmp_path):
    mod = _load_module()
    rc = mod.main(["-s", "NONEXISTENT_SRC_ZZZ", "-o", str(tmp_path), "--dry-run"])
    assert rc == 1
    logs = list(tmp_path.glob("gen_NONEXISTENT_SRC_ZZZ_*.log"))
    assert len(logs) == 1


def test_ds147a_exit_1_on_missing_rubricator(tmp_path):
    mod = _load_module()
    rc = mod.main([
        "-s", "PlpCheck",
        "-o", str(tmp_path),
        "--rubricator-dir", str(tmp_path / "nope"),
        "--dry-run",
    ])
    assert rc == 1


def test_ds147a_log_is_multiline(tmp_path):
    mod = _load_module()
    rc = mod.main(["-s", "PlpCheck", "-o", str(tmp_path), "--dry-run"])
    assert rc == 0
    logs = list(tmp_path.glob("gen_PlpCheck_*.log"))
    assert len(logs) == 1
    text = logs[0].read_text(encoding="utf-8")
    assert chr(92) + "n" not in text, "в логе литералы \\n вместо переводов строк"
    assert text.count(chr(10)) > 10, "лог должен быть многострочным"
    assert "source      : PlpCheck" in text
