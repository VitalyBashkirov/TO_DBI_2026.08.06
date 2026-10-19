# -*- coding: utf-8 -*-
"""DS_144d-e (E2): categories in TestGeneratorV2 - only for plpcheck sources."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / "SRC" / "gui_app.py"


def _read():
    return GUI.read_text(encoding="utf-8")


def _find_method(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def test_ds144d_e_categories_gated_by_sources():
    """In _run_test_generation: _cats gated by selected_file_codes."""
    src = _read()
    tree = ast.parse(src)
    fn = _find_method(tree, "_run_test_generation")
    assert fn is not None, "_run_test_generation not found"
    body = ast.get_source_segment(src, fn) or ""
    assert "_cats = list(getattr(self, " in body, "_cats assignment not found"
    assert "if _cats:" in body, "if _cats: not found"
    assert "if not selected_file_codes:" in body, "empty sources check not found"
    assert "_srcs_norm != {\x27plpcheck\x27}" in body, "_srcs_norm != plpcheck not found"
    assert "categories=_cats" in body, "categories=_cats not found"


def test_ds144d_e_old_direct_pass_removed():
    """Old categories=list(getattr(...)) or None line removed."""
    src = _read()
    old = "categories=list(getattr(self, \x27plpcheck_categories_filter\x27, [])) or None,"
    assert old not in src, "old direct pass categories=... still present"


def test_ds144d_e_logic_simulation():
    """Simulate _run_test_generation gating logic (no Tkinter)."""
    def simulate_cats(selected_file_codes, cats_input):
        _cats = list(cats_input) or None
        if _cats:
            if not selected_file_codes:
                _cats = None
            else:
                _srcs_norm = {str(s).split(".", 1)[0].lower() for s in selected_file_codes}
                if _srcs_norm != {"plpcheck"}:
                    _cats = None
        return _cats

    cats = ["STYLE.PREFIXES"]
    assert simulate_cats(None, cats) is None
    assert simulate_cats([], cats) is None
    assert simulate_cats(["plpcheck"], cats) == ["STYLE.PREFIXES"]
    assert simulate_cats(["plpcheck.X"], cats) == ["STYLE.PREFIXES"]
    assert simulate_cats(["v53"], cats) is None
    assert simulate_cats(["plpcheck", "v53"], cats) is None
    assert simulate_cats(["v53", "tds"], cats) is None
