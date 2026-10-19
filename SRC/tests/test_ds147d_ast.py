# -*- coding: utf-8 -*-
"""DS_147d: гибридный фильтр categories (набор A ∪ набор B)."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TG = PROJECT_ROOT / "SRC" / "analyzer" / "test_generator_v2.py"
GEN = PROJECT_ROOT / "tools" / "gen_test_plp.py"
GUI = PROJECT_ROOT / "SRC" / "gui_app.py"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "SRC"))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))


def _tree(p):
    return ast.parse(p.read_text(encoding="utf-8"))


def _load_gen():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_test_plp_d", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rules_total(log_path):
    text = log_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("rules_total :"):
            return int(line.split(":", 1)[1].strip())
    return -1


def test_ds147d_tg_bom_false():
    assert not TG.read_bytes().startswith(b"\xef\xbb\xbf")


def test_ds147d_tg_ast_parse():
    _tree(TG)


def test_ds147d_tg_has_hybrid_filter():
    src = TG.read_text(encoding="utf-8")
    assert "PLPCHECK_RULE_TO_CATEGORY" in src
    assert "subcategory" in src
    assert "categories" in src


def test_ds147d_gen_bom_false():
    assert not GEN.read_bytes().startswith(b"\xef\xbb\xbf")


def test_ds147d_gen_ast_parse():
    _tree(GEN)


def test_ds147d_gen_has_categories_arg():
    src = GEN.read_text(encoding="utf-8")
    assert "--categories" in src
    assert "categories_csv" in src


def test_ds147d_gui_bom_false():
    assert not GUI.read_bytes().startswith(b"\xef\xbb\xbf")


def test_ds147d_gui_ast_parse():
    _tree(GUI)


def test_ds147d_gui_passes_categories():
    src = GUI.read_text(encoding="utf-8")
    assert "categories=_cats," in src, "categories=_cats, not found (DS_144d-e)"
    assert "plpcheck_categories_filter" in src


def test_ds147d_hybrid_filter_a(tmp_path):
    mod = _load_gen()
    rc = mod.main(["-s", "PlpCheck", "-o", str(tmp_path), "--categories", "STYLE.PREFIXES", "--dry-run"])
    assert rc == 0
    logs = list(tmp_path.glob("gen_PlpCheck_*.log"))
    assert len(logs) == 1
    assert _rules_total(logs[0]) == 20


def test_ds147d_hybrid_filter_b(tmp_path):
    mod = _load_gen()
    rc = mod.main(["-s", "PlpCheck", "-o", str(tmp_path), "--categories", "DBI.PERFORMANCE", "--dry-run"])
    assert rc == 0
    logs = list(tmp_path.glob("gen_PlpCheck_*.log"))
    assert _rules_total(logs[0]) == 17


def test_ds147d_no_filter_v53(tmp_path):
    mod = _load_gen()
    rc = mod.main(["-s", "v53", "-o", str(tmp_path), "--dry-run"])
    assert rc == 0
    logs = list(tmp_path.glob("gen_v53_*.log"))
    assert _rules_total(logs[0]) == 98
